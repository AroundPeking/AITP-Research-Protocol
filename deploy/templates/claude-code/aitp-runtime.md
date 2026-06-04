---
name: aitp-runtime
description: Use after AITP v5 routing has claimed a theoretical-physics task; continue through typed records, validation gates, and trust-controlled memory.
---

# AITP Runtime v5 - Claude Code

## Runtime Loop

Every real research turn starts by restoring typed state:

```text
brief = mcp__aitp__aitp_v5_get_execution_brief(base="{{TOPICS_ROOT}}", session_id=<session-id>)
```

Then decide the next action from the brief:

- `current_focus`: active claim, confidence state, evidence profile, uncertainty
- `flow_profile`: fluid/guided/rigorous/adversarial route
- `risk_assessment` and `action_budget`: how heavy evidence must be
- `evidence_coverage`: missing required outputs
- `next_action_candidates`: safe next actions
- `forbidden_now`: actions blocked until evidence, validation, or a human gate

If the only available packet is a legacy stage brief, migrate or bind a v5
session first. Legacy stages are historical orientation, not the runtime loop.

## Typed Record Boundaries

- `execution_brief` is the working control panel.
- Reference locations and summaries are orientation until linked to evidence.
- A validation result supports only the exact checks and failure modes it covers.
- Partial validation should be narrow, not a broad pass.
- Claim confidence, trust updates, and L2 memory require explicit v5 gates.

## Legacy Topics

For older Markdown topics:

1. Use legacy aliases only to discover the slug.
2. Prefer `mcp__aitp__aitp_v5_migrate_curated_legacy_topic_to_v5` for known
   curated topics.
3. Use `mcp__aitp__aitp_v5_migrate_legacy_topic_to_v5` for generic
   preservation.
4. Continue from the v5 session id returned by migration.

## Physics Validation Discipline

Before treating a result as strong, check dimensional consistency, algebraic
consistency, limiting cases, symmetry or Ward identities, conservation laws,
approximation validity, numerical convergence, benchmarks, and explicit failure
modes where applicable.

Do not bury a failed check in prose. Record it as typed state.
