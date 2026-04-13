# Receipt: Phase 171.2 Positive Replay And Deferred Routing

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "promote_candidate_mirrors_unit_into_repo_canonical_l2_surfaces" -q
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -k "positive_authoritative_rows_and_negative_contradiction_rows_coexist_on_l2_surfaces" -q
python research/knowledge-hub/runtime/scripts/run_formal_positive_l2_acceptance.py --json
python research/knowledge-hub/runtime/scripts/run_positive_negative_l2_coexistence_acceptance.py --json
```

## Observed results

- `pytest-positive-mirror.txt`: `1 passed, 152 deselected in 0.52s`
- `pytest-coexistence-unit.txt`: `1 passed, 7 deselected in 0.33s`
- `replay-formal-positive-l2.json`: `status = success`
- `replay-positive-negative-coexistence.json`: `status = success`

## Deferred lane notes

- `HS model` toy-model lane: positive target + convergence contract still
  missing
- `LibRPA QSGW` first-principles lane: code-method mapping + bounded positive
  target still missing

See `evidence/deferred-lane-routing.md` for the explicit next actions.
