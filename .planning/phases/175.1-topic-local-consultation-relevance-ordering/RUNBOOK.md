# RUNBOOK: Phase 175.1 Topic-Local Consultation Relevance Ordering

## Purpose

Replay the bounded `consult-l2` ranking change that allows explicit fresh-topic
staged rows to compete for the primary consultation surface.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -q
python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "consult_l2" -q
```

## Expected success markers

- `test_topic_local_staged_hit_can_win_primary_surface_when_staging_is_included`
  passes
- when `include_staging=True` and `topic_slug` is provided, a matching local
  staged row can appear in `primary_hits`
- `aitp_service.consult_l2()` still passes its bounded consultation regression
  slice

## Current success boundary

This phase only hardens explicit topic-local consultation ordering for calls
that opt into staging. It does not redesign the broader retrieval stack or
global ranking semantics.
