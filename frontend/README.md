# Frontend

This React/Vite dashboard is the static GitHub Pages experience. It uses a
reviewed data snapshot and makes no OpenAI request in static mode.

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

Run `npm run build` for the production bundle and `npm run test:sites` for the
static-host routing checks. The production build uses the reviewed static
snapshot. In the development preview, **Refresh World Bank data** updates the
local DuckDB data from the World Bank API without running a model.
