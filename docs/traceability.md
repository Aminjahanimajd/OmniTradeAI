# Traceability matrix

FR-16 maps to run configuration, New Analysis and pre-run validation. FR-17
maps to Redis events, the activity API and Agent Room. FR-18 maps to profiles,
report history and the calendar. FR-19 maps to Workflow Lab, validation,
publication and immutable workflow versions. FR-20 maps executed node outputs
to the report API, GUI and PDF. FR-21 maps backend capability options to closed
GUI selectors. FR-22 maps backend port compatibility rules to safe editor
suggestions and connections. FR-23 maps the node description catalog to the
selected-node help panel in Workflow Lab.

| Requirement | Components | Main verification |
|---|---|---|
| FR-01 | auth API, ownership policy | `test_auth.py` |
| FR-02-04 | workflow API, catalog, validator, editor | `test_validator.py`, GUI tests |
| FR-05-06 | scheduler, join policy, event bus | `test_runtime.py` |
| FR-07-08 | evidence adapters and quality gate | `test_evidence.py` |
| FR-09-11 | model contracts, debate and risk graph | scenario integration test |
| FR-12-13 | checkpoint store, cancellation, SSE | recovery and API tests |
| FR-14-15 | lineage builder, report service, artifacts | report tests |
| FR-16-19 | analysis form, Agent Room, profiles, reports, Workflow Lab | API and GUI scenarios |
| FR-20 | runtime node outputs, detailed report builder, report GUI/PDF | `test_reporting.py`, API scenario |
| FR-21 | analysis-options API, New Analysis selectors | API and GUI tests |
| FR-22 | typed catalog suggestions, Workflow Lab safe connection helper | catalog and GUI tests |
| FR-23 | node description catalog, Workflow Lab selected-node panel | catalog and GUI tests |
