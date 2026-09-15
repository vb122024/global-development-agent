# Business Requirements Document — Global Development Intelligence

| Field | Value |
| --- | --- |
| Status | Learning artifact aligned to the implemented MVP |
| Business context | Mini experimental portfolio project |
| Primary outcome | Demonstrate an evidence-led agentic AI workflow for country-development research. |

## 1. Business need

People comparing countries often need to combine official time-series data with narrative evidence from reports. This mini project demonstrates how an AI workflow can retrieve, validate and present those inputs with visible sources and limitations.

The project is intended to help a portfolio reviewer or learner understand the components of an agentic AI system: source ingestion, structured retrieval, RAG, specialised agent roles, guardrails, persistent follow-up context, telemetry and evaluation. It is not an authoritative country-analysis product and users must independently verify outputs before relying on them.

## 2. Business objectives

| ID | Objective | Measure of success |
| --- | --- | --- |
| BRD-01 | Demonstrate trustworthy country comparison. | Users can see selected countries, indicators, years, sources and units in one dashboard. |
| BRD-02 | Demonstrate grounded AI research rather than unverified chat. | Development-data answers show evidence, citations and limitations. |
| BRD-03 | Demonstrate responsible agent design. | Data and report retrieval are bounded; unsupported causal claims and unsafe prompts are rejected or restrained. |
| BRD-04 | Demonstrate cost-aware model usage. | The project records local model tokens, estimated cost, latency and tool completion data. |
| BRD-05 | Provide a portfolio experience that can be shared safely. | The GitHub Pages preview works from reviewed static data without a live service. |
| BRD-06 | Make the project approachable for non-developers. | Documentation explains flow, data sources, controls and design decisions in plain language. |

## 3. Scope

### In scope

- A dashboard for country selection, indicator comparison, charts, tables, map exploration and guided questions.
- World Bank indicators stored locally for structured retrieval.
- Reviewed World Bank reports available for managed RAG retrieval after indexing.
- A local multi-agent workflow for development-data questions.
- Concise low-cost handling for ordinary conversational messages.
- Local follow-up memory, evaluation checks, telemetry and an Evaluation Lab.
- A static GitHub Pages build using reviewed fixture data.

### Out of scope

- Forecasting, investment advice, policy recommendations, or official country rankings.
- Claims that correlation proves causation.
- Public live chat, a hosted production backend, user accounts, or collaboration features.
- Reproducing the raw numeric coordinates of managed embeddings.
- Replacing official World Bank products or source reports.

## 4. Stakeholders

| Stakeholder | Interest | Responsibility |
| --- | --- | --- |
| Project owner | Portfolio quality, local experimentation and source compliance. | Approves data sources, model configuration and publishing. |
| Portfolio reviewer | Evidence of AI product and engineering judgement. | Reviews documentation, workflow and code. |
| Learner / analyst | Clear country comparison and grounded explanation. | Uses outputs as a starting point and verifies sources. |
| Source providers | Correct use and attribution of their material. | Retain ownership and licence terms for source data and reports. |

## 5. Business capabilities

| Capability | Requirement | Business value |
| --- | --- | --- |
| Country comparison | Compare up to ten countries over selected indicators and years. | Makes the use case concrete and easy to review. |
| Evidence-led answers | Retrieve numeric observations and relevant report passages before synthesis. | Reduces unsupported narrative claims. |
| Agent handoffs | Separate structured-data, document-retrieval and synthesis responsibilities. | Makes tool access and evidence lineage inspectable. |
| RAG | Search reviewed, indexed World Bank reports. | Adds source context beyond numerical data. |
| Follow-up memory | Retain a limited, local conversation summary that the user can clear. | Supports natural follow-up questions without unlimited context retention. |
| Evaluation and telemetry | Store local run, tool and model records with deterministic checks. | Supports testing, model comparison and troubleshooting. |
| Static public mode | Provide a dashboard based on reviewed fixture data. | Enables a safe portfolio demonstration. |

## 6. Business rules

1. Numerical facts must identify their source, observation year and unit where applicable.
2. Answers must distinguish observations from interpretation and state meaningful gaps or limitations.
3. The system must not invent citations, report passages, or unavailable data.
4. The system must not claim a causal conclusion without supporting evidence.
5. Document retrieval may only use reviewed documents that are actually indexed in the managed store.
6. The public static mode must not require a live agent workflow.
7. The project owner controls data refresh, document indexing and model experiments in the local environment.

## 7. Success metrics

| Metric | Definition | Decision it informs |
| --- | --- | --- |
| Evaluation pass rate | Passing deterministic checks divided by the checks displayed. | Whether baseline retrieval, citation, safety and budget behaviours remain intact. |
| Run completion rate | Completed local runs divided by displayed local runs. | Whether the workflow is operationally reliable. |
| Tool completion rate | Completed calls divided by calls for each tool. | Whether a dependency or retrieval path is failing. |
| Token use and estimated cost | Stored input/output tokens multiplied by configured prices. | Which model or workflow design is efficient enough for the task. |
| Indexed document readiness | Managed-store file count, status and indexed size. | Whether RAG evidence is available for a question. |

## 8. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Data is stale, incomplete or revised by the source. | Preserve refresh metadata and tell users to verify current source data. |
| Model produces plausible but unsupported prose. | Use bounded retrieval, citations, output validation and deterministic checks. |
| Multi-agent workflow adds latency or cost. | Route casual chat through one low-cost call; record telemetry for comparison. |
| A public portfolio is mistaken for an official analysis product. | Use clear attribution, source links and a verification caveat. |
| Sensitive local runtime state is published accidentally. | Keep runtime state outside the static site and exclude it from version control. |

## 9. Acceptance criteria

The MVP satisfies the business requirements when a reviewer can:

1. Compare countries using visible World Bank data and source context.
2. Submit a development question and see the local evidence-led workflow complete.
3. See an answer that identifies limitations and does not overstate causality.
4. Inspect RAG index readiness and local evaluation/telemetry summaries.
5. Run the public static preview without a live service.
6. Read the supporting documentation and understand the design choices.
