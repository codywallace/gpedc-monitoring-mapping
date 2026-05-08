"""
Streaming scanner for IATI 2.x activity files on disk.

The scanner reads IATI activity XML from a local mirror under
``data/iati-data/datasets/{publisher-slug}/*.xml`` (clone of
https://bulk-data.iatistandard.org/).

Registry indices (reporting orgs, dataset listings) are fetched **dynamically**
over HTTPS at runtime — they are not cached on disk — so analyses always run
against a fresh registry snapshot:

  * https://bulk-data.iatistandard.org/reporting-orgs   (~2 MB JSON)
  * https://bulk-data.iatistandard.org/datasets-full    (~33 MB JSON)

The scanner is deliberately tolerant — IATI files in the wild contain
malformed UTF-8, BOMs, version 1.x dialects, mid-stream encoding errors,
and stale identifiers. We do best-effort ``iterparse`` and skip files that
fail to parse rather than aborting an entire publisher.

The output is a flat dict of presence counts per activity. Polars notebooks
in ``notebooks/`` aggregate these into per-publisher metrics.
"""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

log = logging.getLogger(__name__)


# Project-relative paths — assume notebook / script CWD is repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCES = PROJECT_ROOT / "data"
IATI_DATA_DIR = DATA_SOURCES / "iati-data"
DATASETS_DIR = IATI_DATA_DIR / "datasets"
DONOR_MAPPING_PATH = DATA_SOURCES / "iati_donor_mapping.xlsx"

# IATI bulk-data registry indices — fetched on demand, not cached on disk.
IATI_REPORTING_ORGS_URL = "https://bulk-data.iatistandard.org/reporting-orgs"
IATI_DATASETS_FULL_URL = "https://bulk-data.iatistandard.org/datasets-full"

USER_AGENT = "gpedc-iati-mapping/0.1 (+ https://github.com/gpedc)"


# ---------------------------------------------------------------------------
# Donor mapping (the official MR4 list — 99 reporting-org refs across 78 DPs)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DonorMapping:
    reportingorg_ref: str
    reportingorg_name: str
    donor_code: int | None
    donor_name: str
    comments: str | None = None


def load_donor_mapping(path: Path | None = None) -> list[DonorMapping]:
    """Load the GPEDC official donor → IATI reporting-org-ref map."""
    import openpyxl  # local import keeps notebooks light if unused

    path = path or DONOR_MAPPING_PATH
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    out: list[DonorMapping] = []
    for r in rows[1:]:
        if not any(r):
            continue
        ref = str(r[0]).strip() if r[0] is not None else ""
        if not ref:
            continue
        out.append(
            DonorMapping(
                reportingorg_ref=ref,
                reportingorg_name=(r[1] or "").strip(),
                donor_code=int(r[2]) if r[2] is not None else None,
                donor_name=(r[3] or "").strip(),
                comments=(r[4] or "").strip() or None,
            )
        )
    return out


# ---------------------------------------------------------------------------
# IATI registry — dynamic fetch (no on-disk cache)
# ---------------------------------------------------------------------------


def _fetch_json(
    url: str,
    *,
    timeout: float = 60.0,
    retries: int = 3,
    backoff: float = 2.0,
) -> dict:
    """
    HTTP GET ``url`` and parse JSON. Logs progress and retries transient errors.

    Raises the last exception if all retries fail. Returns the parsed JSON
    document — *never* writes to disk.
    """
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        t0 = time.time()
        try:
            log.debug("fetching %s (attempt %d/%d)", url, attempt, retries)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read()
            data = json.loads(payload)
            log.info(
                "fetched %s — %.1f KB in %.1fs",
                url,
                len(payload) / 1024,
                time.time() - t0,
            )
            return data
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            last_err = e
            log.warning(
                "fetch failed (attempt %d/%d) for %s: %s — retrying in %.1fs",
                attempt,
                retries,
                url,
                e,
                backoff,
            )
            time.sleep(backoff)
            backoff *= 2
    assert last_err is not None
    log.error("giving up on %s after %d attempts", url, retries)
    raise last_err


def load_reporting_orgs() -> list[dict]:
    """
    Fetch the IATI reporting-orgs registry index from
    https://bulk-data.iatistandard.org/reporting-orgs and return the list.

    The response is held in memory only for the duration of the run.
    """
    payload = _fetch_json(IATI_REPORTING_ORGS_URL)
    orgs = payload.get("reporting_orgs") or []
    created = payload.get("index_created", "?")
    log.info("reporting-orgs index — %d orgs, snapshot %s", len(orgs), created)
    return orgs


def load_datasets_index() -> list[dict]:
    """
    Fetch the IATI datasets-full index from
    https://bulk-data.iatistandard.org/datasets-full and return the list.

    Use this when you need per-dataset metadata (XML URLs, hashes, last-known-good
    timestamps). The response is held in memory only.
    """
    payload = _fetch_json(IATI_DATASETS_FULL_URL)
    datasets = payload.get("datasets") or []
    created = payload.get("index_created", "?")
    log.info("datasets-full index — %d datasets, snapshot %s", len(datasets), created)
    return datasets


def publisher_paths_for_org_ref(
    org_ref: str,
    reporting_orgs: list[dict] | None = None,
    datasets_dir: Path | None = None,
) -> list[Path]:
    """
    Map an IATI organisation_identifier (e.g. "XM-DAC-2-10") to one or more
    on-disk publisher directories under datasets/.

    The bulk-data layout uses publisher *slugs* (short_name) for folder names
    rather than the org_ref. We resolve via the reporting-orgs registry.
    """
    reporting_orgs = reporting_orgs or load_reporting_orgs()
    datasets_dir = datasets_dir or DATASETS_DIR
    matches: list[Path] = []
    seen_slugs: set[str] = set()
    for ro in reporting_orgs:
        if (ro.get("organisation_identifier") or "").strip() != org_ref:
            continue
        slug = (ro.get("short_name") or "").strip().lower()
        if not slug or slug in seen_slugs:
            continue
        candidate = datasets_dir / slug
        if candidate.is_dir():
            matches.append(candidate)
            seen_slugs.add(slug)
    return matches


def iter_publisher_files(publisher_dir: Path) -> Iterator[Path]:
    """Yield .xml files in a publisher directory (sorted by size, smallest first)."""
    files = [p for p in publisher_dir.glob("*.xml") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_size)
    yield from files


# ---------------------------------------------------------------------------
# Per-activity feature extractor
# ---------------------------------------------------------------------------

# Codelist references — used for binning, not validation.
TX_CODE_NAMES: dict[str, str] = {
    "1": "Incoming Funds",
    "2": "Outgoing Commitment",
    "3": "Disbursement",
    "4": "Expenditure",
    "5": "Interest Payment",
    "6": "Loan Repayment",
    "7": "Reimbursement",
    "8": "Purchase of Equity",
    "9": "Sale of Equity",
    "10": "Credit Guarantee",
    "11": "Incoming Commitment",
    "12": "Outgoing Pledge",
    "13": "Incoming Pledge",
}

OTHER_ID_NAMES: dict[str, str] = {
    "A1": "Reporting Org Internal",
    "A2": "CRS Activity Identifier",
    "A3": "Previous Activity Identifier",
    "A9": "Other Activity Identifier",
    "B1": "Previous Reporting Org",
    "B9": "Other Organisation",
}

POLICY_MARKER_NAMES: dict[str, str] = {
    "1": "Gender Equality",
    "2": "Aid to Environment",
    "3": "Participatory Dev / Good Governance",
    "4": "Trade Development",
    "5": "Aid Targeting CBD",
    "6": "Aid Targeting UNFCCC Mitigation",
    "7": "Aid Targeting UNFCCC Adaptation",
    "8": "Aid Targeting UNCCD",
    "9": "Reproductive Maternal Newborn Child Health",
    "10": "Disaster Risk Reduction",
    "11": "Disability",
    "12": "Nutrition",
}


def _attr(elt: etree._Element, name: str) -> str | None:
    v = elt.get(name)
    if v is None:
        return None
    v = v.strip()
    return v or None


def extract_activity_features(activity: etree._Element, *, year_now: int) -> dict:
    """
    Compute presence / counts for one <iati-activity> element. Returns a flat
    dict suitable for direct construction of a Polars DataFrame.

    Counts are per-activity. For codelist-coded children we keep the raw set
    of distinct codes seen (joined as a comma-separated string) so notebooks
    can compute distributions without re-parsing XML.
    """
    iid_elt = activity.find("iati-identifier")
    iid = (iid_elt.text or "").strip() if iid_elt is not None else ""

    rep_org = activity.find("reporting-org")
    rep_ref = _attr(rep_org, "ref") if rep_org is not None else None
    rep_type = _attr(rep_org, "type") if rep_org is not None else None
    secondary_reporter = _attr(rep_org, "secondary-reporter") if rep_org is not None else None

    activity_status = (
        _attr(activity.find("activity-status"), "code")
        if activity.find("activity-status") is not None
        else None
    )
    default_currency = _attr(activity, "default-currency")
    hierarchy = _attr(activity, "hierarchy")

    # other-identifier
    oids = activity.findall("other-identifier")
    oid_types = [t for t in (_attr(e, "type") for e in oids) if t]
    has_a1 = "A1" in oid_types
    has_a2 = "A2" in oid_types
    has_a9 = "A9" in oid_types

    # participating-org by role
    poi = activity.findall("participating-org")
    po_roles = [r for r in (_attr(e, "role") for e in poi) if r]
    n_po_funding = po_roles.count("1")
    n_po_accountable = po_roles.count("2")
    n_po_extending = po_roles.count("3")
    n_po_implementing = po_roles.count("4")
    po_types = [t for t in (_attr(e, "type") for e in poi) if t]
    distinct_po_types = ",".join(sorted(set(po_types)))

    # recipient-country / recipient-region (activity-level)
    rcs = [_attr(e, "code") for e in activity.findall("recipient-country")]
    rcs = [c for c in rcs if c]
    distinct_recipient_countries = ",".join(sorted(set(rcs)))
    rrs = [_attr(e, "code") for e in activity.findall("recipient-region")]
    rrs = [r for r in rrs if r]

    # sector
    sec = activity.findall("sector")
    sec_vocabs = [v for v in (_attr(e, "vocabulary") or "1" for e in sec) if v]  # default vocab=1
    distinct_sector_vocabs = ",".join(sorted(set(sec_vocabs)))
    has_sdg_goal_tag = "7" in sec_vocabs
    has_sdg_target_tag = "8" in sec_vocabs

    # policy-marker
    pms = activity.findall("policy-marker")
    pm_codes = [c for c in (_attr(e, "code") for e in pms) if c]
    pm_significant = sum(
        1 for e in pms if (_attr(e, "significance") or "0") in {"1", "2", "3", "4"}
    )
    distinct_pm_codes = ",".join(sorted(set(pm_codes)))

    # budget — count + earliest / latest period-end + statuses
    budgets = activity.findall("budget")
    budget_status_codes = [s for s in (_attr(e, "status") or "1" for e in budgets) if s]
    n_budgets = len(budgets)
    budget_period_end_years: list[int] = []
    for b in budgets:
        pe = b.find("period-end")
        if pe is not None:
            iso = _attr(pe, "iso-date") or ""
            m = re.match(r"(\d{4})", iso)
            if m:
                budget_period_end_years.append(int(m.group(1)))
    n_budgets_forward = sum(1 for y in budget_period_end_years if y >= year_now)
    n_budgets_t1 = sum(1 for y in budget_period_end_years if y == year_now + 1)
    n_budgets_t2 = sum(1 for y in budget_period_end_years if y == year_now + 2)
    n_budgets_t3 = sum(1 for y in budget_period_end_years if y == year_now + 3)
    max_budget_year = max(budget_period_end_years) if budget_period_end_years else None

    # planned-disbursement — same forward analysis
    pds = activity.findall("planned-disbursement")
    pd_period_end_years: list[int] = []
    for p in pds:
        pe = p.find("period-end")
        if pe is not None:
            iso = _attr(pe, "iso-date") or ""
            m = re.match(r"(\d{4})", iso)
            if m:
                pd_period_end_years.append(int(m.group(1)))
    n_planned_disbursements_forward = sum(1 for y in pd_period_end_years if y >= year_now)

    # transactions
    txs = activity.findall("transaction")
    n_transactions = len(txs)
    tx_type_counts: Counter[str] = Counter()
    n_disbursement_channel = 0
    n_aid_type = 0
    n_flow_type = 0
    n_finance_type = 0
    n_tied_status = 0
    n_provider_org_ref = 0
    n_provider_activity_id = 0
    n_receiver_org_ref = 0
    n_receiver_activity_id = 0
    n_tx_sector = 0
    n_tx_recipient_country = 0
    distinct_receiver_org_refs: set[str] = set()
    aid_type_codes: list[str] = []
    flow_type_codes: list[str] = []
    finance_type_codes: list[str] = []
    tied_status_codes: list[str] = []
    disbursement_channel_codes: list[str] = []
    for tx in txs:
        ttype = tx.find("transaction-type")
        if ttype is not None and (c := _attr(ttype, "code")):
            tx_type_counts[c] += 1
        if (e := tx.find("disbursement-channel")) is not None:
            n_disbursement_channel += 1
            if c := _attr(e, "code"):
                disbursement_channel_codes.append(c)
        if (e := tx.find("aid-type")) is not None:
            n_aid_type += 1
            if c := _attr(e, "code"):
                aid_type_codes.append(c)
        if (e := tx.find("flow-type")) is not None:
            n_flow_type += 1
            if c := _attr(e, "code"):
                flow_type_codes.append(c)
        if (e := tx.find("finance-type")) is not None:
            n_finance_type += 1
            if c := _attr(e, "code"):
                finance_type_codes.append(c)
        if (e := tx.find("tied-status")) is not None:
            n_tied_status += 1
            if c := _attr(e, "code"):
                tied_status_codes.append(c)
        if (e := tx.find("provider-org")) is not None:
            if _attr(e, "ref"):
                n_provider_org_ref += 1
            if _attr(e, "provider-activity-id"):
                n_provider_activity_id += 1
        if (e := tx.find("receiver-org")) is not None:
            ref = _attr(e, "ref")
            if ref:
                n_receiver_org_ref += 1
                distinct_receiver_org_refs.add(ref)
            if _attr(e, "receiver-activity-id"):
                n_receiver_activity_id += 1
        if tx.find("sector") is not None:
            n_tx_sector += 1
        if tx.find("recipient-country") is not None:
            n_tx_recipient_country += 1

    n_tx_disbursement = tx_type_counts.get("3", 0)
    n_tx_outgoing_commitment = tx_type_counts.get("2", 0)
    n_tx_expenditure = tx_type_counts.get("4", 0)
    n_tx_incoming_funds = tx_type_counts.get("1", 0)

    # country-budget-items (for on-budget alignment)
    cbi = activity.findall("country-budget-items")
    has_country_budget_items = len(cbi) > 0
    cbi_vocabs = [v for v in (_attr(e, "vocabulary") for e in cbi) if v]

    # default-* attribute-style elements
    has_default_aid_type = activity.find("default-aid-type") is not None
    has_default_flow_type = activity.find("default-flow-type") is not None
    has_default_finance_type = activity.find("default-finance-type") is not None
    has_default_tied_status = activity.find("default-tied-status") is not None

    # document-link with categories — strategy-level
    dls = activity.findall("document-link")
    dl_cats = [
        c
        for c in (_attr(e.find("category"), "code") for e in dls if e.find("category") is not None)
        if c
    ]
    distinct_dl_categories = ",".join(sorted(set(dl_cats)))
    has_dl_a02 = "A02" in dl_cats  # Objectives / Purpose
    has_dl_a08 = "A08" in dl_cats  # Results, outcomes and outputs
    has_dl_b01 = "B01" in dl_cats  # Annual report
    has_dl_b02 = "B02" in dl_cats  # Institutional strategy
    has_dl_b03 = "B03" in dl_cats  # Country strategy paper

    # results & indicators
    results = activity.findall("result")
    n_results = len(results)
    indicators = activity.findall("result/indicator")
    n_indicators = len(indicators)
    n_indicator_refs = sum(1 for ind in indicators if ind.find("reference") is not None)
    n_indicator_with_dimension = sum(
        1
        for ind in indicators
        if any(
            b.find("dimension") is not None
            for b in ind.findall("baseline")
            + ind.findall("period/target")
            + ind.findall("period/actual")
        )
    )
    indicator_ref_vocabs: list[str] = []
    for ind in indicators:
        for ref in ind.findall("reference"):
            v = _attr(ref, "vocabulary")
            if v:
                indicator_ref_vocabs.append(v)
    distinct_indicator_ref_vocabs = ",".join(sorted(set(indicator_ref_vocabs)))

    # related-activity
    rels = activity.findall("related-activity")
    n_related_activity = len(rels)

    # location
    n_location = len(activity.findall("location"))

    # tag (extra cross-cutting tagging)
    n_tag = len(activity.findall("tag"))

    return {
        "iati_identifier": iid,
        "reporting_org_ref": rep_ref,
        "reporting_org_type": rep_type,
        "secondary_reporter": secondary_reporter,
        "activity_status": activity_status,
        "default_currency": default_currency,
        "hierarchy": hierarchy,
        # other-identifier (CRS bridging)
        "has_other_identifier_a1": has_a1,
        "has_other_identifier_a2": has_a2,
        "has_other_identifier_a9": has_a9,
        "n_other_identifier": len(oids),
        # participating-org
        "n_participating_org": len(poi),
        "n_po_funding": n_po_funding,
        "n_po_accountable": n_po_accountable,
        "n_po_extending": n_po_extending,
        "n_po_implementing": n_po_implementing,
        "distinct_po_types": distinct_po_types,
        # geography
        "distinct_recipient_countries": distinct_recipient_countries,
        "n_recipient_country": len(rcs),
        "n_recipient_region": len(rrs),
        # sector / SDG
        "n_sector": len(sec),
        "distinct_sector_vocabs": distinct_sector_vocabs,
        "has_sdg_goal_tag": has_sdg_goal_tag,
        "has_sdg_target_tag": has_sdg_target_tag,
        # policy-marker
        "n_policy_marker": len(pms),
        "n_policy_marker_significant": pm_significant,
        "distinct_pm_codes": distinct_pm_codes,
        # budget / forward-looking
        "n_budget": n_budgets,
        "distinct_budget_status_codes": ",".join(sorted(set(budget_status_codes))),
        "max_budget_year": max_budget_year,
        "n_budget_forward": n_budgets_forward,
        "n_budget_t1": n_budgets_t1,
        "n_budget_t2": n_budgets_t2,
        "n_budget_t3": n_budgets_t3,
        "n_planned_disbursement": len(pds),
        "n_planned_disbursement_forward": n_planned_disbursements_forward,
        # transactions (full breadth)
        "n_transaction": n_transactions,
        "n_tx_outgoing_commitment": n_tx_outgoing_commitment,
        "n_tx_disbursement": n_tx_disbursement,
        "n_tx_expenditure": n_tx_expenditure,
        "n_tx_incoming_funds": n_tx_incoming_funds,
        "n_tx_disbursement_channel": n_disbursement_channel,
        "distinct_disbursement_channel_codes": ",".join(sorted(set(disbursement_channel_codes))),
        "n_tx_aid_type": n_aid_type,
        "distinct_aid_type_codes": ",".join(sorted(set(aid_type_codes))),
        "n_tx_flow_type": n_flow_type,
        "distinct_flow_type_codes": ",".join(sorted(set(flow_type_codes))),
        "n_tx_finance_type": n_finance_type,
        "distinct_finance_type_codes": ",".join(sorted(set(finance_type_codes))),
        "n_tx_tied_status": n_tied_status,
        "distinct_tied_status_codes": ",".join(sorted(set(tied_status_codes))),
        "n_tx_provider_org_ref": n_provider_org_ref,
        "n_tx_provider_activity_id": n_provider_activity_id,
        "n_tx_receiver_org_ref": n_receiver_org_ref,
        "n_tx_receiver_activity_id": n_receiver_activity_id,
        "n_distinct_receiver_org_refs": len(distinct_receiver_org_refs),
        "n_tx_sector": n_tx_sector,
        "n_tx_recipient_country": n_tx_recipient_country,
        # country-budget-items
        "has_country_budget_items": has_country_budget_items,
        "distinct_country_budget_items_vocabs": ",".join(sorted(set(cbi_vocabs))),
        # default-* (activity-level fall-throughs)
        "has_default_aid_type": has_default_aid_type,
        "has_default_flow_type": has_default_flow_type,
        "has_default_finance_type": has_default_finance_type,
        "has_default_tied_status": has_default_tied_status,
        # document-link
        "n_document_link": len(dls),
        "distinct_document_link_categories": distinct_dl_categories,
        "has_dl_a02_objectives": has_dl_a02,
        "has_dl_a08_results": has_dl_a08,
        "has_dl_b01_annual_report": has_dl_b01,
        "has_dl_b02_institutional_strategy": has_dl_b02,
        "has_dl_b03_country_strategy": has_dl_b03,
        # results / indicators
        "n_result": n_results,
        "n_indicator": n_indicators,
        "n_indicator_with_reference": n_indicator_refs,
        "n_indicator_with_dimension": n_indicator_with_dimension,
        "distinct_indicator_ref_vocabs": distinct_indicator_ref_vocabs,
        # other
        "n_related_activity": n_related_activity,
        "n_location": n_location,
        "n_tag": n_tag,
    }


# ---------------------------------------------------------------------------
# Streaming scan over a publisher's directory
# ---------------------------------------------------------------------------


def _iterparse_activities(path: Path) -> Iterator[etree._Element]:
    """Yield <iati-activity> elements from one IATI XML file, then clear them."""
    try:
        ctx = etree.iterparse(
            str(path),
            events=("end",),
            tag="iati-activity",
            recover=True,
            huge_tree=True,
        )
    except (OSError, etree.XMLSyntaxError):
        return
    for _, elt in ctx:
        yield elt
        elt.clear()
        # clear preceding siblings to keep memory flat
        while elt.getprevious() is not None:
            del elt.getparent()[0]


def scan_publisher_dir(
    publisher_dir: Path, *, year_now: int, max_activities: int | None = None
) -> Iterable[dict]:
    """
    Yield per-activity feature dicts for every activity under one publisher.
    Adds `_source_file` and `_publisher_slug` keys for traceability.
    """
    slug = publisher_dir.name
    seen = 0
    for path in iter_publisher_files(publisher_dir):
        try:
            for activity in _iterparse_activities(path):
                features = extract_activity_features(activity, year_now=year_now)
                features["_publisher_slug"] = slug
                features["_source_file"] = path.name
                yield features
                seen += 1
                if max_activities is not None and seen >= max_activities:
                    return
        except (etree.XMLSyntaxError, OSError):
            # skip malformed files; recorded in caller's bookkeeping
            continue
