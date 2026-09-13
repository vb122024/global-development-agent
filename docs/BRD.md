# Business Requirements Document

**Product:** Global Development Intelligence Agent  
**Version:** 2.0 — draft for approval  
**Date:** 11 September 2026  
**Owner and approver:** Project owner  
**Status:** Requirements documentation only. Implementation has not been approved.

## 1. Purpose and document authority

Create a public GitHub portfolio that demonstrates understanding of an end-to-end agentic AI system through a credible World Bank data investigation experience. A visitor can explore a useful static dashboard without paying for or connecting to AI. The owner can demonstrate the full system locally after explicitly activating paid OpenAI access.

This BRD defines the business outcome and scope. The [PRD](PRD.md) defines behavior, technical contracts, acceptance tests and the implementation sequence. The [architecture](flowarchitecture.mmd) is the agreed high-level visual baseline. New user decisions override these documents; changes should be recorded in their revision history. The two earlier detailed architecture/workflow files are absent and are not dependencies.

The architecture is acceptable as a planning baseline. That acceptance does **not** authorize building the application, installing packages, accessing credentials, uploading documents, making paid requests or publishing.

## 2. Business problem and value

A portfolio that lists AI concepts without showing their behavior is difficult to assess. A deployed chatbot can also incur uncontrolled costs and hide the system's data, retrieval, validation and evaluation decisions.

This project will provide inspectable evidence of the complete workflow: source ingestion, structured analytics, retrieval from reports, tool use, model selection, bounded agent actions, safety checks, evaluation and cost measurement. The domain is country economic and development comparisons, using public World Bank sources.

The intended outcome is a demonstrable engineering and product reference project, not a commercial economic advisory service. Its explanations must distinguish reported facts, calculations, source interpretations and model synthesis.

## 3. Users and stakeholders

| User | Need | Successful experience |
|---|---|---|
| Portfolio visitor or hiring reviewer | Understand the project quickly and verify claims | Explore the map, compare countries, inspect citations, view a recorded agent run and measured scorecard |
| Project owner / local administrator | Run demonstrations and control costs | Enable chat deliberately, configure budgets, inspect usage and stop runs |
| Technical reviewer / developer | Reproduce and inspect implementation | Clone the repository, run deterministic checks, rebuild data and follow documented local setup |
| Future maintainer, including Codex | Work without losing requirements | Follow stable requirement IDs, contracts, milestones and explicit approval boundaries |

## 4. Business requirements

All capability areas below are required for the one-day MVP. Deliver the smallest working implementation of each, using the bounded acceptance scope below. Broader coverage and operational hardening are follow-up work; security boundaries remain mandatory.

| ID | Requirement | Completion evidence |
|---|---|---|
| BR-01 | Provide a professional interactive country dashboard | Working map, charts, table, filters, sources and accessible layouts |
| BR-02 | Offer a public static experience with no OpenAI dependency | Pages build operates without keys or backend connections |
| BR-03 | Offer optional local AI chat with predefined questions | Real local demonstration with citations; server-enforced admin switch |
| BR-04 | Use traceable public World Bank data | Source manifest, reproducible snapshots, definitions and missingness reporting |
| BR-05 | Demonstrate RAG | Inspectable document evidence with source-backed citations |
| BR-06 | Demonstrate agent orchestration, tools, MCP and bounded actions | Actual tool execution and artifact creation, not diagram-only claims |
| BR-07 | Measure quality and cost by task and model | Reproducible evaluation results and local cost dashboard |
| BR-08 | Protect secrets and isolate execution | No committed credentials; confinement tests and controlled runtime |
| BR-09 | Keep JavaScript frontend and Python backend separate | Clear repository boundaries and versioned contracts |
| BR-10 | Make the project easy to reproduce and explain | Setup, data rebuild, tests, architecture, demo and limitations documentation |
| BR-11 | Preserve human control and analytical integrity | Explicit data gaps, causal restraint, stop controls and reviewed publication |
| BR-12 | Deliver in reviewable stages | Stage evidence, owner acceptance and no unapproved implementation |

## 5. Scope and release modes

| Mode | Intended user | Data and behavior | Cost exposure |
|---|---|---|---|
| Public static | Anyone viewing GitHub Pages | Snapshot-based interactive analytics, saved answers, evidence and recordings | No runtime OpenAI calls |
| Static public site | Public reviewer | Dashboard, reviewed fixtures and clearly labelled example responses | No backend or live-model calls |
| Local live | Owner after activation | Python agent, OpenAI retrieval/models, report actions and measured evaluations | Bounded paid model, tool and storage usage |

The complete scope requires **three separate DuckDB database files**:

| Database | Required purpose |
|---|---|
| `structured.duckdb` | World Bank economic observations, country details and indicator metadata |
| `telemetry.duckdb` | Agent/model/tool calls, token usage, latency, errors, estimated API costs, billing reconciliation and evaluation results |

Telemetry must remain available locally even when OpenAI hosts evaluations or traces. The owner must be able to compare quality and cost by agent, task, model and configuration version. Private telemetry is excluded from the public repository and site; reviewed aggregate scorecards may be exported.

**Embedding approach:** OpenAI managed vector stores handle embeddings for the initial report-retrieval pipeline. A separate explicit embedding model is only needed for a future custom pipeline. Track ingestion mode, corpus version, available model metadata and associated storage/retrieval costs. Do not invent a model name or embedding token charge when the managed service does not expose it.

**Required evaluation measures:** numeric accuracy, retrieval recall, citation precision, groundedness, tool correctness, guardrail compliance, latency and cost per successful task. Retain case-level results, metric definitions, sample counts and benchmark versions in `telemetry.duckdb`; clearly distinguish live measurements from deterministic fixtures.

The MVP covers India, China, Vietnam and Indonesia, two indicators (current-US-dollar GDP and annual GDP growth), 2015 through the latest available year, and four readable English economic reports, ideally one per country. Other countries remain visible as unselected/no-data on the world map. If a report is unavailable, select a relevant regional report with explicit coverage rather than fabricate evidence.

The one-day deliverable includes one dashboard, three templates, a cited comparison workflow, a real MCP call, a sandboxed Markdown report, owner authentication/chat control, both DuckDB databases, token/cost metrics, and a small measured evaluation scorecard. Use two OpenAI generation models by task; the existing stronger slot may also serve as judge. Managed embeddings are demonstrated through actual indexed report retrieval.

AI development agents perform implementation, integration, tests and documentation. The owner still supplies approval, credentials/payment, spending limits and any required infrastructure access. One day is an execution target after these prerequisites are ready, not a guaranteed unattended completion time.

Out of scope for the initial release: public live chat, multi-user SaaS, non-OpenAI models, autonomous policy/investment decisions, forecasting, fine-tuning, a complete global report archive, mobile-native apps and automatic publication.

## 5.1 Repository usability and development collaboration

The repository must be approachable for a novice programmer: a root navigation guide, short folder READMEs, descriptive modules, a glossary and a walkthrough of one end-to-end request. Runtime agent instructions belong in separate `.txt` files in a dedicated `agent_instructions/` folder, with a clear mapping from instruction file to agent role.

The public repository and GitHub Pages site are different outputs. The repository contains understandable source and safe examples; Pages receives only the static frontend build and reviewed public data. Private environments, credentials and runtime data must never be published.

The owner permits multiple development agents when helpful, including a dedicated Product Design agent. This does not authorize implementation yet. The coordinator remains responsible for consistent contracts, integration and acceptance evidence.

## 6. Success measures

These are proposed acceptance targets, not measured results.

| Measure | Target / decision rule |
|---|---|
| Static isolation | Zero OpenAI or local backend requests while exercising public features |
| Data fidelity | All deterministic numeric fixtures match source snapshot and declared rounding |
| Safety | All mandatory secret, disabled-chat, forbidden-action and sandbox boundary cases pass |
| Agent quality | All 12 MVP acceptance cases pass, with raw results displayed; this is a smoke benchmark, not a generalization claim |
| Citation precision | Every citation in the small reviewed MVP answer set supports its claim |
| Retrieval | Report recall at five on labeled evidence; require non-regression when changing retrieval |
| Cost optimization | Show one controlled comparison; promote a cheaper configuration only when quality gates pass |
| Reproducibility | Documented deterministic checks work from a clean checkout on the supported environment |
| Usability | Reviewer can compare countries and inspect supporting evidence without instructions |

Failure to beat a baseline is an honest portfolio result; it must not be hidden or relabeled as improvement. A small benchmark demonstrates method, not production-wide reliability.

## 7. Budget, schedule and constraints

Target one focused implementation day of approximately 8–10 working hours, using parallel AI development agents and one coordinator. The estimate assumes timely visual selection, usable OpenAI access and budget, compatible sandbox infrastructure and readable source reports. Approval or external-service delays can extend elapsed time. No date or duration guarantees successful completion.

Suggested allocation: readiness/contracts/design 0–1 hour; parallel UI and backend/data work 1–4 hours; live integration 4–6 hours; evaluations/security checks 6–8 hours; documentation, recording and repair buffer 8–10 hours. Detailed dependencies and agent ownership are in PRD section 9.

If the time budget is exhausted, report incomplete capabilities honestly and continue only within authorized scope. A static-only result is a partial milestone, not an all-feature MVP. Never omit mandatory authentication, secret protection or sandbox tests to meet the time target.

No spending ceiling has been supplied. Paid operation must remain disabled until the owner supplies or accepts a per-run and session budget. The system must expose ingestion/storage costs separately from query and evaluation costs. Dollar figures are estimates until reconciled with provider billing; no rate or model availability should be invented.

Python dependencies must be in a project-local virtual environment. JavaScript dependencies must be in project-local `node_modules` with a lockfile; they are not managed by Python's virtualenv. No global package installs or unrelated project changes are allowed. Runtime infrastructure may have storage outside the project; that exception must be disclosed and explicitly accepted before installation or use if it conflicts with the isolation requirement.

## 8. Data governance and responsible use

Every published statistic must carry its indicator definition, unit, year and source. GDP in current dollars measures economic scale and is affected by exchange rates; it is not interchangeable with real growth, welfare or productivity. Missing observations and publication lag must be visible. Country classifications and report dates must be preserved rather than treated as timeless.

Report-derived explanations must retain citations. Correlation is not proof of causation. Generated commentary must be distinguishable from direct source statements. Public accessibility does not automatically grant every reuse right: ingestion and publication must retain applicable source attribution and document-specific terms.

The owner controls document selection, paid activation, configuration promotion and publication. Public exports contain reviewed material only. The repository must never include keys, private sessions, raw sensitive traces or identifying billing details.

### 8.1 Security and access requirements

Security is required across data ingestion, local authentication, agent execution, telemetry and public export. Public World Bank source data may be shareable, but prompts, sessions, credentials, local artifacts and operational records must be treated as private by default.

- **BR-13 — Authentication and authorization:** Public static visitors need no login and receive only reviewed public files. Local live users must authenticate; only the owner can enable chat, change budgets/models, initiate ingestion or manage retention. A UI toggle or loopback address alone is not authorization.
- **BR-14 — Data protection:** Restrict local file access, protect credentials separately, document cloud uploads and retention, and prevent private runtime records from entering public exports. Do not claim that DuckDB or a virtual environment automatically encrypts data.
- **BR-15 — Secure operations:** Validate external documents and tool inputs, maintain redacted security audit records, test access boundaries and document credential revocation, session invalidation and recovery.

Security acceptance requires tests for unauthenticated and unauthorized access, cross-session data access, malicious documents, forbidden file/network actions, secret exposure and unsafe public exports. Mandatory security failures block release regardless of the overall evaluation score. The local threat model does not claim protection against an administrator or malware already controlling the host.

## 9. Risks and responses

| Risk | Required response |
|---|---|
| Scope grows beyond a small portfolio | Deliver one complete comparison first; defer optional indicators and corpus expansion |
| Missing/revised observations | Snapshot data, expose missingness, preserve source versions |
| Poor PDF extraction | Quarantine unusable files; prefer available text; do not publish invented page citations |
| Expensive agents or graders | Deterministic tools first, task routing, bounded context and explicit budgets |
| SDK/sandbox or hosted eval access unavailable | Validate at activation; keep affected capabilities disabled and disclose limitations |
| Secrets leak through UI, logs or recordings | Server-only credentials, redaction and release artifact scanning |
| Static hosting limitations | Export data files and run browser analytics; no Python server on Pages |
| Unsafe generated code or actions | SDK sandbox with tested isolation; no fallback to unrestricted host execution |

## 10. Acceptance and approvals

The owner will review this BRD and the PRD before implementation. Future visual selection uses Product Design as originally requested. API activation, system-level runtime installation and publication have separate decision points; they must not be inferred from architecture approval.

Business acceptance requires all mandatory BR requirements to have linked acceptance evidence. If live evaluation cannot run because paid access remains inactive, the static release may be accepted separately, but the full agentic portfolio is not declared complete.

## 11. Revision history

| Version | Change |
|---|---|
| 2.0 | Reframes delivery as a one-day, AI-agent-led MVP with a working slice of every capability, bounded scope and readiness gates |
| 1.2 | Adds explicit business requirements for authentication, authorization, data protection and security operations |
| 1.1 | Makes telemetry DuckDB mandatory and explicitly captures embedding accounting and agent evaluation metrics; documentation only |
| 1.0 | Consolidates the conversation and current simplified architecture into business requirements; implementation approval pending |
