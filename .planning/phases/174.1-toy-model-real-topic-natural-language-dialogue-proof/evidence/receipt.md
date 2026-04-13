# Receipt: Phase 174.1 Toy-Model Real-Topic Dialogue Proof

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "toy_model_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or human_modification_record_acceptance_script_runs_on_isolated_work_root or transition_history_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_toy_model_real_topic_dialogue_acceptance.py --json
```

## Observed results

- `pytest-toy-model-real-topic-dialogue.txt`: `3 passed, 76 deselected in 3.68s`
- `toy-model-real-topic-dialogue-acceptance.json`: `status = success`

## Key facts

- Fresh topic slug: `fresh-hs-like-chaos-window-finite-size-core`
- Research mode: `toy_model`
- Interaction-state artifact present
- Research-question contract present
- Consultation ids include: `claim:hs-like-chaos-window-finite-size-core`

## Raw artifacts

- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/pytest-toy-model-real-topic-dialogue.txt`
- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/toy-model-real-topic-dialogue-acceptance.json`
