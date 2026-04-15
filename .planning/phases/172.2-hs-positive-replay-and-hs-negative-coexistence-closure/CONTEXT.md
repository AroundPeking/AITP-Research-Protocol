# Phase 172.2: HS Positive Replay And HS Negative Coexistence Closure - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Close milestone `v1.98` with one replayable HS positive/negative coexistence
package and one explicit carry-over note for the deferred `LibRPA QSGW`
first-principles / code-method lane.

</domain>

<decisions>
## Implementation Decisions

### Coexistence proof
- Reuse the new Phase `172.1` positive authoritative-L2 wrapper rather than
  inventing another promotion route.
- Reuse the already-shipped staged HS negative comparator:
  `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`.
- Prove coexistence through both the compiled knowledge report and
  `consult-l2(..., include_staging=True)`.

### Replay closure
- Treat this phase as a replay and evidence package, not as new L2 compiler
  architecture work.
- Store one raw coexistence payload and one short replay runbook for the HS
  lane.

### Deferred routing
- Make the three-lane convergence explicit:
  - pure formal theory: closed positive baseline in `v1.97`
  - toy model numerical + derivation: closed bounded positive baseline in `v1.98`
  - large codebase / first-principles / algorithm development: still deferred
    to the `LibRPA QSGW` lane
- Route only the deferred `LibRPA QSGW` lane forward here; do not start it.

### the agent's Discretion
The coexistence query may be tuned for retrieval overlap, but it must still be
honest and traceable to the positive and negative HS surfaces being checked.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_hs_positive_l2_acceptance.py` already replays the full positive HS
  authoritative landing on an isolated work root.
- The shipped HS negative comparator already lives under
  `canonical/staging/entries/`.
- `consult-l2(include_staging=True)` is already the standard coexistence proof
  surface for positive/negative separation.

### Established Patterns
- Replay closure phases should prefer wrapper scripts plus durable receipts over
  new feature work.
- Deferred lane routing should be captured in markdown under the phase
  `evidence/` directory, not left in chat memory.

### Integration Points
- This phase consumes the new positive authoritative-L2 wrapper from Phase
  `172.1`.
- This phase should close `REQ-HS-04` and `REQ-HS-05` together.

</code_context>

<specifics>
## Specific Ideas

- Coexistence query should include both positive-core and OTOC-mismatch terms.
- Deferred routing note should explicitly name `LibRPA QSGW` as the next
  first-principles / large-codebase positive-L2 target.

</specifics>

<deferred>
## Deferred Ideas

- Do not widen from the bounded HS positive core into shoulder, thermodynamic,
  or larger-system claims.
- Do not execute the `LibRPA QSGW` lane in this phase; only route it.

</deferred>
