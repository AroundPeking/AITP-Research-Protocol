---
name: state-retreat
stage: [L3, L4]
gate: optional
preflight: []
allowed_tools: [Read, Write(state.md)]
post_actions:
  - append_research_md: "Retreated to {target_stage}"
---
