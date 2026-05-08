# Data sources

The analysis draws on five inputs:

1. The **IATI bulk-data service** — the activity XML files.
2. The **IATI registry indices** (`reporting-orgs`, `datasets-full`) — fetched live, never cached on disk.
3. The **GPEDC official donor mapping** — the 99 reporting-org refs that scope the analysis.
4. The **GPEDC MR4 Global Transparency results** — used as a sanity-check baseline.
5. The **GPEDC Methodological Note** and two OECD-DAC working papers — the policy basis for the indicator-by-indicator mapping calls.

## IATI bulk-data service

The bulk-data service at [bulk-data.iatistandard.org](https://bulk-data.iatistandard.org/) is the canonical export of the IATI dataset. It exposes:

- A single ZIP archive (`iati-data.zip`, around 850 MB compressed and 13 GB uncompressed) containing every IATI activity XML file from every publisher in the IATI Registry, organised in per-publisher folders.
- A small JSON index of reporting organisations (~2 MB), with one record per publisher including its IATI organisation identifier, short folder slug, and basic metadata.
- A larger JSON index of datasets (~33 MB), with per-dataset metadata.

The XML files are mirrored locally because re-downloading 13 GB per analysis is impractical. The two registry indices are fetched live at the start of each script run and held in memory only — they're small, and snapshot-currency matters. The reporting-orgs index is what tells the scanner that, for example, donor mapping ref `DE-1` lives in the local folder named `bmz`.

## GPEDC official donor mapping

The file `data/iati_donor_mapping.xlsx` is the GPEDC's own mapping between OECD donor codes and IATI reporting-org refs. It has 99 rows across 78 distinct development partners. The mapping is **many-to-many**:

- One IATI publisher can serve several donor codes — e.g. the African Development Bank publisher feeds both the AfDB and the African Development Fund donor codes; the WHO publisher feeds both the WHO and WHO-Strategic Preparedness codes; the EBRD publisher feeds both IBRD and EBRD.
- One donor can have several IATI publishers — the United Kingdom is split across three (`GB-GOV-1`, `GB-GOV-7`, `GB-GOV-13`); Germany across three (`DE-1`, `XM-DAC-5-7`, `XM-DAC-5-52`); the United States across eleven separate `US-GOV-*` agencies.

Every empirical aggregation in the workbook and the app is done at the **IATI reporting-organisation level** — that's where the data is published — with the parent OECD development partner(s) shown alongside as a context column. Where a publisher has multiple parent donors they're joined with " / " (e.g. the WHO publisher row shows "WHO-Strategic Preparedness and Response Plan / World Health Organisation").

## GPEDC MR4 Global Transparency results

The MR4 published results (`data/GPEDC_Global_Data_20Apr2026.xlsx`) include the IATI dashboard scores GPEDC publishes per round. Notebook 01 cross-checks the per-publisher percentages we compute against that sheet — primarily as a sanity-check that our scan reads the same activities the dashboard does.

## Policy anchors

The mapping calls themselves are anchored in three documents:

- **GPEDC 2023-26 Methodological Note** — defines what each GPEDC question asks for and what its means of verification is. Available from the GPEDC at [effectivecooperation.org](https://www.effectivecooperation.org/landing-page/monitoring). Every Feasibility category was assigned by reading the note's definition for each indicator and matching it against the IATI Standard.
- **OECD-DAC DCD/DAC/STAT(2026)22** — *Linking IATI and CRS: A Multi-Layer Matching Analysis (2000–2024).* Establishes the four-layer matching pipeline. The CRS × IATI interoperability page tests the first two layers empirically.
- **OECD-DAC DCD/DAC/STAT(2025)56** — *Exploring methods to track aid subcontracts.* Pilots IATI's `transaction/receiver-org` element as a Tier-2 supplement to the OECD-DAC Contract Awards database. The Untying & subcontracts page tests the floor metric per publisher.

Both OECD-DAC papers are available via the OECD document portal at [one.oecd.org](https://one.oecd.org/) (search by document number).

## What's not used

- The full IATI Datastore search/query API. The bulk-data approach is preferred because it gives a known-stable snapshot and is easier to reproduce.
- The IATI Registry's CKAN API. Same reasoning — the bulk-data registry index is sufficient for our publisher-folder lookup.
- DAC CRS data directly. Indicator 3.2.1's CRS rating is taken as-given from the GPEDC published results. The CRS × IATI interoperability work tests *the IATI side* of the linkage.
