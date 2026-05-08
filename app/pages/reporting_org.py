"""Reporting-org readiness — per IATI publisher, % of activities populating each GPEDC theme."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
from dash import dash_table, dcc, html

from app.data import DP_COVERAGE

dash.register_page(
    __name__,
    path="/reporting-org",
    name="Reporting-org readiness",
    order=2,
)

# Identity columns (left side of the table) vs theme columns (the heatmap dimensions).
ID_COLS = [
    "reportingorg_ref",
    "reportingorg_name",
    "parent_donor_name(s)",
    "donor_code(s)",
    "publisher_slug",
    "n_activities",
]
THEME_COLS = [
    "crs_interop_pct",
    "forward_looking_pct",
    "annual_predict_pct",
    "country_budget_items_pct",
    "pfm_use_pct",
    "subcontract_pct",
    "untying_pct",
    "country_strategy_pct",
    "results_crf_pct",
    "lnob_marker_pct",
]
THEME_LABELS = {
    "crs_interop_pct": "CRS interoperability",
    "forward_looking_pct": "Forward-looking",
    "annual_predict_pct": "Annual predictability",
    "country_budget_items_pct": "Country budget items",
    "pfm_use_pct": "PFM use",
    "subcontract_pct": "Subcontract visibility",
    "untying_pct": "Untying (tied-status)",
    "country_strategy_pct": "Country strategy (B03)",
    "results_crf_pct": "Results / CRF",
    "lnob_marker_pct": "LNOB markers",
}


def _heatmap_figure(df: pl.DataFrame, top_n: int = 40):
    if df.height == 0:
        return px.bar(title="No data — run scripts/scan_donors.py first")
    df = df.sort("n_activities", descending=True).head(top_n)
    z_data = df.select(THEME_COLS).fill_null(0).to_numpy()
    y_labels = [f"{r['reportingorg_name'][:50]} ({r['reportingorg_ref']})" for r in df.to_dicts()]
    x_labels = [THEME_LABELS[c] for c in THEME_COLS]

    fig = px.imshow(
        z_data,
        labels=dict(x="GPEDC theme", y="IATI reporting organisation", color="% activities"),
        x=x_labels,
        y=y_labels,
        color_continuous_scale="RdYlGn",
        zmin=0,
        zmax=100,
        aspect="auto",
        text_auto=".0f",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(500, 22 * len(y_labels)),
        plot_bgcolor="white",
        coloraxis_colorbar=dict(title="%"),
    )
    fig.update_xaxes(side="top", tickangle=-30)
    return fig


def _summary_table(df: pl.DataFrame) -> dash_table.DataTable:
    if df.height == 0:
        return html.Div("No data available — run the scan first.", className="text-muted")
    rows = df.to_dicts()
    columns = [
        {"name": "Reporting-org ref", "id": "reportingorg_ref"},
        {"name": "Reporting-org name", "id": "reportingorg_name"},
        {"name": "Parent DP(s)", "id": "parent_donor_name(s)"},
        {"name": "Activities", "id": "n_activities", "type": "numeric"},
    ] + [
        {"name": THEME_LABELS[c], "id": c, "type": "numeric", "format": {"specifier": ".1f"}}
        for c in THEME_COLS
    ]
    return dash_table.DataTable(
        id="dp-readiness-table",
        data=rows,
        columns=columns,
        filter_action="native",
        sort_action="native",
        page_size=25,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "6px",
            "fontSize": "0.8rem",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "#1F3864",
            "color": "white",
            "fontWeight": 600,
            "textAlign": "center",
        },
        style_data_conditional=(
            # Heatmap-style colour for each theme column
            [
                {
                    "if": {"filter_query": f"{{{c}}} >= 80", "column_id": c},
                    "backgroundColor": "#63BE7B",
                    "color": "white",
                }
                for c in THEME_COLS
            ]
            + [
                {
                    "if": {"filter_query": f"{{{c}}} >= 60 && {{{c}}} < 80", "column_id": c},
                    "backgroundColor": "#C6EFCE",
                }
                for c in THEME_COLS
            ]
            + [
                {
                    "if": {"filter_query": f"{{{c}}} >= 30 && {{{c}}} < 60", "column_id": c},
                    "backgroundColor": "#FFEB9C",
                }
                for c in THEME_COLS
            ]
            + [
                {
                    "if": {"filter_query": f"{{{c}}} >= 10 && {{{c}}} < 30", "column_id": c},
                    "backgroundColor": "#FCD9B8",
                }
                for c in THEME_COLS
            ]
            + [
                {
                    "if": {"filter_query": f"{{{c}}} < 10", "column_id": c},
                    "backgroundColor": "#FFC7CE",
                }
                for c in THEME_COLS
            ]
        ),
    )


layout = dbc.Container(
    [
        html.H2("Reporting-org readiness", className="mt-3"),
        html.P(
            "Per IATI reporting organisation (the publisher), the % of activities "
            "populating each GPEDC-relevant element. Each row is one IATI publisher; "
            "parent OECD development partner(s) are shown alongside since the GPEDC "
            "donor mapping is many-to-many.",
            className="text-muted",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(
                        "Heatmap — top 40 publishers by activity count", className="text-muted mb-2"
                    ),
                    dcc.Graph(
                        figure=_heatmap_figure(DP_COVERAGE), config={"displayModeBar": False}
                    ),
                ]
            ),
            className="mb-4 shadow-sm",
        ),
        html.H5("Full table (filterable, sortable)", className="mt-4"),
        _summary_table(DP_COVERAGE),
    ],
    fluid=True,
)
