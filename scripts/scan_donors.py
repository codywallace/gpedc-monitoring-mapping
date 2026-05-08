"""
Scan every IATI publisher associated with the reporting-org refs in the
GPEDC official donor mapping (``data/iati_donor_mapping.xlsx``).

A reporting-org-ref can map to multiple parent DPs in the GPEDC mapping
(e.g. ``XM-DAC-46002`` → African Development Bank + African Development Fund;
``XM-DAC-928`` → World Health Organisation + WHO-Strategic Preparedness;
``XI-IATI-EBRD`` → IBRD + EBRD). To avoid double-counting at analysis time,
this script:

  - Fetches the IATI reporting-orgs registry from
    https://bulk-data.iatistandard.org/reporting-orgs (in memory, no disk cache).
  - Resolves every reporting-org-ref to a publisher directory once.
  - Scans each *unique* publisher directory exactly once.
  - Emits a separate publisher↔DP lookup table so the notebooks can surface
    multiple parent DPs against a single IATI reporting org.

Outputs (under ``.tmp/``):

  * activities.parquet           one row per IATI activity
  * publisher_dp_lookup.parquet  publisher_slug × reportingorg_ref × parent DP(s)
  * scan_log.parquet             per-publisher bookkeeping
  * missing_publishers.csv       reporting-org refs with no publisher dir locally

Run via:  ``uv run python scripts/scan_donors.py [--year 2026] [--limit-per-publisher N]``

Logs go to ``logs/scan_donors_{timestamp}.log`` and to stderr.
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from collections import OrderedDict
from pathlib import Path

import polars as pl

from gpedc_iati import (
    DATASETS_DIR,
    load_donor_mapping,
    load_reporting_orgs,
    publisher_paths_for_org_ref,
    scan_publisher_dir,
    setup_logging,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TMP = PROJECT_ROOT / ".tmp"
TMP.mkdir(exist_ok=True)

log = logging.getLogger("scan_donors")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--year",
        type=int,
        default=2026,
        help="Reference year used to compute t+1/t+2/t+3 forward windows",
    )
    p.add_argument(
        "--limit-per-publisher",
        type=int,
        default=None,
        help="Optional cap on activities scanned per publisher (for smoke tests)",
    )
    args = p.parse_args()

    log_path = setup_logging("scan_donors")
    log.info("scan_donors starting — log file: %s", log_path)
    log.info("year=%s, limit_per_publisher=%s", args.year, args.limit_per_publisher)

    donors = load_donor_mapping()
    reporting_orgs = load_reporting_orgs()

    log.info(
        "loaded %d donor mapping rows (%d distinct DPs)",
        len(donors),
        len({d.donor_name for d in donors}),
    )
    log.info("datasets directory: %s", DATASETS_DIR)

    # Resolve every donor mapping entry to its publisher directories.
    publisher_to_donors: OrderedDict[Path, list] = OrderedDict()
    missing: list[dict] = []
    lookup_rows: list[dict] = []

    for d in donors:
        pubs = publisher_paths_for_org_ref(d.reportingorg_ref, reporting_orgs=reporting_orgs)
        if not pubs:
            missing.append(
                {
                    "reportingorg_ref": d.reportingorg_ref,
                    "reportingorg_name": d.reportingorg_name,
                    "donor_code": d.donor_code,
                    "donor_name": d.donor_name,
                }
            )
            log.info("[no publisher dir]  %-24s  (%s)", d.reportingorg_ref, d.donor_name)
            continue
        for pub_dir in pubs:
            publisher_to_donors.setdefault(pub_dir, []).append(d)
            lookup_rows.append(
                {
                    "publisher_slug": pub_dir.name,
                    "reportingorg_ref": d.reportingorg_ref,
                    "reportingorg_name": d.reportingorg_name,
                    "donor_code": d.donor_code,
                    "donor_name": d.donor_name,
                }
            )

    n_pub = len(publisher_to_donors)
    n_resolved = sum(len(v) for v in publisher_to_donors.values())
    n_multi = sum(1 for v in publisher_to_donors.values() if len(v) > 1)
    log.info(
        "unique publisher dirs to scan: %d (%d donor mapping rows resolved)",
        n_pub,
        n_resolved,
    )
    log.info("publishers shared by >1 donor mapping row: %d", n_multi)

    # Scan each unique publisher once. Tag each activity with the FIRST donor
    # mapping entry that resolved to it; the lookup table preserves the rest.
    rows: list[dict] = []
    log_rows: list[dict] = []
    t0 = time.time()
    for pub_dir, ds in publisher_to_donors.items():
        primary = ds[0]
        pub_t0 = time.time()
        n_act = 0
        try:
            for f in scan_publisher_dir(
                pub_dir, year_now=args.year, max_activities=args.limit_per_publisher
            ):
                f["donor_mapping_reportingorg_ref"] = primary.reportingorg_ref
                f["donor_mapping_reportingorg_name"] = primary.reportingorg_name
                f["donor_mapping_donor_name"] = primary.donor_name
                f["donor_mapping_donor_code"] = primary.donor_code
                f["n_donor_mapping_parents"] = len(ds)
                rows.append(f)
                n_act += 1
        except Exception as exc:  # noqa: BLE001 — log + continue per publisher
            log.exception("publisher %s aborted after %d activities: %s", pub_dir.name, n_act, exc)
        elapsed = time.time() - pub_t0
        log_rows.append(
            {
                "publisher_slug": pub_dir.name,
                "reportingorg_ref": primary.reportingorg_ref,
                "reportingorg_name": primary.reportingorg_name,
                "n_donor_mapping_parents": len(ds),
                "n_activities": n_act,
                "elapsed_seconds": round(elapsed, 2),
            }
        )
        extra = f"  (also: {', '.join(d.donor_name for d in ds[1:])})" if len(ds) > 1 else ""
        log.info(
            "%-24s  %-30s  %7d activities  (%.1fs)%s",
            primary.reportingorg_ref,
            pub_dir.name,
            n_act,
            elapsed,
            extra,
        )

    df = pl.from_dicts(rows, infer_schema_length=None) if rows else pl.DataFrame()
    log_df = pl.from_dicts(log_rows, infer_schema_length=None)
    lookup_df = pl.from_dicts(lookup_rows, infer_schema_length=None)

    if len(df) > 0:
        df.write_parquet(TMP / "activities.parquet", compression="zstd")
    log_df.write_parquet(TMP / "scan_log.parquet", compression="zstd")
    lookup_df.write_parquet(TMP / "publisher_dp_lookup.parquet", compression="zstd")

    if missing:
        with open(TMP / "missing_publishers.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(missing[0].keys()))
            w.writeheader()
            w.writerows(missing)

    log.info("done in %.1fs", time.time() - t0)
    log.info(
        "wrote %d activity rows to .tmp/activities.parquet (across %d unique publishers)",
        len(df),
        n_pub,
    )
    log.info("wrote %d publisher-level log rows to .tmp/scan_log.parquet", len(log_df))
    log.info(
        "wrote %d publisher-to-DP lookup rows to .tmp/publisher_dp_lookup.parquet", len(lookup_df)
    )
    log.info(
        "%d donor refs had no matching publisher dir (.tmp/missing_publishers.csv)", len(missing)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
