"""
Launch the Dash web app locally.

Run:  uv run python scripts/run_app.py [--host 127.0.0.1] [--port 8050] [--debug]

The app reads the same parquet outputs the notebooks produce; if the
parquets aren't there yet, every page renders an empty-state placeholder
instead of crashing. To populate the data, run:

    uv run python scripts/scan_donors.py
    uv run python scripts/run_notebooks.py

For deployment, use ``app.main:server`` with gunicorn:

    uv run gunicorn 'app.main:server' --bind 0.0.0.0:8050 --workers 2
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Make the project root importable so ``from app.main import app`` works when
# this script is invoked directly (``uv run python scripts/run_app.py``).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app  # noqa: E402  (import after sys.path tweak)
from gpedc_iati import setup_logging  # noqa: E402

log = logging.getLogger("run_app")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8050)
    p.add_argument(
        "--debug",
        action="store_true",
        help="Enable Dash debug mode (hot reload, verbose tracebacks).",
    )
    args = p.parse_args()

    log_path = setup_logging("run_app")
    log.info("run_app starting — log file: %s", log_path)
    log.info("serving on http://%s:%d (debug=%s)", args.host, args.port, args.debug)

    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
