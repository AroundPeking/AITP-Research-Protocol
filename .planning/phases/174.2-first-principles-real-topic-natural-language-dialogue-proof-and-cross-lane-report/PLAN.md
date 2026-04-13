# Plan: 174.2-01 - Run the first-principles dialogue proof and write the cross-lane comparative report

**Phase:** 174.2
**Axis:** Axis 4 (human evidence) + Axis 5 (agent-facing roadmap clarity)
**Requirements:** REQ-E2E-03, REQ-E2E-04, REQ-E2E-05

## Goal

Close milestone `v2.0` by proving that the public AITP front door can steer
the already-closed bounded `LibRPA QSGW` first-principles lane through one real
natural-language dialogue, then write one honest cross-lane report spanning the
formal, toy-model, and first-principles dialogue proofs.

## Planned Route

### Step 1: Lock the bounded first-principles dialogue target

**Artifacts to write during execution:**
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/TARGET.md`
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/RUNBOOK.md`

Pin down:

- fresh topic slug
- fresh natural-language topic / question / human request
- authoritative target unit id
- canonical mirror path
- preserved bounded non-claims

### Step 2: Add the isolated first-principles dialogue acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_first_principles_real_topic_dialogue_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_librpa_qsgw_target_contract_acceptance.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

The route should:

- reuse the shipped `LibRPA QSGW` positive-L2 acceptance on a fresh work root
- pass through a fresh natural-language first-principles topic, question, and
  human requests
- verify `interaction_state.json` and `research_question.contract.json`
  preserve the dialogue
- verify the canonical claim-card mirror exists
- verify `consult-l2` still returns the bounded `LibRPA QSGW` positive claim

### Step 3: Write the cross-lane comparative report

**Artifacts to write during execution:**
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/evidence/cross-lane-readiness-report.md`

The report must compare:

- formal theory lane
- toy-model numerical + derivation lane
- large codebase / first-principles / algorithm development lane

For each lane, record:

- fresh dialogue topic and authoritative `L2` unit
- steering artifact preservation
- remaining bounded blocker or explicit non-claim
- next widening decision

### Step 4: Leave durable evidence for phase closure

**Artifacts to write during execution:**
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/SUMMARY.md`
- `.planning/phases/174.2-first-principles-real-topic-natural-language-dialogue-proof-and-cross-lane-report/evidence/`

## Acceptance Criteria

- [ ] one real natural-language dialogue run proves the first-principles
      baseline can be entered through the public front door
- [ ] runtime steering artifacts preserve the fresh first-principles request
- [ ] the route stays aligned with the bounded positive authoritative-L2
      first-principles claim
- [ ] one durable cross-lane report compares the three dialogue proofs
- [ ] the report leaves explicit next routing for the remaining blockers
