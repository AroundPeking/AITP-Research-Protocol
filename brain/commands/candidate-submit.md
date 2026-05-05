---
activity:
- integrate
- distill
allowed_tools:
- Read
- Write(L3/candidates/)
blocking_conditions:
- gate_blocked_and_no_override
- derivation_chain_empty
gate: required
intensity_override:
  full: strict
  quick: advisory
  standard: normal
name: candidate-submit
post_actions:
- auto_increment_l4_cycle_count
- trigger_notebook
- append_research_md
preflight:
- all_steps_have_source_refs
- domain_invariants_checked
preflight_conditional:
- check: derivation_chain_not_empty
  when:
    candidate_type: research_claim
stage:
- L3
---
