"""
Build the GPEDC × IATI mapping Excel workbook.

Question this answers: where can the IATI Standard v2.03 (and the IATI
Publishing Statistics dashboard) supplement the *means of verification*
for the GPEDC monitoring framework?

Reference materials consulted:
  - GPEDC 2023-26 Monitoring Questionnaire and Methodological Note (effectivecooperation.org)
  - IATI Standard v2.03 -- iatistandard.org/en/iati-standard/203/
  - IATI Publishing Statistics dashboard -- dev-dashboard.iatistandard.org
  - OECD-DAC paper DCD/DAC/STAT(2026)22 (Linking IATI and CRS) -- one.oecd.org
  - OECD-DAC paper DCD/DAC/STAT(2025)56 (Tracking aid subcontracts) -- one.oecd.org
  - GPEDC MR4 Global Transparency results
  - Local IATI bulk-data mirror

Inputs from the polars notebooks (.tmp/):
  - activities.parquet                       built by scripts/scan_donors.py
  - dp_coverage_summary.parquet              from notebooks/01_dp_coverage.ipynb
  - dp_full_coverage.parquet                 from notebooks/01_dp_coverage.ipynb
  - crs_iati_interop_by_dp.parquet           from notebooks/02_crs_iati_interoperability.ipynb
  - subcontract_visibility_by_dp.parquet     from notebooks/03_untying_subcontracts.ipynb

Output: gpedc_iati_mapping.xlsx
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from gpedc_iati import setup_logging
from gpedc_iati.indicator_mapping import (
    FEASIBILITY_DIRECT,
    FEASIBILITY_EXTERNAL,
    FEASIBILITY_HEX,
    FEASIBILITY_NONE,
    FEASIBILITY_ORDER,
    FEASIBILITY_PARTIAL,
    FEASIBILITY_VALIDATE,
    MAPPING_HEADERS,
    MAPPING_ROWS,
    feasibility_for,
)

log = logging.getLogger("build_mapping")

PROJECT_ROOT = Path(__file__).resolve().parent
TMP = PROJECT_ROOT / ".tmp"

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
WRAP_CENTER = Alignment(wrap_text=True, vertical="center", horizontal="center")
RIGHT = Alignment(horizontal="right", vertical="top")

H1 = Font(name="Calibri", size=16, bold=True, color="1F3864")
H2 = Font(name="Calibri", size=12, bold=True, color="1F3864")
HEAD = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BODY = Font(name="Calibri", size=10)
BODY_BOLD = Font(name="Calibri", size=10, bold=True)

FILL_HEAD = PatternFill("solid", fgColor="1F3864")
FILL_DIM1 = PatternFill("solid", fgColor="E8F1FA")
FILL_DIM2 = PatternFill("solid", fgColor="E8F6EE")
FILL_DIM3 = PatternFill("solid", fgColor="FFF4E2")
FILL_DIM4 = PatternFill("solid", fgColor="F5EBFB")
FILL_ALT = PatternFill("solid", fgColor="FAFAFA")

DIM_FILLS = {
    "1. Whole-of-society": FILL_DIM1,
    "2. State and use of country systems": FILL_DIM2,
    "3. Transparency": FILL_DIM3,
    "4. Leaving no-one behind": FILL_DIM4,
}

GREEN = PatternFill("solid", fgColor="C6EFCE")
LIGHT_GREEN = PatternFill("solid", fgColor="DDEBCB")
YELLOW = PatternFill("solid", fgColor="FFEB9C")
ORANGE = PatternFill("solid", fgColor="FCD9B8")
RED = PatternFill("solid", fgColor="FFC7CE")
GREY = PatternFill("solid", fgColor="F2F2F2")


def style_header(ws: Worksheet, row: int, cols: int, height: int = 38) -> None:
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEAD
        cell.fill = FILL_HEAD
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = BORDER
    ws.row_dimensions[row].height = height


def set_widths(ws: Worksheet, widths: list[int]) -> None:
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_row(ws: Worksheet, row: int, values: list, fill: PatternFill | None = None) -> None:
    for i, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=i, value=val)
        cell.font = BODY
        cell.alignment = WRAP_TOP
        cell.border = BORDER
        if fill is not None:
            cell.fill = fill


def add_title(ws: Worksheet, text: str, ncols: int) -> None:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    cell = ws.cell(row=1, column=1, value=text)
    cell.font = H1
    cell.alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 28


# ---------------------------------------------------------------------------
# Sheet 1 — README
# ---------------------------------------------------------------------------
def build_readme(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "README"
    set_widths(ws, [120])

    sections = [
        (
            "title",
            "GPEDC Monitoring Framework × IATI Standard v2.03 — supplementing means of verification",
        ),
        ("h2", "About this workbook"),
        (
            "p",
            "An indicator-by-indicator mapping of where the IATI Standard v2.03 — the activity standard, transaction-level fields, and the IATI Publishing Statistics dashboard — can supplement the means of verification for the GPEDC monitoring framework, closing the information gap for National Coordinators, Development Partner focal points, and the JST team during a monitoring round.",
        ),
        (
            "p",
            "Noting the broader Financing for Development agenda's call for better interoperability between development-finance data systems and lighter reporting burdens, and the GPEDC's role in tracking the effectiveness of international development cooperation, the mapping surfaces the overlap on concrete touchpoints: untying ODA and tracking local procurement (indicator 2.8.1, supplemented by IATI receiver-org per DCD/DAC/STAT(2025)56); predictability and now-casting (2.4.1.1 / 2.4.1.2, served by the dashboard's Forward-looking metric); cross-referencing and interoperability with the OECD CRS (3.2.1, per DCD/DAC/STAT(2026)22 and the 2026 'external link' field); and streamlining the global and country-level data collection itself, by making the comparative advantage of CRS, PEFA, IATI, and partner-country systems explicit indicator by indicator.",
        ),
        ("h2", "Also available as a web app"),
        (
            "p",
            "The same content — indicator mapping, reporting-org readiness heatmap, CRS×IATI interoperability rates, untying & subcontracts view, and the policy recommendations — is also available as an interactive Plotly Dash web app under app/ in the repository. Run with `uv run python scripts/run_app.py` (default: http://127.0.0.1:8050). The app reads the same parquet outputs the notebooks produce, so it always agrees with this workbook.",
        ),
        ("h2", "Methodology documentation"),
        (
            "p",
            "A separate Sphinx documentation site under docs/ explains the methodology behind every metric — data sources (IATI bulk-data service, registry indices, the GPEDC donor mapping); how reporting-org readiness is calculated step-by-step; the OECD-DAC pipeline reference for the CRS×IATI interoperability metric; and the editorial basis for each feasibility category. Build with `uv run python scripts/build_docs.py`; once the web app is running it serves the docs at http://127.0.0.1:8050/docs/.",
        ),
        ("h2", "Sheets"),
        (
            "p",
            "  • 1_Indicator mapping — every GPEDC indicator with the corresponding IATI element(s), codelists, dashboard metric, and the means-of-verification supplement IATI provides. The Feasibility column is colour-coded and filterable.",
        ),
        (
            "p",
            "  • 2_IATI element reference — every IATI v2.03 element used in the mapping with its XML path, attributes, codelists, and GPEDC relevance. Includes the full transaction-level breadth (transaction-type, value, provider-org, receiver-org, disbursement-channel, sector, recipient-country, flow-type, finance-type, aid-type, tied-status).",
        ),
        (
            "p",
            "  • 3_Dashboard metrics — Forward-looking, Timeliness, Comprehensiveness (Core / Financials / Value-Added) and Coverage methodology, with the GPEDC indicator each one feeds.",
        ),
        (
            "p",
            "  • 4_Reporting-org readiness — per IATI reporting organisation, the % of activities populating each GPEDC-relevant element. Heatmap-coloured. The first columns are the IATI reporting-org ref + name; parent OECD development partner(s) are listed alongside since the GPEDC mapping is many-to-many.",
        ),
        (
            "p",
            "  • 5_CRS×IATI interoperability — per IATI reporting organisation: A1/A2/A9 other-identifier publication rates, tiered into reconciliation modes per OECD-DAC DCD/DAC/STAT(2026)22.",
        ),
        (
            "p",
            "  • 6_Untying & subcontracts — per IATI reporting organisation: transaction/receiver-org rates for the GPEDC indicator-2.8.1 Tier-2 subcontract supplement per OECD-DAC DCD/DAC/STAT(2025)56.",
        ),
        (
            "p",
            "  • 7_Transaction codelist depth — every code in TransactionType, DisbursementChannel, AidType, FlowType, FinanceType, TiedStatus, OtherIdentifierType, with the GPEDC use case for each.",
        ),
        (
            "p",
            "  • 8_Notebook reproduction — pointers from each empirical sheet back to the notebook that produced it.",
        ),
        ("h2", "More on how this is built and how to reproduce it"),
        (
            "p",
            "See the project README on GitHub for installation, the public Python API (`gpedc_iati`), and full reproduction instructions: https://github.com/codywallace/gpedc-monitoring-mapping",
        ),
        ("h2", "Reference documents"),
        (
            "p",
            "  • GPEDC 2023-26 Methodological Note (canonical indicator methodology), Annex 1.1 Monitoring Questionnaire, Annex 6 Guidance for DPs.",
        ),
        (
            "p",
            "  • OECD-DAC: DCD/DAC/STAT(2026)22 (Linking IATI and CRS); DCD/DAC/STAT(2025)56 (Aid subcontracts).",
        ),
        (
            "p",
            "  • IATI Standard v2.03 online: iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/.",
        ),
        ("p", "  • IATI Publishing Statistics dashboard: dev-dashboard.iatistandard.org."),
        ("p", "  • IATI bulk-data service: bulk-data.iatistandard.org."),
        ("p", "  • Financing for Development (broader policy context): financing.desa.un.org."),
    ]

    r = 1
    for kind, text in sections:
        cell = ws.cell(row=r, column=1, value=text)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        if kind == "title":
            cell.font = H1
            ws.row_dimensions[r].height = 28
        elif kind == "h2":
            cell.font = H2
            ws.row_dimensions[r].height = 22
        else:
            cell.font = BODY
            ws.row_dimensions[r].height = max(20, (len(text) // 110 + 1) * 17)
        r += 1


# ---------------------------------------------------------------------------
# Sheet — Indicator mapping
# ---------------------------------------------------------------------------
# The data (MAPPING_ROWS, FEASIBILITY_* constants, feasibility_for) lives in
# gpedc_iati.indicator_mapping so the Dash app and the workbook builder share
# a single source of truth. This file only contains the openpyxl rendering.
FEASIBILITY_FILL: dict[str, PatternFill] = {
    cat: PatternFill("solid", fgColor=FEASIBILITY_HEX[cat]) for cat in FEASIBILITY_ORDER
}


def build_mapping_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("1_Indicator mapping")
    # Column widths — Feasibility (col 4) wide enough for the longest label.
    set_widths(ws, [22, 28, 38, 26, 18, 32, 40, 38, 22, 50, 32])
    add_title(
        ws,
        "GPEDC indicators × IATI v2.03 — supplementing the means of verification",
        len(MAPPING_HEADERS),
    )
    for i, h in enumerate(MAPPING_HEADERS, start=1):
        ws.cell(row=2, column=i, value=h)
    style_header(ws, 2, len(MAPPING_HEADERS))
    ws.freeze_panes = "C3"

    r = 3
    for row_data in MAPPING_ROWS:
        feasibility = feasibility_for(row_data[2])
        # Insert Feasibility as the 4th cell so it's visible and filterable.
        full_row = list(row_data[:3]) + [feasibility] + list(row_data[3:])
        dim_fill = DIM_FILLS.get(row_data[0], FILL_ALT)
        write_row(ws, r, full_row, fill=dim_fill)

        # Re-paint the Feasibility cell with its category-specific colour.
        feas_cell = ws.cell(row=r, column=4)
        feas_cell.fill = FEASIBILITY_FILL.get(feasibility, FILL_ALT)
        feas_cell.font = BODY_BOLD
        feas_cell.alignment = WRAP_CENTER

        longest = max(len(str(v or "")) for v in full_row)
        ws.row_dimensions[r].height = min(220, max(60, longest // 4))
        r += 1
    ws.auto_filter.ref = f"A2:{get_column_letter(len(MAPPING_HEADERS))}{r - 1}"

    # Legend strip below the table — explains the colour code.
    r += 1
    ws.cell(row=r, column=1, value="Legend:").font = BODY_BOLD
    legend_order = [
        FEASIBILITY_DIRECT,
        FEASIBILITY_PARTIAL,
        FEASIBILITY_VALIDATE,
        FEASIBILITY_EXTERNAL,
        FEASIBILITY_NONE,
    ]
    for i, cat in enumerate(legend_order, start=2):
        cell = ws.cell(row=r, column=i, value=cat)
        cell.fill = FEASIBILITY_FILL[cat]
        cell.font = BODY_BOLD
        cell.alignment = WRAP_CENTER
        cell.border = BORDER
    ws.row_dimensions[r].height = 30


# ---------------------------------------------------------------------------
# Sheet — IATI element reference (full transaction breadth)
# ---------------------------------------------------------------------------
IATI_REF_HEADERS = [
    "XML path / element",
    "Attributes & child elements",
    "Codelist(s)",
    "GPEDC relevance",
    "Notes",
]

IATI_REF_ROWS = [
    # ---- Activity-level identification & reporting ----
    (
        "iati-activity",
        "@default-currency, @last-updated-datetime, @xml:lang, @hierarchy, @humanitarian, @linked-data-uri",
        "Currency.",
        "Backbone for all joins; @last-updated-datetime feeds dashboard Timeliness.",
        "Container for all child elements below.",
    ),
    (
        "iati-activity/iati-identifier",
        "(text content)",
        "—",
        "Unique key for project-level joins.",
        "Should be unique across the publisher's portfolio.",
    ),
    (
        "iati-activity/reporting-org",
        "@ref, @type, @secondary-reporter; narrative",
        "OrganisationType.",
        "Identifies the DP (unit of identification for GPEDC Section B). Used to map back to GPEDC donor list.",
        "secondary-reporter=1 means the publisher is republishing someone else's data.",
    ),
    (
        "iati-activity/other-identifier",
        "@ref, @type; owner-org",
        "OtherIdentifierType: A1 Reporting-org internal; A2 CRS Activity Identifier; A3 Previous Activity Identifier; A9 Other Activity Identifier; B1 Previous Reporting-org; B9 Other Org.",
        "FOUNDATIONAL for GPEDC 3.2.1 → CRS interoperability (DCD/DAC/STAT(2026)22). A2 enables direct CRS-record linkage.",
        "Per OECD-paper Layer 1: A1/A2 = highest-confidence cross-system match.",
    ),
    (
        "iati-activity/title and /description",
        "@type (DescriptionType); narrative",
        "DescriptionType.",
        "Used for dashboard Comprehensiveness Core; semantic matching layer (L4) of OECD pipeline.",
        "Up to ~500 chars in IATI vs CRS short=150/long=4000.",
    ),
    # ---- Participation & geography ----
    (
        "iati-activity/participating-org",
        "@ref, @role, @type, @activity-id; narrative",
        "OrganisationRole (1 Funding, 2 Accountable, 3 Extending, 4 Implementing); OrganisationType (10 Gov; 21 Int'l NGO, 22 National NGO, 23 Regional NGO, 24 Univ/Research-based NGO; 30 Public-Private Partnership; 40 Multilateral; 60 Foundation; 70 Private sector, 71 Provider-country, 72 Recipient-country, 73 Third-country; 80 Academic; 90 Other).",
        "Channel-of-delivery proxy for 1.1.4 / 4.1.4; receiver identity for 2.4.1 (public-sector filter when @type=10).",
        "Linked to CRS Channel codes.",
    ),
    (
        "iati-activity/recipient-country",
        "@code, @percentage; narrative",
        "Country (ISO 3166-1 alpha-2).",
        "Filter for all PC-level aggregations.",
        "Mutually exclusive with recipient-region per activity but both at transaction level.",
    ),
    (
        "iati-activity/recipient-region",
        "@code, @vocabulary, @percentage",
        "Region; RegionVocabulary.",
        "Used when activity is multi-country.",
        "—",
    ),
    # ---- Sectoral / cross-cutting ----
    (
        "iati-activity/sector",
        "@vocabulary, @code, @percentage; narrative",
        "SectorVocabulary (1 OECD-DAC 5-digit, 2 DAC 3-digit, 3 COFOG, 4 NACE, 5 NTEE, 6 AidData, 7 SDG Goal, 8 SDG Target, 9 SDG Indicator, 10 Humanitarian Clusters, 11 NAICS, 12 UN System, 98/99 ReportingOrg).",
        "SDG vocabularies (7/8) feed indirect signal for 2.1.1 Q5; DAC purpose codes feed 'public sector' heuristic for 2.4.1.",
        "Default vocabulary=1 if omitted.",
    ),
    (
        "iati-activity/policy-marker",
        "@vocabulary, @code, @significance; narrative",
        "PolicyMarker (1 Gender Equality, 2 Aid to Environment, 3 Participatory Dev/GG, 4 Trade Dev, 5 CBD, 6 UNFCCC Mitigation, 7 UNFCCC Adaptation, 8 UNCCD, 9 RMNCH, 10 DRR, 11 Disability, 12 Nutrition); PolicySignificance (0/1/2 or 3/4).",
        "Direct supplement for 4.2.3 LNOB priorities — partial coverage (no codes for youth, LGBTIQ+, indigenous-as-such, older people, refugees/IDPs).",
        "Vocabulary 1=DAC default; 99 for reporting-org's own.",
    ),
    (
        "iati-activity/humanitarian-scope",
        "@type, @vocabulary, @code; narrative",
        "HumanitarianScopeType, HumanitarianScopeVocabulary (UNGloble Cluster, GLIDE, EMDAT, etc.).",
        "Side context only — no direct GPEDC indicator.",
        "—",
    ),
    (
        "iati-activity/tag",
        "@vocabulary, @code; narrative",
        "TagVocabulary (99 ReportingOrg, others).",
        "Used by some DPs for SDG tagging when sector vocabulary doesn't fit.",
        "—",
    ),
    # ---- Forward-looking financials ----
    (
        "iati-activity/budget",
        "@type, @status; period-start; period-end; value (@currency, @value-date)",
        "BudgetType (1 Original, 2 Revised); BudgetStatus (1 Indicative, 2 Committed); Currency.",
        "FORWARD-LOOKING (2.4.1.2). Annual predictability denominator (2.4.1.1) when @status=2.",
        "Multiple budget elements per activity = multi-period.",
    ),
    (
        "iati-activity/planned-disbursement",
        "@type; period-start; period-end; value (@currency, @value-date); provider-org; receiver-org",
        "BudgetType.",
        "Alternative source for 'scheduled' in 2.4.1.1; complements budget for 2.4.1.2.",
        "Discretionary; not all DPs publish it.",
    ),
    (
        "iati-activity/capital-spend",
        "@percentage",
        "—",
        "Side context.",
        "Share of activity that is capital expenditure.",
    ),
    # ---- TRANSACTION (full breadth) ----
    (
        "iati-activity/transaction",
        "@ref, @humanitarian, @last-updated-datetime",
        "—",
        "Container for all child elements below — the most information-rich part of the standard.",
        "Per activity, repeats 0..N times.",
    ),
    (
        "iati-activity/transaction/transaction-type",
        "@code",
        "TransactionType: 1 Incoming Funds, 2 Outgoing Commitment, 3 Disbursement, 4 Expenditure, 5 Interest Payment, 6 Loan Repayment, 7 Reimbursement, 8 Purchase of Equity, 9 Sale of Equity, 10 Credit Guarantee, 11 Incoming Commitment, 12 Outgoing Pledge, 13 Incoming Pledge.",
        "Code 3 (Disbursement) → 2.4.1.1 numerator. Code 2 (Outgoing Commitment) → committed-line-of-funding signal. Codes 5-10 differentiate flow types for niche analyses.",
        "For GPEDC 'public-sector' aggregation, sum type=3 transactions with disbursement-channel=1 and receiver-org/@type=10.",
    ),
    (
        "iati-activity/transaction/transaction-date",
        "@iso-date",
        "—",
        "Defines reporting year for 2.4.1.1; feeds dashboard Timeliness.",
        "Distinct from value/@value-date (which is the FX reference date).",
    ),
    (
        "iati-activity/transaction/value",
        "(text); @currency, @value-date",
        "Currency.",
        "Amount in context of currency + value-date — needed for cross-currency normalisation.",
        "If currency omitted, falls back to iati-activity/@default-currency.",
    ),
    (
        "iati-activity/transaction/provider-org",
        "@ref, @provider-activity-id, @type; narrative",
        "OrganisationType.",
        "For incoming-funds (type=1) traces upstream funder; foundation for multi-tier flow tracking.",
        "@provider-activity-id closes the loop to the upstream activity.",
    ),
    (
        "iati-activity/transaction/receiver-org",
        "@ref, @receiver-activity-id, @type; narrative",
        "OrganisationType.",
        "FOUNDATIONAL for 2.8.1 subcontract supplement (DCD/DAC/STAT(2025)56). @ref + @receiver-activity-id let us trace funds further down the delivery chain.",
        "Per OECD-paper §40: @ref rarely populated in practice.",
    ),
    (
        "iati-activity/transaction/disbursement-channel",
        "@code",
        "DisbursementChannel: 1 Through central MoF/Treasury; 2 Direct to implementing institution / separate bank account; 3 Aid in kind via NGOs/management companies; 4 Aid in kind, donor-managed.",
        "Code 1 is the strongest evidence for 2.3.3 (use of country PFM). Code 3 signals subcontracting via implementing partners.",
        "Frequently omitted; default = unknown.",
    ),
    (
        "iati-activity/transaction/sector",
        "@vocabulary, @code",
        "SectorVocabulary, Sector.",
        "Allows per-transaction sector tagging when activity has mixed sectors.",
        "Either at activity or transaction level, not both.",
    ),
    (
        "iati-activity/transaction/recipient-country",
        "@code",
        "Country.",
        "Per-transaction PC tagging.",
        "Either at activity or all transactions.",
    ),
    (
        "iati-activity/transaction/recipient-region",
        "@code, @vocabulary",
        "Region.",
        "Multi-country alternative.",
        "—",
    ),
    (
        "iati-activity/transaction/flow-type",
        "@code",
        "FlowType (10 ODA, 20 OOF, 21 Non-export-credit OOF, 22 Officially-supported export credits, 30 Private grants, 35 Private market, 36 Private FDI, 37 Other private flows at market terms, 40 Non-flow, 50 Other flows).",
        "ODA (code 10) is the universe for almost all GPEDC indicators.",
        "Inherits from default-flow-type if absent.",
    ),
    (
        "iati-activity/transaction/finance-type",
        "@code",
        "FinanceType (110 Standard grant, 210 Interest subsidy, 310 Capital subscription on deposit basis, 410 Aid loan exc debt reorg, 421 Reimbursable grant, 510 Common equity, 1100 Guarantees, etc.).",
        "Disambiguates instrument when needed — e.g. excluding loans from 'aid' aggregations.",
        "Inherits from default-finance-type.",
    ),
    (
        "iati-activity/transaction/aid-type",
        "@vocabulary, @code (may repeat with different vocabularies)",
        "AidType vocabulary 1 (DAC default): A01 General budget support; A02 Sector budget support; B01 Core support to NGOs; B02 Core contribs to multilateral; B03 Pooled funds; C01 Project-type; D01 Donor country personnel; D02 Other technical assistance; E01 Scholarships; E02 Imputed student costs; F01 Debt relief; G01 Admin costs; H01 Dev awareness; H02 Refugees in donor country.",
        "PFM-use proxy (2.3.3): A01/A02/B03 ≈ uses country PFM by construction. Vocabulary 2 'Aid Modality' overlay extends the granularity.",
        "Inherits from default-aid-type.",
    ),
    (
        "iati-activity/transaction/tied-status",
        "@code",
        "TiedStatus: 3 Partially tied, 4 Tied, 5 Untied.",
        "Validation cross-check for 2.8.1 (CRS-sourced).",
        "Inherits from default-tied-status.",
    ),
    # ---- Country budget alignment ----
    (
        "iati-activity/country-budget-items",
        "@vocabulary; budget-item (@code, @percentage); description",
        "BudgetIdentifierVocabulary; BudgetIdentifier.",
        "Direct alignment to PC budget classification (1.2.2 / 2.4.2).",
        "Optional; publisher uptake thin (see sheet 4).",
    ),
    # ---- Strategy / documents / results ----
    (
        "iati-activity/document-link",
        "@url, @format; title; description; category; language; document-date",
        "DocumentCategory: A-codes are activity-level (A01 Pre/Post-project, A02 Objectives/Purpose, A03 Budget, A04 Conditions, A05 MoU, A06 Tender, A07 Eval, A08 Results, A09 Memo, A10 Procurement, A11 Bid, A12 Contract); B-codes are organisation-level (B01 Annual report, B02 Institutional strategy, B03 Country strategy paper, B04 Mgmt response, B05 Audit, B06 Country audit, B07 Project audit, B08 Eval briefs, B09 Institutional eval, B10 Country eval).",
        "DIRECT supplement for 3.2.2 (B03), 2.2.1-O (A02), 2.2.1-R (A08).",
        "Activity-level doc-links live inside iati-activity; org-level inside iati-organisation.",
    ),
    (
        "iati-activity/result",
        "@type, @aggregation-status; title; description; document-link; reference; indicator",
        "ResultType (1 Output, 2 Outcome, 3 Impact, 9 Other).",
        "2.2.1-R results framework alignment; 4.2.4 distributional analysis.",
        "Repeatable per activity.",
    ),
    (
        "iati-activity/result/indicator",
        "@measure, @ascending, @aggregation-status; title; description; reference; baseline; period",
        "IndicatorMeasure (1 Unit, 2 Percentage, 3 Nominal, 4 Ordinal, 5 Qualitative).",
        "Per-indicator measurement metadata.",
        "—",
    ),
    (
        "iati-activity/result/indicator/reference",
        "@vocabulary, @code, @indicator-uri",
        "IndicatorVocabulary (1 WHO Registry, 2 Sphere Handbook, 3 US FA Framework, 4 WB-WDI, 5 MDG Indicators, 6 UNOCHA Humanitarian, 7 HIV/AIDS Registry, 8 HIPSO, 9 UN SDG Indicators, 99 Reporting Org). NO 'Country-Owned Results Framework' code in v2.03.",
        "2.2.1-R: SDG-tagged indicators (vocab=9) directly answer 'drawn from country results framework' for the SDG subset.",
        "TAG submission warranted for a CRF code.",
    ),
    (
        "iati-activity/result/indicator/baseline/dimension (also period/target/dimension, period/actual/dimension)",
        "@name, @value; description",
        "Free text — not codelist-controlled.",
        "4.2.4 distributional analysis proxy.",
        "Common names: sex, age, geography.",
    ),
    (
        "iati-activity/related-activity",
        "@ref, @type",
        "RelatedActivityType (1 Parent, 2 Child, 3 Sibling, 4 Co-funded, 5 Third-party).",
        "Used to chain DP activities to MDTFs (relevant for 2.2.1 'co-led MDTF' answer).",
        "—",
    ),
    # ---- Activity-level defaults & misc ----
    (
        "iati-activity/default-aid-type, default-flow-type, default-finance-type, default-tied-status",
        "@code (and @vocabulary on default-aid-type)",
        "AidType, FlowType, FinanceType, TiedStatus.",
        "Activity-level fallback when transactions don't override.",
        "Common pattern — define at activity, override per-transaction only when different.",
    ),
    (
        "iati-activity/legacy-data",
        "@name, @value, @iati-equivalent",
        "—",
        "Side context for migrated data.",
        "—",
    ),
    (
        "iati-activity/conditions",
        "@attached; condition (@type)",
        "ConditionType (1 Policy, 2 Performance, 3 Fiduciary).",
        "Side context.",
        "—",
    ),
    (
        "iati-activity/location",
        "@ref; location-reach; location-id; name; description; activity-description; administrative; point/pos; exactness; location-class; feature-designation",
        "LocationReach, LocationID vocabularies, GeographicLocationClass, etc.",
        "Sub-national targeting for LNOB context — does not directly answer GPEDC questions.",
        "—",
    ),
    # ---- Organisation file ----
    (
        "iati-organisations/iati-organisation/total-budget",
        "period-start; period-end; value",
        "—",
        "Org-level forward budget; back-stop for 2.4.1.2 when activity-level is sparse.",
        "—",
    ),
    (
        "iati-organisations/iati-organisation/recipient-country-budget",
        "recipient-country; period-start; period-end; value",
        "Country.",
        "Org-level forward spend by recipient country — strong fallback for 2.4.1.2 when activity-level budgets are absent.",
        "—",
    ),
    (
        "iati-organisations/iati-organisation/document-link",
        "@url, @format; title; description; category; language; document-date",
        "DocumentCategory (B-codes).",
        "Where DP B03 country strategies live when not attached to activities.",
        "—",
    ),
]


def build_iati_ref(wb: Workbook) -> None:
    ws = wb.create_sheet("2_IATI element reference")
    set_widths(ws, [55, 60, 50, 45, 35])
    add_title(
        ws,
        "IATI v2.03 — every element used in the mapping (full transaction-level breadth)",
        len(IATI_REF_HEADERS),
    )
    for i, h in enumerate(IATI_REF_HEADERS, start=1):
        ws.cell(row=2, column=i, value=h)
    style_header(ws, 2, len(IATI_REF_HEADERS))
    ws.freeze_panes = "A3"

    r = 3
    section_starts = {3, 8, 12, 18, 28, 33}  # rows that start a new family
    for row_data in IATI_REF_ROWS:
        fill = FILL_ALT if r in section_starts else None
        write_row(ws, r, list(row_data), fill=fill)
        longest = max(len(str(v or "")) for v in row_data)
        ws.row_dimensions[r].height = min(180, max(40, longest // 4))
        r += 1
    ws.auto_filter.ref = f"A2:{get_column_letter(len(IATI_REF_HEADERS))}{r - 1}"


# ---------------------------------------------------------------------------
# Sheet — Dashboard metrics
# ---------------------------------------------------------------------------
DASH_HEADERS = [
    "Dashboard metric",
    "Definition",
    "Computation",
    "GPEDC indicator(s) it directly serves",
    "Methodology note",
]

DASH_ROWS = [
    (
        "Forward-looking",
        "Share of a publisher's currently-active activities that carry budgets covering the current and next two fiscal years.",
        "Per publisher and per year N: numerator = # of activities current at start of year N with a budget for year N; denominator = total activities current at start of year N. Activities excluded if <6 months remaining OR ≥90% of commitment already disbursed/expended. Red flag = budgets at multiple hierarchy levels; yellow flag = uses 'budget not provided' attribute.",
        "GPEDC 2.4.1.2 (medium-term predictability) — directly maps to A3_1, A3_2, A3_3.",
        "User filters dashboard rebuild to recipient-country=PC and converts year-N/N+1/N+2 ratios into the three dichotomous f_ij^{t+1..t+3} variables.",
    ),
    (
        "Timeliness",
        "How frequently a publisher updates IATI data, inferred from observed transaction-date changes per month over the last 12 months.",
        "Bucket: Monthly / Quarterly / Six-monthly / Annual / Less than Annual.",
        "GPEDC 2.7.2 sub-question A5_8.2 (DP reports at requested frequency) — direct 1:1 mapping.",
        "Cross-walk: PC's requested AIMS frequency (A5_7) vs DP's Timeliness bucket.",
    ),
    (
        "Comprehensiveness — Core (×2 weight)",
        "Average share of current activities populated with the elements that make an IATI record valid and usable.",
        "Elements: iati-identifier, reporting-org, title, description, activity-status, activity-date, participating-org, recipient-country/region, sector.",
        "Pre-requisite for 2.7.2 (A5_8.3 'DP provides requested information').",
        "Threshold rule: pre-fill A5_8.3 = Yes if Core ≥ 70%.",
    ),
    (
        "Comprehensiveness — Financials (×1 weight)",
        "Coverage of transaction commitment, transaction spend (disbursement/expenditure), transaction currency, budget.",
        "—",
        "Gate for 2.4.1.1 / 2.4.1.2 / 1.2.2 / 2.4.2 — only pre-fill from IATI when Financials ≥ threshold.",
        "Suggested gate: ≥ 75% activities with both transaction-type=2 commitments and type=3 disbursements.",
    ),
    (
        "Comprehensiveness — Value-Added (×1 weight)",
        "Coverage of contact-info, location, conditions, policy-marker, result, document-link, country-budget-items, default-tied-status, capital-spend.",
        "—",
        "Enables: 4.2.3 (policy-marker), 3.2.2 (document-link B03), 2.2.1-R (result/indicator/reference), 4.2.4 (indicator dimension), 1.2.2 (country-budget-items).",
        "Drives most of the 'pre-fill possible' indicators; varies most across publishers.",
    ),
    (
        "Coverage — used in adjusted IATI score for 3.2.1",
        "IATI commitments + disbursements compared against OECD-DAC ODA totals (CRS).",
        "Adjustment factor: ≥80% = 1.0 (Excellent); 60–80% = 0.8 (Good); 40–60% = 0.6 (Fair); <40% = 0.4 (Poor).",
        "GPEDC 3.2.1 directly.",
        "Currently aggregate. Future: project-by-project via IATI other-identifier A2 (DCD/DAC/STAT(2026)22 §35–36).",
    ),
]


def build_dashboard(wb: Workbook) -> None:
    ws = wb.create_sheet("3_Dashboard metrics")
    set_widths(ws, [30, 38, 55, 45, 50])
    add_title(
        ws, "IATI Publishing Statistics dashboard — what each metric measures", len(DASH_HEADERS)
    )
    for i, h in enumerate(DASH_HEADERS, start=1):
        ws.cell(row=2, column=i, value=h)
    style_header(ws, 2, len(DASH_HEADERS))
    ws.freeze_panes = "A3"

    r = 3
    for row_data in DASH_ROWS:
        fill = FILL_ALT if r % 2 else None
        write_row(ws, r, list(row_data), fill=fill)
        longest = max(len(str(v or "")) for v in row_data)
        ws.row_dimensions[r].height = min(220, max(60, longest // 4))
        r += 1


# ---------------------------------------------------------------------------
# Helpers for the per-reporting-org sheets
# ---------------------------------------------------------------------------
# Identity columns shown first on every per-reporting-org sheet.
ID_COLS = [
    "reportingorg_ref",
    "reportingorg_name",
    "parent_donor_name(s)",
    "donor_code(s)",
    "publisher_slug",
]
# Pretty header label per column
HEADER_LABEL = {
    "reportingorg_ref": "IATI reporting-org ref",
    "reportingorg_name": "IATI reporting-org name",
    "parent_donor_name(s)": "Parent development partner(s)",
    "donor_code(s)": "OECD donor code(s)",
    "publisher_slug": "Publisher slug",
}


def _heatmap_colour(v) -> PatternFill | None:
    if v is None:
        return None
    if v >= 80:
        return GREEN
    if v >= 60:
        return LIGHT_GREEN
    if v >= 30:
        return YELLOW
    if v >= 10:
        return ORANGE
    return RED


def _write_per_reportingorg_sheet(
    wb: Workbook,
    sheet_name: str,
    title_text: str,
    parquet_path: Path,
    intro_text: str | None = None,
    tier_col: str | None = None,
) -> None:
    if not parquet_path.exists():
        return
    df = pl.read_parquet(parquet_path)
    headers = list(df.columns)

    # Width per column
    width_for = {
        "reportingorg_ref": 22,
        "reportingorg_name": 45,
        "parent_donor_name(s)": 45,
        "donor_code(s)": 14,
        "publisher_slug": 20,
    }
    widths: list[int] = []
    for h in headers:
        if h in width_for:
            widths.append(width_for[h])
        elif h == tier_col:
            widths.append(48)
        else:
            widths.append(14)

    ws = wb.create_sheet(sheet_name)
    set_widths(ws, widths)
    add_title(ws, title_text, len(headers))

    # Optional intro
    header_row = 2
    if intro_text:
        ws.cell(row=2, column=1, value=intro_text)
        ws.cell(row=2, column=1).font = BODY
        ws.cell(row=2, column=1).alignment = WRAP_TOP
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
        ws.row_dimensions[2].height = 70
        header_row = 3

    for i, h in enumerate(headers, start=1):
        label = HEADER_LABEL.get(h, h.replace("_pct", " %").replace("_", " "))
        ws.cell(row=header_row, column=i, value=label)
    style_header(ws, header_row, len(headers))
    ws.freeze_panes = f"C{header_row + 1}"  # freeze first 2 cols

    r = header_row + 1
    for row in df.to_dicts():
        vals = [row[h] for h in headers]
        write_row(ws, r, vals, fill=FILL_ALT if r % 2 else None)
        for col_i, h in enumerate(headers, start=1):
            if h.endswith("_pct"):
                fill = _heatmap_colour(row[h])
                if fill is not None:
                    ws.cell(row=r, column=col_i).fill = fill
                ws.cell(row=r, column=col_i).alignment = RIGHT
            elif h in {"n_activities", "n_activities_with_tx", "donor_code(s)"}:
                ws.cell(row=r, column=col_i).alignment = RIGHT
            elif h.startswith("n_") or h.startswith("mean_") or h.startswith("total_"):
                ws.cell(row=r, column=col_i).alignment = RIGHT
            if tier_col and h == tier_col:
                tier = row[h] or ""
                if "Project-level" in tier:
                    ws.cell(row=r, column=col_i).fill = GREEN
                elif "Mixed" in tier:
                    ws.cell(row=r, column=col_i).fill = YELLOW
                elif "Aggregate" in tier:
                    ws.cell(row=r, column=col_i).fill = ORANGE
                ws.cell(row=r, column=col_i).font = BODY_BOLD
            if h in {"reportingorg_ref", "reportingorg_name"}:
                ws.cell(row=r, column=col_i).font = BODY_BOLD
        r += 1
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(headers))}{r - 1}"


def build_dp_readiness(wb: Workbook) -> None:
    _write_per_reportingorg_sheet(
        wb,
        "4_Reporting-org readiness",
        "Per IATI reporting-organisation element coverage — % of activities populating each GPEDC-relevant element (notebook 01)",
        TMP / "dp_coverage_summary.parquet",
    )


def build_crs_interop(wb: Workbook) -> None:
    intro = (
        "Per DCD/DAC/STAT(2026)22, OECD's four-layer pipeline matches IATI activities to CRS records "
        "via (L1) other-identifier types A1/A2 = highest confidence, (L2) A9 XM-DAC project numbers, "
        "(L3) donor-specific identifier parsing, (L4) TF-IDF semantic similarity. Overall match rate 21.6 %; "
        "best matches reach 95 % (Netherlands, Norway-Norad). For GPEDC indicator 3.2.1 the practical "
        "implication is: where A1/A2/A9 publication is high, the financial-coverage adjustment can move "
        "from aggregate flow-type to project-by-project reconciliation. The new 2026 CRS field "
        "'external link' for IATI identifiers is the bridge."
    )
    _write_per_reportingorg_sheet(
        wb,
        "5_CRS×IATI interoperability",
        "CRS↔IATI interoperability per IATI reporting organisation — A1/A2/A9 other-identifier rates (notebook 02)",
        TMP / "crs_iati_interop_by_dp.parquet",
        intro_text=intro,
        tier_col="crs_iati_link_tier",
    )


def build_untying(wb: Workbook) -> None:
    intro = (
        "Per DCD/DAC/STAT(2025)56, GPEDC 2.8.1 (untied aid) is currently CRS-only and captures Tier 1 "
        "(prime contracts) only. IATI's receiver-org/@ref + receiver-activity-id can supplement with "
        "Tier 2 (subcontracts) where prime contractors publish to IATI. The OECD pilot found receiver-org/@ref "
        "is rarely populated — country-of-origin must usually be derived through name search. The table below "
        "shows the practical floor per IATI reporting organisation: what share of activities populate "
        "receiver-org/@ref at all."
    )
    _write_per_reportingorg_sheet(
        wb,
        "6_Untying & subcontracts",
        "GPEDC 2.8.1 supplement — IATI receiver-org visibility per IATI reporting organisation (notebook 03)",
        TMP / "subcontract_visibility_by_dp.parquet",
        intro_text=intro,
    )


# ---------------------------------------------------------------------------
# Sheet — Transaction-level codelist depth
# ---------------------------------------------------------------------------
TXLIST_HEADERS = ["Codelist", "Code", "Name", "GPEDC use case"]

TXLIST_ROWS = [
    # TransactionType
    ("TransactionType", "1", "Incoming Funds", "Trace upstream funder (provider-org)"),
    ("TransactionType", "2", "Outgoing Commitment", "Committed line of funding for 2.4.1.1"),
    ("TransactionType", "3", "Disbursement", "Numerator for 2.4.1.1 annual predictability"),
    ("TransactionType", "4", "Expenditure", "Operational spend; rarely used for GPEDC"),
    ("TransactionType", "5", "Interest Payment", "—"),
    ("TransactionType", "6", "Loan Repayment", "—"),
    ("TransactionType", "7", "Reimbursement", "—"),
    ("TransactionType", "8", "Purchase of Equity", "—"),
    ("TransactionType", "9", "Sale of Equity", "—"),
    ("TransactionType", "10", "Credit Guarantee", "—"),
    ("TransactionType", "11", "Incoming Commitment", "Recipient-side commitment confirmation"),
    ("TransactionType", "12", "Outgoing Pledge", "Indicative commitment — predictability signal"),
    ("TransactionType", "13", "Incoming Pledge", "—"),
    # DisbursementChannel
    (
        "DisbursementChannel",
        "1",
        "Through central MoF/Treasury",
        "STRONG signal for 2.3.3 PFM use; 1.2.2 / 2.4.2 on-budget",
    ),
    (
        "DisbursementChannel",
        "2",
        "Direct to implementing institution / separate bank account",
        "Implies parallel to MoF; 2.3.3 weaker",
    ),
    (
        "DisbursementChannel",
        "3",
        "Aid in kind via NGOs/management companies",
        "Subcontracting flag for 2.8.1",
    ),
    ("DisbursementChannel", "4", "Aid in kind, donor-managed", "Donor-direct; not on-budget"),
    # AidType (vocabulary 1, DAC)
    ("AidType (DAC)", "A01", "General budget support", "2.3.3 = uses country PFM by construction"),
    ("AidType (DAC)", "A02", "Sector budget support", "2.3.3 = uses country PFM by construction"),
    ("AidType (DAC)", "B01", "Core support to NGOs", "Pure NGO modality"),
    (
        "AidType (DAC)",
        "B02",
        "Core contributions to multilateral institutions",
        "Multilateral pass-through",
    ),
    (
        "AidType (DAC)",
        "B03",
        "Contributions to specific-purpose programmes / pooled funds",
        "2.3.3 partial PFM; 2.2.1 'co-led MDTF'",
    ),
    ("AidType (DAC)", "C01", "Project-type intervention", "2.3.3 typically parallel systems"),
    ("AidType (DAC)", "D01", "Donor country personnel", "TA, donor-managed"),
    ("AidType (DAC)", "D02", "Other technical assistance", "TA, in-country"),
    ("AidType (DAC)", "E01", "Scholarships / training in donor country", "—"),
    ("AidType (DAC)", "E02", "Imputed student costs", "—"),
    ("AidType (DAC)", "F01", "Debt relief", "—"),
    ("AidType (DAC)", "G01", "Administrative costs", "Usually excluded from 2.8.1"),
    ("AidType (DAC)", "H01", "Development awareness", "Donor-side"),
    (
        "AidType (DAC)",
        "H02",
        "Refugees in donor country",
        "In-donor refugee costs (excluded from 2.8.1 by definition)",
    ),
    # FlowType
    ("FlowType", "10", "ODA", "GPEDC universe"),
    ("FlowType", "20", "OOF", "Other Official Flows — outside GPEDC scope unless flagged"),
    ("FlowType", "21", "Non-export-credit OOF", "—"),
    ("FlowType", "22", "Officially-supported export credits", "—"),
    ("FlowType", "30", "Private grants", "—"),
    ("FlowType", "35", "Private market", "—"),
    ("FlowType", "36", "Private FDI", "—"),
    ("FlowType", "37", "Other private flows at market terms", "—"),
    ("FlowType", "40", "Non-flow", "—"),
    ("FlowType", "50", "Other flows", "—"),
    # FinanceType (selected)
    ("FinanceType (selected)", "110", "Standard grant", "Typical grant"),
    ("FinanceType (selected)", "210", "Interest subsidy", "—"),
    (
        "FinanceType (selected)",
        "410",
        "Aid loan excl. debt reorganisation",
        "Concessional loan — counts toward ODA",
    ),
    ("FinanceType (selected)", "421", "Reimbursable grant", "—"),
    ("FinanceType (selected)", "510", "Common equity", "Equity investment"),
    ("FinanceType (selected)", "1100", "Guarantees", "Risk-bearing"),
    # TiedStatus
    ("TiedStatus", "3", "Partially tied", "Cross-validation for 2.8.1"),
    ("TiedStatus", "4", "Tied", "Cross-validation for 2.8.1"),
    ("TiedStatus", "5", "Untied", "Cross-validation for 2.8.1"),
    # OtherIdentifierType
    (
        "OtherIdentifierType",
        "A1",
        "Reporting Org's internal activity identifier",
        "OECD pipeline L1",
    ),
    (
        "OtherIdentifierType",
        "A2",
        "CRS Activity Identifier",
        "OECD pipeline L1 — flagship for interoperability",
    ),
    ("OtherIdentifierType", "A3", "Previous Activity Identifier", "ID-change tracking"),
    ("OtherIdentifierType", "A9", "Other Activity Identifier", "OECD pipeline L2 (XM-DAC format)"),
    ("OtherIdentifierType", "B1", "Previous Reporting Org Identifier", "Org change tracking"),
    ("OtherIdentifierType", "B9", "Other Organisation Identifier", "—"),
]


def build_codelist_depth(wb: Workbook) -> None:
    ws = wb.create_sheet("7_Transaction codelist depth")
    set_widths(ws, [22, 12, 50, 60])
    add_title(
        ws,
        "Transaction-level codelist depth — every code, every GPEDC use case",
        len(TXLIST_HEADERS),
    )
    for i, h in enumerate(TXLIST_HEADERS, start=1):
        ws.cell(row=2, column=i, value=h)
    style_header(ws, 2, len(TXLIST_HEADERS))
    ws.freeze_panes = "A3"

    r = 3
    last_codelist = None
    for row_data in TXLIST_ROWS:
        codelist = row_data[0]
        fill = FILL_ALT if codelist == last_codelist else None
        # subtle separator at codelist boundary
        if codelist != last_codelist and last_codelist is not None:
            for c in range(1, len(TXLIST_HEADERS) + 1):
                ws.cell(row=r, column=c).border = Border(
                    top=Side(border_style="medium", color="1F3864")
                )
        write_row(ws, r, list(row_data), fill=fill)
        if row_data[3] != "—" and "STRONG" in (row_data[3] or "").upper():
            ws.cell(row=r, column=4).fill = GREEN
        ws.row_dimensions[r].height = max(20, len(row_data[3] or "") // 5)
        last_codelist = codelist
        r += 1
    ws.auto_filter.ref = f"A2:{get_column_letter(len(TXLIST_HEADERS))}{r - 1}"


# ---------------------------------------------------------------------------
# Sheet — Notebook reproduction
# ---------------------------------------------------------------------------
NOTEBOOK_HEADERS = ["Notebook", "Question it answers", "Inputs", "Outputs", "Re-run command"]

NOTEBOOK_ROWS = [
    (
        "notebooks/01_dp_coverage.ipynb",
        "For each of the 99 reporting-org refs in the GPEDC official donor mapping, what share of their IATI activities populate each GPEDC-relevant element?",
        ".tmp/activities.parquet (built by scripts/scan_donors.py); .tmp/scan_log.parquet; data/GPEDC_Global_Data_20Apr2026.xlsx (Global Transparency sheet for sanity-check).",
        ".tmp/dp_coverage_summary.parquet → sheet 4 of this workbook; .tmp/dp_full_coverage.parquet (per-element detail).",
        "uv run jupyter lab notebooks/01_dp_coverage.ipynb",
    ),
    (
        "notebooks/02_crs_iati_interoperability.ipynb",
        "Per donor, what is the publication rate of the three CRS-relevant other-identifier types (A1, A2, A9), and how does it compare to the OECD pipeline match rates in DCD/DAC/STAT(2026)22?",
        ".tmp/activities.parquet; hardcoded reference table from the OECD paper.",
        ".tmp/crs_iati_interop_by_dp.parquet → sheet 5.",
        "uv run jupyter lab notebooks/02_crs_iati_interoperability.ipynb",
    ),
    (
        "notebooks/03_untying_subcontracts.ipynb",
        "Per donor, how often is transaction/receiver-org/@ref populated — i.e. how feasible is using IATI to supplement GPEDC 2.8.1 with subcontract visibility per DCD/DAC/STAT(2025)56?",
        ".tmp/activities.parquet.",
        ".tmp/subcontract_visibility_by_dp.parquet → sheet 6; disbursement_channel_dist.parquet; tied_status_dist.parquet.",
        "uv run jupyter lab notebooks/03_untying_subcontracts.ipynb",
    ),
]


def build_notebooks_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("8_Notebook reproduction")
    set_widths(ws, [42, 60, 50, 50, 35])
    add_title(
        ws,
        "Polars notebooks under notebooks/ — how this analysis is reproducible end-to-end",
        len(NOTEBOOK_HEADERS),
    )
    for i, h in enumerate(NOTEBOOK_HEADERS, start=1):
        ws.cell(row=2, column=i, value=h)
    style_header(ws, 2, len(NOTEBOOK_HEADERS))
    ws.freeze_panes = "A3"

    r = 3
    for row_data in NOTEBOOK_ROWS:
        fill = FILL_ALT if r % 2 else None
        write_row(ws, r, list(row_data), fill=fill)
        longest = max(len(str(v or "")) for v in row_data)
        ws.row_dimensions[r].height = min(180, max(50, longest // 3))
        r += 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    log_path = setup_logging("build_mapping")
    log.info("build_mapping starting — log file: %s", log_path)

    wb = Workbook()
    build_readme(wb)
    build_mapping_sheet(wb)
    build_iati_ref(wb)
    build_dashboard(wb)
    build_dp_readiness(wb)
    build_crs_interop(wb)
    build_untying(wb)
    build_codelist_depth(wb)
    build_notebooks_sheet(wb)

    out = PROJECT_ROOT / "gpedc_iati_mapping.xlsx"
    wb.save(out)
    log.info("wrote %s", out)


if __name__ == "__main__":
    main()
