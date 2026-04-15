# RUNBOOK: Phase 174.1 Toy-Model Real-Topic Dialogue Proof

## Purpose

Replay the toy-model real natural-language dialogue proof on an isolated work
root and confirm that the promotion-gate regressions remain green.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "toy_model_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or human_modification_record_acceptance_script_runs_on_isolated_work_root or transition_history_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_toy_model_real_topic_dialogue_acceptance.py --json
```

## Expected success markers

- topic slug: `fresh-hs-like-chaos-window-finite-size-core`
- `interaction_state.json` exists on the fresh topic runtime root
- `research_question.contract.json` exists on the fresh topic runtime root
- canonical claim mirror exists for
  `claim:hs-like-chaos-window-finite-size-core`
- `consult-l2` still surfaces `claim:hs-like-chaos-window-finite-size-core`
- promotion-gate actor-binding regressions remain green

## Current success boundary

This phase proves steering fidelity for the already-closed bounded toy-model
lane. It does not claim thermodynamic closure, larger-system continuation, or
any widening beyond the robust finite-size HS-like core.
