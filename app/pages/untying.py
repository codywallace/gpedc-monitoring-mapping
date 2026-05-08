"""Untying ODA & subcontracts — receiver-org publication rates per IATI reporting organisation."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
from dash import dash_table, dcc, html

from app.data import SUBCONTRACT

dash.register_page(
    __name__,
    path="/untying",
    name="Untying & subcontracts",
    order=4,
)


def _bar(df: pl.DataFrame, top_n: int = 30):
    if df.height == 0:
        return px.bar(title="No data — run scripts/scan_donors.py first")
    df = df.sort("n_activities_with_tx", descending=True).head(top_n)
    pdf = df.with_columns(
        label=pl.col("reportingorg_name").str.slice(0, 38)
        + " ("
        + pl.col("reportingorg_ref")
        + ")",
    ).to_pandas()
    fig = px.bar(
        pdf,
        x="any_receiver_ref_pct",
        y="label",
        orientation="h",
        labels={
            "any_receiver_ref_pct": "% of activities with at least one transaction/receiver-org/@ref",
            "label": "",
        },
        color="any_receiver_ref_pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text="any_receiver_ref_pct",
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        height=max(500, 22 * top_n),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        yaxis=dict(autorange="reversed"),
    )
    return fig


def _table(df: pl.DataFrame):
    if df.height == 0:
        return html.Div("No data available.", className="text-muted")
    cols = [
        {"name": "Reporting-org ref", "id": "reportingorg_ref"},
        {"name": "Reporting-org name", "id": "reportingorg_name"},
        {"name": "Parent DP(s)", "id": "parent_donor_name(s)"},
        {"name": "Activities w/ transactions", "id": "n_activities_with_tx", "type": "numeric"},
        {
            "name": "Receiver-org/@ref %",
            "id": "any_receiver_ref_pct",
            "type": "numeric",
            "format": {"specifier": ".1f"},
        },
        {
            "name": "Receiver-activity-id %",
            "id": "any_receiver_activity_id_pct",
            "type": "numeric",
            "format": {"specifier": ".1f"},
        },
        {
            "name": "Mean distinct receivers / activity",
            "id": "mean_distinct_receivers",
            "type": "numeric",
            "format": {"specifier": ".2f"},
        },
        {
            "name": "Disbursement %",
            "id": "any_disbursement_pct",
            "type": "numeric",
            "format": {"specifier": ".1f"},
        },
        {"name": "Total disbursement tx", "id": "total_disbursement_tx", "type": "numeric"},
    ]
    return dash_table.DataTable(
        data=df.to_dicts(),
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
                    "filter_query": "{any_receiver_ref_pct} >= 80",
                    "column_id": "any_receiver_ref_pct",
                },
                "backgroundColor": "#63BE7B",
                "color": "white",
            },
            {
                "if": {
                    "filter_query": "{any_receiver_ref_pct} >= 50 && {any_receiver_ref_pct} < 80",
                    "column_id": "any_receiver_ref_pct",
                },
                "backgroundColor": "#C6EFCE",
            },
            {
                "if": {
                    "filter_query": "{any_receiver_ref_pct} >= 20 && {any_receiver_ref_pct} < 50",
                    "column_id": "any_receiver_ref_pct",
                },
                "backgroundColor": "#FFEB9C",
            },
            {
                "if": {
                    "filter_query": "{any_receiver_ref_pct} < 20",
                    "column_id": "any_receiver_ref_pct",
                },
                "backgroundColor": "#FFC7CE",
            },
        ],
    )


layout = dbc.Container(
    [
        html.H2("Untying ODA & subcontracts", className="mt-3"),
        html.P(
            "GPEDC indicator 2.8.1 (untied aid) is currently sourced from the OECD-DAC "
            "Contract Awards database, which captures only Tier-1 prime contracts. "
            "IATI's transaction/receiver-org element can supplement with Tier-2 "
            "(subcontracts) where prime contractors publish to IATI — but only when "
            "receiver-org/@ref is structurally populated. The chart below shows the "
            "practical floor per IATI reporting organisation.",
            className="text-muted",
        ),
        dbc.Alert(
            [
                "Per OECD-DAC paper ",
                html.Strong("DCD/DAC/STAT(2025)56"),
                ", receiver-org/@ref is rarely populated by prime contractors today, "
                "so country-of-origin must usually be derived through name search. "
                "Alignment of downstream-publishing guidance across DPs that mandate "
                "IATI for their implementing partners (BE, DK, NL, UK, soon SE) is the "
                "precondition for the activity-traceability network to actually form.",
            ],
            color="info",
            className="small",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(
                        "transaction/receiver-org/@ref population — top 30 publishers",
                        className="text-muted mb-2",
                    ),
                    dcc.Graph(figure=_bar(SUBCONTRACT), config={"displayModeBar": False}),
                ]
            ),
            className="mb-4 shadow-sm",
        ),
        html.H5("Full table", className="mt-4"),
        _table(SUBCONTRACT),
    ],
    fluid=True,
)
