---
allowed_tools:
- Read
- Agent
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: verify-run
preflight:
- gate_ready_or_override
- candidate_exists
stage:
- L4
---
