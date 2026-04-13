# Receipt: Phase 171.1 Positive/Negative L2 Coexistence

## Replay commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -k "positive_authoritative_rows_and_negative_contradiction_rows_coexist_on_l2_surfaces" -q
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "positive_negative_l2_coexistence_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_positive_negative_l2_coexistence_acceptance.py --json
```

## Observed results

- `pytest-coexistence-unit.txt`: `1 passed, 7 deselected in 0.30s`
- `pytest-coexistence-script.txt`: `1 passed, 71 deselected in 4.73s`
- `positive-negative-l2-coexistence-acceptance.json`: `status = success`

## Coexistence state

- Positive theorem row:
  - `knowledge_id = theorem:jones-ch4-finite-product`
  - `authority_level = authoritative_canonical`
  - `knowledge_state = trusted`
- Negative contradiction row:
  - `knowledge_id = staging:jones-finite-product-theorem-classification-failure`
  - `authority_level = non_authoritative_staging`
  - `knowledge_state = contradiction_watch`

## Consultation proof

- Query text: `Jones finite product theorem classification failure`
- Retrieval profile: `l4_adjudication`
- Canonical ids include: `theorem:jones-ch4-finite-product`
- Staged ids include:
  `staging:jones-finite-product-theorem-classification-failure`

## Raw artifacts

- `.planning/phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/pytest-coexistence-unit.txt`
- `.planning/phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/pytest-coexistence-script.txt`
- `.planning/phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/positive-negative-l2-coexistence-acceptance.json`
