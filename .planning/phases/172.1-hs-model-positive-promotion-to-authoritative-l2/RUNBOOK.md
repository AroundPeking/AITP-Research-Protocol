# RUNBOOK: Phase 172.1 HS Positive Authoritative-L2 Closure

## Purpose

Replay the bounded HS-like positive-L2 closure using the fresh toy-model topic
from Phase `172`.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "hs_positive_l2_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_hs_positive_l2_acceptance.py --json
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "transition_history_acceptance_script_runs_on_isolated_work_root or human_modification_record_acceptance_script_runs_on_isolated_work_root" -q
```

## What the wrapper does

1. Reuses the Phase `172` target-contract acceptance on a fresh isolated work root.
2. Seeds a minimal TPKN backend for backend-side promotion.
3. Requests, approves, and promotes the bounded HS-like positive candidate.
4. Verifies the repo-local canonical claim-card mirror exists.
5. Recompiles workspace memory, graph, and knowledge reports.
6. Runs `consult-l2` and verifies the promoted claim reappears on the read path.

## Expected success markers

- topic slug: `hs-like-finite-size-chaos-window-core`
- run id: one fresh `*-bootstrap` run
- target unit id: `claim:hs-like-chaos-window-finite-size-core`
- canonical mirror:
  `canonical/claim-cards/claim_card--hs-like-chaos-window-finite-size-core.json`
- `consult-l2` query:
  `HS-like finite-size chaos window robust core`
- consultation ids include:
  `claim:hs-like-chaos-window-finite-size-core`

## Next bounded gap

Phase `172.1` closes the positive authoritative landing itself. The next gap is
Phase `172.2`: replay the positive lane against the existing HS negative
comparator on the same compiled and consultation surfaces, then route the
deferred `LibRPA QSGW` lane forward explicitly.
