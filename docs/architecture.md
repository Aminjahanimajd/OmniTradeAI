# Architecture

## Context and safety boundary

The browser sends commands to the API. The workflow service owns graph state and
scheduling. Evidence, model and report services execute typed tasks. PostgreSQL
stores durable state, Redis Streams transports versioned events, and an artifact
store keeps exports with hashes. There is no broker interface.

```mermaid
flowchart LR
  U["Analyst"] --> GUI["React workflow IDE"]
  GUI --> API["API service"]
  API --> PG[("PostgreSQL schemas")]
  API --> RS[("Redis Streams")]
  RS --> WF["Workflow service"]
  WF --> RS
  RS --> EV["Evidence service"]
  RS --> MG["Model gateway"]
  RS --> RP["Report service"]
  EV --> DP["Market/news/macro/social providers"]
  MG --> LM["Fake or OpenAI-compatible model"]
  RP --> FS["Hashed artifacts"]
  EV --> RS
  MG --> RS
  RP --> RS
  API -. "SSE events" .-> GUI
```

## Main run state

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running
  running --> degraded: optional branch fails
  degraded --> succeeded: report completes
  running --> succeeded
  running --> cancelling
  cancelling --> cancelled
  running --> failed: required branch or budget fails
  running --> interrupted: worker crash
  interrupted --> running: idempotent resume
  succeeded --> [*]
  failed --> [*]
  cancelled --> [*]
```

## Event rules

Every event has `schema_version`, `event_id`, `event_type`, `run_id`, optional
`node_id`, `trace_id`, `occurred_at`, and a typed payload. Consumers store event
IDs before effects. Delivery is at least once; effects are idempotent. Consumer
groups isolate services. Failed events enter a dead-letter stream after bounded
retries.

## Data ownership

The API schema owns users and access data. Workflow owns workflow versions,
runs, node runs, checkpoints and events. Evidence owns normalized evidence and
provider call records. Model owns calls and budget usage. Report owns decisions,
claims, reports and artifact metadata. Cross-service access uses IDs and APIs,
not direct table coupling.

