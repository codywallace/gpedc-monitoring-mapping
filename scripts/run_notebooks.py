"""
Execute the three Polars notebooks under ``notebooks/`` in order, in-place.

This is the headless equivalent of opening Jupyter and running each notebook
end-to-end. It is used for CI / one-shot reproduction; the notebooks remain
the canonical documentation.

Run:  ``uv run python scripts/run_notebooks.py``

Logs go to ``logs/run_notebooks_{timestamp}.log`` and to stderr.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from gpedc_iati import setup_logging

NOTEBOOKS = [
    "notebooks/01_dp_coverage.ipynb",
    "notebooks/02_crs_iati_interoperability.ipynb",
    "notebooks/03_untying_subcontracts.ipynb",
]

log = logging.getLogger("run_notebooks")


def main() -> int:
    log_path = setup_logging("run_notebooks")
    log.info("run_notebooks starting — log file: %s", log_path)

    root = Path(__file__).resolve().parents[1]
    for nb in NOTEBOOKS:
        path = root / nb
        if not path.exists():
            log.error("missing notebook: %s", nb)
            return 1
        log.info("executing %s", nb)
        rc = subprocess.call(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=600",
                str(path),
            ]
        )
        if rc != 0:
            log.error("%s returned exit code %d", nb, rc)
            return rc
        log.info("%s OK", nb)

    log.info("all notebooks executed; .tmp/ parquet outputs are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
