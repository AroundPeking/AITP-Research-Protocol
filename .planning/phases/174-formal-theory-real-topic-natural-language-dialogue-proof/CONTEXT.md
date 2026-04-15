# Phase 174: Formal-Theory Real-Topic Natural-Language Dialogue Proof - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove that the public AITP front door can steer the closed formal-theory
baseline through one real natural-language dialogue without hidden seed state
or authority drift.

</domain>

<decisions>
## Implementation Decisions

### Real-topic target
- Use the user-requested formal-theory direction centered on von Neumann
  algebras / Jones-style operator-algebra content.
- Keep the real dialogue tied to the already-closed bounded positive formal-L2
  route from `v1.97`, rather than opening a brand-new theorem family.

### Honesty constraints
- The run must start from a fresh natural-language request and use the public
  entry surfaces first.
- Do not bypass the front door by seeding hidden runtime or source-layer state.
- The test may reuse known source material only through explicit public-facing
  routing steps and durable topic artifacts.

### the agent's Discretion
The exact natural-language wording may vary, but it must stay recognizably in
the von Neumann algebra / Jones formal-theory lane and remain bounded to the
already-proved positive baseline.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_formal_positive_l2_acceptance.py` is the bounded positive-L2 formal
  baseline from `v1.97`.
- `fresh-jones-finite-dimensional-factor-closure` is the canonical positive
  formal route already known to land honestly in authoritative `L2`.

### Established Patterns
- Real-topic E2E tests should begin from natural language and then prove that
  the route remains bounded and honest all the way through the runtime
  surfaces.
- The current milestone is not about creating a new positive formal theorem; it
  is about proving real natural-language steering fidelity.

### Integration Points
- Phase `174` establishes the formal-theory leg of the three-lane dialogue E2E.
- Phase `174.1` and `174.2` will mirror the same philosophy for toy-model and
  first-principles lanes.

</code_context>

<specifics>
## Specific Ideas

- Likely natural-language prompt family:
  “Help me study a bounded von Neumann algebra / Jones finite-factor question
  and keep the route tied to one already-proved positive formal result.”
- The proof should record where the front door still asks for human steering
  and where it can proceed mechanically.

</specifics>

<deferred>
## Deferred Ideas

- Do not expand this phase into the toy-model or first-principles lanes.
- Do not reopen positive-L2 closure mechanics already settled in `v1.97`.

</deferred>
