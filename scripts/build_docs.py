"""
Build the Sphinx methodology docs to ``docs/_build/html``.

Run:  uv run python scripts/build_docs.py [--clean]

Equivalent to ``uv run sphinx-build -b html docs docs/_build/html`` with a
log file at ``logs/build_docs_{timestamp}.log``.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from gpedc_iati import setup_logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_SRC = PROJECT_ROOT / "docs"
DOCS_OUT = DOCS_SRC / "_build" / "html"

log = logging.getLogger("build_docs")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--clean", action="store_true", help="Remove docs/_build before building.")
    args = p.parse_args()

    log_path = setup_logging("build_docs")
    log.info("build_docs starting — log file: %s", log_path)

    if args.clean and DOCS_OUT.parent.exists():
        log.info("removing %s", DOCS_OUT.parent)
        shutil.rmtree(DOCS_OUT.parent)

    cmd = [sys.executable, "-m", "sphinx", "-b", "html", str(DOCS_SRC), str(DOCS_OUT)]
    log.info("running: %s", " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        log.error("sphinx-build returned exit code %d", rc)
        return rc
    log.info("docs built — open %s/index.html", DOCS_OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
