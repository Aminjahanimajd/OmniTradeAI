# Agile delivery plan and backlog

We use Agile only. Scrum gives planning, backlog, review and retrospective.
XP gives small stories, pair review, tests and refactoring. DevOps gives CI and
repeatable Docker delivery. Each increment repeats planning, analysis, design,
implementation, testing, integration, review and retrospective.

| Increment | Goal | Main stories | Planned hours | Definition of done |
|---|---|---|---:|---|
| I1 | Walking skeleton | Docker, GUI shell, login, stub run | 20 | One browser-to-API path works |
| I2 | Safe workflow design | Editor, CRUD, graph schema, validator | 28 | Invalid graph reasons are visible |
| I3 | Event execution | Scheduling, states, SSE, checkpoints | 34 | Parallel deterministic fixture run |
| I4 | Trusted evidence | Adapters, normalization, time guard, formulas | 28 | Bad or stale data is rejected |
| I5 | Typed analysis | Gateway and four specialist branches | 24 | Invalid model output cannot enter graph |
| I6 | Decision workflow | Debate, proposal, three risk views, validator | 28 | Bounded complete decision path |
| I7 | Explainable product | Reports, history, lineage, security, telemetry | 22 | Every claim is traceable |
| I8 | Release evidence | Failure, load, deployment, final UML and report | 16 | Docker demo and evidence pack pass |

Total: 200 team hours. Mohammadamin and Mehdi rotate lead and reviewer roles.
Both implement frontend, backend, database and tests. Actual progress, owners,
burndown and test evidence will be added only after work occurs.

