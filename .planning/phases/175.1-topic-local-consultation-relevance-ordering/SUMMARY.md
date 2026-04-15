# Phase 175.1 Summary: Topic-Local Consultation Relevance Ordering

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 1 (layer-internal optimization) + Axis 2 (inter-layer connection)

## What was done

Phase `175.1` closed the bounded consultation-ranking slice of milestone
`v2.1`.

### Fixes landed

- `consult_canonical_l2()` now accepts `topic_slug` and can use it when the
  caller explicitly asks to include staging
- topic-local staged rows are normalized so they can appear on the primary
  consultation surface instead of being trapped in `staged_hits` only
- `aitp_service.consult_l2()` now forwards `topic_slug` into the low-level
  consultation path
- traversal and legacy canonical consultation behavior remain intact for the
  bounded existing regression slices

## Acceptance criteria

- [x] Topic-local staged rows can appear on the primary consultation surface when a fresh-topic call explicitly includes staging
- [x] Unrelated canonical carryover no longer dominates the primary surface in that bounded case
- [x] Consultation recording remains compatible after the ranking change

## Evidence

| Artifact | Location | Purpose |
|----------|----------|---------|
| `pytest-l2-graph-activation.txt` | `phases/175.1-topic-local-consultation-relevance-ordering/evidence/` | Full consultation-activation regression receipt, including the new topic-local primary-surface test |
| `pytest-aitp-service-consult-l2.txt` | `phases/175.1-topic-local-consultation-relevance-ordering/evidence/` | Service-level consultation regression receipt |
| `receipt.md` | `phases/175.1-topic-local-consultation-relevance-ordering/evidence/` | Human-readable replay receipt |

## What this phase proved

1. Fresh-topic local staged rows no longer have to stay trapped in a secondary
   staging-only surface when the caller explicitly requests staging context.
2. The consultation path can stay bounded and backwards-compatible while still
   surfacing the locally relevant row first.
3. The service-level consultation wrapper remains compatible after forwarding
   topic-local context into the low-level ranking path.
