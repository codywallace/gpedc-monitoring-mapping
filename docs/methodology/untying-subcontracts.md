# Untying & subcontracts

The `/untying` page (and sheet 6 of the workbook) measures, per IATI reporting organisation, **the share of activities that populate `transaction/receiver-org/@ref`** — the floor metric for whether GPEDC indicator 2.8.1 (Aid is untied) can be supplemented with a Tier-2 (subcontract) view from IATI.

## What's the question

GPEDC indicator 2.8.1 is currently sourced from the **OECD-DAC Contract Awards database**, which captures only Tier-1 prime contracts (donor → prime contractor). The OECD-DAC paper **DCD/DAC/STAT(2025)56** — *Exploring methods to track aid subcontracts* — pilots IATI's `transaction/receiver-org` element as a Tier-2 (subcontract) supplement, on the principle that:

- Tier-1 contracts are dominated by suppliers in donor countries (Australia and the UK both report 100 % of ODA as untied; in practice ~91 % of the value of Australia's prime contracts and ~85 % of the UK's go to donor-country firms).
- Tier-2 (the subcontracts those prime contractors then award) is where the actual procurement opportunity for local suppliers exists. Australia's PERFORMS data shows that locally-registered suppliers receive 70 % of subcontracts by count.

For GPEDC monitoring to capture this, the data needs to flow through IATI in a structured form. Two IATI elements are central:

```{list-table}
:header-rows: 1
:widths: 30 70

* - IATI element
  - What it carries
* - `transaction/receiver-org/@ref`
  - Formal organisation reference of the receiving entity (org-id.guide-compatible identifier where possible). When populated and resolvable, lets us identify whether the subcontractor is locally registered.
* - `transaction/receiver-org/@receiver-activity-id`
  - IATI activity identifier of the *receiving organisation's own* activity. Closes the loop and lets us trace funds further down the chain (Tier 3 etc.)
```

For both, the OECD-DAC pilot finds population is rare in practice, especially among prime contractors. Country-of-origin usually has to be derived through name search.

## What's measured

Per IATI publisher, restricted to activities that have at least one `<transaction>` element:

```{list-table}
:header-rows: 1
:widths: 30 70

* - Metric
  - Definition
* - `n_activities_with_tx`
  - Number of activities with at least one transaction (the denominator for everything else)
* - `any_receiver_ref_pct`
  - Share of those activities with at least one transaction populating `receiver-org/@ref`
* - `any_receiver_activity_id_pct`
  - Share with at least one transaction populating `receiver-org/@receiver-activity-id` (the link to the receiver's own IATI activity — fundamentally how the traceability network forms)
* - `mean_distinct_receivers`
  - Mean count of distinct `receiver-org/@ref` values per activity (a fan-out signal — how many different organisations a typical activity disburses to)
* - `any_disbursement_pct`
  - Share of activities with at least one `transaction-type='3'` (Disbursement). Sanity-check that the publisher actually publishes financial flows, not just commitments.
* - `total_disbursement_tx`
  - Total disbursement transactions across all the publisher's activities (volume signal)
```

These are computed in [`notebook 03`](https://github.com/codywallace/gpedc-monitoring-mapping/blob/main/notebooks/03_untying_subcontracts.ipynb) and written to `subcontract_visibility_by_dp.parquet`.

## Heatmap colour thresholds

The bar chart on `/untying` and the conditional formatting on the table use a four-bucket scale tuned for the receiver-org metric (which is generally lower than the readiness percentages):

```{list-table}
:header-rows: 1
:widths: 20 20 60

* - `any_receiver_ref_pct`
  - Colour
  - Reading
* - ≥ 80 %
  - Green
  - Most activities name receivers — Tier-2 visibility is broadly possible
* - 50–80 %
  - Light green
  - Solid; usable for project-level reconciliation
* - 20–50 %
  - Yellow
  - Partial; usable for sectoral / sample analysis
* - < 20 %
  - Red
  - Rare; receiver identification has to come from text mining
```

## Disbursement-channel and tied-status distributions

The notebook also produces two supporting distributions:

- **`disbursement_channel_dist.parquet`** — for each publisher, the count of activities populating each of the four `disbursement-channel/@code` values (1 Through central MoF/Treasury; 2 Direct to implementing institution; 3 Aid in kind via NGOs/management companies; 4 Aid in kind, donor-managed). Code 1 is the strongest evidence for GPEDC indicator 2.3.3 (use of country PFM). Code 3 signals subcontracting via implementing partners.
- **`tied_status_dist.parquet`** — for each publisher, the count of activities populating each `tied-status/@code` value (3 Partially tied, 4 Tied, 5 Untied). Used as a secondary cross-check on the CRS-sourced 2.8.1 figure: where IATI tied-status disagrees with CRS, that's a flag for reconciliation.

## What this measures vs what it doesn't

- This is a **floor metric**: how often can a structured organisation reference *be obtained* for the receiver? Whether that reference resolves to a *locally-registered local* entity is a separate question. INGOs registered in developing countries can legitimately appear "locally registered" by org-id.guide standards without representing local capacity — see [`org-id.guide`](https://org-id.guide/) and the IATI Org ID Guide [announcement](https://iatistandard.org/en/news/org-id-guide-launched/).
- **Tier-3 and beyond** is where the real subcontracting story lives — local CSOs receiving subcontracts from locally-registered prime contractors who themselves received Tier-2 work from the donor's prime contractor. Capturing this requires the full network to publish to IATI, which is currently mandated only by Belgium, Denmark, the Netherlands, the UK, and (from Q4 2025) Sweden. See the [policy recommendations](https://github.com/codywallace/gpedc-monitoring-mapping#policy-recommendations) for what would have to change for this to scale.
- The metric is **publisher-level**, not project-level. A publisher with a high `any_receiver_ref_pct` may still have specific projects where receiver-org isn't populated. Drill-down to individual activities requires going back to the activity-level parquet (`.tmp/activities.parquet`).
