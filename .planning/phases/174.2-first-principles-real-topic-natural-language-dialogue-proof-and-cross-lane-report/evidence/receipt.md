# Receipt: Phase 174.2 First-Principles Real-Topic Dialogue Proof And Cross-Lane Report

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "formal_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or toy_model_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or first_principles_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_first_principles_real_topic_dialogue_acceptance.py --json
```

## Observed results

- `pytest-three-lane-real-topic-dialogues.txt`: `3 passed, 77 deselected in 8.72s`
- `first-principles-real-topic-dialogue-acceptance.json`: `status = success`

## Key facts

- Fresh topic slug: `fresh-librpa-qsgw-deterministic-reduction-consistency-core`
- Research mode: `first_principles`
- Interaction-state artifact present
- Research-question contract present
- Consultation ids include:
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`

## Raw artifacts

- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/evidence/pytest-three-lane-real-topic-dialogues.txt`
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/evidence/first-principles-real-topic-dialogue-acceptance.json`
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/evidence/cross-lane-readiness-report.md`
