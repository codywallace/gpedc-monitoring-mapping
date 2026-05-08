# syntax=docker/dockerfile:1.7
#
# Container image for the GPEDC × IATI mapping web app.
#
# Bakes in:
#   - the Dash app under /app/app/
#   - the reusable package /app/src/gpedc_iati/
#   - the pre-computed parquet outputs from .tmp/
#   - the Excel workbook (downloadable via the app)
#   - the pre-built Sphinx documentation site (served at /docs/)
#
# Does NOT include the IATI bulk-data XML mirror (~13 GB) or the donor-mapping
# spreadsheets — those are inputs to the offline scan + notebook pipeline,
# not to the runtime app.
#
# Build:    docker build -t gpedc-iati .
# Run:      docker run --rm -p 8050:8050 gpedc-iati

FROM python:3.14-slim

# Unprivileged runtime user. Build steps stay as root so `uv sync` can write
# /app/.venv; we chown + switch to `app` once everything is in place.
RUN groupadd --system --gid 1000 app \
 && useradd  --system --uid 1000 --gid app --home /home/app --shell /usr/sbin/nologin app \
 && mkdir -p /home/app && chown -R app:app /home/app

# Pull a pinned uv binary from the official image. Adjust the tag as needed.
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH=/app \
    GPEDC_LOG_DIR=/tmp/logs

WORKDIR /app

# ---------------------------------------------------------------------------
# Dependency layer — cached separately so code edits don't reinstall packages.
# ---------------------------------------------------------------------------
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---------------------------------------------------------------------------
# Project source code (editable bits — invalidated on every commit).
# ---------------------------------------------------------------------------
COPY src/ ./src/
COPY app/ ./app/
COPY build_mapping.py ./
COPY README.md ./

# Install the project itself now that the source is present. hatchling reads
# README.md per the `readme = "README.md"` entry in pyproject.toml, so it must
# be present in the build context for `uv sync` to install the project.
RUN uv sync --frozen --no-dev

# ---------------------------------------------------------------------------
# Pre-computed artefacts shipped with the image. Build these locally first:
#   uv run python scripts/scan_donors.py          (writes .tmp/*.parquet)
#   uv run python scripts/run_notebooks.py        (writes per-DP parquets)
#   uv run python build_mapping.py                (writes gpedc_iati_mapping.xlsx)
#   uv run python scripts/build_docs.py           (writes docs/_build/html/)
# ---------------------------------------------------------------------------
COPY .tmp/ ./.tmp/
COPY gpedc_iati_mapping.xlsx ./
COPY docs/_build/html/ ./docs/_build/html/

# Drop privileges before runtime. `app` owns /app so it can read the venv,
# parquets, workbook, and docs; it cannot write outside /tmp at runtime when
# the container is started with `read_only: true` + a tmpfs for /tmp (see
# docker-compose.yml).
RUN chown -R app:app /app
USER app

EXPOSE 8050

# Production server — gunicorn against the Flask `server` object the Dash app
# exposes. Two workers is comfortable on a small droplet; tune via env if
# needed. Logs go to stdout/stderr so `docker logs` and the host's journald
# pick them up.
CMD ["gunicorn", "app.main:server", \
     "--bind", "0.0.0.0:8050", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
