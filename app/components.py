"""
Shared UI components for the Dash app — navbar, footer, helpers.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

from gpedc_iati.indicator_mapping import FEASIBILITY_HEX, FEASIBILITY_ORDER


def navbar() -> dbc.Navbar:
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("GPEDC × IATI mapping", href="/"),
                dbc.Nav(
                    [
                        dbc.NavLink("Overview", href="/", active="exact"),
                        dbc.NavLink("Indicator mapping", href="/indicator-mapping", active="exact"),
                        dbc.NavLink(
                            "Reporting-org readiness", href="/reporting-org", active="exact"
                        ),
                        dbc.NavLink("CRS × IATI", href="/crs-iati", active="exact"),
                        dbc.NavLink("Untying & subcontracts", href="/untying", active="exact"),
                        dbc.NavLink("Recommendations", href="/recommendations", active="exact"),
                        dbc.NavLink(
                            "Methodology ↗", href="/docs/", external_link=True, target="_blank"
                        ),
                        dbc.NavLink(
                            "GitHub ↗",
                            href="https://github.com/codywallace/gpedc-monitoring-mapping",
                            external_link=True,
                            target="_blank",
                        ),
                    ],
                    pills=True,
                    className="ms-auto",
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        sticky="top",
        className="mb-4",
    )


def footer() -> dbc.Container:
    return dbc.Container(
        html.Footer(
            html.Small(
                [
                    "Project repository ",
                    html.A(
                        "on GitHub",
                        href="https://github.com/codywallace/gpedc-monitoring-mapping",
                        target="_blank",
                    ),
                    " · workbook deliverable: ",
                    html.Code("gpedc_iati_mapping.xlsx"),
                    " · IATI Standard v2.03 · GPEDC monitoring framework",
                ],
                className="text-muted",
            ),
            className="my-4 text-center",
        ),
        fluid=True,
    )


def feasibility_legend() -> dbc.Row:
    """Render the 5-bucket Feasibility legend as colour-coded badges."""
    return dbc.Row(
        [
            dbc.Col(
                html.Span(
                    cat,
                    style={
                        "backgroundColor": f"#{FEASIBILITY_HEX[cat]}",
                        "padding": "4px 10px",
                        "borderRadius": "4px",
                        "fontSize": "0.85rem",
                        "fontWeight": 500,
                        "display": "inline-block",
                    },
                ),
                width="auto",
            )
            for cat in FEASIBILITY_ORDER
        ],
        className="g-2 mb-3",
    )


def kpi_card(title: str, value: str | int, hex_colour: str, subtitle: str = "") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    title,
                    className="card-title text-muted text-uppercase",
                    style={"fontSize": "0.75rem", "letterSpacing": "0.05em"},
                ),
                html.H2(
                    str(value),
                    className="display-5",
                    style={"color": f"#{hex_colour}", "fontWeight": 700},
                ),
                html.Small(subtitle, className="text-muted") if subtitle else None,
            ]
        ),
        className="h-100 shadow-sm",
    )
