# RUNBOOK: Phase 173.1 LibRPA QSGW Positive Authoritative-L2 Closure

## Purpose

Replay the bounded `LibRPA QSGW` positive-L2 closure using the fresh
first-principles topic from Phase `173`.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_positive_l2_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py --json
```

## What the wrapper does

1. Reuses the Phase `173` target-contract acceptance on a fresh isolated work root.
2. Seeds a minimal TPKN backend for backend-side promotion.
3. Requests, approves, and promotes the bounded `LibRPA QSGW` candidate.
4. Verifies the repo-local canonical claim-card mirror exists.
5. Recompiles workspace memory, graph, and knowledge reports.
6. Runs `consult-l2` and verifies the promoted claim reappears on the read path.

## Expected success markers

- topic slug: `librpa-qsgw-deterministic-reduction-consistency-core`
- run id: one fresh `*-bootstrap` run
- target unit id: `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- canonical mirror:
  `canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`
- `consult-l2` query:
  `LibRPA QSGW deterministic reduction thread consistency core`
- consultation ids include:
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`

## Next bounded gap

Phase `173.1` closes the positive authoritative landing itself. The next gap is
Phase `173.2`: replay the positive lane and write the explicit three-lane
convergence closure.
