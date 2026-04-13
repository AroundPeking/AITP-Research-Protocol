# Phase 171.1: L2 Surface Hardening Under Real Positive/Negative Coexistence - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove that the new authoritative positive formal-theory landing from Phase
`171` can coexist with the existing `negative_result -> contradiction_watch`
surface without losing authority separation, provenance visibility, or
retrieval visibility across the compiled L2 reports and `consult-l2`.

</domain>

<decisions>
## Implementation Decisions

### Coexistence proof surface
- Reuse the real Phase `171` positive theorem and projection surfaces instead
  of inventing synthetic positive-only fixtures for the main acceptance lane.
- Keep the negative side explicitly non-authoritative: it must remain a staged
  `negative_result` that compiles as `contradiction_watch`, not a fake
  canonical theorem competitor.
- Force coexistence through one shared lexical topic/query surface so the same
  compile + consultation pass can see both the positive authoritative row and
  the negative contradiction row.

### Hardening strategy
- Start with failing regression tests before adding any new acceptance code.
- Prefer new regression coverage and a dedicated coexistence acceptance lane
  over schema widening or retrieval redesign.
- Patch only the smallest surface if the tests expose real authority or
  provenance drift.

### the agent's Discretion
The exact negative-result title/query wording is at the agent's discretion as
long as it honestly describes a bounded failure or non-widening result and
causes the coexistence surfaces to be mechanically exercised.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `runtime/scripts/run_formal_positive_l2_acceptance.py` already proves the
  fresh formal positive landing and repo-local L2 parity.
- `knowledge_hub/l2_compiler.py` already compiles canonical rows and staged
  rows into one workspace knowledge report.
- `knowledge_hub/l2_graph.py` already exposes canonical hits plus optional
  `staged_hits` through `consult_canonical_l2(..., include_staging=True)`.
- `knowledge_hub/l2_staging.py` already has `stage_negative_result_entry()`
  for durable negative-result staging.

### Established Patterns
- Runtime acceptance scripts typically create isolated work roots, call CLI or
  service surfaces, and emit one JSON payload with durable artifact paths.
- L2 regression tests live in `test_l2_graph_activation.py` and
  `test_runtime_scripts.py`.
- Compiled L2 trust separation is currently encoded through
  `authority_level` + `knowledge_state`, not through a unified ranking score.

### Integration Points
- The new phase should extend the runtime acceptance surface with one
  coexistence script.
- Unit/regression coverage should target `materialize_workspace_knowledge_report`
  and `consult_canonical_l2(..., include_staging=True)`.

</code_context>

<specifics>
## Specific Ideas

- Query around `Jones finite product theorem` should surface the authoritative
  theorem row while a bounded failure/widening warning with overlapping terms
  surfaces in `staged_hits`.
- The knowledge report should show:
  - positive row: `authority_level=authoritative_canonical`,
    `knowledge_state=trusted`
  - negative row: `authority_level=non_authoritative_staging`,
    `knowledge_state=contradiction_watch`
- Provenance refs must stay populated on both rows.

</specifics>

<deferred>
## Deferred Ideas

- Do not widen this phase into multi-mode positive closure.
- Do not redesign consultation ranking beyond what the coexistence proof needs.
- Do not canonicalize the negative result unless a later milestone explicitly
  asks for that route.

</deferred>
