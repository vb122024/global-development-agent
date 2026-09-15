# Product Requirements Document — Global Development Intelligence

| Field | Value |
| --- | --- |
| Status | Learning artifact aligned to the implemented MVP |
| Product type | Local research application with a static portfolio preview |
| Primary user | A reviewer, learner, or analyst comparing country-development data |
| Success measure | A user can obtain a source-backed comparison, inspect its evidence path, and understand whether it came from static or live mode. |

## 1. Problem and opportunity

Country comparisons commonly combine time-series statistics with narrative reports. A normal chat response can be fluent but may not make the data source, reporting period, units, or document evidence easy to inspect. This MVP demonstrates a small, inspectable workflow that retrieves approved World Bank material before producing a development-data answer.

The product is deliberately a portfolio demonstration, not an authoritative analytical service. Users must verify data, dates, units, citations, and generated text before relying on it.

## 2. Product goals

1. Let a user compare up to ten countries across selected World Bank indicators and years.
2. Show the underlying comparison through a chart, table, world map, and source links.
3. Support guided or free-text questions through a local agent workflow.
4. Ground narrative report claims with retrieval from reviewed World Bank documents when they are indexed.
5. Make the workflow inspectable through agent progress, evidence, evaluation results, document-index status, and local telemetry.
6. Provide a static GitHub Pages experience that works without a live backend.

## 3. Non-goals

- Forecasting, investment advice, country rankings, or policy recommendations.
- Claiming causal relationships from correlation alone.
- Replacing official World Bank dashboards or source reports.
- Publicly exposing local runtime data, conversation context, or application configuration.
- Providing raw managed-vector coordinates; the managed service exposes file/index metadata instead.

## 4. Users and key jobs

| User | Job to be done | Desired outcome |
| --- | --- | --- |
| Portfolio reviewer | Understand how the system uses data, RAG, agents and evaluations. | A visible, credible evidence path. |
| Learner | Explore country indicators and ask a development question. | A concise answer with sources and limitations. |
| Local project owner | Refresh approved data and monitor the workflow. | A controlled local runtime and clear run records. |

## 5. MVP requirements

| ID | Requirement | Priority | Acceptance evidence |
| --- | --- | --- | --- |
| PRD-01 | Show country selection, indicator selection, chart, table and map. | Must | Dashboard updates when a user changes selection. |
| PRD-02 | Limit comparison to ten countries and provide a search/add interaction. | Must | UI prevents more than ten selections. |
| PRD-03 | Provide guided prompts that populate, but do not submit, the question field. | Must | A model request starts only after **Ask agent**. |
| PRD-04 | Route casual chat through one concise model response. | Must | A greeting does not invoke specialist data tools. |
| PRD-05 | Route development-data questions through structured retrieval, optional document retrieval and synthesis. | Must | Run telemetry records the completed workflow and answer contains evidence/limitations. |
| PRD-06 | Retrieve numerical values only from approved World Bank observations. | Must | Returned values carry source URL, year and unit metadata. |
| PRD-07 | Retrieve report passages only from indexed, reviewed documents. | Must | If the index is unavailable, the answer says so rather than inventing a passage. |
| PRD-08 | Retain short local follow-up context and allow the user to clear it. | Should | Follow-up can use the latest saved summaries; clear removes them. |
| PRD-09 | Record runs, tool calls, model usage and deterministic evaluation results locally. | Must | Evaluation Lab shows the latest local records. |
| PRD-10 | Offer a public static mode with reviewed fixtures and no live request. | Must | Static build works without the Python service. |

## 6. User journey

1. The user selects countries, an indicator and a period; the dashboard redraws from the available snapshot.
2. The user chooses a guided question or writes a question.
3. Selecting **Ask agent** starts the request. The interface displays the bounded handoff status while work is active.
4. The service classifies the request. Casual chat receives a brief reply; development questions retrieve data and, when ready, report evidence.
5. The synthesis response presents an answer, source references, and limitations. The application records the local run.
6. The user can ask a follow-up or inspect the separate Evaluation Lab to understand aggregate quality checks and indexed-document status.

## 7. Quality and safety requirements

- Present source, observation year, and units alongside numerical claims.
- Do not make unsupported causal conclusions.
- Block known unsafe instructions and arbitrary database access.
- Respect the per-run budget setting before a live request runs.
- Keep local runtime state outside the public static build.
- Clearly label demonstration data and limitations.

## 8. Product metrics

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Evaluation pass rate | Passed deterministic checks ÷ checks shown. | Detects regressions in retrieval, citation, safety and budget rules. |
| Completed-run rate | Completed runs ÷ displayed runs. | Shows whether the local workflow completes reliably. |
| Tool completion rate | Completed calls ÷ tool calls, grouped by tool. | Highlights retrieval or validation failures. |
| Token usage and estimated cost | Stored input/output token totals and configured price calculation. | Supports model and workflow cost experiments. |
| Indexed-document readiness | Managed store status, file count and indexed size. | Confirms whether report retrieval can be used. |

## 9. Release criteria

The MVP is ready for a portfolio review when automated tests pass, the static build works, the data refresh is bounded to the approved indicator/country list, live answers are validated, documentation names the data sources, and no local runtime files are tracked for publication.
