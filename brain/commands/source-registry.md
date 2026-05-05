---
allowed_tools:
- Read
- Write(L0/)
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: source-registry
post_actions:
- append_research_md
preflight:
- gate_ready_or_override
stage:
- L0
- L1
---
