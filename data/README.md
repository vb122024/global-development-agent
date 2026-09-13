# Data

`fixtures/` contains a small, clearly labeled static snapshot derived from the
World Bank Indicators API. Run `scripts/bootstrap_data.py` to create the two
ignored runtime databases in `data/runtime/`.

- `structured.duckdb`: country, indicator, observation and provenance tables.
- `telemetry.duckdb`: runs, model/tool usage, estimated cost, evaluations and security events.

The fixture is for reproducible demos. Refresh it from the cited API before making
current-data claims.

`frontend/public/data/world-bank-2019-2024.json` is a reviewed, source-labelled
static export of a live 12 September 2026 World Bank Indicators API refresh:
17 countries, two indicators, 2019–2024, 204 observations. It contains no
credentials. GitHub Pages can read this file without a backend. Refreshing the
local database does not automatically publish a new static snapshot; run
`backend/.venv/bin/python scripts/export_static_data.py` after reviewing a
complete refresh and before committing an updated public snapshot.
