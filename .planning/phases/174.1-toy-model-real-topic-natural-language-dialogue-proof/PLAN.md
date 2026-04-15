# Plan: 174.1-01 - Run one real natural-language dialogue proof for the toy-model baseline

**Phase:** 174.1
**Axis:** Axis 2 (inter-layer connection) + Axis 5 (agent-facing steering)
**Requirements:** REQ-E2E-02

## Goal

Prove that the public AITP front door can steer the already-closed bounded
toy-model baseline through one fresh natural-language dialogue, while keeping
the route tied to the authoritative HS-like finite-size positive core.

## Planned Route

### Step 1: Lock the bounded toy-model dialogue target

**Artifacts to write during execution:**
- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/TARGET.md`
- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/RUNBOOK.md`

Pin down:

- fresh topic slug
- fresh natural-language topic / question / human request
- authoritative target unit id
- canonical mirror path
- preserved exact-HS negative comparator

### Step 2: Add the isolated toy-model dialogue acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_toy_model_real_topic_dialogue_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_hs_positive_l2_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_hs_toy_model_target_contract_acceptance.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

The route should:

- reuse the shipped HS positive-L2 acceptance on a fresh work root
- pass through a fresh natural-language toy-model topic, question, and human
  request
- verify `interaction_state.json` and `research_question.contract.json`
  preserve the dialogue
- verify the canonical claim-card mirror exists
- verify `consult-l2` still returns the bounded HS-like positive claim

### Step 3: Re-verify promotion-gate bindings stay green

**Command to preserve as supporting evidence:**
- `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "toy_model_real_topic_dialogue_acceptance_script_runs_on_isolated_work_root or human_modification_record_acceptance_script_runs_on_isolated_work_root or transition_history_acceptance_script_runs_on_isolated_work_root" -q`

Keep the toy-model dialogue proof compatible with the already-requested
promotion-gate actor binding checks.

### Step 4: Leave durable evidence for phase closure

**Artifacts to write during execution:**
- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/SUMMARY.md`
- `.planning/phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/`

## Acceptance Criteria

- [ ] one real natural-language dialogue run proves the toy-model baseline can
      be entered through the public front door
- [ ] runtime steering artifacts preserve the fresh toy-model request
- [ ] the route stays aligned with the bounded HS-like positive authoritative-L2 claim
- [ ] promotion-gate regression acceptances still pass on isolated work roots
- [ ] one dedicated acceptance lane proves the route mechanically
