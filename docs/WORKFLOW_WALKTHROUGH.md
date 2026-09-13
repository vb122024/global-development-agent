# Local workflow walkthrough

This project has two deliberate modes. The public GitHub Pages build reads only
bundled JSON and makes no backend or OpenAI request. The local preview can
refresh public World Bank data and run the full agent workflow. The public mode
stays self-contained and read-only.

## Architecture

![Global Development Intelligence architecture](images/global-development-architecture.png)

The browser is a JavaScript dashboard. During local development, its requests
pass through the server-side [Vite proxy](../frontend/scripts/local-data-proxy.mjs),
which keeps local application requests separate from browser code. The
[FastAPI service](../backend/app/main.py) owns all data access, agents and
telemetry. The public GitHub Pages build reads bundled JSON only.

## What each dashboard control does

| Dashboard control | Frontend code | Backend path | Result |
| --- | --- | --- | --- |
| Country checkboxes, search, indicator and average-period controls | [`App.jsx`](../frontend/src/App.jsx) | None in static mode | Recalculates the chart, table and map from the packaged World Bank snapshot. |
| Refresh World Bank data (local development only) | [`App.jsx`](../frontend/src/App.jsx) → [`agentAdapter.js`](../frontend/src/lib/agentAdapter.js) | [`local-data-proxy.mjs`](../frontend/scripts/local-data-proxy.mjs) → `POST` [`main.py`](../backend/app/main.py) → [`data_refresh.py`](../backend/app/data_refresh.py) | Calls the public World Bank API, validates the allowlist, and saves observations plus source URLs to `data/runtime/structured.duckdb`. No OpenAI model is called. |
| Guided prompt buttons | [`AgentWorkspace.jsx`](../frontend/src/components/AgentWorkspace.jsx) | None | Fill the question box only. They never start a model request; the user selects **Ask agent** to proceed. |
| Ask agent | [`App.jsx`](../frontend/src/App.jsx) → [`agentAdapter.js`](../frontend/src/lib/agentAdapter.js) | Static: [`demoData.js`](../frontend/src/data/demoData.js). Local: proxy → `POST` [`main.py`](../backend/app/main.py). | Short greetings or non-economic small talk in supported languages return immediately without a model or specialist handoff. The local app uses checked DuckDB data for simple facts and the configured live agent for research questions. The response appears in the read-only **Agent answer** text area. |
| Agent progress | [`AgentWorkspace.jsx`](../frontend/src/components/AgentWorkspace.jsx) | None | While a request runs, shows a fixed handoff timeline: working, waiting for the prior specialist, handed over, then completed. It does not loop after completion. |
| Clear follow-up memory | [`App.jsx`](../frontend/src/App.jsx) → [`agentAdapter.js`](../frontend/src/lib/agentAdapter.js) | Proxy → `DELETE` [`main.py`](../backend/app/main.py) → [`conversation_memory.py`](../backend/app/conversation_memory.py) | Deletes the current local browser session's retained context and clears the visible answer. |
| Inspect document index | [`App.jsx`](../frontend/src/App.jsx) → [`agentAdapter.js`](../frontend/src/lib/agentAdapter.js) | Proxy → `GET` [`main.py`](../backend/app/main.py) → [`vector_store.py`](../backend/app/vector_store.py) | Shows indexed bytes, attached files and uploaded-but-unattached PDFs. It does not upload, attach, index, embed or invoke a model. OpenAI-managed stores do not expose raw embedding coordinates. |

## Data sources

The statistics originate from the official [World Bank Indicators API](https://api.worldbank.org/v2/)
and its [World Development Indicators catalogue](https://databank.worldbank.org/source/world-development-indicators).
The app records the exact request URLs and retrieval timestamp in DuckDB.

Narrative evidence comes from two reviewed World Bank PDFs listed in
`docs/corpus/catalog.json`: [World Development Report 2024](https://www.worldbank.org/en/publication/wdr2024)
and [Poverty, Prosperity, and Planet 2024](https://www.worldbank.org/en/publication/poverty-prosperity-and-planet).

## RAG and multi-agent path

The production-ready path is intentionally different from a generic single
chat completion:

1. The **orchestrator** interprets the request and hands bounded work to
   specialists.
2. The **structured-data specialist** retrieves time series from the structured
   DuckDB file; it cannot execute arbitrary SQL.
3. The **document-retrieval specialist** queries the OpenAI-managed vector
   store after the owner has approved indexing of the reviewed PDFs. OpenAI
   performs compatible document and query embeddings inside managed file
   search; the app does not create an inconsistent local query vector.
4. The **synthesis agent** combines only those tool results, includes citations,
   states data limitations, and records model, token and cost telemetry in
   `data/runtime/telemetry.duckdb`.

This division is useful when a question requires both numbers and report
context. A single OpenAI API call can write fluent prose, but it cannot by
itself prove which stored observation or report passage
supports a claim. The specialists provide least-privilege retrieval, auditable
handoffs, reusable evaluation targets, and the option to use inexpensive
models for routing while reserving a stronger model for synthesis. For a simple
one-off question, a single API call is simpler; this design is for an
inspectable portfolio workflow rather than pretending every query needs an
agent team.

## Why these features exist

| Feature | Why it is included | Practical limit |
| --- | --- | --- |
| Multiple agents and handoffs | Separates the responsibilities for numeric facts, report retrieval and synthesis. This makes the evidence path auditable and lets each specialist receive only the tools it needs. | For a simple factual query, one model call is faster and cheaper. The workspace exposes the handoff sequence so the trade-off is visible. |
| RAG | Retrieves relevant passages from approved World Bank reports before narrative claims are written. This grounds explanations in source material rather than relying only on a model's general knowledge. | PDFs must be attached and indexed in the managed vector store before live report retrieval can be claimed. [`vector_store.py`](../backend/app/vector_store.py) reports that status. |
| Managed embeddings | OpenAI-managed file search creates compatible document and query embeddings within the same vector store, avoiding a mismatched client-side query embedding. | OpenAI does not expose raw embedding coordinates. The app displays file/index status and retrieved evidence, rather than pretending the vectors are inspectable. |
| DuckDB structured store | Keeps World Bank time-series queries fast, local and bounded. It makes chart values and tool results reproducible without arbitrary database access. | Refreshed values are only as current as the last explicit World Bank refresh. |
| DuckDB telemetry and follow-up memory | Records runs, tool calls, token/cost metadata and a short session context. Follow-up questions can stay coherent while avoiding an unlimited transcript. | Only the three latest compact summaries are sent to a live follow-up; memory is cleared by the user or expires after 30 days. |
| Static GitHub Pages mode | Gives reviewers a safe, interactive portfolio demo with no backend connection or paid request. | It uses packaged data and labelled example answers rather than live agents. |

## Follow-up memory

Local chat creates an opaque browser session ID in `localStorage`. After a
completed question, the backend saves a short question and answer excerpt in
`data/runtime/telemetry.duckdb`. A live follow-up receives at most the three
latest summaries, so it can interpret references such as “compare that with
the United States” without receiving an unlimited transcript.

The separate local `evaluation-ui` reads that telemetry and the managed-vector-store
inspection endpoint to show evaluation results, local run history, model usage,
tool activity, and indexed-file status. OpenAI keeps managed raw embedding
coordinates private, so the UI deliberately displays file-level index metadata
rather than a fabricated vector table.

Memory expires after 30 days and can be removed immediately with **Clear
follow-up memory**. The public GitHub Pages build creates, stores and sends no
conversation memory. Retained context is a conversation aid only: the agent
still retrieves structured and document evidence for claims.

## Commands for a local review

From the project root, start the Python API in one terminal:

```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Start the dashboard in another:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 4173
```

Run checks without model calls:

```bash
backend/.venv/bin/python -m pytest -q backend/tests
cd frontend && npm run build && npm run test:sites
```
