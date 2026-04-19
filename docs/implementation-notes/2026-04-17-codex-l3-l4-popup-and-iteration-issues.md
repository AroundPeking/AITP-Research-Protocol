# Codex L3-L4 Popup And Iteration Issues

Date: 2026-04-17

Status: implementation issue report, not protocol

Context: these issues were exposed during a real Codex-driven AITP continuation of the QSGW revision topic
`jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests`.

This note is intentionally evidence-led. It records what was observed in a real topic, what part of the stack appears responsible, and what should be fixed first.

## Executive summary

The current Codex + AITP path is usable, but the L3-L4 operator experience is still weaker than intended.

The main issues exposed by the QSGW session are:

1. AITP did not raise a real human checkpoint after the new L3 plan became execution-relevant.
2. Even when popup payload support exists in the kernel, the Codex front door does not turn it into a native user-facing interactive prompt.
3. L3-L4 iteration files are materialized early, but a real L4 return is often absent, leaving `l4_return` and `l3_synthesis` in a persistent placeholder state.
4. Some derived runtime surfaces lag behind updated contracts and steering, so a topic can temporarily present mixed old/new wording.
5. Long steering directions can be truncated in the auto-generated innovation-direction text, even when the raw operator request still contains the full intent.

## Session used as evidence

Primary topic:

- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/`

Representative runtime surfaces:

- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/topic_dashboard.md`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/research_question.contract.md`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/validation_contract.active.md`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/next_action_decision.json`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/operator_checkpoint.active.json`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/pending_decisions.json`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/runtime/h_plane.audit.json`

Representative L3 iteration files:

- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/L3/runs/2026-04-09-024330-bootstrap/iterations/iteration-001/plan.md`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/L3/runs/2026-04-09-024330-bootstrap/iterations/iteration-001/l4_return.md`
- `research/knowledge-hub/topics/jcp-qsgw-revision-ri-v-vs-lri-and-molecular-pulay-aux-basis-tests/L3/runs/2026-04-09-024330-bootstrap/iterations/iteration-001/l3_synthesis.md`

Relevant implementation files:

- `research/knowledge-hub/knowledge_hub/aitp_codex.py`
- `research/knowledge-hub/knowledge_hub/popup_support.py`
- `research/knowledge-hub/knowledge_hub/aitp_service.py`
- `research/knowledge-hub/knowledge_hub/aitp_cli.py`

## Issue 1: No real operator checkpoint was raised after L3 plan refinement

### Expected behavior

After a topic transitions from vague continuation to an execution-relevant plan, AITP should be able to raise a human checkpoint when the next route has non-obvious consequences.

Examples:

- choosing which molecule should be the reviewer-facing Pulay-recovery example
- choosing whether to prioritize numerical reruns or reviewer-response wording first
- choosing whether to treat an apparent improvement as a positive benchmark or only as a bounded negative or partial result

### Observed behavior

The topic updated its contracts and next-action surfaces, but no active checkpoint was materialized.

Observed files showed:

- `operator_checkpoint.active.json`
  - `status = "cancelled"`
  - `active = false`
- `pending_decisions.json`
  - `pending_count = 0`
- `h_plane.audit.json`
  - checkpoint status remained cancelled

So the system did not fail to display an existing checkpoint. It failed to create one.

### Likely root cause

The current transition logic is too permissive around contract-sync and route-shaping steps. It treats them as safe continuation work rather than as moments that can require explicit operator confirmation.

### Impact

The operator experience feels flatter than intended. The user expects "AITP noticed this is a real branching point and asked me," but the system instead silently keeps going.

## Issue 2: Codex front door does not convert popup payloads into a native interactive prompt

### Expected behavior

If a popup-worthy state exists, the Codex-facing path should surface it as a native interactive question instead of only printing markdown or requiring manual CLI resolution.

### Observed behavior

Popup support exists in the kernel, but the Codex front door does not consume it.

Evidence:

- `popup_support.py` contains:
  - popup detection
  - popup payload construction
  - markdown rendering
  - `build_ask_user_question_payload(...)`
- `aitp_service.py::topic_popup(...)` returns:
  - `popup`
  - `markdown`
  - `ask_user_question`

However:

- `aitp_codex.py` does not call `topic_popup(...)` before continuing deeper execution.
- `aitp_codex.py` does not inspect or forward `ask_user_question`.
- `aitp_cli.py` blocks on popup gates by printing markdown and a manual resolution hint:
  - `Resolve with: aitp popup --topic-slug ... --choice <index>`

So the popup pipeline exists in the service layer, but the Codex front door does not wire it into a user-visible interaction.

### Impact

The user experience in Codex is weaker than in the intended design:

- AITP can know that a human gate exists.
- But Codex does not automatically present it as a proper interactive question.

This makes the operator feel like they must manually inspect internal state instead of being naturally asked.

## Issue 3: L3-L4 iteration shells are materialized even when no real L4 return exists

### Expected behavior

If an iteration is created, either:

- a real L4 return should be materialized, or
- the iteration state should clearly say it is a plan-only shell and not a completed L3-L4 loop.

### Observed behavior

The iteration files exist:

- `plan.md`
- `l4_return.md`
- `l3_synthesis.md`

But in the observed run:

- `l4_return.md` stayed `pending`
- `l3_synthesis.md` stayed `pending_l4_return`
- no durable `returned_execution_result.json` was present for that run

This produces a half-realized loop:

- the iteration file structure exists
- but the scientific return artifact does not

### Impact

The filesystem suggests that a full L3-L4-L3 cycle happened, but in reality only the shell was materialized. This is confusing during audit and handoff.

## Issue 4: Derived runtime surfaces can lag behind updated contracts

### Expected behavior

After contract or steering updates, the main human-facing surfaces should refresh consistently:

- `topic_dashboard.md`
- `topic_state.json`
- `next_action_decision.*`
- `topic_synopsis.*`

### Observed behavior

After the new reviewer-facing direction was written, some surfaces updated immediately while others still carried older summaries such as:

- old `pending_actions`
- old "first validation route"
- older route summaries in human-facing notes

This was partially repairable by targeted edits and by rerunning status or next, but the refresh was not atomic.

### Impact

During live use, the user can see mixed state:

- one file says the topic is now about Pulay recovery, AC sensitivity, and periodic LRI clarification
- another still says the next step is "Convert the topic statement into explicit source and candidate artifacts"

That weakens trust in the runtime surfaces.

## Issue 5: Steering-direction truncation in auto-generated direction text

### Expected behavior

A long but explicit user direction should survive durable steering in a faithful way.

### Observed behavior

The raw operator request was preserved, but the auto-generated parsed direction in:

- `innovation_direction.md`
- `control_note.md`

initially lost the third clause about the periodic-system LRI clarification and the 2021 PRM benchmark anchor.

The missing intent could still be recovered from:

- the raw operator request
- the steering summary

but the compact direction text itself was incomplete.

### Impact

This is not a total loss of state, but it weakens the reliability of auto-generated direction summaries for long, compound requests.

## What worked well

To keep the diagnosis honest, several parts did work:

- Codex front-door install was repairable and reached `aitp doctor -> Overall: clean`
- current-topic routing was successfully restored to the correct QSGW topic
- required-read gating worked
- contract and next-action rewriting was possible once the right files were edited
- the runtime did preserve enough state for recovery rather than losing the topic completely

## Most important fixes, in order

### Fix 1: checkpoint semantics after L3 planning

Introduce a rule that can automatically materialize an operator checkpoint after plan refinement when:

- the selected action is not auto-runnable
- multiple execution routes remain genuinely open
- the next step changes evidence interpretation or reviewer-facing framing

This is the most important user-facing repair.

### Fix 2: wire popup payloads into Codex front door

Extend `aitp_codex.py` so that, before deeper continuation:

1. it calls `topic_popup(...)`
2. if `needs_popup == true`, it consumes `ask_user_question`
3. it surfaces a real interactive prompt to the Codex user instead of only a markdown box or CLI hint

The service layer already exposes most of the required payload.

### Fix 3: distinguish plan shell from completed loop

When L3 iteration files are created without a real L4 execution return, the iteration should declare that explicitly as a shell or pre-return state, rather than looking like a completed but empty loop.

### Fix 4: stronger surface refresh after contract rewrite

Contract rewrites should invalidate and rebuild all dependent summaries in one pass, especially:

- `topic_dashboard.md`
- `topic_state.json`
- `topic_synopsis.*`
- `validation_review_bundle.*`

### Fix 5: safer steering parsing for long compound requests

Long directions with multiple clauses should either:

- preserve the whole operator request in the compact direction field, or
- split it into a structured list instead of truncating after the first two clauses

## Suggested acceptance tests

The following tests should be added or tightened.

### Popup and checkpoint tests

- A Codex topic with a requested checkpoint should cause the front door to surface an interactive question, not only a printed markdown popup.
- A post-plan route ambiguity should create an operator checkpoint artifact instead of silently continuing.

### L3-L4 materialization tests

- If no `returned_execution_result` exists, `l4_return` should be labeled as shell-only or pre-return.
- `l3_synthesis` should not look like a completed summary when no L4 return artifact exists.

### Contract-refresh tests

- After steering updates the research question, all dependent summaries should reflect the new selected action in the same orchestration pass.

### Steering-parsing tests

- A three-clause direction request should preserve all clauses in durable steering state.

## Practical recommendation for next implementation pass

Do not start by changing all of L3-L4 orchestration at once.

A safer sequence is:

1. implement popup consumption in the Codex front door
2. add one concrete post-plan checkpoint trigger
3. only then refine the deeper L3-L4 return semantics

This should improve user trust quickly without destabilizing the rest of the runtime.
