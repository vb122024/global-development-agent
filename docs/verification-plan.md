# MVP Verification Plan

**Product:** Global Development Intelligence Agent  
**Basis:** BRD v2.0, PRD v2.0, and `flowarchitecture.mmd`  
**Purpose:** Independent acceptance checklist for the one-day MVP

## Result labels

- **PASS:** Verified with reproducible evidence.
- **FAIL:** Implemented behavior violates an acceptance criterion.
- **BLOCKED:** Required dependency or credential is unavailable; this is not a pass.
- **NOT IMPLEMENTED:** Required capability is absent.
- **NOT APPLICABLE:** Only when the requirement is explicitly outside the MVP.

Deterministic fixtures, replayed responses, and estimated telemetry must be labeled as such. They cannot be reported as live OpenAI results.

## 1. Repository and environment

- [ ] JavaScript frontend and Python backend have independent entrypoints and dependency manifests.
- [ ] Python packages install only in `backend/.venv`; JavaScript packages remain in `frontend/node_modules`.
- [ ] Lockfiles exist and no global installation is required.
- [ ] Root and folder READMEs explain setup, shutdown, modes, entrypoints, data, prompts, and tests for a novice reader.
- [ ] Agent instructions are readable `.txt` files under `agent_instructions/`; no large prompt is embedded in Python.
- [ ] `.gitignore` excludes secrets, virtual environments, local databases, raw reports, sessions, traces, caches, and generated private artifacts.
- [ ] Static build succeeds without `OPENAI_API_KEY`.

## 2. Structured data and provenance

- [ ] `structured.duckdb` exists separately and contains countries, indicators, observations, sources/snapshots, and document manifest data needed by the MVP.
- [ ] Scope includes India, China, Vietnam, and Indonesia; GDP (`NY.GDP.MKTP.CD`) and annual GDP growth (`NY.GDP.MKTP.KD.ZG`); 2015 through the latest available snapshot year.
- [ ] Each displayed value resolves to indicator definition, unit, year, source URL, snapshot identifier/date, and country ISO3.
- [ ] Nulls remain null, regional aggregates do not appear as countries, and nominal GDP is not used to calculate real GDP growth.
- [ ] Fixture/source checks verify representative values and rounding.
- [ ] Repeated ingestion is idempotent; duplicate observation keys are rejected.
- [ ] Failed refresh preserves the prior usable snapshot.

## 3. Reports and retrieval

- [ ] Four readable English World Bank reports are represented, ideally one per selected country; unavailable coverage is disclosed.
- [ ] Managed-vector-store ingestion metadata records corpus/file hashes, status, timestamps, and vector store reference.
- [ ] Unavailable embedding model, dimensions, or token usage remains null with an availability reason.
- [ ] Citations resolve to real evidence; nonexistent file IDs and invented page numbers fail validation.

## 4. Dashboard and static hosting

- [ ] React/JavaScript dashboard contains a world map, linked trend chart, sortable comparison table, filters/reset, source drawer, and at least three question templates.
- [ ] Map selection has an accessible selector/table equivalent.
- [ ] GDP and GDP-growth labels, units, years, freshness, missingness, and static/replay status are visible and correct.
- [ ] Loading, empty, partial, error, and chat-disabled states are usable.
- [ ] Keyboard navigation, visible focus, text alternatives, contrast, reduced motion, desktop, and narrow mobile layouts are checked.
- [ ] Static mode uses reviewed local assets through DuckDB-Wasm or the declared JSON fallback.
- [ ] Full static interaction makes zero requests to OpenAI or the local Python backend.
- [ ] Public build contains no admin activation path, secret, private prompt/session/trace, raw telemetry, or backend/config/private-data directory.
- [ ] GitHub Pages base paths and refreshed/direct navigation work.

## 5. Backend, agents, tools, and actions

- [ ] Backend exposes safe health/capability status and validated API contracts; errors omit provider stack traces and secrets.
- [ ] Direct chat calls fail safely while chat is disabled.
- [ ] One orchestrator and one bounded research specialist use separate instruction files.
- [ ] Model routing uses OpenAI models by task, logs the actual model, and limits escalation by rule and budget.
- [ ] Deterministic Python performs numeric calculations and data validation.
- [ ] One actual read-only MCP call and deterministic structured-data tools are traceable.
- [ ] Tool inputs allowlist countries/indicators, bound date ranges, and reject arbitrary SQL, URLs, and host shell access.
- [ ] One UI-to-agent request returns validated answer text, facts, citations, chart/table data, limitations, snapshot IDs, and usage summary.
- [ ] Turns, context, retries, tool calls, output, concurrency, cancellation, and time are bounded.
- [ ] Report action generates Markdown only in a scoped sandbox output area and validates it before download.
- [ ] If the isolation backend is unavailable, workspace actions fail closed with no unrestricted host-shell fallback.

## 6. Authentication, authorization, and security

- [ ] Every local route except minimal health/login bootstrap requires authentication.
- [ ] Login is rate limited; pairing secret is not committed, logged, or placed in a URL; logout/expiry/revocation invalidate the session.
- [ ] Server-side owner checks protect chat settings, budgets/models, ingestion, retention, usage, evaluations, runs, and artifacts.
- [ ] A second session cannot inspect/cancel another session's run or download its artifact.
- [ ] CSRF, Origin/Host, and allowlisted CORS checks reject foreign or forged mutating requests.
- [ ] API key is backend-only; frontend bundles, worker mounts, logs, responses, recordings, and repository contain no key value.
- [ ] Prompt/document/tool-result injection cannot alter permissions, expose secrets, or invoke forbidden actions.
- [ ] Oversized/malformed files, path traversal, symlink escape, forbidden network access, and disallowed output destinations are rejected.
- [ ] Private files use restrictive permissions; audit events record login/admin/denial/export/cleanup activity with redaction.
- [ ] Secret scan covers tracked files, history where available, built assets, public data, and demos.
- [ ] Manifest-scoped cleanup and last-good snapshot recovery do not affect files outside the project.

## 7. Telemetry, cost, and evaluation

- [ ] `telemetry.duckdb` exists separately and persists runs, agent/model/tool calls, ingestion jobs, pricing, evaluation results, reconciliation status, and security events.
- [ ] Stable event IDs prevent duplicate accounting; success, failure, retry, cancellation, and missing-usage fixtures aggregate correctly after restart.
- [ ] Telemetry captures task/agent/model, token categories, latency, errors/retries, prompt/config/corpus versions, and dated price version.
- [ ] Unknown usage/prices stay null with reasons; cached and reasoning tokens are not double counted.
- [ ] Per-query, evaluation, managed storage/retrieval, and ingestion costs are separated; billed and estimated values are distinguished.
- [ ] Budget reservation and settlement work; exhausted or unknown-priced configurations block new paid calls while retaining incurred usage.
- [ ] Eleven fixed MVP cases cover numeric/units, retrieval/citation, missing evidence/causal restraint, injection/forbidden tool, and budget/failure behavior.
- [ ] Numeric accuracy, recall@5, citation precision, groundedness, tool correctness, guardrail compliance, latency, and cost per successful task expose definitions, numerators/denominators, sample counts, and failures.
- [ ] Baseline and one candidate use the same cases/snapshots; a cheaper candidate is promoted only when the same quality gates pass.
- [ ] Hosted evaluation IDs are retained when live access exists; otherwise hosted status is `unavailable` and the real local harness remains clearly labeled.

## 8. Final release gates

- [ ] Deterministic unit/integration tests and frontend build pass from documented commands.
- [ ] Core browser interactions and visible content are verified, not inferred from build or HTTP success.
- [ ] No mandatory security test fails.
- [ ] No displayed numeric claim is unsourced, has the wrong unit/year, or silently substitutes a different latest year.
- [ ] Static artifact contains no AI/backend connectivity and works without credentials.
- [ ] Live capabilities are reported as PASS only when exercised with real provider access; otherwise they remain BLOCKED.
- [ ] Known limitations and post-MVP items are documented without presenting mocks as complete features.
- [ ] No GitHub publication or remote deployment occurs without a separate owner request.

## Evidence to retain

Record exact commands, exit codes, test summaries, browser/network observations, screenshots where useful, database schema/count checks, secret-scan scope, and each blocker. The final report will map evidence to the sections above and distinguish verified behavior from code inspection.
