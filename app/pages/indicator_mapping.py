"""Indicator mapping page — filterable, colour-coded data table."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, html

from app.components import feasibility_legend
from gpedc_iati.indicator_mapping import (
    FEASIBILITY_HEX,
    FEASIBILITY_ORDER,
    MAPPING_HEADERS,
    rows_with_feasibility,
)

dash.register_page(
    __name__,
    path="/indicator-mapping",
    name="Indicator mapping",
    order=1,
)


# Build the row dicts once on import.
_ALL_ROWS: list[dict] = [
    dict(zip(MAPPING_HEADERS, row, strict=True)) for row in rows_with_feasibility()
]


def _table(rows: list[dict]) -> dash_table.DataTable:
    return dash_table.DataTable(
        id="indicator-mapping-table",
        data=rows,
        columns=[{"name": h, "id": h} for h in MAPPING_HEADERS],
        filter_action="native",
        sort_action="native",
        page_size=30,
        style_as_list_view=False,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "verticalAlign": "top",
            "padding": "8px",
            "fontSize": "0.85rem",
            "fontFamily": "system-ui, -apple-system, sans-serif",
            "whiteSpace": "normal",
            "height": "auto",
            "maxWidth": "420px",
        },
        style_header={
            "backgroundColor": "#1F3864",
            "color": "white",
            "fontWeight": 600,
            "textAlign": "center",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": f'{{Feasibility}} = "{cat}"', "column_id": "Feasibility"},
                "backgroundColor": f"#{FEASIBILITY_HEX[cat]}",
                "fontWeight": 600,
                "textAlign": "center",
            }
            for cat in FEASIBILITY_ORDER
        ],
        style_cell_conditional=[
            {"if": {"column_id": "Indicator / sub-indicator"}, "minWidth": "260px"},
            {"if": {"column_id": "How IATI supplements the MoV"}, "minWidth": "320px"},
            {"if": {"column_id": "IATI element(s) at v2.03"}, "minWidth": "260px"},
            {"if": {"column_id": "Codelists / attributes"}, "minWidth": "260px"},
        ],
    )


layout = dbc.Container(
    [
        html.H2("Indicator mapping", className="mt-3"),
        html.P(
            "Every GPEDC indicator with the corresponding IATI element(s), codelists, "
            "dashboard metric, and means-of-verification supplement. "
            "Use the column filter row to slice; click headers to sort.",
            className="text-muted",
        ),
        feasibility_legend(),
        html.Div(
            [
                html.Label("Filter by Feasibility:", className="me-2 small text-muted"),
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "All",
                            id={"type": "feas-filter", "index": "ALL"},
                            color="primary",
                            outline=False,
                            size="sm",
                            className="me-1",
                        ),
                    ]
                    + [
                        dbc.Button(
                            cat,
                            id={"type": "feas-filter", "index": cat},
                            color="primary",
                            outline=True,
                            size="sm",
                            className="me-1",
                        )
                        for cat in FEASIBILITY_ORDER
                    ],
                ),
            ],
            className="mb-3",
        ),
        _table(_ALL_ROWS),
    ],
    fluid=True,
)


@callback(
    Output("indicator-mapping-table", "data"),
    Input({"type": "feas-filter", "index": dash.ALL}, "n_clicks"),
)
def _filter_rows(_clicks):
    """Filter the table when a feasibility quick-filter button is clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return _ALL_ROWS
    triggered = ctx.triggered[0]["prop_id"]
    if not triggered or "." not in triggered:
        return _ALL_ROWS
    # triggered looks like '{"index":"Direct supplement","type":"feas-filter"}.n_clicks'
    import json

    try:
        comp = json.loads(triggered.split(".")[0])
        idx = comp.get("index", "ALL")
    except (ValueError, KeyError):
        return _ALL_ROWS
    if idx == "ALL":
        return _ALL_ROWS
    return [r for r in _ALL_ROWS if r["Feasibility"] == idx]
