# Phase 172.1: HS Model Positive Promotion To Authoritative L2 - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Promote the bounded HS-like finite-size chaos-window core from the fresh
toy-model target contract into one authoritative canonical `L2` unit with
durable repo-local receipts and consultation parity.

</domain>

<decisions>
## Implementation Decisions

### Promotion route
- Reuse the bounded positive target from Phase `172`:
  `candidate:hs-chaos-window-finite-size-core`.
- Promote it through the explicit human gate:
  `request_promotion -> approve_promotion -> promote_candidate`.
- Keep the promoted scope bounded to the robust finite-size core
  `0.4 <= alpha <= 1.0`.

### Authority and read-path proof
- Prove the promoted unit lands as
  `claim:hs-like-chaos-window-finite-size-core`.
- Require a repo-local canonical mirror at
  `canonical/claim-cards/claim_card--hs-like-chaos-window-finite-size-core.json`.
- Require compiled workspace reports and `consult-l2` to expose the same
  promoted unit on an isolated work root.

### Promotion API guardrail
- Re-verify the promotion-gate acceptance surfaces that depend on the CLI-side
  actor fields:
  `requested_by`, `approved_by`, `rejected_by`, `promoted_by`.
- Treat those acceptance receipts as supporting evidence for the HS promotion
  lane rather than as a separate milestone slice.

### the agent's Discretion
The exact temporary backend root may vary, but the promoted authoritative unit
and repo-local canonical mirror must stay stable.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_hs_toy_model_target_contract_acceptance.py` already builds the fresh
  toy-model topic shell and benchmark contract on an isolated work root.
- `run_formal_positive_l2_acceptance.py` shows the authoritative-L2 wrapper
  pattern: isolated work root, backend promotion, compiled-report parity, and
  `consult-l2` parity.
- `AITPService.request_promotion`, `approve_promotion`, and
  `promote_candidate` already expose the needed human-gated route.

### Established Patterns
- Acceptance scripts should return one JSON payload with durable artifact paths.
- Authoritative-L2 closure requires both backend-side promotion receipts and a
  repo-local canonical mirror.
- Phase receipts should include both the isolated acceptance lane and the
  supporting targeted pytest regressions.

### Integration Points
- The fresh HS positive target contract becomes the only input to this phase.
- Positive/negative coexistence against the shipped HS contradiction route is
  deferred to Phase `172.2`.

</code_context>

<specifics>
## Specific Ideas

- Fresh topic slug should stay `hs-like-finite-size-chaos-window-core`.
- The promoted authoritative unit id should be
  `claim:hs-like-chaos-window-finite-size-core`.
- The natural-language consultation proof should use:
  `HS-like finite-size chaos window robust core`.

</specifics>

<deferred>
## Deferred Ideas

- Do not widen this phase into positive/negative coexistence; that is Phase
  `172.2`.
- Do not route `LibRPA QSGW` carry-over here; that belongs in the replay and
  deferred-routing closure.

</deferred>
