---
allowed_tools:
- Read
- Write(L2/)
- Write(state.md)
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: promote
preflight:
- all_verifiers_passed
- human_review_complete
stage:
- L4
---
