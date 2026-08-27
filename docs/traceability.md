# Traceability matrix

FR-16 maps to run configuration, New Analysis and pre-run validation. FR-17
maps to Redis events, the activity API and Agent Room. FR-18 maps to profiles,
report history and the calendar. FR-19 maps to Workflow Lab, validation,
publication and immutable workflow versions. FR-20 maps executed node outputs
to the report API, GUI and PDF. FR-21 maps backend capability options to closed
GUI selectors. FR-22 maps backend port compatibility rules to safe editor
suggestions and connections. FR-23 maps the node description catalog to the
selected-node help panel in Workflow Lab.
FR-24-27 map the Connections tab, session connection registry, real provider
adapters, model gateway, run preconditions, profile policy and report outputs.
FR-28 maps option cardinality to adaptive New Analysis and Profile controls.
FR-29 maps Bedrock bearer-token input to the direct Converse client, configured
model list, redaction tests and live verification. FR-30 maps the in-app How to
Use page to `docs/USER_GUIDE.md`.
FR-31 maps the shared active-workflow policy to Workflow Lab and New Analysis.
FR-32 maps provider labels, capability roles, safe verification errors, and
failed-public-feed cleanup to the catalog, Connections, and New Analysis. FR-33 maps saved Profile model defaults to the
verified choices shown on New Analysis.
FR-34 maps Redis terminal events and final checkpoints to API report recovery.
FR-35 maps node appearance metadata and safe draft reset to Workflow Lab and the
workflow reset endpoint.

| Requirement | Components | Main verification |
|---|---|---|
| FR-01 | auth API, ownership policy | `test_auth.py` |
| FR-02-04 | workflow API, catalog, validator, editor | `test_validator.py`, GUI tests |
| FR-05-06 | scheduler, join policy, event bus | `test_runtime.py` |
| FR-07-08 | evidence adapters, freshness filtering and runtime quality gate | `test_evidence.py`, `test_stale_optional_news_degrades_without_stopping_report`, strict-mode test |
| FR-09-11 | model contracts, debate and risk graph | scenario integration test |
| FR-12-13 | checkpoint store, pause/resume/cancel controls, Run History, SSE | runtime recovery, API control, and GUI tests |
| FR-14-15 | lineage builder, report service, artifacts | report tests |
| FR-16-19 | analysis form, Agent Room, profiles, reports, Workflow Lab | API and GUI scenarios |
| FR-20 | runtime node outputs, detailed report builder, report GUI/PDF | `test_reporting.py`, API scenario |
| FR-21 | analysis-options API, New Analysis selectors | API and GUI tests |
| FR-22 | typed catalog suggestions, Workflow Lab safe connection helper | catalog and GUI tests |
| FR-23 | node description catalog, Workflow Lab selected-node panel | catalog and GUI tests |
| FR-24-25 | connection API, session registry, run preconditions, real provider chains | `test_api.py`, `test_providers.py` |
| FR-26 | provider catalog, model discovery, OpenAI-compatible and native clients | model gateway tests and live verification |
| FR-27 | profile, agent prompt context, risk and decision executors | runtime and report tests |
| FR-28 | adaptive selectors and fixed-option summaries | `AnalysisPage.test.ts` and browser inspection |
| FR-29 | Bedrock connection input, direct Converse client and model list | `test_model_gateway.py`, `test_api.py`, live check |
| FR-30 | expandable How to Use tab and downloadable user guide | guide unit test and content review |
| FR-31 | active workflow helper, Workflow Lab, New Analysis | unit test and two-run demo |
| FR-32 | provider catalog, error policy, Connections, provider map and data chains | API and GUI unit tests |
| FR-33 | Profile defaults, analysis options, New Analysis | frontend build and browser inspection |
| FR-34 | terminal-event reconciliation, checkpoint report rebuild, runtime-budget degradation | `test_completed_worker_events_recover_late_non_aapl_report` |
| FR-35 | Workflow Lab node controls, `ui_color` draft metadata, draft reset endpoint | `test_workflow_draft_can_reset_without_replacing_published_version`, browser check |
| FR-36 | run configuration contract, configured graph validator, readable API errors | `test_configuration_matrix.py` and GUI tests |
| FR-37 | Frankfurter FX adapter, evidence hashes and currency metadata | provider unit test and live AMD report |
