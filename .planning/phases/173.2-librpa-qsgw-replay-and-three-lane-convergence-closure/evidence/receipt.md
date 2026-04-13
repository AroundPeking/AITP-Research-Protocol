# Receipt: Phase 173.2 LibRPA QSGW Replay And Three-Lane Convergence Closure

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_positive_l2_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py --json
```

## Observed results

- `pytest-librpa-qsgw-positive-l2.txt`: `1 passed, 76 deselected in 2.79s`
- `replay-librpa-qsgw-positive-l2.json`: `status = success`

## Positive-L2 replay proof

- Promoted claim:
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- Canonical mirror:
  `claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`
- Consultation query:
  `LibRPA QSGW deterministic reduction thread consistency core`

## Raw artifacts

- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/evidence/pytest-librpa-qsgw-positive-l2.txt`
- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/evidence/replay-librpa-qsgw-positive-l2.json`
- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/evidence/three-lane-convergence.md`
