# Overview

## What this is

A structured, indicator-by-indicator mapping of where the **IATI Standard v2.03** can supplement the means of verification for the **GPEDC monitoring framework**, plus an empirical test of those mapping calls against every IATI publisher associated with the 99 reporting-org refs in the GPEDC official donor mapping.

The output ships in three forms — an Excel workbook for sharing and offline review, a Plotly Dash web app for interactive browsing, and three reproducible Polars notebooks that produce the empirical sheets. All three render the same underlying data: the workbook builder, the web app, and the notebooks share a single source of truth for the indicator-mapping table and consume the same set of parquet outputs.

## What it answers

For each of the 29 GPEDC indicators / sub-indicators covered, the mapping classifies the role IATI can play:

- **Direct supplement** — IATI directly answers the GPEDC question.
- **Partial / proxy supplement** — IATI captures most but not all of what's asked.
- **Cross-validation / context only** — useful side-channel, not a primary source.
- **Already sourced externally** — CRS / PEFA / dashboard already feeds in.
- **Not supplementable from IATI** — partner-country self-report or out of IATI scope.

The classification is editorial — based on indicator-by-indicator review of (a) what the GPEDC means of verification asks, (b) which IATI element exists, and (c) whether that element actually answers the question. The full per-indicator mapping is on the [feasibility categorisation](feasibility-categorisation.md) page.

## What's measured empirically

For the indicators where IATI does play a role, the analysis tests how well it works in practice. Three pages on the web app and three sheets in the workbook each cover one slice:

- **Reporting-org readiness** — per IATI publisher, the share of activities populating each GPEDC-relevant element. ([Methodology](reporting-org-readiness.md).)
- **CRS × IATI interoperability** — per publisher, the rate at which `iati-activity/other-identifier` of types A1, A2, A9 is populated — the foundation for project-level reconciliation between IATI and CRS. ([Methodology](crs-iati-interoperability.md).)
- **Untying & subcontracts** — per publisher, the rate at which `transaction/receiver-org/@ref` is populated — the floor metric for the IATI-based Tier-2 supplement to the OECD-DAC Contract Awards database. ([Methodology](untying-subcontracts.md).)

## Design choices

A few decisions shape every section:

**Per IATI reporting organisation, not per OECD donor.** The GPEDC official donor mapping is many-to-many — one IATI publisher can serve several OECD donor codes, and one donor can have several IATI publishers. All empirical aggregations are done at the IATI reporting-organisation level (that's where the data is published) with the parent OECD development partner(s) shown alongside as a context column.

**Live registry, mirrored XML.** The IATI reporting-orgs and datasets indices are fetched dynamically at the start of each run and held in memory only — every analysis runs against a fresh registry snapshot. The bulk activity XML files are mirrored locally because they're large; only the small JSON indices are fetched per run.

**Tolerant scanning.** IATI files in the wild contain malformed UTF-8, BOMs, version 1.x dialects, mid-stream encoding errors, and stale identifiers. The scanner uses recovery-mode parsing and skips files that fail rather than aborting an entire publisher.

## What this is not

- **Not an automated questionnaire pre-fill system.** It identifies *where* IATI publication could supplement a GPEDC means of verification. The decision to actually use it for any given indicator is a methodology call for the GPEDC monitoring round.
- **Not a replacement for the GPEDC monitoring framework.** Several indicators are explicitly classified "Not supplementable from IATI" because they ask about partner-country processes (parliamentary oversight, NDP quality, civic-space environment, mutual accountability) that are out of IATI scope.
- **Not a replacement for the OECD-DAC CRS or for PEFA.** CRS remains the authoritative annual ODA statistical record, PEFA the authoritative PFM-quality assessment. The mapping is explicit about which system carries which information.
