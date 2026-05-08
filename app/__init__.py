"""GPEDC × IATI mapping — Dash web app.

Mirrors the analysis in ``gpedc_iati_mapping.xlsx`` as an interactive
multi-page Plotly Dash app. Reads from the same parquet outputs the
notebooks produce; never recomputes data.

Entrypoint: ``app.main`` exposes ``app`` (Dash) and ``server`` (Flask).
"""
