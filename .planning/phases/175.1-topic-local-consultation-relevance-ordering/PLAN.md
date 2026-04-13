# Plan: 175.1-01 - Raise topic-local staged relevance above unrelated canonical carryover

**Phase:** 175.1
**Axis:** Axis 1 (layer-internal optimization) + Axis 2 (inter-layer connection)
**Requirements:** L2H-03

## Goal

Make `consult-l2` capable of surfacing topic-local staged rows on the primary
consultation surface when the caller explicitly asks about a fresh topic and
includes staging.

## Planned Route

### Step 1: Reproduce the ranking defect with a focused consultation test

**Files:**
- `research/knowledge-hub/tests/test_l2_graph_activation.py`

Add a failing test showing that:

- an unrelated canonical hit and a local staged hit both match the query
- with `include_staging=True` and a concrete `topic_slug`, the local staged hit
  should win the primary surface

### Step 2: Implement bounded topic-local primary-surface ranking

**Files:**
- `research/knowledge-hub/knowledge_hub/l2_graph.py`
- `research/knowledge-hub/knowledge_hub/aitp_service.py`

Minimal implementation:

- pass `topic_slug` into the low-level consultation path
- normalize staged rows so they can appear in `primary_hits`
- apply a bounded topic-local boost only when the call explicitly targets a
  topic and includes staging

### Step 3: Re-verify consultation slices

**Commands to preserve as evidence:**
- `python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -q`
- `python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "consult_l2" -q`

### Step 4: Leave durable closure artifacts

**Artifacts to write during execution:**
- `.planning/phases/175.1-topic-local-consultation-relevance-ordering/RUNBOOK.md`
- `.planning/phases/175.1-topic-local-consultation-relevance-ordering/SUMMARY.md`
- `.planning/phases/175.1-topic-local-consultation-relevance-ordering/evidence/`

## Acceptance Criteria

- [ ] topic-local staged rows can appear on the primary consultation surface
      when a fresh-topic call explicitly includes staging
- [ ] unrelated canonical carryover no longer dominates the primary surface in
      that bounded case
- [ ] consultation recording remains compatible after the ranking change
