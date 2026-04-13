# Phase 173.1: LibRPA QSGW Positive Promotion To Authoritative L2 - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Promote the bounded `LibRPA QSGW` deterministic-reduction consistency core from
the fresh first-principles target contract into one authoritative canonical
`L2` unit with durable repo-local receipts and consultation parity.

</domain>

<decisions>
## Implementation Decisions

### Promotion route
- Reuse the bounded positive target from Phase `173`:
  `candidate:librpa-qsgw-deterministic-reduction-consistency-core`.
- Promote it through the explicit human gate:
  `request_promotion -> approve_promotion -> promote_candidate`.
- Keep the promoted scope bounded to the deterministic-reduction consistency
  core on the `H2O/really_tight iter=10` reference workflow.

### Authority and read-path proof
- Prove the promoted unit lands as
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`.
- Require a repo-local canonical mirror at
  `canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`.
- Require compiled workspace reports and `consult-l2` to expose the same
  promoted unit on an isolated work root.

### Honesty constraints
- Preserve the explicit non-claims from Phase `173`: no full QSGW convergence,
  no whole-codebase closure, no multi-system portability claim.
- Keep the promotion tied to the real codebase/workflow anchors and existing
  validator evidence, not to a prose-only abstraction.

### the agent's Discretion
The exact temporary backend root may vary, but the promoted authoritative unit
and repo-local canonical mirror must stay stable.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_librpa_qsgw_target_contract_acceptance.py` now builds the fresh
  first-principles topic shell, source anchors, bounded target contract, and
  candidate ledger on an isolated work root.
- `run_hs_positive_l2_acceptance.py` shows the simplest manual-promotion
  pattern for a bounded `claim_card` candidate.
- `AITPService.request_promotion`, `approve_promotion`, and
  `promote_candidate` already expose the needed human-gated route.

### Established Patterns
- Acceptance scripts should return one JSON payload with durable artifact paths.
- Authoritative-L2 closure requires both backend-side promotion receipts and a
  repo-local canonical mirror.
- The bounded target-contract wrapper is the clean input surface for this phase;
  do not rebuild the bounded route from scratch.

### Integration Points
- Phase `173.1` consumes the candidate ledger and trust artifacts produced by
  Phase `173`.
- Phase `173.2` can then close replay and three-lane convergence once the
  authoritative QSGW claim exists.

</code_context>

<specifics>
## Specific Ideas

- Fresh topic slug should stay
  `librpa-qsgw-deterministic-reduction-consistency-core`.
- The promoted authoritative unit id should be
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`.
- The natural-language consultation proof should use a query centered on:
  `LibRPA QSGW deterministic reduction thread consistency core`.

</specifics>

<deferred>
## Deferred Ideas

- Do not widen this phase into replay or three-lane convergence closure; that
  is Phase `173.2`.
- Do not reopen the bounded-target selection debate unless a real promotion
  blocker appears.

</deferred>
