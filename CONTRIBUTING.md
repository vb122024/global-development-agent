# Contributing

Keep changes small and readable for a novice contributor. Put frontend code in
`frontend/`, Python services in `backend/`, agent prompts in
`agent_instructions/`, fixtures in `data/fixtures/`, and product documentation
in `docs/`.

Before opening a change:

```bash
cd backend && .venv/bin/python -m pytest -q
cd frontend && npm run build && npm run test:sites
```

Never commit `.env.local`, runtime databases, logs, generated reports, or API
keys. A data change must preserve source URL, period, units, retrieval date, and
fixture status. An agent prompt change must rerun the evaluation suite.

Before committing, review the proposed public files with:

```bash
git status --short
git diff --cached --check
```
