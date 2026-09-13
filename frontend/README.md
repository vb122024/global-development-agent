# Frontend

This React/Vite dashboard is the static GitHub Pages experience. It uses a
reviewed data snapshot and makes no OpenAI request in static mode.

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

Run `npm run build` for the production bundle and `npm run test:sites` for the
static-host routing checks. The production build hides all local admin controls.
In the development preview, use **Refresh World Bank data**. The Vite
development server holds the private owner token in `backend/.env.local`, so it
never reaches the browser. The refresh updates local DuckDB data and makes no
OpenAI model call. Production builds omit the local refresh route.
