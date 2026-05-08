# Pipeline

The full chain — from raw IATI XML to the workbook and the web app — is intentionally simple. Three stages, each with a single responsibility:

```text
                              IATI bulk-data ZIP
                                     │
                                     ▼
                  data/iati-data/datasets/{slug}/*.xml
                                     │
              (live registry fetch   │
               every script run)    │
                                     ▼
                          scripts/scan_donors.py
                                     │
                                     ▼
                              .tmp/*.parquet
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
      notebooks/01_dp_coverage  notebooks/02_crs    notebooks/03_untying
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     ▼
                             .tmp/*.parquet
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
       build_mapping.py     app/ (Dash + Plotly)   ad-hoc Polars analysis
                │                    │
                ▼                    ▼
    gpedc_iati_mapping.xlsx    web app at :8050
```

## Stage 1 — Scan the IATI XML

`scripts/scan_donors.py` walks every IATI publisher associated with the GPEDC official donor mapping. For each `<iati-activity>` element, it records which GPEDC-relevant elements are populated and writes one row per activity to `.tmp/activities.parquet`.

A few practical points:

- The IATI registry index (which maps publisher refs like `DE-1` to folder names like `bmz`) is fetched live from the bulk-data service at the start of each run — so analyses always run against a current snapshot of the registry. The bulk XML files themselves are mirrored locally because they're large.
- Some publishers in the donor mapping don't publish to IATI at all (a handful of DAC bilaterals, a few non-DAC actors). Those are recorded in `missing_publishers.csv` and skipped.
- Some IATI publishers are referenced by more than one OECD donor code in the GPEDC mapping (e.g. the African Development Bank publisher serves both the AfDB and AfDF donor codes; the WHO publisher serves both the World Health Organisation and WHO-Strategic Preparedness donor codes). The scanner visits each publisher exactly once and emits a separate `publisher_dp_lookup.parquet` table that preserves all parent-DP relationships.
- The scanner is tolerant of malformed files — IATI XML in the wild contains encoding errors, version 1.x dialects, and stale references. It uses recovery-mode parsing and skips files that fail rather than aborting the run.

A typical run takes 12–15 minutes on a laptop and produces ~648,000 activity rows.

## Stage 2 — Aggregate per publisher

Three Polars notebooks under `notebooks/` each take a focused slice of the activity-level data and produce one parquet output per topic:

- **`01_dp_coverage.ipynb`** — for each IATI publisher, the share of activities populating each GPEDC-relevant element, then rolled up to ten themed percentages. Feeds the reporting-org readiness page and sheet 4 of the workbook.
- **`02_crs_iati_interoperability.ipynb`** — A1 / A2 / A9 `other-identifier` rates per publisher and a tiered reconciliation classification. Feeds the CRS × IATI page and sheet 5.
- **`03_untying_subcontracts.ipynb`** — `transaction/receiver-org` population rates and supporting distributions (disbursement-channel, tied-status). Feeds the untying & subcontracts page and sheet 6.

All three group at the **IATI reporting-organisation level** (the publisher) and join the parent OECD donor name(s) as a context column. They run in seconds against the activity parquet from Stage 1.

Notebooks can be executed interactively (`uv run jupyter lab notebooks/`) or headlessly (`uv run python scripts/run_notebooks.py`).

## Stage 3 — Render

Two artefacts read the same parquets and the same indicator-mapping definition:

- **`build_mapping.py`** writes the Excel workbook `gpedc_iati_mapping.xlsx` — nine sheets covering the indicator mapping, the IATI element reference, the dashboard-metric methodology, the per-publisher empirical sheets, and a notebook-reproduction guide.
- **`app/`** is the Plotly Dash web app — six pages mirroring the workbook, plus a Methodology link that opens this documentation site.

Neither recomputes data. The indicator-mapping table, the feasibility categorisation, and the colour palette live in `gpedc_iati.indicator_mapping` and are imported by both — single source of truth.

## Logging

Every script (the scanner, the notebook runner, the workbook builder, the app launcher, and the docs builder) writes a per-run log file to `logs/{script}_{timestamp}.log` and mirrors INFO+ messages to the console. Both `.tmp/` and `logs/` are gitignored — they're per-environment artefacts.
