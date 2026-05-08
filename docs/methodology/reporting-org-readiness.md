# Reporting-org readiness

The most-asked question on the web app's `/reporting-org` page (and sheet 4 of the workbook) is simple: **for each IATI publisher in the GPEDC universe, how often do they actually populate the elements GPEDC monitoring would lean on?**

The answer is built up in three layers, from individual activities up to a single percentage per publisher per GPEDC theme.

## How the percentages are built

**Step 1 — for each activity.** When the scanner reads an IATI activity XML, it records whether each GPEDC-relevant element is populated (yes/no) and how many of each type are present. Examples: does this activity carry a CRS Activity Identifier in its `other-identifier`? Does it have a forward-looking budget? Does it tag any policy markers? Does its `transaction/receiver-org` carry a structured organisation reference?

**Step 2 — for each publisher.** Group every activity that publisher has ever published. For each element, compute the share of activities populating it. A publisher with 80 % `forward-looking` means: out of all that publisher's activities, 80 % carry a budget extending into the future.

**Step 3 — roll up to GPEDC themes.** Average the per-element percentages into ten themes that match the GPEDC indicator groups. These ten percentages are what the heatmap shows.

## What's in each theme

Each theme rolls up one or more IATI elements that, taken together, signal whether the publisher is publishing the data the corresponding GPEDC indicator would draw on:

| Theme | What it measures | IATI element(s) behind it |
| --- | --- | --- |
| CRS interoperability | Cross-references between IATI and the CRS at project level | `iati-activity/other-identifier` types A1, A2, A9 |
| Forward-looking | Whether forward budgets are published — the basis for predictability | `iati-activity/budget`, `planned-disbursement` with future periods |
| Annual predictability | The financial-flow data needed to compute the GPEDC annual-predictability ratio | `iati-activity/transaction` (commitments, disbursements) and `budget` |
| Country budget items | Direct alignment to the partner-country budget classification | `iati-activity/country-budget-items` |
| PFM use | Use of country public-financial-management systems | `transaction/aid-type` (especially A01/A02/B03) |
| Subcontract visibility | Tier-2 transparency of who receives funds | `transaction/receiver-org/@ref` |
| Untying (tied-status) | Cross-check on the CRS-sourced untied-aid figure | `transaction/tied-status`, `default-tied-status` |
| Country strategy | DP country-strategy publication | `document-link[@category='B03']` |
| Results / CRF | Project results frameworks tied to recognised vocabularies | `result/indicator/reference`, indicator dimensions |
| LNOB markers | Population-group focus in DP activities | `policy-marker` (codes 1, 9, 11, 12, 3 with significance ≥ 1) |

Each theme percentage is the simple mean of its constituent per-element percentages — no weighting, no normalisation. The full mapping from raw IATI feature to themed percentage lives in [`notebook 01`](https://github.com/codywallace/gpedc-monitoring-mapping/blob/main/notebooks/01_dp_coverage.ipynb).

## How the heatmap colours work

The same five-bucket scale runs across every theme:

- **Green (≥ 80 %)** — strong, element populated on most activities
- **Light green (60–80 %)** — solid
- **Yellow (30–60 %)** — partial
- **Orange (10–30 %)** — sparse
- **Red (< 10 %)** — effectively absent

The thresholds are uniform across themes by design — a 60 % `country_budget_items_pct` (which is rare) reads the same colour as a 60 % `forward_looking_pct` (which is common among "Excellent"-rated dashboard publishers). The heatmap is meant to surface raw publication discipline, not a relative score.

## What this measures and what it doesn't

This is a **publication-presence** measure: does the publisher include the relevant IATI element on a given activity? It is **not**:

- A correctness check. A publisher can populate `country-budget-items` with a non-existent budget code, or tag every activity with `policy-marker[@code='1']` regardless of relevance. Presence is the floor.
- A relevance-adjusted figure. Some elements only make sense for some activity types — `tied-status` for procurement-eligible aid; `country-budget-items` for activities that flow through the public sector. A 40 % rate may be 100 % of where the element is relevant.
- A current-only snapshot. The scan reads the publisher's full archive, including closed activities. Recent practice can differ from the archive average.
- An indicator-by-indicator verdict. Whether the published value satisfies the underlying GPEDC question is the [feasibility categorisation](feasibility-categorisation.md), made indicator by indicator.

These caveats apply uniformly to every cell of the heatmap. The reporting-org readiness page is a starting point for "where would IATI even let GPEDC look here?" — not the final word on data quality.
