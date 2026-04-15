# Phase 173.2: LibRPA QSGW Replay And Three-Lane Convergence Closure - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Close milestone `v1.99` with one replayable `LibRPA QSGW` positive-L2 package
and one explicit three-lane convergence note covering the formal-theory,
toy-model, and first-principles baselines.

</domain>

<decisions>
## Implementation Decisions

### Replay closure
- Reuse the already-proven `run_librpa_qsgw_positive_l2_acceptance.py` wrapper
  instead of inventing a second promotion script.
- Treat this phase as a replay/evidence package, not as another runtime
  feature.

### Three-lane convergence note
- Write explicit closure notes for the three user-requested research
  directions:
  - pure formal theory
  - toy model numerical + derivation
  - large codebase / first-principles / algorithm development
- Treat `v1.97`, `v1.98`, and `v1.99` as the three bounded positive baselines.

### the agent's Discretion
The convergence note may recommend the next milestone around broad
real-topic natural-language dialogue testing, as long as it stays bounded and
does not pretend those tests are already complete.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_formal_positive_l2_acceptance.py` remains the bounded formal positive-L2
  replay lane.
- `run_hs_positive_l2_acceptance.py` remains the bounded toy-model positive-L2
  replay lane.
- `run_librpa_qsgw_positive_l2_acceptance.py` is now the bounded
  first-principles / code-method positive-L2 replay lane.

### Established Patterns
- Replay closure phases should prefer raw receipts, a concise runbook, and one
  explicit carry-over note over new architecture work.
- Milestone closure evidence lives in phase-level runbooks, receipts, and
  explicit summaries.

### Integration Points
- Phase `173.2` should close `REQ-QSGW-05`.
- Once this phase closes, `v1.99` is ready for milestone lifecycle handling.

</code_context>

<specifics>
## Specific Ideas

- Replay package should include:
  - the `LibRPA QSGW` positive-L2 acceptance command
  - the focused runtime-script pytest command
- The convergence note should explicitly say the next unclosed frontier is
  broad real-topic natural-language testing across the three closed baselines.

</specifics>

<deferred>
## Deferred Ideas

- Do not start the broad three-lane natural-language dialogue tests in this
  phase.
- Do not reopen the bounded closure of any already-shipped lane.

</deferred>
