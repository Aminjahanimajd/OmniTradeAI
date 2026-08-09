# Product requirements

## Scope

OmniTrade AI supports students and analysts who need repeatable stock analysis.
It accepts a stock ticker, as-of time, workflow version, provider policy, model
policy, and budgets. It returns an explainable decision-support report with
lineage. It excludes portfolios, crypto, broker orders, and autonomous trading.

## Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | A local user can log in and access only owned workflows and runs. | API authorization tests |
| FR-02 | A user can create and edit a graph using 31 allowed node types. | Editor and API tests |
| FR-03 | The validator rejects invalid structure, types, loops, joins, evidence and budgets. | Validator test set |
| FR-04 | Only a valid immutable workflow version can be published. | Version tests |
| FR-05 | The engine schedules ready nodes in parallel and merges deterministically. | Scheduler tests and event trace |
| FR-06 | Required and optional failures create failed or degraded outcomes. | Failure-policy tests |
| FR-07 | Provider calls use bounded timeout, retry and fallback policies. | Adapter tests |
| FR-08 | Evidence is normalized and checked for ticker, time, freshness, unit, currency and provenance. | Evidence tests |
| FR-09 | Four specialists produce schema-validated reports through a model gateway. | Contract tests |
| FR-10 | Bull and bear research can repeat only within a declared iteration bound. | Loop tests |
| FR-11 | Three risk views are evaluated and combined before decision validation. | Workflow integration test |
| FR-12 | Users can cancel and resume safely from checkpoints without duplicated effects. | Recovery tests |
| FR-13 | Run events are available by SSE with reconnect support. | API/SSE tests |
| FR-14 | Every report claim links to evidence and provider metadata. | Lineage completeness test |
| FR-15 | Reports can be exported as JSON, HTML and PDF artifacts with hashes. | Export tests |
| FR-16 | A user can customize analysts, research depth, risk profile, data mode, models, report detail, language, freshness and budgets for each run. | API validation and New Analysis browser test |
| FR-17 | A live Agent Room shows real node events, agent state, collaboration order and each agent output impact. | Activity API and browser scenario |
| FR-18 | Profiles save default analysis choices and a calendar gives access to report history. | Profile API and report-history browser test |
| FR-19 | Draft graph changes affect execution only after validation and publication; each run stores the exact version. | Invalid-graph, publication and run-version tests |
| FR-20 | A report contains the saved point of view, confidence, reasoning and evidence references of every executed specialist, researcher and risk agent. | Detailed report API and PDF tests |
| FR-21 | Ticker, model, language, currency and data-mode selectors show only values supported by the backend. | Options API and browser test |
| FR-22 | Workflow Lab suggests port-compatible next nodes and blocks an incompatible edge before it becomes part of the draft. | Catalog-contract and editor tests |
| FR-23 | Selecting a workflow node shows a short plain-language explanation of its role. | Catalog description and Workflow Lab tests |

## Quality requirements

| ID | Quality | Measurable target |
|---|---|---|
| QR-01 | Reliability | Idempotent event handling and checkpoint recovery |
| QR-02 | Security | JWT auth, ownership checks, no secrets in events or logs |
| QR-03 | Performance | 95% API reads under 500 ms locally; bounded concurrency |
| QR-04 | Testability | Deterministic fake model and fixtures; workflow core >=80% coverage |
| QR-05 | Explainability | 100% decision claims have lineage or are marked unsupported |
| QR-06 | Maintainability | Typed contracts, service boundaries, migrations and ADRs |
| QR-07 | Safety | Decision-support warning; no execution API or broker adapter |
