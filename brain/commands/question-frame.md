---
allowed_tools:
- Read
- Write(L1/)
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: question-frame
post_actions:
- append_research_md
preflight:
- gate_ready_or_override
stage:
- L1
---
