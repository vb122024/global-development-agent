# Project Guide

This guide is the shortest map of the application for someone new to programming. Folder-specific setup commands live in each folder's README.

## How one question moves through the project

1. The JavaScript dashboard gathers selected countries, indicator, years, and the user's question.
2. In static mode, the frontend answers from reviewed example data and makes no backend request.
3. In local mode, every submitted message reaches the configured live model. Casual conversation uses one low-cost model turn without tools.
4. Development-data questions use the full workflow: the orchestrator hands work to narrow specialists that query `structured.duckdb` and the OpenAI managed vector store.
5. OpenAI-managed file search retrieves passages from selected World Bank reports only after explicit indexing approval; query embedding happens inside that service.
6. The synthesis agent produces a source-backed answer. Python validates numeric facts and citation identifiers.
7. `telemetry.duckdb` records the run, agents, tools, models, tokens, cost estimate, latency, evaluation results, and redacted security events.
8. The UI renders only the validated answer, evidence, chart/table data, limitations, and safe usage summary.

## Where to change what

| Change | Folder |
|---|---|
| Page layout, colors, map, charts, or chat panel | `frontend/src/` |
| HTTP routes, authentication, or response contracts | `backend/` and `contracts/` |
| Agent roles and writing behavior | `agent_instructions/*.txt` |
| Tool permissions, budgets, and validation | Python code under `backend/`; prompts cannot override these controls |
| World Bank source selection and data refresh | `scripts/`, `config/`, and `data/` |
| Evaluation cases and graders | `evals/` |

## Glossary

- **Agent:** a model with instructions and approved tools for one bounded responsibility.
- **RAG:** retrieving relevant report passages before generating an answer.
- **Embedding:** a numeric representation used for semantic search. OpenAI managed vector stores create document and query embeddings for the live retrieval path.
- **MCP:** a typed protocol through which an agent can call approved data tools.
- **Guardrail:** deterministic code that blocks or validates an input, tool action, or output.
- **Sandbox:** an isolated execution environment for agent-created files or commands. A Python virtual environment isolates packages, not operating-system access.

## What is public

GitHub Pages receives only the built frontend and allowlisted static data. It does not receive the Python backend, real API keys, private telemetry, sessions, raw reports, or local artifacts. Publishing remains a separate owner action.
