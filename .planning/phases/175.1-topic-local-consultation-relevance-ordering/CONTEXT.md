# Phase 175.1: Topic-Local Consultation Relevance Ordering - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Improve `consult-l2` ranking so clear fresh-topic queries can surface the most
relevant local staged entries before unrelated canonical carryover from older
topics.

</domain>

<decisions>
## Implementation Decisions

### Primary surface behavior
- Keep the existing canonical consultation path intact for legacy consumers.
- When the caller explicitly opts into staging and provides a fresh
  `topic_slug`, allow topic-local staged rows to compete for the primary
  consultation surface instead of isolating them to a secondary list only.

### Bounded locality signal
- Use explicit runtime context first: `topic_slug` and staged-row topic
  metadata.
- Prefer minimal ranking changes over a large retrieval rewrite; the goal is to
  fix fresh-topic locality, not redesign `consult-l2` wholesale.

### the agent's Discretion
The exact boost formula may vary, but it must remain bounded, explicit, and
test-backed. Cross-topic global ranking redesign stays out of scope.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `consult_canonical_l2()` in `l2_graph.py` already computes canonical primary
  hits, canonical expanded hits, and staged hits separately.
- `aitp_service.consult_l2()` already accepts `topic_slug`, but the lower-level
  `consult_canonical_l2()` path currently ignores it.

### Established Patterns
- Retrieval profiles define preferred unit types and traversal expansion.
- Existing tests in `test_l2_graph_activation.py` already cover canonical
  consultation, expanded traversal, and optional staging inclusion.

### Integration Points
- Phase `175.1` consumes the cleaner staging rows from Phase `175`.
- Phase `175.2` will need the improved primary-surface ranking to prove the
  multi-paper real-topic acceptance lane honestly.

</code_context>

<specifics>
## Specific Ideas

- Add one focused test where a topic-local staged row and an unrelated
  canonical row both match the query, but the local staged row should win when
  the call clearly targets the fresh topic.
- Normalize staged rows enough that they can safely appear in the primary
  consultation surface without breaking downstream consultation recording.

</specifics>

<deferred>
## Deferred Ideas

- Full retrieval-profile redesign or semantic reranking beyond the bounded
  topic-local boost.
- Canonical provenance enrichment for every historical unit.
- Multi-topic global relevance calibration beyond the fresh local-topic slice.

</deferred>
