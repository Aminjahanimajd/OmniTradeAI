# Current implementation evidence

This file records real results only. It is not a claim about student work hours
or individual ownership.

| Increment | Implemented evidence |
|---|---|
| I1 | Docker Compose, React GUI, JWT login, public API, and browser path |
| I2 | 31-node catalog, visual editing, CRUD, typed graph, validator, immutable publication |
| I3 | Custom parallel scheduler, versioned events, SSE, Redis Streams, checkpoints, cancel and resume |
| I4 | Recorded/live adapter boundary, fallback policy, evidence time gate, technical and fundamental formulas |
| I5 | OpenAI-compatible gateway, deterministic fake model, typed output validation, four specialist nodes |
| I6 | Bull/bear debate, bounded loop, proposal, three risk views, and decision validation |
| I7 | PostgreSQL service schemas, ownership tests, report history, node lineage, JSON/HTML/PDF export |
| I8 | Failure scenario, worker-crash simulation, restart recovery, CI, Docker deployment, generated sequence diagram |

Verified on 27 August 2026:

- 210 backend tests and 12 frontend tests passed.
- Custom workflow core coverage: 89%.
- Ruff and strict mypy passed.
- Frontend unit test, TypeScript build, and production Vite build passed.
- Playwright browser scenario passed.
- Eight Compose containers started; PostgreSQL and Redis were healthy.
- A live AMD run completed all 34 nodes using Bedrock, real provider data,
  EUR conversion, and four debate rounds with no failed event.
- A distributed AAPL fixture run completed with 120 Redis events, complete
  lineage, and a 1,856-byte PDF export.
- The same run and its 120 events were available after restarting the API
  container, showing PostgreSQL recovery.
- A delayed distributed run changed from `cancelling` to `cancelled` through
  the Redis cancellation signal.
- The controlled failure scenario produced 126 events and resumed from
  checkpoint 12. Its final status was degraded because one optional social
  source failed as planned.

Generated evidence is stored in `artifacts/defense/`. Future burndown, velocity,
hours, authors, screenshots, and live-provider results must be added only when
the students really produce them.
