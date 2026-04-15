# RUNBOOK: Phase 174.2 First-Principles Real-Topic Dialogue Proof And Cross-Lane Report

## Purpose

Replay the first-principles real natural-language dialogue proof and confirm
that the three requested research directions now each have one bounded honest
dialogue proof.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "formal_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or toy_model_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or first_principles_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_first_principles_real_topic_dialogue_acceptance.py --json
```

## Expected success markers

- topic slug: `fresh-librpa-qsgw-deterministic-reduction-consistency-core`
- `interaction_state.json` exists on the fresh topic runtime root
- `research_question.contract.json` exists on the fresh topic runtime root
- canonical claim mirror exists for
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- `consult-l2` still surfaces
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- the three dialogue tests for formal, toy, and first-principles lanes all pass

## Cross-lane baseline after this phase

- formal theory real-dialogue baseline: Phase `174`
- toy-model real-dialogue baseline: Phase `174.1`
- first-principles / code-method real-dialogue baseline: Phase `174.2`
