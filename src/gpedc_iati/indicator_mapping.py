"""
Single source of truth for the GPEDC × IATI indicator mapping table.

Both the Excel workbook builder (``build_mapping.py``) and the Dash web app
(``app/``) import from this module so they render the same content.

The shape is split in two:

  * ``MAPPING_HEADERS`` — the 11 column headers, in display order.
  * ``MAPPING_ROWS``    — 29 indicator tuples, *without* the Feasibility cell.
                         The Feasibility category is resolved at render time
                         from ``FEASIBILITY_BY_INDICATOR`` via ``feasibility_for()``.

  * ``FEASIBILITY_*``       — the five category constants.
  * ``FEASIBILITY_HEX``     — display colour per category as a hex string
                              (no openpyxl / plotly dependency, callers wrap as needed).
  * ``FEASIBILITY_ORDER``   — canonical ordering for filters / legends.
  * ``FEASIBILITY_BY_INDICATOR`` — indicator-prefix → category list.
  * ``feasibility_for(indicator)`` — resolver, longest-prefix match.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Feasibility categorisation
# ---------------------------------------------------------------------------

FEASIBILITY_DIRECT = "Direct supplement"
FEASIBILITY_PARTIAL = "Partial / proxy supplement"
FEASIBILITY_VALIDATE = "Cross-validation / context only"
FEASIBILITY_EXTERNAL = "Already sourced externally"
FEASIBILITY_NONE = "Not supplementable from IATI"

FEASIBILITY_ORDER: list[str] = [
    FEASIBILITY_DIRECT,
    FEASIBILITY_PARTIAL,
    FEASIBILITY_VALIDATE,
    FEASIBILITY_EXTERNAL,
    FEASIBILITY_NONE,
]

# Display colours (hex, no '#'). Wrap with ``#`` for CSS / plotly,
# or pass to openpyxl PatternFill(fgColor=...) directly.
FEASIBILITY_HEX: dict[str, str] = {
    FEASIBILITY_DIRECT: "63BE7B",  # green
    FEASIBILITY_PARTIAL: "C6EFCE",  # light green
    FEASIBILITY_VALIDATE: "FFEB9C",  # yellow
    FEASIBILITY_EXTERNAL: "BDD7EE",  # blue
    FEASIBILITY_NONE: "D9D9D9",  # grey
}


# Indicator-prefix → feasibility category.  Resolved as a startswith()
# against the indicator title; longest prefix wins so that
# ``2.2.1 (O)`` / ``(R)`` / ``(D)`` get distinct categories.
FEASIBILITY_BY_INDICATOR: list[tuple[str, str]] = [
    ("1.1.1", FEASIBILITY_NONE),
    ("1.1.4", FEASIBILITY_VALIDATE),
    ("1.2.1", FEASIBILITY_NONE),
    ("1.2.2", FEASIBILITY_PARTIAL),
    ("1.3.1", FEASIBILITY_NONE),
    ("2.1.1", FEASIBILITY_NONE),
    ("2.2.1 (O)", FEASIBILITY_VALIDATE),
    ("2.2.1 (R)", FEASIBILITY_PARTIAL),
    ("2.2.1 (D)", FEASIBILITY_NONE),
    ("2.3.1 / 2.3.2", FEASIBILITY_EXTERNAL),
    ("2.3.3", FEASIBILITY_PARTIAL),
    ("2.4.1.1", FEASIBILITY_DIRECT),
    ("2.4.1.2", FEASIBILITY_DIRECT),
    ("2.5.1", FEASIBILITY_NONE),
    ("2.6.1", FEASIBILITY_NONE),
    ("2.7.1", FEASIBILITY_NONE),
    ("2.7.2", FEASIBILITY_DIRECT),
    ("2.8.1", FEASIBILITY_EXTERNAL),
    ("3.1.1", FEASIBILITY_NONE),
    ("3.2.1", FEASIBILITY_EXTERNAL),
    ("3.2.2", FEASIBILITY_DIRECT),
    ("4.1.1", FEASIBILITY_NONE),
    ("4.1.4", FEASIBILITY_VALIDATE),
    ("4.2.1", FEASIBILITY_NONE),
    ("4.2.2", FEASIBILITY_NONE),
    ("4.2.3", FEASIBILITY_PARTIAL),
    ("4.2.4", FEASIBILITY_PARTIAL),
    ("4.3.1", FEASIBILITY_NONE),
    ("4.3.3", FEASIBILITY_VALIDATE),
]


def feasibility_for(indicator: str) -> str:
    """Resolve the feasibility category for an indicator title via longest-prefix match.

    More-specific prefixes (e.g. ``2.2.1 (O)``) win over shorter ones (``2.2.1``)
    by sorting longest-first.
    """
    for prefix, feas in sorted(FEASIBILITY_BY_INDICATOR, key=lambda t: -len(t[0])):
        if indicator.startswith(prefix):
            return feas
    raise KeyError(f"no feasibility category for indicator {indicator!r}")


# ---------------------------------------------------------------------------
# The mapping table
# ---------------------------------------------------------------------------

MAPPING_HEADERS: list[str] = [
    "Dimension",
    "Component",
    "Indicator / sub-indicator",
    "Feasibility",
    "GPEDC question ID(s)",
    "Current means of verification",
    "IATI element(s) at v2.03",
    "Codelists / attributes",
    "Dashboard metric",
    "How IATI supplements the MoV",
    "Notes",
]

# 10-column source rows (Feasibility is inserted as the 4th cell at render time).
MAPPING_ROWS: list[tuple] = [
    # ============ Dimension 1 — Whole-of-society ============
    (
        "1. Whole-of-society",
        "1.1 Engagement and dialogue",
        "1.1.1 PCs engage diversity of stakeholders in NDP preparation",
        "A1_2",
        "Partner-country self-report.",
        "—",
        "—",
        "—",
        "Not supplementable. Domestic stakeholder consultation in PC planning is not within the IATI scope.",
        "Retain as survey question.",
    ),
    (
        "1. Whole-of-society",
        "1.1 Engagement and dialogue",
        "1.1.4 DP engages diversity of stakeholders in country-level strategy",
        "B1_2, B1_4",
        "DP focal-point self-report.",
        "iati-activity/participating-org (with @role, @type)",
        "OrganisationRole (1 Funding, 2 Accountable, 3 Extending, 4 Implementing); OrganisationType (10 Gov, 21–24 NGO variants, 40 Multilateral, 60 Foundation, 70–73 Private sector, 80 Academic).",
        "Comprehensiveness — Core (participating-org).",
        "participating-org tells us who is implementing, not who was consulted in drafting. Partial signal — the strategy *exists and was published* (via document-link[@category='B03']) is verifiable; *who was consulted* is not.",
        "Retain survey-level reporting; surface document-link B03 evidence as a confirmation aid.",
    ),
    (
        "1. Whole-of-society",
        "1.2 Parliamentary oversight",
        "1.2.1 PCs report dev-coop info to parliaments regularly",
        "A5_12, A5_12.1",
        "PC self-report.",
        "—",
        "—",
        "—",
        "Not supplementable.",
        "Retain.",
    ),
    (
        "1. Whole-of-society",
        "1.2 Parliamentary oversight",
        "1.2.2 / 2.4.2 Development co-operation recorded on national budget",
        "A3_4 (PC), B3_3 (DP)",
        "PC reports b_ij from budget; DP reports s_ij; ratio per DP-PC link. Heavy DP-focal-point dependency and frequent missing values.",
        "iati-activity/country-budget-items[@vocabulary] / budget-item[@code]; iati-activity/budget[@status='2' Committed] period-end ≥ reporting year; iati-activity/transaction[@transaction-type='3' Disbursement] with recipient-country=PC and disbursement-channel='1' (via central MoF/Treasury).",
        "BudgetIdentifierVocabulary, BudgetIdentifier, BudgetStatus, TransactionType, DisbursementChannel.",
        "country-budget-items adoption thin (see sheet 4).",
        "STRONG MoV supplement when country-budget-items is published — direct alignment to PC budget classifications. Where not, the recipient-country + receiver-org[@type='10' Gov] + disbursement-channel='1' heuristic gives a usable denominator (s_ij) without bilateral DP-focal-point coordination.",
        "User-flagged priority. Document the heuristic in the MR5 methodology note.",
    ),
    (
        "1. Whole-of-society",
        "1.3 CSO enabling environment",
        "1.3.1 CSO enabling environment (EEA, 4 modules)",
        "C_1 – C_17",
        "Three-way perceptions survey (Gov, CSO, DP focal points).",
        "—",
        "—",
        "—",
        "Not supplementable. Civic-space measurement.",
        "Retain.",
    ),
    # ============ Dimension 2 — State and use of country systems ============
    (
        "2. State and use of country systems",
        "2.1 Planning",
        "2.1.1 Quality of NDP (11 elements, Q1–Q11)",
        "A1_1 – A1_22",
        "PC self-report on NDP existence, consultation, online availability, alignment with sector/subnational plans, costing, etc.",
        "—",
        "—",
        "—",
        "Not supplementable from IATI. The NDP is a PC artefact, not an aid activity.",
        "Out of IATI scope.",
    ),
    (
        "2. State and use of country systems",
        "2.2 Respect country's policy space (SDG 17.15.1)",
        "2.2.1 (O) DP project objectives drawn from CRFs/planning tools",
        "B2_6",
        "DP focal point reports per project; one of 6 answer categories.",
        "iati-activity/document-link[@category='A02' Objectives/Purpose, 'B03' Country strategy paper]; iati-activity/related-activity[@type='1' Parent].",
        "DocumentCategory.",
        "—",
        "Document-link signals existence and online availability of the strategy/objectives doc but does not tell us whether the project objectives were *drawn from* the NDP. Partial supplement — confirms publication; does not validate alignment.",
        "Retain survey; surface A02/B03 link in the questionnaire UI.",
    ),
    (
        "2. State and use of country systems",
        "2.2 Respect country's policy space (SDG 17.15.1)",
        "2.2.1 (R) Share of project results indicators drawn from CRFs",
        "B2_10.1 / B2_10",
        "DP focal point reports two integers per project.",
        "iati-activity/result/indicator/reference[@vocabulary, @code, @indicator-uri]",
        "IndicatorVocabulary (1 WHO, 2 Sphere, 4 WB-WDI, 5 MDG, 9 UN SDG, 99 Reporting Org). *No code for 'Country-Owned Results Framework' in v2.03.*",
        "Comprehensiveness — Value-Added (result).",
        "Direct supplement for SDG-tagged indicators (vocabulary=9). For CRF-tagged indicators, requires per-country @indicator-uri convention OR an addition to the IndicatorVocabulary codelist. Submit to IATI TAG.",
        "Mid-priority. SDG share is pre-fillable today.",
    ),
    (
        "2. State and use of country systems",
        "2.2 Respect country's policy space (SDG 17.15.1)",
        "2.2.1 (D) Share of results indicators reported via govt statistical systems",
        "B2_10.2",
        "DP focal point self-report.",
        "—",
        "—",
        "—",
        "Not natively captured. Could be inferred from result/indicator/document-link if DPs cite NSO/NSS sources, but not deterministic.",
        "Retain survey.",
    ),
    (
        "2. State and use of country systems",
        "2.3 Public financial management",
        "2.3.1 / 2.3.2 PEFA quality and change",
        "External (PEFA database)",
        "Already external.",
        "—",
        "—",
        "—",
        "PEFA-sourced; no IATI overlap.",
        "Already pre-filled from external.",
    ),
    (
        "2. State and use of country systems",
        "2.3 Public financial management",
        "2.3.3 DPs use PC PFM systems for public-sector flows",
        "B3_5/6/7/8",
        "DP focal-point reports four amounts (budget execution, financial reporting, audit, procurement) and the denominator (PS).",
        "iati-activity/transaction[@transaction-type='3'] with aid-type[@code='A01'/'A02'] (general/sector budget support) or 'B03' (pooled fund); iati-activity/default-aid-type; iati-activity/transaction/disbursement-channel[@code='1'] (central MoF).",
        "AidType, DisbursementChannel.",
        "Comprehensiveness — Value-Added (default-aid-type, default-flow-type) + Financials (transaction).",
        "Proxy supplement: A01/A02/B03 transactions with disbursement-channel=1 give a strong floor on 'amount that uses country PFM by construction'. C01 (project-type) implies parallel systems unless contradicted by aid-type. DP focal point still confirms the 4-way split for non-budget-support amounts.",
        "Useful cross-check; not a full replacement.",
    ),
    (
        "2. State and use of country systems",
        "2.4 National budget",
        "2.4.1.1 Annual predictability (DP-PC)",
        "B3_2 (disbursed), B3_3 (scheduled)",
        "Both numbers from DP focal point; bilateral coordination.",
        "iati-activity/transaction[@transaction-type='3' Disbursement] for numerator; iati-activity/planned-disbursement (period covering reporting year) OR iati-activity/budget[@status='2' Committed] for denominator. Filter to recipient-country=PC.",
        "TransactionType (3 Disbursement, 2 Outgoing Commitment, 4 Expenditure); BudgetStatus (1 Indicative, 2 Committed); BudgetType (1 Original, 2 Revised); transaction/value/@value-date for currency normalisation.",
        "Coverage (financial coverage vs DAC CRS totals); Comprehensiveness — Financials.",
        "DIRECT MoV supplement. JST can compute both numerator and denominator from IATI for any DP with sufficient Financials comprehensiveness; PC validates the resulting ratio. Eliminates the bilateral DP-PC reconciliation.",
        "Methodology note must specify: which transaction-types form the numerator; how to handle multi-currency value-dates; how to define 'public sector' (recipient-country + disbursement-channel + receiver-org/@type=10).",
    ),
    (
        "2. State and use of country systems",
        "2.4 National budget",
        "2.4.1.2 Medium-term predictability (t+1, t+2, t+3)",
        "A3_1, A3_2, A3_3",
        "PC confirms per-DP whether forward spending plans were received for each of three years.",
        "iati-activity/budget (multiple, with period-start/period-end covering future fiscal years); iati-activity/planned-disbursement (forward periods); iati-organisations/iati-organisation/recipient-country-budget (org-file fallback).",
        "BudgetStatus, BudgetType.",
        "Forward-looking (the dashboard's flagship metric — % of currently-active activities with budgets covering year N, N+1, N+2; excludes activities with <6 months remaining or ≥90 % already disbursed).",
        "DIRECT and DEFINITIONAL MoV supplement — IATI's forward-looking metric *is* the GPEDC question if the PC accepts IATI publication as a forward spending plan. Per-DP dichotomous f_ij^{t+1..t+3} drops out of the dashboard rebuild filtered to recipient-country=PC.",
        "Flagship use case — explicitly cited in OECD JST paper. Note: forward-looking is the weakest dashboard component even for 'Excellent' publishers (UNDP=62, World Bank=70).",
    ),
    (
        "2. State and use of country systems",
        "2.5 Gender budgeting (SDG 5.c.1)",
        "2.5.1 PC systems track gender allocations",
        "A4_1.1 – A4_3.3",
        "PC self-report (13 yes/no).",
        "iati-activity/policy-marker[@code='1' Gender Equality]/@significance",
        "PolicyMarker; PolicySignificance (0 Not targeted, 1 Significant, 2 Principal).",
        "Comprehensiveness — Value-Added.",
        "Side-information at most. Indicator is about the PC's *own* PFM, not what DPs fund. Policy-marker tells you DP behaviour, not government behaviour.",
        "Out of IATI scope for the indicator itself.",
    ),
    (
        "2. State and use of country systems",
        "2.6 Accountability mechanisms",
        "2.6.1 5 elements of mutual accountability",
        "A2_1 – A2_15",
        "PC self-report.",
        "—",
        "—",
        "—",
        "Not supplementable. (OECD SCM31 paper proposes removing this indicator.)",
        "Retain or remove per SC decision.",
    ),
    (
        "2. State and use of country systems",
        "2.7 Information management",
        "2.7.1 PC has dev-coop information-management system",
        "A5_1 – A5_7",
        "PC self-report.",
        "—",
        "—",
        "—",
        "PC system question; not IATI.",
        "Retain.",
    ),
    (
        "2. State and use of country systems",
        "2.7 Information management",
        "2.7.2 DPs report to country AIMS at requested frequency",
        "A5_8.1, A5_8.2, A5_8.3",
        "PC confirms per-DP three booleans.",
        "iati-activity (presence) for the DP filtered to recipient-country=PC; whole-publisher iati-organisation last-updated-datetime cadence.",
        "—",
        "Timeliness (Monthly/Quarterly/Six-monthly/Annual/Less-than-Annual buckets); Comprehensiveness — Core.",
        "MoV supplement IF the PC's AIMS ingests IATI (e.g. via AidStream or d-portal). Then publishing to IATI satisfies A5_8.1; cadence maps onto Timeliness; A5_8.3 maps onto Comprehensiveness.",
        "Pre-fill only where the PC has agreed IATI counts as a feed into its AIMS.",
    ),
    (
        "2. State and use of country systems",
        "2.8 Procurement",
        "2.8.1 Aid is untied (CRS commitments)",
        "External (CRS)",
        "OECD CRS data on tied/partially-tied/untied ODA commitments.",
        "iati-activity/transaction/tied-status[@code]; iati-activity/default-tied-status",
        "TiedStatus (3 Partially tied, 4 Tied, 5 Untied).",
        "Comprehensiveness — Value-Added.",
        "Cross-validation only. CRS remains the primary source.",
        "DCD/DAC/STAT(2025)56 proposes IATI as Tier-2 (subcontract) supplement — see sheet 6.",
    ),
    # ============ Dimension 3 — Transparency ============
    (
        "3. Transparency",
        "3.1 Countries' action",
        "3.1.1 PC public availability of NDP, progress reports, MA results, IDC",
        "A1_1.3, A1_19.1, A2_15, A5_11",
        "Four boolean sub-indicators; PC supplies links.",
        "—",
        "—",
        "—",
        "Not IATI — these are PC-published links unrelated to aid activity data.",
        "Out of scope.",
    ),
    (
        "3. Transparency",
        "3.2 Development partners' action",
        "3.2.1 DPs report to global systems (CRS + IATI)",
        "External (CRS rating + IATI dashboard adjusted score)",
        "DPs rated Excellent/Good/Fair/Needs improvement on each.",
        "iati-activity (whole publisher); iati-activity/other-identifier[@type='A1'/'A2'/'A9'] for project-level CRS-IATI linkage.",
        "OtherIdentifierType (A1 Reporting-org Internal, A2 CRS Activity Identifier, A3 Previous, A9 Other Activity Identifier, B1 Previous Reporting Org, B9 Other Org).",
        "Timeliness, Forward-looking, Comprehensiveness, Coverage (each weighted 1/3 within the IATI score; coverage adjusts the score: ≥80%×1.0, 60–80%×0.8, 40–60%×0.6, <40%×0.4).",
        "ALREADY supplements via the dashboard adjustment. Future improvement (DCD/DAC/STAT(2026)22): replace aggregate flow-type Coverage with project-by-project reconciliation when A2 adoption grows. The new 2026 CRS field 'external link' for IATI identifiers is the lever.",
        "See sheet 5 for per-DP A1/A2/A9 status.",
    ),
    (
        "3. Transparency",
        "3.2 Development partners' action",
        "3.2.2 DPs make country-level strategies publicly available",
        "B1_1.2, B1_1.3",
        "DP focal point reports link per country.",
        "iati-activity/document-link[@category='B03' Country strategy paper] (per activity); iati-organisations/iati-organisation/document-link (per organisation, including B02 Institutional Strategy).",
        "DocumentCategory (A01 Pre/Post-project, A02 Objectives, A03 Budget, A04 Conditions, A05 MoU, A07 Evaluation, A08 Results, B01 Annual report, B02 Institutional Strategy, B03 Country strategy paper, B09/B10 Evaluations).",
        "Comprehensiveness — Value-Added.",
        "DIRECT supplement. Where a DP publishes B03 with recipient-country=PC, JST extracts URL and pre-fills the link.",
        "Cleanest pre-fill in the framework.",
    ),
    # ============ Dimension 4 — Leaving no-one behind ============
    (
        "4. Leaving no-one behind",
        "4.1 Consultation",
        "4.1.1–4.1.3 PC engages women/youth/vulnerable groups",
        "A1_2, A1_20.1, A2_14.1",
        "PC self-report.",
        "—",
        "—",
        "—",
        "Not supplementable.",
        "Retain.",
    ),
    (
        "4. Leaving no-one behind",
        "4.1 Consultation",
        "4.1.4 DP engages vulnerable-group CSOs in country strategy prep",
        "B1_4",
        "DP focal-point self-report.",
        "iati-activity/participating-org[@role='4', @type='22 NGO / 23 Regional NGO']; iati-activity/policy-marker[@code='1' Gender, '11' Disability, '3' Participatory Dev/Good Gov].",
        "OrganisationType, PolicyMarker, PolicySignificance.",
        "—",
        "Weak signal. Implementing-partner identity ≠ consultation evidence.",
        "Retain.",
    ),
    (
        "4. Leaving no-one behind",
        "4.2 Targets and results",
        "4.2.1 NDP includes development priorities for population groups",
        "A1_3.1",
        "PC self-report.",
        "—",
        "—",
        "—",
        "Not IATI.",
        "Out of scope.",
    ),
    (
        "4. Leaving no-one behind",
        "4.2 Targets and results",
        "4.2.2 NDP targets/results disaggregated",
        "A1_5, A1_6",
        "PC self-report.",
        "iati-activity/result/indicator/baseline/dimension; iati-activity/result/indicator/period/target/dimension; iati-activity/result/indicator/period/actual/dimension",
        "dimension/@name and @value are free text — not codelist-controlled.",
        "—",
        "Indirect: shows whether DPs aligned with the PC use disaggregation. Doesn't answer the NDP-side question.",
        "Retain for the NDP-side question.",
    ),
    (
        "4. Leaving no-one behind",
        "4.2 Targets and results",
        "4.2.3 DP country strategies include priorities for population groups",
        "B1_6",
        "DP focal-point self-report.",
        "iati-activity/policy-marker[@code='1' Gender, '11' Disability, '12' Nutrition, '9' RMNCH, '3' PDGG] with @significance≥1; iati-activity/document-link[@category='B03'] for groups not represented in the PolicyMarker codelist.",
        "PolicyMarker codes 1–12; PolicySignificance.",
        "Comprehensiveness — Value-Added (policy-marker).",
        "Direct supplement for women / disability / RMNCH / nutrition via policy-marker. No PolicyMarker codes for *youth*, *LGBTIQ+*, *indigenous* (alone), *older people*, *refugees/IDPs* — those remain survey-reported.",
        "Partial supplement for the population groups covered by the codelist.",
    ),
    (
        "4. Leaving no-one behind",
        "4.2 Targets and results",
        "4.2.4 DPs use distributional analysis for beneficiary targets/results",
        "B2.11a, B2.11b",
        "DP focal-point reports per project.",
        "iati-activity/result/indicator/baseline/dimension OR period/target/dimension OR period/actual/dimension (presence)",
        "—",
        "Comprehensiveness — Value-Added (result).",
        "Proxy: project flagged 'yes' if any indicator carries ≥1 dimension in baseline/target/actual. Not strictly 'distributional analysis was conducted' but a reasonable signal.",
        "Per-activity gating; PC validates.",
    ),
    (
        "4. Leaving no-one behind",
        "4.3 Data and statistics",
        "4.3.1 Data-based assessments inform NDP",
        "A1_13 – A1_16",
        "PC self-report.",
        "—",
        "—",
        "—",
        "Not IATI.",
        "Out of scope.",
    ),
    (
        "4. Leaving no-one behind",
        "4.3 Data and statistics",
        "4.3.3 Data-based assessments inform DP country strategies",
        "B1_7",
        "DP focal-point self-report.",
        "iati-activity/document-link[@category='A01' Pre/post-project, 'A08' Results, 'B03' Country strategy]",
        "DocumentCategory.",
        "—",
        "Document-link signals only that the strategy / appraisal exists and is published; whether the assessment was data-driven is not captured structurally.",
        "Retain as survey question.",
    ),
]


# ---------------------------------------------------------------------------
# Convenience: render-time row builder
# ---------------------------------------------------------------------------


def rows_with_feasibility() -> list[list]:
    """Return MAPPING_ROWS with the resolved Feasibility category inserted as the 4th cell.

    The result is a list of lists with len == len(MAPPING_HEADERS) (== 11).
    """
    out: list[list] = []
    for row in MAPPING_ROWS:
        feas = feasibility_for(row[2])
        out.append(list(row[:3]) + [feas] + list(row[3:]))
    return out
