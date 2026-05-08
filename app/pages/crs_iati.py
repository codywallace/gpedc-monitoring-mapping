"""CRS × IATI interoperability — A1/A2/A9 publication rates per IATI reporting organisation."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
from dash import dash_table, dcc, html

from app.data import CRS_INTEROP

dash.register_page(
    __name__,
    path="/crs-iati",
    name="CRS × IATI interoperability",
    order=3,
)

TIER_COLOURS = {
    "Project-level reconciliation possible": "#63BE7B",
    "Mixed — partial reconciliation + L3 parsing": "#FFEB9C",
    "Aggregate ratio only (or L3 parsing if known)": "#FCD9B8",
}


def _stacked_bar(df: pl.DataFrame, top_n: int = 30):
    if df.height == 0:
        return px.bar(title="No data — run scripts/scan_donors.py first")
    df = df.sort("n_activities", descending=True).head(top_n)

    long = df.select(["reportingorg_ref", "reportingorg_name", "a1_pct", "a2_pct", "a9_pct"]).melt(
        id_vars=["reportingorg_ref", "reportingorg_name"],
        value_vars=["a1_pct", "a2_pct", "a9_pct"],
        variable_name="identifier_type",
        value_name="pct",
    )
    label_map = {
        "a1_pct": "A1 (Reporting-org Internal)",
        "a2_pct": "A2 (CRS Activity Identifier)",
        "a9_pct": "A9 (Other Activity Identifier)",
    }
    long = long.with_columns(
        identifier_type=pl.col("identifier_type").replace_strict(label_map),
        label=pl.col("reportingorg_name").str.slice(0, 38)
        + " ("
        + pl.col("reportingorg_ref")
        + ")",
    )

    fig = px.bar(
        long.to_pandas(),
        x="pct",
        y="label",
        color="identifier_type",
        orientation="h",
        labels={"pct": "% of activities", "label": "", "identifier_type": "other-identifier type"},
        color_discrete_map={
            "A1 (Reporting-org Internal)": "#1F77B4",
            "A2 (CRS Activity Identifier)": "#2CA02C",
            "A9 (Other Activity Identifier)": "#FF7F0E",
        },
        barmode="group",
    )
    fig.update_layout(
        height=max(500, 22 * top_n),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
    )
    return fig


def _table(df: pl.DataFrame) -> dash_table.DataTable:
    if df.height == 0:
        return html.Div("No data available.", className="text-muted")
    rows = df.to_dicts()
    cols = [
        {"name": "Reporting-org ref", "id": "reportingorg_ref"},
        {"name": "Reporting-org name", "id": "reportingorg_name"},
        {"name": "Parent DP(s)", "id": "parent_donor_name(s)"},
        {"name": "OECD code(s)", "id": "donor_code(s)"},
        {"name": "Activities", "id": "n_activities", "type": "numeric"},
        {"name": "A1 %", "id": "a1_pct", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "A2 %", "id": "a2_pct", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "A9 %", "id": "a9_pct", "type": "numeric", "format": {"specifier": ".1f"}},
        {
            "name": "Any A1/A2/A9 %",
            "id": "any_crs_id_pct",
            "type": "numeric",
            "format": {"specifier": ".1f"},
        },
        {"name": "Reconciliation tier", "id": "crs_iati_link_tier"},
    ]
    return dash_table.DataTable(
        data=rows,
        columns=cols,
        filter_action="native",
        sort_action="native",
        page_size=30,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px", "fontSize": "0.85rem"},
        style_header={
            "backgroundColor": "#1F3864",
            "color": "white",
            "fontWeight": 600,
            "textAlign": "center",
        },
        style_data_conditional=[
            {
                "if": {
                    "filter_query": f'{{crs_iati_link_tier}} = "{tier}"',
                    "column_id": "crs_iati_link_tier",
                },
                "backgroundColor": colour,
                "fontWeight": 600,
            }
            for tier, colour in TIER_COLOURS.items()
        ]
        + [
            {
                "if": {"filter_query": "{any_crs_id_pct} >= 80", "column_id": "any_crs_id_pct"},
                "backgroundColor": "#63BE7B",
                "color": "white",
            },
            {
                "if": {
                    "filter_query": "{any_crs_id_pct} >= 30 && {any_crs_id_pct} < 80",
                    "column_id": "any_crs_id_pct",
                },
                "backgroundColor": "#FFEB9C",
            },
            {
                "if": {"filter_query": "{any_crs_id_pct} < 30", "column_id": "any_crs_id_pct"},
                "backgroundColor": "#FFC7CE",
            },
        ],
    )


layout = dbc.Container(
    [
        html.H2("CRS × IATI interoperability", className="mt-3"),
        html.P(
            "Per IATI reporting organisation, the share of activities populating "
            "the three CRS-relevant other-identifier types (A1, A2, A9). The "
            "reconciliation tier is derived from the combined A1+A2+A9 rate, "
            "following the OECD-DAC four-layer matching pipeline in "
            "DCD/DAC/STAT(2026)22.",
            className="text-muted",
        ),
        dbc.Alert(
            [
                html.Strong("OECD-DAC recommendation: "),
                "publishers should populate ",
                html.Code("iati-activity/other-identifier[@type='A2']"),
                " with the CRS Activity Identifier. The new 2026 voluntary ",
                html.Code("external link"),
                " field on the CRS side is the matching mechanism.",
            ],
            color="info",
            className="small",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(
                        "A1 / A2 / A9 rates — top 30 publishers by activity count",
                        className="text-muted mb-2",
                    ),
                    dcc.Graph(figure=_stacked_bar(CRS_INTEROP), config={"displayModeBar": False}),
                ]
            ),
            className="mb-4 shadow-sm",
        ),
        html.H5("Full table", className="mt-4"),
        _table(CRS_INTEROP),
    ],
    fluid=True,
)
