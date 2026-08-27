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
| FR-07 | Provider calls use bounded timeout, retry and only user-selected real-provider chains. | Adapter tests |
| FR-08 | Evidence is normalized and checked for ticker, time, freshness, unit, currency and provenance. Future, stale market, and stale fundamental evidence stop the run. With degraded mode enabled, stale news, sentiment, or macro branches are excluded and reported as quality warnings. | Evidence and degraded time-guard tests |
| FR-09 | Four specialists produce schema-validated reports through a model gateway. | Contract tests |
| FR-10 | Bull and bear research can repeat only within a declared iteration bound. | Loop tests |
| FR-11 | Three risk views are evaluated and combined before decision validation. | Workflow integration test |
| FR-12 | Users can safely pause active runs and resume paused, failed, or interrupted runs from durable checkpoints without duplicated completed work. Cancel remains final. | Runtime recovery and API control tests |
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
| FR-24 | A user can configure and verify session-only data and model credentials without exposing secrets in durable state or API responses. | Connection API and secret-redaction tests |
| FR-25 | Docker analysis runs reject recorded evidence and unverified providers instead of silently using prepared data. | Run precondition and provider-chain tests |
| FR-26 | Model choices cover the providers and model modes offered by the TradingAgents reference, including local, cloud, Bedrock and custom compatible endpoints. | Connection catalog and model-discovery tests |
| FR-27 | Investment horizon, experience, loss limit, position limit and excluded sectors change prompts, risk thresholds, decision validation or report guidance. | Policy executor tests and report inspection |
| FR-28 | Configuration pages show a selector only when at least two valid choices exist; one choice is applied automatically and no choices produce an actionable setup message. | Adaptive-control unit test and browser inspection |
| FR-29 | Amazon Bedrock accepts either a Bedrock bearer token or temporary AWS credentials and exposes all user-configured model IDs to analysis. | Bearer-header test, secret-redaction test and live verification |
| FR-30 | A topic-based in-app guide provides expandable steps for every index range and an openable/downloadable complete guide file. | How-to page, guide unit test and downloadable artifact |
| FR-31 | New Analysis automatically runs the latest published Workflow Lab graph and cannot select an unrelated workflow. | Shared active-workflow helper and graph-change scenario |
| FR-32 | Data-chain controls show every verified provider in each supported role; HTTP 403/429 errors are explained safely, and failed optional public feeds are removed instead of left pending. | Connection catalog, API policy, provider map and unit tests |
| FR-33 | Profile saves the default verified AI provider and quick/deep models; New Analysis permits a per-run change when alternatives exist. | Profile UI and adaptive-control tests |
| FR-34 | A distributed run that completed after the API transport timeout is recovered from final events and checkpoints; its report remains available and a runtime-budget overrun is marked degraded. | Late non-AAPL recovery API test |
| FR-35 | Workflow Lab lets a user rename, recolor, delete, and reset a node, or reset the whole draft, without replacing published versions or old reports. | Draft reset API test and Workflow Lab browser check |
| FR-36 | Every offered New Analysis setting forms a valid workflow contract; invalid manual budgets return a readable field or graph error before queueing. | Configuration matrix and frontend error-format tests |
| FR-37 | Non-USD market and fundamental values use a real historical FX rate, with source, rate, and original currency kept in lineage. | Provider conversion and live-run tests |

## Quality requirements

| ID | Quality | Measurable target |
|---|---|---|
| QR-01 | Reliability | Idempotent event handling and checkpoint recovery |
| QR-02 | Security | JWT auth, ownership checks, write-only session credentials, no secrets in durable data, events, reports or logs |
| QR-03 | Performance | 95% API reads under 500 ms locally; bounded concurrency |
| QR-04 | Testability | Deterministic fake model and fixtures; workflow core >=80% coverage |
| QR-05 | Explainability | 100% decision claims have lineage or are marked unsupported |
| QR-06 | Maintainability | Typed contracts, service boundaries, migrations and ADRs |
| QR-07 | Safety | Decision-support warning; no execution API or broker adapter |
