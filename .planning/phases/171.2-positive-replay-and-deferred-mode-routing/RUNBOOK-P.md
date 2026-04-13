# RUNBOOK-P: Positive L2 Replay Package

## Purpose

Replay the full positive-L2 baseline from milestone `v1.97` after Phases `171`
and `171.1`.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "promote_candidate_mirrors_unit_into_repo_canonical_l2_surfaces" -q
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -k "positive_authoritative_rows_and_negative_contradiction_rows_coexist_on_l2_surfaces" -q
python research/knowledge-hub/runtime/scripts/run_formal_positive_l2_acceptance.py --json
python research/knowledge-hub/runtime/scripts/run_positive_negative_l2_coexistence_acceptance.py --json
```

## Expected success markers

### Fresh positive landing

- topic slug: `fresh-jones-finite-dimensional-factor-closure`
- theorem id: `theorem:jones-ch4-finite-product`
- projection id:
  `topic_skill_projection:fresh-jones-finite-dimensional-factor-closure`
- repo-local compiled reports:
  - `canonical/compiled/workspace_memory_map.json`
  - `canonical/compiled/workspace_graph_report.json`
  - `canonical/compiled/workspace_knowledge_report.json`
- `consult-l2` returns `theorem:jones-ch4-finite-product`

### Positive/negative coexistence

- theorem row remains `authoritative_canonical / trusted`
- negative row remains
  `non_authoritative_staging / contradiction_watch`
- coexistence query:
  `Jones finite product theorem classification failure`
- `consult-l2(..., include_staging=True)` returns:
  - canonical ids including `theorem:jones-ch4-finite-product`
  - staged ids including
    `staging:jones-finite-product-theorem-classification-failure`

## Raw receipts

- `evidence/replay-formal-positive-l2.json`
- `evidence/replay-positive-negative-coexistence.json`
- `evidence/pytest-positive-mirror.txt`
- `evidence/pytest-coexistence-unit.txt`
