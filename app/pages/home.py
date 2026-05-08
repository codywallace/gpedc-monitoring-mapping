"""Home page — context, headline finding, and section navigation."""

from __future__ import annotations

from collections import Counter

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from gpedc_iati.indicator_mapping import (
    FEASIBILITY_HEX,
    FEASIBILITY_ORDER,
    MAPPING_ROWS,
    feasibility_for,
)

dash.register_page(__name__, path="/", name="Overview", order=0)


# Pre-compute the 5-bucket counts from MAPPING_ROWS (same data as the workbook).
_FEAS_COUNTS: Counter[str] = Counter(feasibility_for(r[2]) for r in MAPPING_ROWS)


def _feasibility_card(category: str) -> dbc.Card:
    """One coloured KPI card for a single feasibility category."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H1(
                    str(_FEAS_COUNTS[category]),
                    style={
                        "color": f"#{FEASIBILITY_HEX[category]}",
                        "fontWeight": 700,
                        "marginBottom": "0.2rem",
                    },
                ),
                html.Div(category, className="small text-muted"),
            ]
        ),
        className="text-center shadow-sm h-100",
        style={"borderTop": f"4px solid #{FEASIBILITY_HEX[category]}"},
    )


def _section_card(title: str, body: str, href: str) -> dbc.Card:
    """A nav card pointing to one of the analysis pages."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(body, className="card-text small text-muted"),
                dbc.Button("Open →", href=href, color="primary", size="sm", outline=True),
            ]
        ),
        className="h-100 shadow-sm",
    )


def _feasibility_chart() -> px.bar:
    cats = list(FEASIBILITY_ORDER)
    counts = [_FEAS_COUNTS[c] for c in cats]
    fig = px.bar(
        x=counts,
        y=cats,
        orientation="h",
        text=counts,
        color=cats,
        color_discrete_map={c: f"#{FEASIBILITY_HEX[c]}" for c in cats},
        labels={"x": "GPEDC indicators", "y": ""},
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        plot_bgcolor="white",
        yaxis=dict(autorange="reversed"),
    )
    fig.update_traces(textposition="outside")
    return fig


layout = dbc.Container(
    [
        html.H1("GPEDC × IATI mapping", className="mt-3"),
        html.P(
            "Where can the IATI Standard v2.03 — the activity standard, transaction-level "
            "fields, and the IATI Publishing Statistics dashboard — supplement the means of "
            "verification for the GPEDC monitoring framework, so National Coordinators, "
            "Development Partner focal points, and the JST team can lean on data already "
            "published openly?",
            className="lead",
        ),
        html.Hr(),
        html.H4("Headline finding", className="mt-4"),
        html.P(
            f"Of {sum(_FEAS_COUNTS.values())} GPEDC indicators / sub-indicators, the "
            "Feasibility breakdown of how IATI maps to each is:",
            className="text-muted",
        ),
        dbc.Row(
            [
                dbc.Col(_feasibility_card(cat), xs=12, md=6, lg=4, xl=True, className="mb-3")
                for cat in FEASIBILITY_ORDER
            ],
            className="g-3 mb-4",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(
                        "Indicator counts by feasibility category", className="text-muted mb-3"
                    ),
                    dcc.Graph(figure=_feasibility_chart(), config={"displayModeBar": False}),
                ]
            ),
            className="mb-4 shadow-sm",
        ),
        html.H4("Browse the analysis", className="mt-4"),
        dbc.Row(
            [
                dbc.Col(
                    _section_card(
                        "Indicator mapping",
                        "Filterable, colour-coded view of every GPEDC indicator with the IATI "
                        "elements, codelists, and dashboard metric that map to it.",
                        "/indicator-mapping",
                    ),
                    md=6,
                    lg=4,
                    className="mb-3",
                ),
                dbc.Col(
                    _section_card(
                        "Reporting-org readiness",
                        "Per IATI reporting organisation, the % of activities populating each "
                        "GPEDC-relevant element. Heatmap-coloured.",
                        "/reporting-org",
                    ),
                    md=6,
                    lg=4,
                    className="mb-3",
                ),
                dbc.Col(
                    _section_card(
                        "CRS × IATI interoperability",
                        "Per IATI reporting organisation: A1/A2/A9 other-identifier publication "
                        "rates, tiered into reconciliation modes per OECD-DAC paper "
                        "DCD/DAC/STAT(2026)22.",
                        "/crs-iati",
                    ),
                    md=6,
                    lg=4,
                    className="mb-3",
                ),
                dbc.Col(
                    _section_card(
                        "Untying & subcontracts",
                        "Per IATI reporting organisation: transaction/receiver-org publication "
                        "rates as a Tier-2 supplement to GPEDC indicator 2.8.1 per "
                        "DCD/DAC/STAT(2025)56.",
                        "/untying",
                    ),
                    md=6,
                    lg=4,
                    className="mb-3",
                ),
                dbc.Col(
                    _section_card(
                        "Policy recommendations",
                        "Eight ordered recommendations, from quick wins (publishers can do this "
                        "today) to structural / most ambitious.",
                        "/recommendations",
                    ),
                    md=6,
                    lg=4,
                    className="mb-3",
                ),
            ]
        ),
    ],
    fluid=True,
)
