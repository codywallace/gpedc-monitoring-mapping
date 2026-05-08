# gpedc-monitoring-mapping

Mapping where the **IATI Standard v2.03** can supplement the means of verification for the **GPEDC monitoring framework**, so that the JST team, National Coordinators, and Development Partner focal points can lean on data already published openly to close the information gap that runs through every monitoring round.

The analysis ships in three forms:

- **Web app** — [gpedc-iati-mapping.codywallace.dev](https://gpedc-iati-mapping.codywallace.dev) — browse the indicator-by-indicator mapping, the per-publisher readiness heatmap, the CRS × IATI interoperability rates, the untying view, and the policy recommendations interactively. The same site serves the methodology documentation at [`/docs/`](https://gpedc-iati-mapping.codywallace.dev/docs/).
- **Excel workbook** — [`gpedc_iati_mapping.xlsx`](gpedc_iati_mapping.xlsx) in this repo — the full mapping in spreadsheet form, including the colour-coded feasibility column, the per-publisher readiness heatmap, and the IATI element reference. Download and open in Excel / Numbers / LibreOffice.
- **Reproducible Polars pipeline** — clone this repo and run the scripts under [`scripts/`](scripts/) to regenerate the parquet outputs, the workbook, and the documentation site from raw IATI publisher data. See [Inspecting the analysis locally](#inspecting-the-analysis-locally) below.

---

## Overview

The broader Financing for Development ([FFD](https://financing.desa.un.org/ffd4)) agenda has long called for better interoperability between development-finance data systems, lighter reporting burdens on partner countries, and improved transparency along the aid delivery chain. The **Global Partnership for Effective Development Cooperation (GPEDC)** sits inside that broader effort, with its own monitoring framework tracking the effectiveness of international development cooperation across whole-of-society engagement, country-systems use, transparency, and leaving-no-one-behind.

A number of practical workstreams are pushing in the same direction. They show up directly in the GPEDC framework:

- **Untying ODA and tracking local procurement.** GPEDC indicator 2.8.1 currently sources tying-status from the OECD-DAC Contract Awards database, which only captures Tier-1 prime contracts. Pilot work on Tier-2 (subcontracts) using IATI's `transaction/receiver-org` element (OECD-DAC paper DCD/DAC/STAT(2025)56) shows that a substantial share of the actual procurement opportunity sits at the subcontract level, where local suppliers are much more present.
- **Predictability and now-casting.** GPEDC indicators 2.4.1.1 (annual) and 2.4.1.2 (medium-term) ask DPs and partner countries to confirm forward spending plans bilaterally — yet the IATI Publishing Statistics dashboard's *Forward-looking* metric is already computing exactly that signal, per publisher and per recipient country, using `iati-activity/budget` and `planned-disbursement`.
- **Cross-referencing and interoperability across systems.** GPEDC indicator 3.2.1 today rates DP transparency separately on CRS and IATI, with an aggregate-level coverage adjustment between them. The OECD-DAC's project-level matching pipeline (DCD/DAC/STAT(2026)22) and the new 2026 voluntary `external link` field on the CRS side make a per-project reconciliation tractable as publishers populate `iati-activity/other-identifier[@type='A2']`.
- **Streamlining global and country-level data collection.** Each round, much of what National Coordinators reconcile with DP focal points (forward spending plans, on-budget figures, country-strategy publication, results-framework alignment) is already in the public domain via IATI. The comparative advantage is clear: CRS is the authoritative annual ODA statistical record, PEFA is the authoritative PFM-quality assessment, IATI is the most-current openly-published activity-level feed, and partner-country AIMS / NDP / accountability mechanisms are the authoritative sources on country-side process. Each system covers what the others can't, and the gain comes from using each where it's genuinely strongest rather than asking the same question of every system.

This repository tackles one slice of that overall picture: a structured, indicator-by-indicator mapping of where the IATI Standard v2.03 (the activity standard, the transaction-level fields, and the IATI Publishing Statistics dashboard) **directly answers**, **partially answers**, **cross-validates**, **is already used**, or **does not apply to** each of the 29 GPEDC indicators / sub-indicators — and an empirical test of those mapping calls against every IATI publisher associated with the 99 reporting-org refs in the GPEDC official donor mapping.

---

## Why this is useful

The GPEDC monitoring round currently asks National Coordinators and DP focal points to confirm large amounts of information bilaterally — forward spending plans, on-budget figures, country-strategy publication, results-framework alignment, untied-aid status — much of which is **already published in IATI**. Surfacing that overlap concretely:

- Closes the information gap for National Coordinators by pointing at structured public data they can validate against, rather than reconciling figures from scratch.
- Reduces the coordination overhead on DP focal points by signalling what's already covered by their organisation's IATI publication.
- Gives the JST team a defensible, indicator-by-indicator basis for where IATI is the right means of verification, where it's a partial proxy, and where the question genuinely needs a survey response.
- Slots into the broader effort to streamline global and country-level data collection on development cooperation, by being explicit about which system carries which information best.

---

## Headline finding

Of the 29 GPEDC indicators / sub-indicators covered, the **Feasibility** column on `1_Indicator mapping` in [`gpedc_iati_mapping.xlsx`](gpedc_iati_mapping.xlsx) is colour-coded into five buckets:

| Feasibility | Count | Examples |
| --- | --- | --- |
| **Direct supplement** — IATI directly answers the question | 5 | 2.4.1.1 / 2.4.1.2 predictability, 2.7.2 AIMS reporting, 3.2.2 DP country strategy publication |
| **Partial / proxy supplement** — IATI captures most but not all | 6 | 1.2.2 on-budget recording, 2.3.3 PFM use, 2.2.1-R results frameworks, 4.2.3 LNOB priorities, 4.2.4 distributional analysis |
| **Cross-validation / context only** — useful side-channel, not primary source | 4 | 1.1.4 stakeholder consultation, 2.2.1-O CRF objectives, 4.1.4 vulnerable-group consultation, 4.3.3 data-driven assessments |
| **Already sourced externally** — CRS / PEFA / dashboard already feeds in | 3 | 2.3.1 / 2.3.2 PEFA, 2.8.1 CRS untied aid, 3.2.1 DP transparency rating |
| **Not supplementable from IATI** — PC self-report or out of IATI scope | 11 | NDP quality, mutual accountability, parliamentary oversight, civic-space EEA, gender budgeting |

A reader can filter on this column directly to slice the table by category.

---

## Strengths

Where IATI works particularly well as a supplemental source for the GPEDC monitoring framework:

- **Forward-looking financial data (indicators 2.4.1.1, 2.4.1.2).** This is where IATI is most directly *the answer* — the `budget` and `planned-disbursement` elements with future period-end dates are exactly what the GPEDC predictability indicators ask for, and the dashboard already aggregates them per publisher per recipient country. Where DPs publish them well, no bilateral reconciliation is needed.
- **DP country-strategy publication (indicator 3.2.2).** `document-link[@category='B03']` is a one-to-one map to "is the country strategy publicly available?". Cleanest pre-fill in the framework where publishers populate it.
- **DP transparency rating (indicator 3.2.1) — already in the methodology.** The IATI portion of the rating is already computed by the dashboard (Timeliness × Forward-looking × Comprehensiveness, adjusted by Coverage vs CRS). The opportunity is to refine the Coverage adjustment from aggregate flow-type to project-level once `other-identifier[@type='A2']` adoption grows.
- **Public-financial-management-use proxy (indicator 2.3.3).** `transaction[@aid-type='A01' or 'A02' or 'B03']` (general / sector budget support, pooled funds) combined with `disbursement-channel='1'` (through central MoF/Treasury) gives a strong floor on "amount that uses country PFM by construction" — a useful cross-check on DP focal-point reporting.
- **LNOB priorities in DP strategies (indicator 4.2.3) — partial.** `policy-marker` codes 1 (Gender), 11 (Disability), 9 (RMNCH), 12 (Nutrition), 3 (Participatory Dev / Good Governance) directly map to GPEDC's LNOB question for the population groups they cover, with `@significance≥1` distinguishing principal vs significant focus.
- **Distributional analysis proxy (indicator 4.2.4).** Presence of `dimension` elements on `result/indicator/baseline`, `period/target`, or `period/actual` is a deterministic, per-activity signal that disaggregation is built into the project's results monitoring.
- **Always-current, structured, and standardised.** Unlike CRS (annual), IATI publication is meant to be ongoing and machine-readable. For DPs that publish well, the data is there *before* a GPEDC round opens, not reconstructed at the end.

## Limitations

These are the binding constraints on any IATI-based supplement to GPEDC, and the considerations to plan around:

- **IATI is a voluntary publishing initiative.** There is no mandate. Of the 99 reporting-org refs in the GPEDC official donor mapping, 7 don't publish to IATI at all (Romania, Lithuania, Canada Finance, Japan MFA, OPEC Fund, IDB Invest, Omidyar). Several DAC members are missing from IATI entirely (Austria, Czechia, Estonia, Hungary, Iceland, Latvia, Luxembourg, Poland, Portugal, per OECD-DAC paper [DCD/DAC/STAT(2026)22](documents/DCD-DAC-STAT(2026)22.en.pdf)). For those DPs the IATI route is simply not available.
- **The Standard is consistent; publisher interpretations vary.** IATI provides a machine-readable schema, but each organisation maps its internal business logic to that schema differently. Some DPs treat an IATI activity as one project; others as one programme covering many projects. Some populate `budget` with `@status=1` (Indicative), others with `@status=2` (Committed). Some publish at activity level only; others at transaction level. This drives much of the per-publisher variation visible on sheet 4 of the workbook and means JST methodology has to define interpretation rules per indicator (e.g. "for 2.4.1.1, sum `transaction-type=3` with `recipient-country=PC`").
- **Forward-looking is the most valuable use case AND the weakest dashboard component**, even for "Excellent" publishers (UNDP=62, World Bank=70, AfDB=70). The IATI-derived "no forward budget published" answer is, however, the *correct* answer for GPEDC 2.4.1.2 — it surfaces the gap objectively rather than letting DP focal points self-report.
- **`country-budget-items` is effectively unused at scale**, with one striking exception: WHO and UNICEF publish it on 100 % of their activities. For everyone else, on-budget recording (indicators 1.2.2 / 2.4.2) has to lean on a `recipient-country` + `receiver-org/@type=10 (Government)` + `disbursement-channel=1` heuristic.
- **Policy-marker coverage is inverted from dashboard scores.** "Good"-rated BMZ publishes rich markers with significance; "Excellent"-rated World Bank publishes none. The IATI dashboard rates *comprehensiveness*, not *what is published* — a publisher can be Excellent on Core elements while being silent on Value-Added elements like `policy-marker` and `result`. Per-publisher gating per indicator is required.
- **`receiver-org/@ref` is rarely populated structurally**, even by good IATI publishers, so the Tier-2 untying view for indicator 2.8.1 is feasible only for the DPs that mandate IATI publication for their implementing partners (Belgium, Denmark, Netherlands, UK, soon Sweden).
- **Identifier coverage for local civil society is incomplete.** [org-id.guide](https://org-id.guide/) gives a path to globally-unambiguous organisation identifiers, but it depends on national registries — many of which don't cover local CSOs in low-income or fragile contexts, while INGOs registered in developing countries can appear "locally registered" without representing local capacity. This is the structural limit on using IATI to measure de-facto local procurement.
- **Onus on publishing organisations.** All of the above resolves with publisher discipline. The flywheel only turns if the data is used.

---

## Policy recommendations

Ordered by attainability — the quickest, highest-impact actions first; the most ambitious last. Most of these recommendations only require publishing organisations to use elements that **already exist in the IATI Standard v2.03**; one requires an extension to the Standard itself; the last few are coordination problems.

### Quick wins (publishers can do this today)

**1. Publish the CRS Activity Identifier in IATI `other-identifier[@type='A2']`.** Already an OECD-DAC recommendation in [DCD/DAC/STAT(2026)22](documents/DCD-DAC-STAT(2026)22.en.pdf). Direct support for GPEDC indicator 3.2.1: enables financial coverage to shift from aggregate flow-type comparison to project-level reconciliation. Today only Netherlands MFA, BMZ, Norad, EC INTPA, and a handful of others populate it consistently; everyone else is leaving the easiest interoperability win on the table. The new 2026 voluntary `external link` field on the CRS side is the matching mechanism on the OECD side.

**2. Publish DP country strategies as `document-link[@category='B03']` with the recipient country attached.** Direct support for GPEDC indicator 3.2.2 — JST extracts the URL and pre-fills the questionnaire with no bilateral coordination. Many DPs already publish the strategy PDF on their organisation file or website; the missing piece is structured per-recipient tagging.

**3. Cross-reference IATI publications to partner-country AIMS using `other-identifier`.** Where a project is registered in a country's AIMS with its own ID, publishing that ID as an `other-identifier` lets National Coordinators map IATI publications to the domestic record without bilateral reconciliation. A natural extension of the same pattern OECD recommends for CRS.

**4. Improve forward-budget population.** The IATI Publishing Statistics dashboard's *Forward-looking* metric is the GPEDC indicator 2.4.1.2 answer if publishers populate `iati-activity/budget` (or `planned-disbursement`) covering the next two-to-three fiscal years. Even "Excellent"-rated publishers (UNDP=62, World Bank=70, AfDB=70) score below their own ceilings here. No standard change required; pure publisher discipline.

### Medium-term: Standard extension and donor coordination

**5. Add a Country-Owned Results Framework code to `IndicatorVocabulary`.** v2.03 has codes for SDG indicators (`9`), WDI (`4`), MDG (`5`), Sphere, HIPSO, etc. — but no shared semantic for "this indicator is drawn from the country results framework", which is the actual question GPEDC indicator 2.2.1 (R) asks. Today the only path is `vocabulary='99'` (Reporting Org) with a free-text `@indicator-uri`. Adding a CRF code would make per-project CRF alignment machine-readable across publishers.

**6. Establish DP ownership of routine downstream publishing as standard practice.** The IATI Standard already provides every primitive needed to chain funds through the delivery network at activity level: `iati-activity/participating-org` with `@role` (1 Funding, 2 Accountable, 3 Extending, 4 Implementing) + `@ref` + `@type` + `@activity-id` identifies who's involved in an activity and links to that organisation's own IATI publication; `transaction/provider-org/@provider-activity-id` and `transaction/receiver-org/@receiver-activity-id` carry the equivalent links at the transaction level for individual flows; `iati-organisation/document-link` and the organisation file as a whole connect organisation-level metadata. Together these make it possible to traverse from a donor's IATI activity → its prime contractor's IATI activity → that contractor's sub-contractor's IATI activity, etc. The blocker is not the Standard but the *guidance*. The DPs that currently mandate IATI publication for their implementing partners (Belgium, Denmark, Netherlands, the UK, and from Q4 2025 Sweden) each give different guidance on scope, cadence, level of detail, what counts as a sub-grant vs. sub-contract, and how the `participating-org/@activity-id` and `transaction/*-activity-id` links should be populated. Aligning that downstream-publishing guidance across DPs — so that an implementing partner working for two donors publishes consistently for both, with structured organisation references and activity-id links — is the precondition for the activity-traceability network to actually form, and for IATI to deliver the Tier-2 supplement to GPEDC indicator 2.8.1 that [DCD/DAC/STAT(2025)56](documents/DCD-DAC-STAT(2025)56.en.pdf) envisages.

### Structural / most ambitious

**7. Close the [org-id.guide](https://org-id.guide/) gap for local civil society organisations.** Truly capturing untying-of-aid at the Tier-2 level depends on being able to identify whether a subcontractor is a *locally-registered local* entity. This is a structural limitation: many local CSOs in low-income or fragile contexts cannot obtain national accreditation or registry identifiers, so org-id.guide has limited coverage there. At the same time, INGOs registered in developing countries can legitimately appear "locally registered" without representing local capacity. ([IATI Org ID Guide announcement](https://iatistandard.org/en/news/org-id-guide-launched/) and [org-id.guide](https://org-id.guide/) document the current scope.) A genuine measure of local procurement requires investment in national CSO registry coverage and, where registries don't exist, in disambiguation conventions that distinguish locally-rooted entities from in-country INGO branches. This is bigger than IATI alone — it spans Open Contracting, philanthropy, and the broader civil-society data ecosystem — but IATI is one of the relevant data flows pushing for it.

**8. GPEDC proactively uses IATI data to drive trilateral conversations (PC ↔ DP ↔ JST).** The data-quality gap on IATI publication is fundamentally a flywheel problem: if the data isn't used, publishers don't invest in improving it; if it's used, they do. By systematically surfacing per-publisher gaps (forward-looking weak, country-budget-items missing, receiver-org un-typed, etc.) at country level during each monitoring round, GPEDC creates a direct feedback loop that incentivises better DP publication — which in turn closes the GPEDC monitoring's own data-collection loop. The strongest version of this recommendation: GPEDC accepts IATI publication as a means of verification by default for the indicators where it's a *Direct supplement*, and publishes per-DP gap reports for the indicators where it's a *Partial supplement*.

---

## What's in the workbook

| Sheet | What it shows |
| --- | --- |
| **README** | One-page sheet guide. |
| **1_Indicator mapping** | Every GPEDC indicator × the IATI element(s), codelists, and dashboard metric that map to it. The `Feasibility` column is colour-coded and filterable. |
| **2_IATI element reference** | Every IATI v2.03 element used in the mapping, with full transaction-level breadth (transaction-type, value, provider-org, receiver-org, disbursement-channel, sector, recipient-country, flow-type, finance-type, aid-type, tied-status), organisation-file elements, and codelists. |
| **3_Dashboard metrics** | Forward-looking, Timeliness, Comprehensiveness (Core / Financials / Value-Added) and Coverage methodology, with the GPEDC indicator each one feeds. |
| **4_Reporting-org readiness** | Per **IATI reporting organisation** (the publisher), the % of activities populating each GPEDC-relevant element. Heatmap-coloured. The first columns are the IATI reporting-org ref + name; parent OECD development partner(s) are shown alongside since the GPEDC mapping is many-to-many. |
| **5_CRS×IATI interoperability** | Per IATI reporting organisation: A1/A2/A9 `other-identifier` rates, tiered into reconciliation modes per OECD-DAC paper DCD/DAC/STAT(2026)22. |
| **6_Untying & subcontracts** | Per IATI reporting organisation: `transaction/receiver-org` rates for the indicator-2.8.1 Tier-2 subcontract supplement per OECD-DAC paper DCD/DAC/STAT(2025)56. |
| **7_Transaction codelist depth** | Every code in TransactionType, DisbursementChannel, AidType, FlowType, FinanceType, TiedStatus, OtherIdentifierType — with the GPEDC use case for each. |
| **8_Notebook reproduction** | Pointers from each empirical sheet back to the notebook that produced it. |

---

## What's in the web app

The Plotly Dash app under [`app/`](app/) is the same content as the workbook, made interactive. It reads from the same `.tmp/*.parquet` outputs the notebooks produce — never recomputes data — so the workbook and the app are guaranteed to agree.

| Page | What it shows |
| --- | --- |
| **`/` — Overview** | Headline finding (5 KPI cards + horizontal bar) and section navigation. |
| **`/indicator-mapping`** | The full indicator mapping with quick-filter buttons by Feasibility category, plus per-column sort and search. The Feasibility cell is colour-coded the same way as the workbook. |
| **`/reporting-org`** | Per-publisher heatmap (top 40 publishers by activity count) plus the full sortable / filterable table with conditional-formatted percentage cells. |
| **`/crs-iati`** | A1 / A2 / A9 `other-identifier` rates per IATI reporting organisation with tier-coloured reconciliation classification. |
| **`/untying`** | `transaction/receiver-org/@ref` population per publisher, RdYlGn colour scale. |
| **`/recommendations`** | The eight ordered policy recommendations as colour-banded cards (quick wins → medium-term → structural). |

The data layer ([`app/data.py`](app/data.py)) loads each parquet once on import; pages share those DataFrames. The indicator mapping, feasibility categorisation, and colour palette live in [`src/gpedc_iati/indicator_mapping.py`](src/gpedc_iati/indicator_mapping.py) and are imported by both the app and `build_mapping.py` — single source of truth.

```text
                       .tmp/*.parquet
                          │
  ┌───────────────────────┼───────────────────────┐
  │                       │                       │
  ▼                       ▼                       ▼
build_mapping.py     app/ (Dash + Plotly)    ad-hoc Polars analysis
  │                       │
  ▼                       ▼
gpedc_iati_mapping.xlsx   webapp at :8050
```

---

## Reference materials

- **GPEDC 2023-26 Methodological Note** — canonical indicator definitions and means-of-verification for every component of the framework. Available from the [GPEDC](https://www.effectivecooperation.org/landing-page/monitoring), along with the Monitoring Questionnaire and the DP / CSO / TU / Private-Sector Guidance annexes.
- **OECD-DAC DCD/DAC/STAT(2026)22** *Linking IATI and CRS: A Multi-Layer Matching Analysis (2000–2024).* Available via the OECD document portal at [one.oecd.org](https://one.oecd.org/) (search by document number).
- **OECD-DAC DCD/DAC/STAT(2025)56** *Exploring methods to track aid subcontracts.* Available via [one.oecd.org](https://one.oecd.org/).
- **IATI Standard v2.03** online — [iatistandard.org/en/iati-standard/203/](https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/).
- **IATI Publishing Statistics dashboard** — [dev-dashboard.iatistandard.org](https://dev-dashboard.iatistandard.org/).
- **IATI bulk-data service** — [bulk-data.iatistandard.org](https://bulk-data.iatistandard.org/) (mirrored locally for the activity XML; registry indices fetched live).

---

## Inspecting the analysis locally

Three options, ordered by setup cost.

### View the workbook (no setup)

Download [`gpedc_iati_mapping.xlsx`](gpedc_iati_mapping.xlsx) from this repo and open it in Excel, Numbers, or LibreOffice. The first sheet (`README`) explains the workbook's structure; the **Feasibility** column on `1_Indicator mapping` is the headline filter described above.

### Run the web app locally (Docker, ~3 min first build)

The repo ships a `Dockerfile` and a local-dev compose override. The image bakes in the parquet outputs, the workbook, and the pre-built methodology docs — at runtime you only need Docker:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build
# → http://127.0.0.1:8050
# → http://127.0.0.1:8050/docs/
```

The container runs as a non-root user with a read-only filesystem and dropped capabilities — same hardening posture used for the public deployment. See [SECURITY.md](SECURITY.md).

### Reproduce from raw IATI data (full pipeline)

```bash
uv sync                                       # Python 3.13+, uv-managed env

# 1. Scan every reporting-org listed in the GPEDC donor mapping.
#    Reads XML from data/iati-data/datasets/{publisher-slug}/*.xml
#    and writes .tmp/activities.parquet (~648 K rows on the latest run).
uv run python scripts/scan_donors.py --year 2026

# 2. Run the three Polars notebooks headlessly.
uv run python scripts/run_notebooks.py

# 3. Rebuild the workbook from the parquet outputs.
uv run python build_mapping.py

# 4. (Optional) Launch the Dash app on http://127.0.0.1:8050.
uv run python scripts/run_app.py

# 5. (Optional) Build the methodology docs.
uv run python scripts/build_docs.py
```

The scan in step 1 expects the IATI bulk-data XML mirror at `data/iati-data/datasets/`. Pull it from [bulk-data.iatistandard.org](https://bulk-data.iatistandard.org/) — the full mirror is ~13 GB. Registry indices are fetched live and held in memory only; nothing is cached on disk. Every entry point logs to `logs/{script}_{timestamp}.log`.

If you don't yet have `uv`:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

---

## Documentation

A Sphinx site under [`docs/`](docs/) explains the methodology behind every metric the app and workbook display: data sources, IATI bulk-data mechanics, how reporting-org readiness is calculated, the CRS × IATI tier classification, and the editorial basis for the feasibility categories.

Live at [gpedc-iati-mapping.codywallace.dev/docs/](https://gpedc-iati-mapping.codywallace.dev/docs/), or build locally:

```bash
uv run python scripts/build_docs.py
```

| Page | Contents |
| --- | --- |
| `methodology/overview` | What the project answers, design decisions, scope. |
| `methodology/data-sources` | The IATI bulk-data service, registry indices, GPEDC donor mapping, OECD-DAC anchors. |
| `methodology/pipeline` | Scan → notebooks → outputs → app + workbook. ASCII diagram and per-stage description. |
| `methodology/reporting-org-readiness` | How per-publisher coverage rates are computed, element-by-element, with the 10 themed roll-ups and heatmap thresholds. |
| `methodology/crs-iati-interoperability` | A1 / A2 / A9 logic, OECD-DAC pipeline, tier classification, what we test vs what's out of scope. |
| `methodology/untying-subcontracts` | The `transaction/receiver-org/@ref` floor metric and what it does / doesn't capture. |
| `methodology/feasibility-categorisation` | The 5-bucket scheme + every indicator with its category and rationale. |
| `api` | Auto-generated API reference for the `gpedc_iati` package. |
| `references` | Source documents and external links. |

---

## Quality gates

Every push and PR to `main` runs through GitHub Actions:

- **Lint + format** — [`ruff`](https://docs.astral.sh/ruff/) check and format-check (config in [`pyproject.toml`](pyproject.toml)).
- **Docs build** — `sphinx-build` with `-W` (warnings-as-errors) so broken cross-references break CI.
- **Dockerfile lint** — `hadolint`.
- **Dependency audit** — `pip-audit` against the runtime requirements export.
- **Secret scan** — `gitleaks` over the diff.

Local mirrors of these run as `pre-commit` hooks ([config](.pre-commit-config.yaml)) so most issues are caught at commit time. Set up with:

```bash
uv sync --group dev
uv run pre-commit install
```

---

## Public API

The reusable package is at [`src/gpedc_iati/`](src/gpedc_iati/).

```python
from gpedc_iati import (
    # Donor / publisher resolution
    load_donor_mapping,           # → list[DonorMapping]
                                  #   The 99 reporting-org refs in the GPEDC official donor mapping.
    load_reporting_orgs,          # → list[dict]
                                  #   Live fetch of the IATI reporting-orgs registry index.
    load_datasets_index,          # → list[dict]
                                  #   Live fetch of the IATI datasets-full index.
    publisher_paths_for_org_ref,  # str → [Path]
                                  #   Resolve an IATI organisation_identifier to local publisher dir(s).

    # Activity scanning
    scan_publisher_dir,           # Path, year_now=int → Iterable[dict]
                                  #   Stream every activity in one publisher's XML files;
                                  #   yields one feature dict per <iati-activity>.
    extract_activity_features,    # lxml.Element, year_now=int → dict
                                  #   ~70 GPEDC-relevant features per activity. Stable schema.

    # Logging
    setup_logging,                # script_name → log file Path
                                  #   Console (INFO) + per-run log file (DEBUG) under logs/.
)
```

`extract_activity_features` returns a flat dict covering every IATI v2.03 element that the mapping touches: `other-identifier` (A1 / A2 / A9 for CRS interoperability); `participating-org`, `recipient-country`, `sector` (with vocabulary, including SDG goal/target); `policy-marker` (with significance); `budget` (with forward-window flags `n_budget_t1`, `n_budget_t2`, `n_budget_t3`); `planned-disbursement`; the full `transaction` breadth (type, value, provider-org, receiver-org, disbursement-channel, aid-type, flow-type, finance-type, tied-status, sector, recipient-country); `country-budget-items`; `document-link` (with category); `result/indicator/reference` and `result/indicator/.../dimension`. The schema is documented inline at [`src/gpedc_iati/iati_scan.py`](src/gpedc_iati/iati_scan.py).

---

## License

MIT.
