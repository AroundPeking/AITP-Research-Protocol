---
allowed_tools:
- Read
- Write(L4/reviews/)
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: verify-results
preflight:
- gate_ready_or_override
- candidate_exists
stage:
- L4
---
