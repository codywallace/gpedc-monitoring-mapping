"""
Dash multi-page app entrypoint.

Run locally:
    uv run python -m app.main
    # or, equivalently:
    uv run python app/main.py

Run via gunicorn (deployment):
    uv run gunicorn 'app.main:server' --bind 0.0.0.0:8050 --workers 2

Pages auto-register via ``dash.register_page`` in ``app/pages/*.py``.
"""

from __future__ import annotations

import logging
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Dash
from flask import abort, send_from_directory

from app.components import footer, navbar
from gpedc_iati import setup_logging

setup_logging("app")
log = logging.getLogger("app.main")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_HTML_DIR = PROJECT_ROOT / "docs" / "_build" / "html"

# Use Dash's built-in pages discovery; pages register themselves at import time.
app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=[dbc.themes.FLATLY],
    title="GPEDC × IATI mapping",
    suppress_callback_exceptions=True,
)
server = app.server  # for gunicorn


# Liveness probe — used by docker-compose healthcheck and by external monitors.
@server.route("/healthz")
def _healthz():  # type: ignore[no-untyped-def]
    return {"status": "ok"}, 200


# Serve the Sphinx-built methodology docs at /docs/* (if they've been built).
# Build with:  uv run sphinx-build -b html docs docs/_build/html
@server.route("/docs/", strict_slashes=False)
@server.route("/docs/<path:subpath>")
def _serve_docs(subpath: str = "index.html"):  # type: ignore[no-untyped-def]
    if not DOCS_HTML_DIR.exists():
        abort(
            404,
            description=(
                "Methodology docs have not been built yet. "
                "Run: uv run sphinx-build -b html docs docs/_build/html"
            ),
        )
    target = (DOCS_HTML_DIR / subpath).resolve()
    if target.is_dir():
        target = target / "index.html"
        subpath = f"{subpath.rstrip('/')}/index.html"
    if not str(target).startswith(str(DOCS_HTML_DIR.resolve())):
        abort(404)  # path traversal guard
    return send_from_directory(DOCS_HTML_DIR, subpath)


app.layout = dbc.Container(
    [
        navbar(),
        dbc.Container(dash.page_container, fluid=True, className="px-4"),
        footer(),
    ],
    fluid=True,
    className="px-0",
)


def main() -> int:
    log.info("starting Dash on http://127.0.0.1:8050")
    app.run(host="127.0.0.1", port=8050, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
