# OmniTrade AI Engineering Rules

Every increment must use the local `professional_software_engineer` skill in
`../skills/professional_software_engineer/SKILL.md`.

- Build OmniTrade AI as an independent project. Never modify or copy the
  `../TradingAgents` implementation.
- Treat pretrained models, libraries, APIs, and formulas as third-party or
  data functions. Our assessed complexity is the workflow engine, validation,
  scheduling, failure handling, recovery, and traceability.
- Keep requirements, code, tests, and evidence linked by stable IDs.
- Never add broker execution. The product provides decision support only.
- Keep all retries and loops bounded. Validate data time, source, units,
  currency, freshness, and ticker before analysis.
- Use fake models and recorded providers in CI. Live tests are separate.
- Do not claim a feature or result in the report until it has real evidence.
- Each story has a lead and reviewer; rotate these roles between both students.

