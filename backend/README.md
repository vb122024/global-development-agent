# Backend

This folder contains the Python API, data access, agent routing and telemetry code.

## Local setup

```bash
cd backend
uv venv .venv
uv sync --extra dev
.venv/bin/python ../scripts/bootstrap_data.py
.venv/bin/pytest
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The application starts with live chat disabled. Copy `.env.example` to
`.env.local` only after setting a private owner token. Add `OPENAI_API_KEY` later
through a secure local secret mechanism; never commit it.

Admin requests use `X-Admin-Token` and mutating requests also use
`X-CSRF-Token` with the same local development secret. This is deliberately a
single-owner local MVP and must not be exposed to a network.

The owner can call `POST /api/admin/refresh-data` to fetch a bounded selection of
17 supported countries (up to 10 per request) and the two GDP indicators from the public World Bank
Indicators API. It replaces only the requested country/indicator/year scope in
the structured DuckDB database and records source URLs and retrieval time.
`POST /api/admin/clean-data` currently performs a read-only quality check and
returns findings; it does not call OpenAI or alter source values. Both routes
require the owner and CSRF headers. The public static export is generated
separately with `scripts/export_static_data.py` after review.
