# Phase 171.2: Positive Replay And Deferred Mode Routing - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Close milestone `v1.97` with one mechanical replay package for the positive-L2
proof and one explicit routing note for the deferred `toy_model` and
`first_principles` positive-L2 lanes.

</domain>

<decisions>
## Implementation Decisions

### Replay closure
- Reuse the already-proven scripts from Phases `171` and `171.1` instead of
  inventing a third acceptance surface.
- Treat the replay package as a runbook + raw receipts bundle, not as a new
  runtime feature.

### Deferred routing
- Route the user-requested lane convergence to exactly three research
  directions:
  - pure formal theory
  - toy model numerical + derivation
  - large codebase / first-principles / algorithm development
- Keep the formal lane closed as the new baseline.
- Write explicit blocker and next-action notes for `toy_model` and
  `first_principles` rather than pretending they are already positive-L2-ready.

### the agent's Discretion
The exact wording of the deferred blockers is at the agent's discretion as long
as it stays honest, bounded, and aligned with the user's named targets
(`HS model`, `LibRPA QSGW`).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_formal_positive_l2_acceptance.py` is already the public positive-L2
  replay lane.
- `run_positive_negative_l2_coexistence_acceptance.py` is already the L2
  coexistence hardening replay lane.
- Phase `171` and `171.1` already contain receipts, summaries, and targeted
  pytest coverage.

### Established Patterns
- Milestone closure evidence lives in phase-level runbooks, receipts, and
  explicit summaries.
- Deferred route notes should stay in `.planning/phases/.../evidence/` or
  runbook-adjacent markdown, not hidden in chat.

### Integration Points
- This phase should update roadmap/state/requirements to show that the
  positive-L2 baseline is replayable and that the remaining multi-mode work is
  explicitly routed.

</code_context>

<specifics>
## Specific Ideas

- Replay package should include:
  - fresh positive-L2 closure command
  - positive/negative coexistence command
  - targeted pytest commands for the main regression points
- Deferred blockers should explicitly name:
  - `HS model` toy-model positive target gap
  - `LibRPA QSGW` first-principles/code-method mapping gap

</specifics>

<deferred>
## Deferred Ideas

- Do not widen into actually executing the `toy_model` or `first_principles`
  positive-L2 closures in this milestone.
- Do not start the next milestone here; only make the next actions explicit.

</deferred>
