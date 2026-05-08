"""
Data access layer for the Dash app.

Reads the parquet outputs produced by ``scripts/scan_donors.py`` and the
notebooks under ``notebooks/``. Loads on import (cheap — total ~50 KB
across all summary parquets) and re-uses the same Polars DataFrames across
all pages.

This module is the *only* place pages read data from. Pages should import
the cached DataFrames here, not load them themselves.
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

log = logging.getLogger("app.data")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TMP = PROJECT_ROOT / ".tmp"


def _load_parquet(name: str) -> pl.DataFrame:
    path = TMP / name
    if not path.exists():
        log.warning("missing parquet %s — page data will be empty", path)
        return pl.DataFrame()
    df = pl.read_parquet(path)
    log.debug("loaded %s — %d rows × %d cols", name, df.height, df.width)
    return df


# Per-reporting-org coverage summary (notebook 01)
DP_COVERAGE = _load_parquet("dp_coverage_summary.parquet")
DP_COVERAGE_FULL = _load_parquet("dp_full_coverage.parquet")

# CRS×IATI interoperability (notebook 02)
CRS_INTEROP = _load_parquet("crs_iati_interop_by_dp.parquet")

# Subcontract / receiver-org (notebook 03)
SUBCONTRACT = _load_parquet("subcontract_visibility_by_dp.parquet")
DISBURSEMENT_CHANNEL_DIST = _load_parquet("disbursement_channel_dist.parquet")
TIED_STATUS_DIST = _load_parquet("tied_status_dist.parquet")

# Scan log (per-publisher activity counts, missing publishers)
SCAN_LOG = _load_parquet("scan_log.parquet")
PUBLISHER_DP_LOOKUP = _load_parquet("publisher_dp_lookup.parquet")


def has_data() -> bool:
    """Return True if at least the headline summary parquets are populated."""
    return DP_COVERAGE.height > 0 and CRS_INTEROP.height > 0 and SUBCONTRACT.height > 0
