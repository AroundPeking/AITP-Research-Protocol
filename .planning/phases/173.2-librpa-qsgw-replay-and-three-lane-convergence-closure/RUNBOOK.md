# RUNBOOK: Phase 173.2 LibRPA QSGW Replay And Three-Lane Convergence Package

## Purpose

Replay the bounded `LibRPA QSGW` positive-L2 proof and record the resulting
three-lane convergence baseline.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_positive_l2_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py --json
```

## Expected success markers

- claim id: `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- canonical mirror:
  `canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`
- `consult-l2` query:
  `LibRPA QSGW deterministic reduction thread consistency core`
- consultation ids include:
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`

## Three-lane baseline after this phase

- formal theory baseline: `v1.97`
- toy-model baseline: `v1.98`
- first-principles / code-method baseline: `v1.99`
