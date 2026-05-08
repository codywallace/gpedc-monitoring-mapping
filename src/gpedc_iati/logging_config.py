"""
Project-wide logging.

Console (stderr) gets INFO; the per-run log file under ``logs/`` gets DEBUG.
Call :func:`setup_logging` once at the start of every entry point (scripts,
notebooks). Subsequent calls are idempotent — handlers are not duplicated.

Log filenames follow ``logs/{script_name}_{YYYYMMDD-HHMMSS}.log`` so a session
can be reconstructed in chronological order.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Override with GPEDC_LOG_DIR for read-only filesystems (e.g. the production
# container, where /app is read-only and logs must go to a tmpfs-mounted /tmp).
LOGS_DIR = Path(os.environ.get("GPEDC_LOG_DIR", PROJECT_ROOT / "logs"))

_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"
_CONFIGURED = False


def setup_logging(
    script_name: str = "gpedc_iati",
    *,
    console_level: int | str = logging.INFO,
    file_level: int | str = logging.DEBUG,
) -> Path:
    """
    Configure the root logger to write to console + a per-run log file.

    Returns the resolved log file path so callers can mention it in their
    own startup banner.
    """
    global _CONFIGURED

    LOGS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS_DIR / f"{script_name}_{timestamp}.log"

    if _CONFIGURED:
        return log_path

    fmt = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(console_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # Quiet the noisier third-party libraries
    for noisy in ("urllib3", "asyncio", "matplotlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True
    logging.getLogger(__name__).info(
        "logging initialised — file=%s, pid=%s, cwd=%s",
        log_path,
        os.getpid(),
        Path.cwd(),
    )
    return log_path
