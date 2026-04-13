# Receipt: Phase 172.2 HS Replay And Coexistence Closure

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "hs_positive_negative_coexistence_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_hs_positive_negative_coexistence_acceptance.py --json
```

## Observed results

- `pytest-hs-coexistence-script.txt`: `1 passed, 74 deselected in 1.74s`
- `hs-positive-negative-coexistence-acceptance.json`: `status = success`

## Coexistence state

- Positive claim row:
  - `knowledge_id = claim:hs-like-chaos-window-finite-size-core`
  - `authority_level = authoritative_canonical`
  - `knowledge_state = trusted`
- Negative staged row:
  - `knowledge_id = staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`
  - `authority_level = non_authoritative_staging`
  - `knowledge_state = contradiction_watch`

## Consultation proof

- Query text:
  `HS-like finite-size chaos window robust core OTOC Lyapunov exponent regime mismatch`
- Retrieval profile: `l4_adjudication`
- Canonical ids include: `claim:hs-like-chaos-window-finite-size-core`
- Staged ids include:
  `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`

## Raw artifacts

- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/evidence/pytest-hs-coexistence-script.txt`
- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/evidence/hs-positive-negative-coexistence-acceptance.json`
- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/evidence/deferred-lane-routing.md`
