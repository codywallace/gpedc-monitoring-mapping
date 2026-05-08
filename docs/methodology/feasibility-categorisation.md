# Feasibility categorisation

The `Feasibility` column on the `1_Indicator mapping` sheet (and the `/indicator-mapping` page in the web app) places each of the 29 GPEDC indicators / sub-indicators into one of five buckets. This page documents how those calls were made.

## The five buckets

```{list-table}
:header-rows: 1
:widths: 25 15 60

* - Category
  - Colour
  - Definition
* - Direct supplement
  - Green
  - The IATI Standard provides an element that *directly answers* the GPEDC question. The dashboard or activity-level data is, modulo publisher discipline, exactly what the GPEDC indicator asks for.
* - Partial / proxy supplement
  - Light green
  - IATI captures most but not all of what the GPEDC question asks. A reasonable proxy from structured data, but the GPEDC focal-point reporting still has a role to play.
* - Cross-validation / context only
  - Yellow
  - IATI provides useful side-channel context but isn't the primary source. Helpful for spotting inconsistencies, not for replacing the survey response.
* - Already sourced externally
  - Blue
  - The GPEDC framework already pulls from CRS, PEFA, or the IATI dashboard for this indicator. IATI can refine the methodology (e.g. via project-level reconciliation per OECD-DAC DCD/DAC/STAT(2026)22) but doesn't replace the existing source.
* - Not supplementable from IATI
  - Grey
  - The GPEDC question is about partner-country processes or perceptions that IATI doesn't capture (parliamentary oversight, NDP quality, civic-space environment, mutual accountability, etc.). The survey is the only source.
```

The categorisation is **editorial**: each indicator was reviewed against (a) the GPEDC methodological note's definition of what the indicator asks for and what its means of verification is; (b) the relevant IATI v2.03 elements; (c) whether the IATI element actually answers the question, partially answers, cross-validates, is already used, or is out of scope.

## Where the categorisation lives in code

The single source of truth is [`gpedc_iati.indicator_mapping`](https://github.com/codywallace/gpedc-monitoring-mapping/blob/main/src/gpedc_iati/indicator_mapping.py). Both the workbook builder and the web app import from there.

```{code-block} python
:caption: src/gpedc_iati/indicator_mapping.py — the resolver

FEASIBILITY_BY_INDICATOR: list[tuple[str, str]] = [
    ("1.1.1",          FEASIBILITY_NONE),
    ("1.1.4",          FEASIBILITY_VALIDATE),
    ("1.2.2",          FEASIBILITY_PARTIAL),
    ("2.2.1 (O)",      FEASIBILITY_VALIDATE),
    ("2.2.1 (R)",      FEASIBILITY_PARTIAL),
    ("2.2.1 (D)",      FEASIBILITY_NONE),
    ...
]


def feasibility_for(indicator: str) -> str:
    """Resolve via longest-prefix match against the indicator title.

    Longer prefixes (``2.2.1 (O)``) win over shorter ones (``2.2.1``)
    so that sub-indicators get distinct categories.
    """
    for prefix, feas in sorted(FEASIBILITY_BY_INDICATOR, key=lambda t: -len(t[0])):
        if indicator.startswith(prefix):
            return feas
    raise KeyError(f"no feasibility category for indicator {indicator!r}")
```

## The 29 indicators, by category

```{list-table}
:header-rows: 1
:widths: 12 25 63

* - Indicator
  - Category
  - Why
* - 1.1.1
  - Not supplementable
  - Domestic stakeholder consultation in PC planning isn't within IATI scope.
* - 1.1.4
  - Cross-validation / context
  - `participating-org` shows who's implementing, not who was consulted in drafting; partial signal at best.
* - 1.2.1
  - Not supplementable
  - PC reporting to its own parliament — domestic process.
* - 1.2.2 / 2.4.2
  - Partial / proxy
  - `country-budget-items` is the structured answer (rare); recipient-country + receiver-org/@type=10 + disbursement-channel=1 is the heuristic fallback.
* - 1.3.1
  - Not supplementable
  - CSO enabling-environment perceptions survey — not IATI.
* - 2.1.1
  - Not supplementable
  - The NDP is a PC artefact, not aid activity data.
* - 2.2.1 (O)
  - Cross-validation / context
  - `document-link[@category='A02'/'B03']` confirms strategy publication; doesn't validate that project objectives were *drawn from* the NDP.
* - 2.2.1 (R)
  - Partial / proxy
  - `result/indicator/reference` directly carries SDG-tagged indicators (vocab=9). For CRF-tagged indicators, IATI v2.03 has no shared vocabulary code — see [policy recommendations](https://github.com/codywallace/gpedc-monitoring-mapping#policy-recommendations) #5.
* - 2.2.1 (D)
  - Not supplementable
  - Whether DPs use government statistical systems isn't structurally captured.
* - 2.3.1 / 2.3.2
  - Already sourced externally
  - PEFA database is the canonical source.
* - 2.3.3
  - Partial / proxy
  - `transaction/aid-type` codes A01 / A02 / B03 plus `disbursement-channel='1'` give a strong floor on "uses country PFM by construction"; non-budget-support amounts still need DP focal-point reporting.
* - 2.4.1.1
  - Direct supplement
  - `transaction[@transaction-type='3']` for the numerator and `planned-disbursement` (or `budget[@status='2']`) for the denominator — both directly available, eliminating bilateral DP-PC reconciliation.
* - 2.4.1.2
  - Direct supplement
  - The dashboard's *Forward-looking* metric *is* the GPEDC question if the PC accepts IATI publication as a forward spending plan.
* - 2.5.1
  - Not supplementable
  - About the PC's *own* PFM, not what DPs fund. Policy-marker tells you DP behaviour, not government behaviour.
* - 2.6.1
  - Not supplementable
  - Mutual accountability — PC self-report.
* - 2.7.1
  - Not supplementable
  - PC AIMS existence — PC self-report.
* - 2.7.2
  - Direct supplement
  - The dashboard's Timeliness and Comprehensiveness components map directly onto the three sub-questions about DP reporting cadence and completeness.
* - 2.8.1
  - Already sourced externally
  - CRS Contract Awards database remains the primary source. IATI's `tied-status` is a useful cross-check; `receiver-org` enables a Tier-2 supplement (see OECD-DAC paper DCD/DAC/STAT(2025)56).
* - 3.1.1
  - Not supplementable
  - PC-published links to NDP, progress reports, etc. — not aid activity data.
* - 3.2.1
  - Already sourced externally
  - The IATI dashboard already feeds the IATI portion of the rating. The opportunity is to refine the financial-coverage adjustment from aggregate flow-type to per-project once `other-identifier[@type='A2']` adoption grows.
* - 3.2.2
  - Direct supplement
  - `document-link[@category='B03' Country strategy paper]` is a one-to-one map. Cleanest pre-fill in the framework where publishers populate it.
* - 4.1.1 / 4.1.2 / 4.1.3
  - Not supplementable
  - PC consultation of vulnerable groups — domestic process.
* - 4.1.4
  - Cross-validation / context
  - `participating-org[@role='4']` and `policy-marker` codes 1, 11, 3 hint at vulnerable-group focus but are not consultation evidence.
* - 4.2.1
  - Not supplementable
  - NDP priority-setting — domestic.
* - 4.2.2
  - Not supplementable
  - NDP target / results disaggregation — NDP-side question.
* - 4.2.3
  - Partial / proxy
  - `policy-marker` codes 1 (Gender), 11 (Disability), 9 (RMNCH), 12 (Nutrition), 3 (Participatory Dev / Good Gov) directly map to GPEDC's question for the population groups the codelist covers; *youth*, *LGBTIQ+*, *indigenous*, *older people*, *refugees / IDPs* aren't in the codelist.
* - 4.2.4
  - Partial / proxy
  - Presence of `dimension` elements on `result/indicator/baseline / period/target / period/actual` is a deterministic signal of disaggregated monitoring; not strictly proof that distributional analysis was performed, but a reasonable proxy.
* - 4.3.1
  - Not supplementable
  - Data-driven assessment behind the NDP — domestic process.
* - 4.3.3
  - Cross-validation / context
  - `document-link[@category='A01' / 'A08' / 'B03']` confirms the strategy / appraisal exists; whether it was data-driven isn't structurally captured.
```

## Distribution

The five categories aren't designed to balance — each indicator is placed wherever the methodology + IATI Standard alignment puts it. The actual distribution comes out:

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Category
  - Count
  - Implication
* - Direct supplement
  - 5
  - The flagship use cases — predictability (annual + medium-term), AIMS reporting, country strategy publication.
* - Partial / proxy supplement
  - 6
  - Structured signal, plus residual survey work for what the codelist / element doesn't cover.
* - Cross-validation / context only
  - 4
  - Useful side-channel; survey remains primary.
* - Already sourced externally
  - 3
  - PEFA, CRS, dashboard already feed in.
* - Not supplementable from IATI
  - 11
  - Largest bucket — and the right answer. Country-side process and perception questions belong in the survey; IATI scope is aid activity data.
```

The largest bucket being "Not supplementable" is the most important methodology finding. The point of the mapping is to be honest about that, so the GPEDC framework can focus IATI use where it actually adds value and keep the survey instrument for the questions that need it.
