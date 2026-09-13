# Product Requirements Document

**Product:** Global Development Intelligence Agent  
**Version:** 2.0 — draft for approval  
**Date:** 11 September 2026  
**Status:** Planning only; do not build until the owner approves implementation.  
**Companions:** [BRD](BRD.md) · [Architecture](flowarchitecture.mmd)

## 1. Purpose and interpretation

This document is the implementation contract and end-to-end workplan for a JavaScript dashboard with a separate Python agent backend. It incorporates the user's requests and the simplified architecture without adding implementation clutter to the diagram.

“Must” denotes a requirement. “Proposed” denotes a suggested default requiring confirmation as part of document approval or at its indicated activation gate. No feature, benchmark, credential integration or sandbox behavior is currently implemented or verified. Only these requirements documents are being created in this stage.

Priority P0 means required for the one-day MVP at the bounded depth defined below. P1 is post-MVP expansion. All feature categories remain represented; extensive scale, automation and broad testing are reduced. A P0 live requirement does not prevent a deterministic partial milestone, but a fixture milestone cannot be labeled the all-feature MVP.

### 1.1 One-day MVP delivery contract

Target 8–10 focused working hours after implementation approval and readiness checks. Multiple AI development agents write the code, integrate, test and document it. The owner is not expected to program, but must provide approvals, credentials/payment, budget and access that AI agents cannot independently supply. The target is conditional, not a guarantee.

| Capability | Required working MVP slice |
|---|---|
| Dashboard | One responsive JavaScript dashboard with world map, one trend view, comparison table, source drawer and three templates |
| Numeric data | India, China, Vietnam, Indonesia; two GDP indicators; 2015 through latest available year; explicit nulls and provenance |
| Reports and embeddings | Four readable English reports, ideally one per country; actual OpenAI managed indexing and retrieval; no custom embedding pipeline |
| Two DuckDB stores | Structured data and persistent telemetry files, including real usage and evaluation rows |
| Runtime agents | One orchestrator plus one bounded research specialist; two OpenAI generation models mapped by task |
| MCP and tools | One actual MCP read call plus deterministic numeric functions |
| Agent action | One sandbox-generated Markdown comparison report, validated before download |
| Security/admin | Single-owner local login, session/CSRF/origin controls, chat enable/disable, cancellation, protected files/secrets and audit events |
| Evaluation | Twelve fixed acceptance cases, basic metric readout and one controlled configuration comparison |
| Hosted evaluation | One small hosted run if account supports it; otherwise real local harness with explicit reason and hosted status marked unavailable |
| Costs | Actual per-call tokens, dated estimated prices, simple model/task totals, limits and storage/retrieval accounting; reconciliation interface may remain unavailable without billing permission |
| Public portfolio | Static build with DuckDB-Wasm and JSON fallback, saved answer, short recording, beginner README and navigation guide; no live AI |

All existing P0 contracts apply within this slice. Comprehensive threat-model hardening, large-scale corpus coverage, a 40-case held-out benchmark, repeated optimization sweeps, custom embeddings and automated billing synchronization are post-MVP depth. Their absence must be documented, while implemented controls must actually work.

The existing repository layout is an ownership map, not a requirement to create empty modules or multiple abstraction layers. Implement only the files needed for this slice; keep instruction text separate and explain every populated folder.

## 2. Product modes and user journeys

### 2.1 Static exploration

A visitor opens the dashboard, sees the dataset date and static-demo label, chooses an indicator/year and selects countries on the map or through an accessible selector. The trend chart and comparison table update together. A source drawer explains definitions, missing values and provenance. A template opens a saved example with its original run date and evidence. No free-text submission to AI is available.

### 2.2 Local investigation

The owner starts the project, checks capability status, deliberately enables chat and chooses a template. The backend validates scope and budget, creates a typed plan, retrieves numeric and report evidence, synthesizes an answer and validates it. The UI shows the answer, limitations, citations, chart/table results and local usage summary. Follow-ups retain bounded session context and explicit country/year filters.

### 2.3 Local administration

The owner can disable chat, stop active runs, inspect failed requests, change permitted model mappings/budgets and inspect evaluation results. Disabling chat must take effect on the server. The public build has no effective admin activation mechanism.

### 2.4 Report action and evaluation

The owner requests a comparison report. An isolated agent workspace produces a scoped artifact; the backend validates it before making it downloadable. The owner runs a fixed evaluation suite, compares cost and quality with a baseline and reviews the proposed configuration change before promotion.

## 3. Functional requirements and acceptance criteria

### 3.1 Dashboard and frontend

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| UI-01 | P0 | JavaScript React frontend, proposed Vite build; no Python UI runtime | Frontend builds independently and consumes documented contracts |
| UI-02 | P0 | Professional Product Design-led dashboard with map, trends and sortable comparison table | Owner selects visual direction before UI implementation; linked controls work |
| UI-03 | P0 | Country, indicator and year/range filters with reset | Selection is consistent across views; invalid combinations show an explanation |
| UI-04 | P0 | Clearly distinguish current-dollar GDP from annual real GDP growth | Every axis, tooltip and table column has correct units and years |
| UI-05 | P0 | Source drawer and visible freshness/coverage | User can inspect source, definition, snapshot date and missingness |
| UI-06 | P0 | Static/live mode labels and predefined question templates | Saved responses never appear to be newly generated answers |
| UI-07 | P0 | Responsive and keyboard-operable interface | Verify desktop and narrow mobile viewport; map has equivalent table/selector access |
| UI-08 | P0 | Loading, empty, partial, error and disabled states | Network/data failures do not leave a blank screen or fabricated content |
| UI-09 | P1 | Additional indicators and public evaluation summary | Data definitions and actual measured sample counts accompany each addition |

Proposed screen structure: shared dashboard; evidence drawer; local chat panel; local admin/evaluation view; public “How it works” and demo material. Avoid creating separate pages for each indicator. Proposed chart library is ECharts; map geometry rendering choice follows design and bundle-size review.

Initial templates: compare GDP growth across selected countries; show GDP scale and growth over a period; find economic-update evidence for a reported change; explain evidence limitations. Proposed expansion templates require the relevant indicators to have been ingested first.

### 3.2 World Bank ingestion and structured storage

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| DATA-01 | P0 | Ingest GDP, growth, country and indicator metadata from World Bank APIs | Pagination, response schema and fixture comparisons pass |
| DATA-02 | P0 | Store domain observations in `structured.duckdb` | Repeat ingestion is idempotent for a snapshot; no duplicate observation keys |
| DATA-03 | P0 | Preserve raw source snapshots and provenance locally | Every displayed observation resolves to source URL and snapshot manifest |
| DATA-04 | P0 | Keep nulls, aggregates and incompatible metrics explicit | Null never becomes zero; regional aggregates excluded from country map |
| DATA-05 | P0 | Version snapshots and use serialized writes | Failed refresh leaves previous published snapshot usable |
| DATA-06 | P1 | Add six proposed indicators after the core slice | Definitions, units, coverage and tests added with each indicator |

Initial sources:

| Dataset | Endpoint/example | Ingestion behavior |
|---|---|---|
| Current-dollar GDP | `https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&date=2015:2025&per_page=1000&page=1` | Follow returned page count; retain year/value and source metadata |
| Annual GDP growth | Same route with `NY.GDP.MKTP.KD.ZG` | Preserve annual percent units; never calculate this from nominal GDP |
| Countries | `https://api.worldbank.org/v2/country?format=json&per_page=400` | Follow pagination; retain country codes, region and income classification |
| Indicator definitions | `https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=100&page=1` | Keep source-specific definitions and notes |
| Report catalog | `https://search.worldbank.org/api/v3/wds?format=json&qterm=economic%20update&rows=10&os=0` | Paginate by offset; select records and download available `pdfurl`/`txturl` |

The date range above is an example, not a rule to discard newer observations. Proposed production query range starts in 2015 and ends at the current year; UI shows latest *available* year. Country scope and corpus defaults are recorded in section 12.

Proposed expansion codes: `NY.GDP.PCAP.KD`, `FP.CPI.TOTL.ZG`, `SP.POP.TOTL`, `SL.UEM.TOTL.ZS`, `BX.KLT.DINV.WD.GD.ZS`, `NV.IND.MANF.ZS`. Verify current metadata before activation. World Bank metadata supplies coordinates but not country boundary polygons; use a separately attributed geometry dataset with an ISO crosswalk and boundary disclaimer.

### 3.3 Documents and vector retrieval

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| RAG-01 | P0 live | Curate relevant reports with license, date, language and extraction checks | Failed/unreadable files are quarantined; approved manifest is reproducible |
| RAG-02 | P0 live | Use OpenAI managed vector stores for selected documents | Record file/index status and verify retrieval against labeled evidence |
| RAG-05 | P0 live | Resolve each citation back to its source | No nonexistent file IDs or invented page numbers accepted |

Managed vector stores perform chunking and embedding, so a separate embedding API/model is not required in this path. Explicit embedding experiments are optional later work.

**RAG-07 — Embedding observability (P0 live):** Record managed versus explicit ingestion mode, corpus/file hashes, vector store reference, indexing status, timestamps and any reported embedding model/version/dimensions in `telemetry.duckdb`. If a managed API does not expose model identity or embedding token usage, store null with an explanatory availability status. Do not infer embedding charges from document size. For any later explicit embedding pipeline, record the selected OpenAI embedding model, dimensions, input tokens and dated rate. Account for managed storage/retrieval and explicit embedding costs separately, without double counting.

Acceptance: each ingestion job resolves to its corpus and processing status; unavailable managed fields are marked unavailable; any explicit embedding calls have attributable usage and costs. [OpenAI retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)

Proposed retrieval path: validate the question → retrieve matching report passages using managed file search → deduplicate passages → merge with SQL facts → validate citations. If metadata filtering is unavailable in the selected API surface, explicitly post-filter returned evidence and measure recall; never imply filtering happened when it did not.

### 3.4 Backend, tools and agent behavior

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| AG-01 | P0 live | Python OpenAI Agents SDK with typed input/output and narrow tools | Real request travels from UI through SDK and returns validated output |
| AG-02 | P0 live | One orchestrator baseline with bounded research specialist | Specialist is invoked for an evidence task when needed; no mandatory fan-out |
| AG-03 | P0 live | Expose read-only World Bank/data tools through a Python MCP server | SDK performs an actual MCP tool call with logged result/status |
| AG-04 | P0 live | Use deterministic Python for arithmetic and data validation | Golden numeric cases match without asking a model to calculate |
| AG-05 | P0 live | OpenAI-only task-specific model routing | Actual model per call logged; escalation requires defined trigger and budget |
| AG-06 | P0 live | Generate a cited report through a scoped action | Valid artifact downloadable; path escapes and unsafe output rejected |
| AG-07 | P0 live | Bound turns, context, retries, time and tool calls | Limit exhaustion returns a controlled status and records usage |
| AG-08 | P0 live | Show concise plan and evidence trail | User can understand tool decisions without exposing hidden chain-of-thought |

Use standard `Agent`, `Runner.run`, structured outputs and `@function_tool` where appropriate; verify current interfaces against the pinned SDK during implementation. Agent workspace operations use the SDK sandbox integration described in section 6. [OpenAI Agents guide](https://developers.openai.com/api/docs/guides/agents)

Proposed model slots: router/extractor, synthesis, escalation and judge. Choose available OpenAI model IDs and dated prices at paid activation; record model aliases and actual response model. Simple filters and calculations use no model. Escalation should follow complexity or failed supported-output validation, not uncalibrated self-reported model confidence.

MCP tools: list indicators, retrieve a bounded series and retrieve country metadata. Online World Bank refresh is an explicit ingestion operation; normal questions query the frozen snapshot. Tool arguments use allowlisted indicator/country IDs and bounded date ranges. Do not expose arbitrary SQL, arbitrary URLs or a generic host shell.

### 3.5 Chat, administration and credentials

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| ADM-01 | P0 | Default chat disabled; enforce capability status in backend | Direct API request fails safely when disabled, even if UI is manipulated |
| ADM-02 | P0 live | Local authenticated owner control for flag, cancellation and budgets | Non-admin request cannot change settings; origin/CSRF protections tested |
| ADM-03 | P0 | Public build excludes live transport and admin activation | Full static interaction produces zero OpenAI/backend calls |
| SEC-01 | P0 | Keep secrets out of browser, repository, logs and recordings | Scan source/history/build/demo outputs before public release |
| SEC-02 | P0 live | Defer credential setup; attempt only selected macOS Keychain item later | No bulk password access or plaintext output; failure gives a safe alternative |
| SEC-03 | P0 live | Backend-only secret injection | Worker filesystem and frontend environment contain no API key |

Future `.env.example` contains names with empty/example values only. The owner's API key and payment are not active requirements for writing these documents. During later activation, verify supported macOS Keychain access; Apple Passwords visibility is not proof that the item can be programmatically retrieved. If unavailable, use a backend environment variable or ignored local file selected by the owner.

Chat readiness requires enabled flag, credentials, budget, model access and sandbox health. On disable/cancel, reject new work and cancel active execution best-effort; already submitted calls can still be billed. Local API binds to loopback with allowlisted origins, session isolation, request limits and an authenticated owner session. Public mode must not attempt to discover a localhost backend.

### 3.6 Security, authentication and data protection

The initial product is single-owner and local. Public Pages is anonymous and contains only approved public material; it has no login that unlocks backend features. Multi-user accounts, public backend hosting and enterprise SSO are outside this release and would require a separate security design.

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| SEC-04 | P0 live | Authenticate every local API session except minimal health and login bootstrap | Unauthenticated chat, data, usage, run and artifact requests are denied |
| SEC-05 | P0 live | Enforce server-side owner permissions and resource ownership | A different session cannot inspect or cancel another session's run or download its artifact; non-owner cannot change admin settings |
| SEC-06 | P0 live | Protect session lifecycle and browser-origin boundary | Expired/revoked sessions fail; logout invalidates server session; CSRF and foreign-origin requests fail |
| SEC-07 | P0 | Classify and minimize stored/uploaded data | Public exports contain only allowlisted public fields; credentials and private prompts never enter the corpus |
| SEC-08 | P0 live | Secure local persistence and transport | Private files use restrictive permissions; external API calls validate HTTPS certificates; no claim of automatic database encryption |
| SEC-09 | P0 live | Treat documents, prompts and tool results as untrusted | Injection attempts cannot change permissions, expose secrets or trigger forbidden actions |
| SEC-10 | P0 | Validate ingestion and query boundaries | Oversized files, malformed formats, path escapes, arbitrary SQL and disallowed download destinations are rejected |
| SEC-11 | P0 live | Maintain redacted security audit records | Login outcomes, admin changes, denials, exports and cleanup actions are recorded without secret values |
| SEC-12 | P0 | Provide dependency and release security checks | Lockfiles, dependency review, secret scanning and public artifact inspection complete before release |
| SEC-13 | P0 live | Support revocation, retention and recovery | Session revocation, credential replacement and manifest-scoped deletion are tested; failed refresh can recover last-good data |

**Proposed authentication mechanism:** use a local one-time pairing secret delivered through the owner's terminal, never committed or placed in a URL. Exchange it for an opaque server-side session through a rate-limited login endpoint, then invalidate the pairing secret. Store session-token hashes server-side and use an HttpOnly, SameSite cookie. Protect mutating requests with CSRF validation plus Origin/Host checks; CORS is not authentication. Regenerate session identifiers on login, bound failed attempts and use proposed 30-minute idle / eight-hour absolute expiry. Restart invalidates sessions by default. Secure cookies are mandatory on HTTPS; any loopback-HTTP development exception must be explicitly documented and tested, never reused for remote hosting. No external network binding or remote authentication deployment is authorized by this plan.

**Data classes:** public source observations and reviewed metadata; private local prompts/sessions/artifacts/telemetry; secret credentials and session tokens. Keep secrets in the selected Keychain/backend mechanism, not in DuckDB. Private runtime directories should be owner-only and private files owner-readable/writable where supported. The design does not assume DuckDB encryption at rest. Document dependence on host disk protection without changing FileVault/system settings; stronger at-rest encryption is a separate design decision if sensitive datasets are later introduced. Backups of private files must inherit protection and retention rules.

**Cloud boundary:** only selected rights-checked public documents are uploaded for retrieval. User questions and retrieved evidence may be sent to OpenAI during live operation; explain this before enabling live chat. Sensitive trace payload capture is off by default; log IDs/status/usage instead. Review any evaluation dataset or trace upload for private content. Deletion must track local files and hosted file/vector resources separately and disclose failed or provider-delayed cleanup.

**Input and execution boundaries:** validate request schemas, lengths, country/indicator IDs and dates; parameterize SQL against approved queries with read-only connections. Disallow arbitrary attachments and URLs in initial chat. The ingestion downloader must allowlist expected HTTPS source hosts, revalidate redirects, reject private/loopback/link-local destinations and apply file size/time/type limits. Parse documents in a confined worker with no executable macros or active content. Agent instructions cannot grant permissions; deterministic code enforces all tool and sandbox limits. Sanitize report and chat rendering to prevent script injection.

**Audit and recovery:** store security events in a dedicated `security_events` table in `telemetry.duckdb`, including timestamp, pseudonymous actor/session reference, action, resource, outcome and correlation ID. Never store tokens or raw keys. These local logs are diagnostic, not tamper-proof forensic evidence. Document how to disable chat, revoke sessions, rotate a compromised API key, stop workers and inspect affected exports. A leaked key must be revoked; deleting it from the latest source file alone is insufficient.

Security test fixtures must cover unauthenticated requests, expired sessions, unauthorized admin actions, cross-session access, CSRF, hostile Host/Origin values, SQL injection, malicious Markdown, report prompt injection, download redirects, path/symlink escape, oversized inputs, secret redaction, cleanup and public build isolation. Keep findings and repaired-test evidence with the release checklist.

## 4. Data and API contracts

### 4.1 Storage schemas

Two separate DuckDB files are required. `telemetry.duckdb` is the persistent local record for operational and evaluation analysis even when hosted OpenAI traces/evals are enabled. It is not optional or a replacement for the structured domain database.

| Store | Proposed tables | Core constraints |
|---|---|---|
| `structured.duckdb` | observations, countries, indicators, sources, snapshots, document_manifest | Observation key is source + country + indicator + year + snapshot; retain nulls and definitions |
| `telemetry.duckdb` (required operational store) | runs, agent_calls, model_calls, tool_calls, ingestion_jobs, pricing, eval_runs, eval_results, billing_reconciliation, security_events | Request/event IDs prevent duplicate accounting; unknown usage remains unknown |

Report originals, extracted passages and generated artifacts are scoped files with manifest references, not embedded wholesale in domain tables. Shared IDs join document and structured snapshots. One owning process writes each database; agent workers receive immutable read-only snapshots. Refresh uses staging, validation and atomic manifest promotion, keeping the previous snapshot on failure.

Observation fields include source ID, country ISO3, indicator ID, year, value, unit, definition reference, snapshot ID and fetched timestamp. A latest-common-year comparison must not silently substitute each country's different latest year.


### 4.2 Proposed HTTP contract

| Route | Purpose | Access |
|---|---|---|
| `POST /api/auth/login`, `/api/auth/logout` | One-time pairing exchange and session invalidation | Local bootstrap / authenticated session |
| `GET /health` | Liveness without secret details | Local |
| `GET /api/capabilities` | Mode, chat readiness and safe reason codes | Local session |
| `GET /api/countries`, `/api/indicators`, `/api/series` | Validated read-only analytics | Local session |
| `POST /api/chat` | Start bounded run, return run ID | Chat capability required |
| `GET /api/runs/{id}` | Status and validated final result | Owning session |
| `POST /api/runs/{id}/cancel` | Request cancellation | Owning session/admin |
| `GET /api/artifacts/{id}` | Validated artifact download | Owning session |
| `PATCH /api/admin/settings` | Chat switch, permitted budgets/models | Authenticated owner |
| `GET /api/admin/usage`, `/api/admin/evals` | Cost and evaluation readouts | Authenticated owner |

Polling is the first delivery mechanism; streaming is optional if it does not complicate validation. Run states: queued, running, completed, partial, refused, failed, cancelled. Every error returns a safe code/message and run ID if one exists, without raw credentials or provider stack traces.

Answer schema: run ID, status, answer text, facts, citations, chart/table data, limitations, snapshot IDs and local usage summary. Chart specs are allowlisted data/config, never executable JavaScript. Public exports use the same display schema after removing private operational metadata.

## 5. Evaluation and cost requirements

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| EV-01 | P0 live | Fixed benchmark exercises actual SDK path | Repeatable results tied to code, prompt, model and corpus versions |
| EV-02 | P0 live | Hosted OpenAI evaluation where supported, with local fallback | Hosted run IDs retained, or documented access limitation and real local harness |
| EV-03 | P0 live | Deterministic checks plus calibrated model grading | Numeric/security failures cannot be overridden by a favorable model score |
| EV-04 | P0 live | Compare cost/quality on fixed cases | Report raw counts, variability and baseline results, including failures |
| COST-01 | P0 live | Persist agent/model/tool calls, tokens and costs in `telemetry.duckdb` | Records survive restart; call-level fields aggregate into consistent run totals |
| COST-02 | P0 live | Enforce explicit budgets and execution limits | Exhausted budget prevents new paid calls; retries remain counted |
| COST-03 | P0 live | Separate estimated and billed amounts | Unknown prices flagged; reconciliation never duplicates costs |

OpenAI offers datasets, graders, eval runs and trace-based evaluation. Check exact hosted support at activation and retain local task-level records regardless. [Agent evaluation guide](https://developers.openai.com/api/docs/guides/agent-evals)

### 5.1 Required telemetry and metric definitions

Each agent invocation has a stable ID, parent invocation/run ID, role, task, start/end timestamps and outcome. Model and tool calls link to that invocation. Include successful, failed, retried and cancelled attempts; missing provider usage remains unknown. Store evaluator identity/version, case ID, expected evidence, score/pass status and explanation alongside code/model/prompt/corpus versions. Hosted evaluation IDs link back to the same local case records.

| Metric | Definition and measurement |
|---|---|
| Numeric accuracy | Correct numeric assertions divided by evaluated assertions, using fixed source values and declared rounding tolerance |
| Retrieval recall at five | Relevant labeled evidence items found in the top five divided by all relevant labeled items; report aggregation and no-relevance cases |
| Citation precision | Citations supporting their associated claim divided by evaluated citations; independently flag answers missing required citations |
| Groundedness | Claim-level supported/unsupported judgments from calibrated grading; retain rubric scores and human review samples |
| Tool correctness | Required tool/argument/result assertions passed divided by tested assertions |
| Guardrail compliance | Safety cases with the expected refusal, restriction or safe completion divided by safety cases; mandatory failures block release |
| Latency | End-to-end and per-call durations; p50/p95 with sample counts and timeout rate |
| Cost per successful task | Total estimated cost of all attempts in the cohort divided by tasks passing the quality gate; null when none pass |

The local dashboard must filter by agent, task, model, run date, corpus and evaluation/configuration version. Show token categories, estimated USD, reconciliation status, errors/retries and metric denominators. One-time ingestion and ongoing storage costs appear separately from per-query and evaluation costs. Unknown values must not silently disappear from aggregates; display their count and cost-coverage status.

Acceptance: a fixture containing a success, failure, retry and missing-usage call produces expected totals and unknown counts; duplicate event ingestion does not change totals; persisted evaluation results can be compared after restart. Public exports contain only reviewed aggregates without private prompts or account identifiers.

### 5.2 Benchmark and optimization method

MVP benchmark: 11 fixed acceptance cases — three numeric/units, two report retrieval/citation, two missing-evidence/causal-restraint, two prompt-injection/forbidden-tool and two budget/failure cases. Run each once for the baseline and once for one candidate configuration. Review all generated answers in this small set. This suite is a smoke benchmark, not a held-out estimate of production reliability. Authentication, session boundaries, secret scanning and sandbox confinement also have mandatory deterministic security tests outside these 11 cases.

Post-MVP: expand to 40 stratified cases, split development/held-out data and repeat model-dependent runs at least three times. Add observed regressions without presenting development-set tuning as independent validation.

Deterministic graders check values and declared rounding tolerance, units/years, valid citation IDs, tool permissions, output schema, disabled-chat behavior and confinement. Human-labeled evidence supports recall@5 and citation precision. A sampled OpenAI judge assesses relevance, groundedness and causal restraint; calibrate with owner-reviewed samples.

MVP release gates: all 12 acceptance cases pass, all mandatory numeric/security assertions pass, and every citation in the reviewed answer set supports its claim. Display raw counts, unsupported claims and missing citations. Report latency and retrieval measurements with their small sample sizes; do not make p95 or cost-saving claims statistically stronger than the evidence. A candidate may be promoted only after the same gates pass. These are targets, not current scores.

Record run/span/request IDs, task, model, input/cached-input/output/reported-reasoning tokens, latency, retries, errors, prompt/config/corpus version and price version. Estimated token USD is `(uncached_input * input_rate + cached_input * cached_rate + output * output_rate) / 1,000,000`. Do not count cached tokens twice or add reasoning tokens again when already included in output totals.

Track file-search/tool fees, vector storage, optional embedding jobs and judge costs separately. Unknown usage/prices remain null with a reason, never zero. Use a separately privileged optional reconciliation process for provider Usage/Costs APIs; do not give billing admin credentials to agents. Report reconciliation at available aggregation, not invented per-request invoice precision.

Before each paid call reserve a conservative budget amount; settle actual usage afterward. Unknown-priced models cannot be enabled. Limit output tokens, turns, retries, retrieval size and concurrent runs. Proposed initial limits: one live run at a time, one escalation, one repair, two transient retries and a 120-second request deadline. Monetary budgets require owner input before live activation. Storage costs continue outside requests: set an expiry/cleanup policy and show accumulated storage separately.

Optimization sequence: baseline → one change to model/prompt/context/top-k/cache/routing → same cases and snapshots → quality/cost comparison → owner-reviewed version promotion. Cost per passing case includes failed attempts in the numerator. Deterministic fixtures and replay metrics must be labeled; no fabricated live results.

## 6. Project isolation and agent sandbox

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| ENV-01 | P0 | Python dependencies in `backend/.venv` and locked project metadata | Setup does not install into system Python |
| ENV-02 | P0 | JavaScript packages in `frontend/node_modules`, pinned lockfile | No global npm installs or unrelated project modifications |
| ENV-03 | P0 | Keep project data, caches, logs and artifacts in ignored project paths | Setup/cleanup report exact owned paths and leave other projects intact |
| SBX-01 | P0 live | Use OpenAI SDK sandbox facilities for agent workspace execution | Real report action executes in a verified sandbox |
| SBX-02 | P0 live | Deny broad host access and contain writes | Escape, symlink, secret-read and forbidden-network tests pass |
| SBX-03 | P0 live | Fail closed without an available isolation backend | No automatic host-shell fallback |
| SBX-04 | P0 live | Bound resources and clean up worker lifecycle | Success, failure and cancellation release workers; only reviewed output retained |

Use `SandboxAgent` and the current SDK sandbox configuration for tasks that inspect files, execute code or create artifacts. A proposed `DockerSandboxClient` provides local execution isolation; the SDK abstraction alone is not an OS security boundary. Exact imports/options must be verified against the chosen SDK version before implementation. [Sandbox Agents guide](https://developers.openai.com/api/docs/guides/agents/sandboxes)

Trusted backend orchestration and deterministic allowlisted tools run in the project environment; all model-generated shell/code/filesystem work runs in the sandbox. The worker receives only read-only snapshots and a scoped writable output area. No home directory, Keychain, API secrets, Docker socket, privileged mode or broad host mounts. Use non-root execution, process/resource/time limits and network denial by default. Model API calls are made by the trusted controller, outside the worker.

A virtualenv isolates dependencies; it does not isolate process access. Docker or another execution provider can require software and image storage outside the project. **Do not install it silently or promise all infrastructure physically resides in the folder.** First inspect available compatible infrastructure after build approval. If the folder-only requirement cannot be met, present a concrete exception or alternative for the owner's decision. Keep live workspace execution disabled in the meantime.

Proposed cleanup: ephemeral worker deleted after each run; raw local traces retained seven days; reviewed demo artifacts retained until removed; vector store expiry proposed at seven inactive days, subject to supported API semantics. No background scheduler is created unless requested. Cleanup targets only resources tracked in this project's manifest.

## 7. Nonfunctional requirements and verification

| ID | Requirement | Proposed verification |
|---|---|---|
| NFR-01 | Static hosting without a database server | Pages artifact contains static JS/assets/data only; browser uses DuckDB-Wasm with JSON fallback |
| NFR-02 | Portable browser assets | Bundle required Wasm/workers/extensions; test deployment base path and avoid requiring unsupported custom headers |
| NFR-03 | Accessible interaction | Keyboard, focus, contrast, reduced motion and text alternatives; target WCAG 2.2 AA behavior without claiming certification |
| NFR-04 | Useful performance | Proposed initial load under 5 seconds and filter response under 500 ms on recorded desktop test setup; measure before asserting |
| NFR-05 | Reproducible dependency setup | Lockfiles, documented supported versions and clean-checkout deterministic checks |
| NFR-06 | Robust external failures | Bounded retries/backoff; stale snapshot remains usable; report service failure honestly |
| NFR-07 | Safe content display | Sanitize rendered Markdown; no arbitrary HTML or executable chart code |
| NFR-08 | Operational transparency | Redacted logs, health status, run IDs and predictable shutdown; no hidden model requests |

Performance targets are proposed for the bounded sample, not a promise for arbitrary global data volumes. Record browser, hardware, dataset size and network conditions. API latency is measured separately from UI responsiveness.

## 8. Proposed repository structure

Only documentation exists for this task. Create the following later, after implementation approval:

```text
global-development-agent/
  README.md
  LICENSE
  SECURITY.md
  CONTRIBUTING.md
  .gitignore
  .env.example
  frontend/
    package.json
    package-lock.json
    node_modules/                 # ignored, local packages
    src/{components,pages,adapters,styles}/
    public/demo/                  # reviewed allowlisted assets only
    tests/
  backend/
    pyproject.toml
    uv.lock
    .venv/                        # ignored, local Python environment
    src/gdi/{api,agents,tools,mcp,ingestion,storage,sandbox,telemetry,security}/
    tests/
  agent_instructions/             # human-readable runtime prompts, separate from Python code
    README.md                     # purpose, inputs and tools for each agent
    orchestrator.txt
    researcher.txt
    report_writer.txt
    evaluator.txt
  contracts/                      # versioned JSON schemas
  config/                         # non-secret routing, sources, pricing, limits
  data/
    samples/                      # small sanitized structured DuckDB files
    local/                        # ignored raw files, databases and snapshots
  evals/{cases,graders}/
  evals/results/                   # ignored raw results
  scripts/                        # ingestion, checks, exports, evals, cleanup
  .runtime/                       # ignored project cache/log/worker metadata
  artifacts/                      # ignored local reports
  demos/                          # reviewed recordings and scorecards
  docs/{BRD.md,PRD.md,flowarchitecture.mmd}
  docs/PROJECT_GUIDE.md            # beginner walkthrough and where to make changes
  .github/workflows/              # deterministic CI and static build; no live AI job by default
```

Map app-owned caches to the project where supported. Respect existing system runtime installations without changing their global configuration. Do not clone helper repositories into the user's home directory as part of this project.

### 8.1 Beginner navigation and instruction files

- **REPO-01:** The root README must explain what each top-level folder does, the static versus live modes, and the shortest deterministic-check path. Each major code/data folder must contain a short README describing its contents and entrypoint.
- **REPO-02:** `docs/PROJECT_GUIDE.md` must trace one question from JavaScript UI through the Python backend, tools and data to the answer. Include a glossary, example commands, expected output and a “where to change what” table. Avoid unnecessary abstractions and duplicate helper layers.
- **REPO-03:** Runtime agent instructions must live in separate UTF-8 `.txt` files under `agent_instructions/`, not as large prompt strings embedded in Python. The backend loads them by stable project-relative paths, validates required files at startup and records their version/hash per run. Missing instructions fail with a clear error. Keep these files free of secrets.
- **REPO-04:** Python code retains tool permissions, schemas, budgets and enforcement; editing a prompt must not bypass security controls. Prompt changes require relevant evaluation checks. Each agent instruction file explains role, evidence rules, allowed responsibilities, output and abstention behavior.
- **REPO-05:** Use descriptive names, small cohesive modules and comments explaining non-obvious decisions. Document environment setup and shutdown without assuming prior knowledge of Python virtualenvs, npm or API keys.
- **REPO-06:** Keep source code, generated files and public assets visibly separate. Publish only the frontend build artifact to Pages, with a repository-aware asset base path and static-safe routing. Do not publish the repository root or copy backend/config/private-data folders into the site. Validate direct navigation and refreshed URLs; hash routing is the proposed simple default if multiple routes are needed.
- **REPO-07:** GitHub CI runs deterministic checks from locked dependencies and builds static assets without live service credentials. Rebuild scripts produce small sanitized DuckDB examples; mutable databases, environments, caches and large source downloads remain ignored. The README links the architecture, requirements, demos and deployment instructions.

Acceptance: a novice reader can identify the frontend entrypoint, Python entrypoint, prompts, data and tests from the folder guide; change a documented display label or prompt without searching the entire repository; and distinguish what is published from what remains local.

### 8.2 Multi-agent implementation collaboration

The owner permits multiple development agents when useful, including a dedicated **Product Design agent**. This is a development work arrangement, separate from the product's runtime orchestrator and research specialist.

After implementation approval, use a primary coordinator plus up to three concurrent development agents, including Product Design. Coordinate these bounded assignments:

| Development role | Responsibility | Boundary |
|---|---|---|
| Primary coordinator | Requirements, shared contracts, integration and acceptance evidence | Owns cross-cutting decisions and resolves conflicts |
| Product Design agent | Read Product Design guidance, prepare visual choices, specify components and review UI fidelity/accessibility | Works before frontend build; owner selects the visual direction |
| Backend/data agent | Python ingestion, DuckDB, SDK tools and sandbox integration | Consumes agreed contracts; no frontend redesign |
| Verification agent | Independent functional, static-hosting and safety review | Reports evidence and fixes within explicitly assigned scope |

Use only as many agents as useful independent work supports. Assign non-overlapping files where possible and agree shared contracts before parallel implementation. All agents inherit the same project-local dependency, secret-handling and approval restrictions. Do not start build agents merely because this collaboration approach is authorized; the implementation approval gate still applies.

## 9. One-day implementation workplan

Every phase below is **not started**. Explicit implementation approval is required. The phases are dependency checkpoints within one implementation day, not separate days. The implementer records changed files, checks, evidence and limitations.

### 9.1 Parallel execution and critical path

| Target window | Coordinator | Product Design / frontend agent | Backend/data agent | Verification agent |
|---|---|---|---|---|
| Hour 0–1 | Readiness, contracts, scope lock and key/budget/sandbox decisions | Visual choices; obtain owner selection | Source readability and schema planning; scaffold backend only after build approval | Acceptance fixtures and security checklist |
| Hour 1–4 | Authentication, telemetry foundations and integration ownership | Implement selected dashboard against shared fixtures | Ingestion, two database schemas, report indexing and MCP/tools | Prepare independent contract/security checks; review completed components |
| Hour 4–6 | Integrate SDK model routing, chat, budgets and sandbox action | Connect local/static adapters and admin controls | Wire evidence results and support runtime integration | Exercise actual end-to-end flow; report defects |
| Hour 6–8 | Run measured evaluation comparison and triage fixes | Fix UI/accessibility/static-network issues | Fix numeric/retrieval/sandbox defects | Validate security, persistence, budgets and clean setup |
| Hour 8–10 | Final acceptance, beginner documentation and handoff | Static packaging and short demonstration recording | Rebuild/cleanup instructions and source manifest | Final regression and public artifact checks |

The coordinator and backend agent agree schema ownership before editing; the backend agent owns database migrations, the coordinator owns authentication and telemetry event collection. Shared contract changes are serialized. The Product Design agent owns visual selection and frontend work; verification may propose fixes but edits only assigned files.

Critical path: build approval → readable sources/contracts → actual indexing and sandbox readiness → integrated answer/action → measured evaluation/security checks. Frontend implementation waits for visual selection, while independent data work can proceed after build approval. Indexing, access issues or late approvals can extend the day. Do not trade away mandatory controls or label mock runs as completed live features.

### 9.2 Phase checklist


| Phase | Dependencies | Work and deliverables | Exit / acceptance |
|---|---|---|---|
| 0 — Requirements review | Current stage | BRD, PRD and existing simplified architecture | Owner approves implementation and resolves scope defaults as needed |
| 1 — Visual selection | Phase 0 approval | Product Design brief and visual alternatives using realistic data labels | Owner selects visual direction; no UI scaffold before selection |
| 2 — Local foundation | Phase 0; UI work also requires Phase 1 | Separate JS/Python structure, lockfiles, ignore rules, config, schemas and security threat model; inspect runtime prerequisites | Deterministic health/setup checks pass; no global installation or secret values |
| 3 — Numeric vertical slice | Phase 2 | World Bank ingestion, structured DuckDB, country crosswalk and static exports | Pagination, units, nulls, duplicate and snapshot recovery checks pass |
| 4 — Static dashboard | Phases 1–3 | Map, charts, table, filters, source drawer and example UI | Browser interaction, mobile/keyboard and zero-backend-network checks pass |
| 5 — Live readiness | Phase 2 plus explicit paid activation | Secure credential handling, local authentication/session controls, available models/prices, budgets, persistent telemetry schema and compatible sandbox | Credential isolation and worker confinement tests pass; otherwise retain the static public demo |
| 6 — Evidence layer | Phases 3 and 5 | Curated reports, vector indexing and evidence mapping | Known evidence retrieved with a corpus version manifest |
| 7 — Agent workflow | Phases 5–6 | SDK orchestrator, research specialist, MCP/function tools, guards and report action | One complete UI-to-agent-to-cited-answer journey and confined artifact creation |
| 8 — Admin and operations | Phases 5–7 | Server-side chat switch, run cancellation, budgets, telemetry and cleanup | Direct disabled-chat bypass fails; cost fields and limits verified |
| 9 — Evaluation and optimization | Phases 6–8 | Twelve-case suite, one hosted run or documented fallback, one comparison and compact cost dashboard | Required gates pass; actual measurements and failed experiments documented |
| 10 — Portfolio packaging | Phases 4 and 9 for all-feature MVP | README, setup/data scripts, samples, data card, limitations, demo recording and public scorecard | Clean-checkout reproduction and release artifact checks pass |
| 11 — Publication — outside one-day build target | Explicit later publishing request | Public repo push and static GitHub Pages deployment | Deployed UI verified; no key/backend/model requests; static label visible |

Phases 3–4 can complete while paid access is unavailable. They form a useful separately accepted static milestone. Do not mark phases 5–9 complete with mocks. Add the extra indicators and corpus breadth only after the first end-to-end slice is verified.

A future standalone implementation instruction is: implement the approved phases from this PRD, preserve the current architecture, use project-local JavaScript/Python dependencies, enforce the stated source and safety contracts, stop at explicit activation/publication gates, and provide acceptance evidence rather than claiming completion from compilation alone.

## 10. Traceability and test plan

| Business requirement | Product requirements | Principal evidence |
|---|---|---|
| BR-01 | UI-01–UI-08, NFR-03–NFR-04; UI-09 post-MVP | Visual selection and interactive browser checks |
| BR-02 | ADM-03, NFR-01–NFR-02 | Static network recording and built artifact inspection |
| BR-03 | AG-01, ADM-01–ADM-02 | Local live journey and disabled-chat API test |
| BR-04 | DATA-01–DATA-05; DATA-06 post-MVP | Source fixtures, manifests and quality checks |
| BR-05 | RAG-01, RAG-02, RAG-05, RAG-07 | Labeled retrieval results |
| BR-06 | AG-02–AG-08, SBX-01 | Real MCP/tool trace and report artifact |
| BR-07 | EV-01–EV-04, COST-01–COST-03, RAG-07 | Persistent telemetry, embedding accounting and versioned scorecards |
| BR-08 | SEC-01–SEC-13, ENV-01–ENV-03, SBX-01–SBX-04 | Secret scan, confinement and cleanup checks |
| BR-09 | UI-01, AG-01, section 4 | Separate entrypoints and contract tests |
| BR-10 | NFR-05–NFR-08, phases 10–11 | Clean-checkout reproduction and documentation |
| BR-11 | DATA-04, RAG-05, ADM-02, EV-03 | Missingness, citation, cancel and causal-restraint cases |
| BR-12 | Section 9 and approval record | Per-phase evidence and owner decisions |
| BR-13 | SEC-04–SEC-06 | Authentication, authorization and session-boundary tests |
| BR-14 | SEC-07–SEC-08, SEC-13 | Data classification, permissions, retention and recovery checks |
| BR-15 | SEC-09–SEC-13 | Injection tests, redacted audit events and incident runbook |

Test layers: deterministic unit tests for transformations and limits; integration tests for database/MCP/API contracts; live bounded tests for provider and sandbox behavior; UI interaction tests for both adapters; 12-case MVP acceptance evaluation; post-MVP held-out evaluation; static deployment verification when publication is requested. Normal CI uses deterministic fixtures and clearly reports live checks as skipped. Paid evaluation is manually invoked with a budget, not run on every commit.

Release failures requiring repair include leaked secret values, unsourced numeric claims, fake live measurements, wrong units, public AI connectivity, disabled-chat bypass, unsafe artifact paths and sandbox escape. Do not waive these because an aggregate score is high.

## 11. Failure behavior and release checklist

| Failure | Required response |
|---|---|
| Live service unavailable | Keep local live chat unavailable; retain the static dashboard |
| World Bank API unavailable | Use dated last-good snapshot and show freshness; never invent updates |
| Vector indexing/retrieval fails | Exclude failed file; disclose reduced narrative evidence |
| Graph has no valid path | Use supported numeric/vector evidence or abstain; record retrieval mode |
| Model output fails validation | One bounded repair; otherwise return partial/abstention |
| Budget exhausted | Stop new calls, preserve supported result and usage |
| Worker unavailable or unsafe | Refuse workspace action; never switch to unrestricted host shell |
| Wasm unsupported | Use bounded JSON exports with equivalent core dashboard filters |

Before publication: verify source permissions/attribution; scan tracked files and history, assets and recordings; publish only allowlisted exports; remove private sessions, raw traces and account IDs; build without an OpenAI key; test relative paths and full static interaction; show recorded dates and actual benchmark status. Repository code license does not replace source-data licenses.

Completion requires the owner to review the delivered local experience. Publication remains a separate instruction. No remote infrastructure or scheduler is created automatically.

## 12. Decisions pending and proposed defaults

These items do not block writing the requirements. They must be resolved before the dependent implementation phase.

| Decision | Proposed default | Needed before |
|---|---|---|
| Initial domain scope | Two GDP indicators and metadata; 2015 onward; India, China, Vietnam and Indonesia | Phase 3 |
| Narrative scope | Four readable English economic reports covering the four selected countries | Phase 6 |
| Telemetry storage — confirmed requirement | Separate ignored `telemetry.duckdb`; schema implemented before live calls | Phases 5–8 |
| UI direction | Product Design alternatives, then owner choice | Phase 2 UI work |
| Models and prices | Current available OpenAI task-specific models; no fixed IDs yet | Phase 5 |
| Monetary ceilings | Owner-selected per-run and session budget | Phase 5 |
| Sandbox backend | SDK Docker integration if compatible infrastructure is available | Phase 5; separate approval for outside-folder infrastructure |
| Credentials | Selected Keychain item if supported, otherwise backend-only local environment | Phase 5 |
| Hosted evaluation access | Verify platform support; retain local real-workflow fallback | Phase 9 |
| Retention | Seven-day local raw traces and inactive vector-store expiry where supported | Phases 5–8 |
| Publishing and code license | No publishing yet; choose license before public release | Phase 11 |

## 13. References and revision history

Official sources guide implementation; refresh SDK signatures, model availability, rates and account capabilities before activation. No source examples constitute authorization to install or run anything.

- [World Bank API call structures](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures)
- [Country metadata API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898590-country-api-queries)
- [World Bank report API](https://documents.worldbank.org/en/publication/documents-reports/api)
- [OpenAI Agents](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI sandbox agents](https://developers.openai.com/api/docs/guides/agents/sandboxes)
- [OpenAI retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- [OpenAI agent evaluations](https://developers.openai.com/api/docs/guides/agent-evals)
- [OpenAI Usage and Costs API](https://platform.openai.com/docs/api-reference/usage)
- [DuckDB-Wasm](https://duckdb.org/docs/current/clients/wasm/overview)
- [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

| Version | Change |
|---|---|
| 2.0 | Reframes delivery as a one-day, AI-agent-led MVP with a working slice of every capability, bounded scope and readiness gates |
| 1.2 | Adds security requirements SEC-04 through SEC-13, authentication/session design, data protection and security acceptance tests |
| 1.1 | Requires the third DuckDB database, agent-call records, embedding observability and defined evaluation metrics; no implementation authorized |
| 1.0 | Requirements, acceptance tests, isolation contract and phased implementation plan; awaiting owner approval |
