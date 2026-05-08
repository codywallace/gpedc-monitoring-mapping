"""Policy recommendations page — eight ordered recommendations with concrete examples."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(
    __name__,
    path="/recommendations",
    name="Recommendations",
    order=5,
)


def _rec_card(number: int, title: str, body, bucket_colour: str = "#1F3864") -> dbc.Card:
    """One recommendation rendered as a card with a coloured number badge."""
    return dbc.Card(
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        str(number),
                        style={
                            "backgroundColor": bucket_colour,
                            "color": "white",
                            "fontWeight": 700,
                            "fontSize": "2rem",
                            "borderRadius": "0.375rem 0 0 0.375rem",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "minHeight": "120px",
                        },
                    ),
                    width=1,
                ),
                dbc.Col(
                    [
                        html.H5(title, className="mt-3"),
                        html.Div(body, className="small text-muted mb-3"),
                    ],
                    width=11,
                ),
            ],
            className="g-0",
        ),
        className="mb-3 shadow-sm",
    )


def _bucket_header(label: str, sub: str, colour: str) -> html.Div:
    return html.Div(
        [
            html.H4(label, className="mt-4 mb-1"),
            html.P(sub, className="text-muted small mb-3"),
        ],
        style={"borderLeft": f"4px solid {colour}", "paddingLeft": "12px"},
    )


layout = dbc.Container(
    [
        html.H2("Policy recommendations", className="mt-3"),
        html.P(
            "Ordered by attainability — the quickest, highest-impact actions first; "
            "the most ambitious last. Most recommendations only require publishing "
            "organisations to use elements that already exist in the IATI Standard v2.03; "
            "one is a Standard extension; the last few are coordination problems.",
            className="text-muted",
        ),
        _bucket_header("Quick wins", "Publishers can do this today", "#63BE7B"),
        _rec_card(
            1,
            "Publish the CRS Activity Identifier in IATI other-identifier[@type='A2']",
            html.Span(
                [
                    "Already an OECD-DAC recommendation in DCD/DAC/STAT(2026)22. Direct support "
                    "for GPEDC indicator 3.2.1: enables financial coverage to shift from "
                    "aggregate flow-type comparison to project-level reconciliation. Today "
                    "only Netherlands MFA, BMZ, Norad, EC INTPA, and a handful of others "
                    "populate it consistently. The 2026 voluntary ",
                    html.Code("external link"),
                    " field on the CRS side is the matching mechanism.",
                ]
            ),
            "#63BE7B",
        ),
        _rec_card(
            2,
            "Publish DP country strategies as document-link[@category='B03']",
            "Direct support for GPEDC indicator 3.2.2 — JST extracts the URL and pre-fills "
            "the questionnaire with no bilateral coordination. Many DPs already publish "
            "the strategy PDF on their organisation file or website; the missing piece "
            "is structured per-recipient tagging.",
            "#63BE7B",
        ),
        _rec_card(
            3,
            "Cross-reference IATI publications to partner-country AIMS using other-identifier",
            "Where a project is registered in a country's AIMS with its own ID, "
            "publishing that ID as an other-identifier lets National Coordinators map "
            "IATI publications to the domestic record without bilateral reconciliation. "
            "A natural extension of the same pattern OECD recommends for CRS.",
            "#63BE7B",
        ),
        _rec_card(
            4,
            "Improve forward-budget population",
            "The IATI Publishing Statistics dashboard's Forward-looking metric is the "
            "GPEDC indicator 2.4.1.2 answer if publishers populate iati-activity/budget "
            "(or planned-disbursement) covering the next two-to-three fiscal years. Even "
            '"Excellent"-rated publishers (UNDP=62, World Bank=70, AfDB=70) score below '
            "their own ceilings here. No standard change required; pure publisher "
            "discipline.",
            "#63BE7B",
        ),
        _bucket_header(
            "Medium-term: Standard extension and donor coordination",
            "Requires a codelist extension or DP-side guidance alignment",
            "#FFEB9C",
        ),
        _rec_card(
            5,
            "Add a Country-Owned Results Framework code to IndicatorVocabulary",
            "v2.03 has codes for SDG indicators (9), WDI (4), MDG (5), Sphere, HIPSO, "
            "etc., but no shared semantic for 'this indicator is drawn from the country "
            "results framework' — which is what GPEDC indicator 2.2.1 (R) actually asks. "
            "Today the only path is vocabulary='99' (Reporting Org) with a free-text "
            "@indicator-uri. Adding a CRF code makes per-project CRF alignment "
            "machine-readable across publishers.",
            "#FFEB9C",
        ),
        _rec_card(
            6,
            "Establish DP ownership of routine downstream publishing as standard practice",
            html.Span(
                [
                    "The IATI Standard already provides every primitive needed to chain "
                    "funds through the delivery network at activity level: ",
                    html.Code("iati-activity/participating-org"),
                    " with ",
                    html.Code("@role"),
                    " (1 Funding, 2 Accountable, 3 Extending, 4 Implementing) + ",
                    html.Code("@ref"),
                    " + ",
                    html.Code("@type"),
                    " + ",
                    html.Code("@activity-id"),
                    "; transaction-level ",
                    html.Code("provider-org/@provider-activity-id"),
                    " and ",
                    html.Code("receiver-org/@receiver-activity-id"),
                    "; and the iati-organisation file. The blocker is not the Standard but "
                    "the guidance. The DPs that currently mandate IATI publication for their "
                    "implementing partners (Belgium, Denmark, Netherlands, the UK, and from "
                    "Q4 2025 Sweden) each give different guidance on scope, cadence, and "
                    "level of detail. Aligning that downstream-publishing guidance is the "
                    "precondition for the activity-traceability network to form, and for "
                    "IATI to deliver the Tier-2 subcontract supplement to GPEDC indicator "
                    "2.8.1 that DCD/DAC/STAT(2025)56 envisages.",
                ]
            ),
            "#FFEB9C",
        ),
        _bucket_header(
            "Structural / most ambitious",
            "Multi-stakeholder coordination beyond IATI alone",
            "#FCD9B8",
        ),
        _rec_card(
            7,
            "Close the org-id.guide gap for local civil society organisations",
            html.Span(
                [
                    "Truly capturing untying-of-aid at the Tier-2 level depends on being "
                    "able to identify whether a subcontractor is a locally-registered local "
                    "entity. Many local CSOs in low-income or fragile contexts cannot obtain "
                    "national accreditation, so ",
                    html.A("org-id.guide", href="https://org-id.guide/", target="_blank"),
                    " has limited coverage there. At the same time, INGOs registered in "
                    "developing countries can legitimately appear 'locally registered' "
                    "without representing local capacity. A genuine measure of local "
                    "procurement requires investment in national CSO registry coverage and "
                    "disambiguation conventions distinguishing locally-rooted entities from "
                    "in-country INGO branches. Bigger than IATI alone — spans Open "
                    "Contracting, philanthropy, and the broader civil-society data "
                    "ecosystem.",
                ]
            ),
            "#FCD9B8",
        ),
        _rec_card(
            8,
            "GPEDC proactively uses IATI data to drive trilateral conversations (PC ↔ DP ↔ JST)",
            "The data-quality gap on IATI publication is fundamentally a flywheel "
            "problem: if the data isn't used, publishers don't invest in improving it; "
            "if it's used, they do. By systematically surfacing per-publisher gaps "
            "(forward-looking weak, country-budget-items missing, receiver-org un-typed, "
            "etc.) at country level during each monitoring round, GPEDC creates a "
            "direct feedback loop that incentivises better DP publication — which in "
            "turn closes the GPEDC monitoring's own data-collection loop. The strongest "
            "version: GPEDC accepts IATI publication as a means of verification by "
            "default for indicators where it's a Direct supplement, and publishes per-DP "
            "gap reports for the indicators where it's a Partial supplement.",
            "#FCD9B8",
        ),
        html.Hr(className="mt-5"),
        html.P(
            [
                "These recommendations are the same as in the project ",
                html.A(
                    "README on GitHub",
                    target="_blank",
                    href="https://github.com/codywallace/gpedc-monitoring-mapping#policy-recommendations",
                ),
                ".",
            ],
            className="text-muted small mt-3",
        ),
    ],
    fluid=True,
)
