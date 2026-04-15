# RUNBOOK: Phase 172.2 HS Replay And Coexistence Package

## Purpose

Replay the bounded HS positive-L2 proof together with the shipped HS negative
comparator on one isolated work root.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "hs_positive_negative_coexistence_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_hs_positive_negative_coexistence_acceptance.py --json
```

## Expected success markers

### Positive authoritative row

- claim id: `claim:hs-like-chaos-window-finite-size-core`
- authority: `authoritative_canonical`
- state: `trusted`

### Negative staged row

- entry id: `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`
- authority: `non_authoritative_staging`
- state: `contradiction_watch`

### Consultation proof

- query:
  `HS-like finite-size chaos window robust core OTOC Lyapunov exponent regime mismatch`
- `consult-l2(..., include_staging=True)` canonical ids include:
  `claim:hs-like-chaos-window-finite-size-core`
- staged ids include:
  `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`

## Carry-over after this phase

With the bounded HS lane replayable, the next unclosed research direction is
the user-requested `LibRPA QSGW` first-principles / large-codebase lane.
