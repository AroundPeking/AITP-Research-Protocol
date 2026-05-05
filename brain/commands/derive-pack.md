---
allowed_tools:
- Read
- Write(L3/candidates/)
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: derive-pack
preflight:
- derivation_chain_not_empty
stage:
- L3
---
