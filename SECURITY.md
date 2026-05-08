# Security

## Reporting a vulnerability

Email **[codywallace.dev@gmail.com](mailto:codywallace.dev@gmail.com)** with
the subject line `[security] gpedc`. Please do not open a public GitHub
issue. I aim to acknowledge within 72 hours.

## What's enforced in this repo

| Control | Where | Catches |
| --- | --- | --- |
| `gitleaks` (pre-commit + CI) | [`.pre-commit-config.yaml`](.pre-commit-config.yaml), [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Secrets pasted into tracked files |
| `detect-private-key` (pre-commit) | [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | OpenSSH / PEM private keys |
| `pip-audit` (CI) | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Python dependencies with known CVEs |
| Dependabot | [`.github/dependabot.yml`](.github/dependabot.yml) | Stale Python deps, GitHub Actions, and the Python base image |
| Hadolint (CI) | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Common Dockerfile mis-uses |

## Container hardening posture

The runtime image and compose service apply standard defence-in-depth
basics. Useful as a starting point if you want to run the app in your own
environment:

| Control | Where |
| --- | --- |
| Non-root user (`app`, UID 1000) | [`Dockerfile`](Dockerfile) — `USER app` after build |
| `read_only: true` filesystem | [`docker-compose.yml`](docker-compose.yml) |
| `tmpfs:/tmp` for runtime scratch | [`docker-compose.yml`](docker-compose.yml) |
| `no-new-privileges` | [`docker-compose.yml`](docker-compose.yml) |
| `cap_drop: [ALL]` | [`docker-compose.yml`](docker-compose.yml) |
| Liveness probe on `/healthz` | [`docker-compose.yml`](docker-compose.yml) + [`app/main.py`](app/main.py) |
| Path-traversal guard on the `/docs/` route | [`app/main.py`](app/main.py) |

## Threat model

In scope:

- Accidental secret commits (covered by gitleaks + `.gitignore`).
- Known-CVE Python dependencies (pip-audit + Dependabot).
- Container escape via root processes (mitigated by non-root user, dropped
  caps, read-only fs, no-new-privileges).
- Path traversal on `/docs/<subpath>` (guarded in [`app/main.py`](app/main.py)).

Explicitly **not** in scope:

- Authenticated abuse — the public app has no login. Anyone with the URL
  can read everything. This is intentional: the data is public. If you
  fork this for a non-public dataset, add an authentication layer (e.g.
  Cloudflare Access) before exposing the tunnel publicly.
