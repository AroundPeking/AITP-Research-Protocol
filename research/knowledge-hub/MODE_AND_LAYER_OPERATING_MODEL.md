# Mode and layer operating model

Status: implementation-grounded reference

This file is the shortest unified explanation of how AITP currently combines:

- task type,
- lane / research mode,
- runtime mode,
- macro layers,
- `L3` subplanes,
- and transition/backedge posture.

It is intentionally grounded in the current implementation, not only in the
architecture freeze prose.

## 1. Why this file exists

AITP now exposes several different control axes.
They are related, but they are not interchangeable.

The most common source of confusion is assuming that:

- `task_type` is the same as `runtime_mode`, or
- `resume_stage` is the same as the current `L3` subplane, or
- the layer map alone explains which runtime mode will be selected.

That is not how the current implementation works.

## 2. The six active axes

### 2.1 Task type

Examples:

- `open_exploration`
- `conjecture_attempt`
- `target_driven_execution`

Current role:

- semantic framing for the topic and control plane
- visible in the runtime control-plane projection
- useful for human interpretation and future template selection

Current implementation note:

- `task_type` is propagated into `control_plane.task_type`
- it is not currently the primary switch that selects `runtime_mode`

Actual sources:

- `topic_state.task_type`
- `topic_synopsis.task_type`
- `runtime_focus.task_type`
- assembled by `knowledge_hub/control_plane_support.py`

### 2.2 Lane / research mode

Examples:

- `toy_model`
- `toy_numeric`
- `formal_derivation`

Current role:

- names the research lane or discipline-specific working posture
- shapes topic synopsis and downstream formal-theory expectations

Current implementation note:

- lane is exposed through `topic_synopsis.lane` and `control_plane.lane`
- `research_mode` is preserved as a topic-level axis, not collapsed into runtime mode

### 2.3 Runtime mode

Current values:

- `discussion`
- `explore`
- `verify`
- `promote`

Current role:

- primary execution-mode classifier for the progressive-disclosure runtime bundle
- controls foreground layers, allowed backedges, required writeback, and
  transition posture

Actual implementation source:

- `knowledge_hub/mode_envelope_support.py`

Current derivation rule:

- `discussion` when idea clarification or an active operator checkpoint is blocking
- `promote` when the selected action is explicitly promotion/writeback facing
- `verify` when the topic is in `L4`, the selected action is validation-heavy,
  or explicit verification triggers are active
- otherwise `explore`

### 2.4 Current macro layer

Current values:

- `L0`
- `L1`
- `L2`
- `L3`
- `L4`

Current role:

- the top-level epistemic stage for the topic
- still read from durable topic/runtime state first

Actual implementation source:

- `topic_state.resume_stage`
- `topic_state.last_materialized_stage`
- derived in `knowledge_hub/layer_graph_support.py`

### 2.5 `L3` subplane

Current values:

- `L3-A` analysis
- `L3-R` result integration
- `L3-D` distillation preparation

Current role:

- refine the overloaded `L3` macro layer into operationally distinct nodes

Actual implementation source:

- inferred in `knowledge_hub/layer_graph_support.py`
- materialized as `runtime/topics/<topic_slug>/layer_graph.generated.json|md`

Current inference rule:

- `L3-A` for normal candidate shaping / route comparison
- `L3-R` when `L4` has already returned evidence and the topic is integrating that return
- `L3-D` when the promotion/distillation boundary is active

### 2.6 Transition posture

Current values:

- `boundary_hold`
- `backedge_transition`
- `forward_transition`

Current role:

- says whether the current bounded work should remain local, backedge to an
  earlier surface, or move across the `L4 -> L2` boundary

Actual implementation source:

- derived in `knowledge_hub/mode_envelope_support.py`
- consumed in queue shaping by:
  - `runtime/scripts/decide_next_action.py`
  - `runtime/scripts/orchestrator_contract_support.py`

Current derivation rule:

- `forward_transition` for active promotion intent
- `backedge_transition` for non-trivial consultation, capability-gap blocker,
  or contradiction-driven recovery
- otherwise `boundary_hold`

## 3. What actually drives runtime behavior

In the current AITP implementation, the main runtime-driving bundle is:

1. `runtime_mode`
2. `active_submode`
3. `mode_envelope`
4. `transition_posture`

This is the machine-readable control contract exported by:

- `runtime/topics/<topic_slug>/runtime_protocol.generated.json`
- schema: `runtime/schemas/progressive-disclosure-runtime-bundle.schema.json`

The practical consequence is:

- `task_type` is visible and important
- but `runtime_mode + transition_posture` is the stronger operational switch

## 4. The current mode envelopes

As currently implemented in `knowledge_hub/mode_envelope_support.py`:

### `discussion`

- foreground layers: `L0`, `L1`, `L3`
- allowed backedges: `L1 -> L0`, `L1/L3 -> L2`
- required writeback:
  - `idea_packet`
  - `operator_checkpoint`
  - `research_question_contract`

### `explore`

- foreground layers: `L1`, `L3`
- allowed backedges: `L3 -> L0`, `L3 -> L2`
- required writeback:
  - `candidate_packets`
  - `route_choice_notes`
  - `source_recovery_notes`

### `verify`

- foreground layers: `L4`
- allowed backedges: `L4 -> L0`, `L4 -> L2`
- required writeback:
  - `validation_result_artifacts`
  - `contradiction_artifacts`
  - `decision_or_route_updates`

### `promote`

- foreground layers: `L4`, `L2`
- allowed backedges: `promote -> L4`, `promote -> L0`, `promote -> L2`
- required writeback:
  - `promotion_gate`
  - `promotion_decision`
  - `backend_receipt`

## 5. The actual cross-layer relationship

The current implementation plus protocol docs together say:

- main normative route: `L0 -> L1 -> L3 -> L4 -> L2`
- bounded low-risk shortcut: `L0 -> L1 -> L2`
- `L2` is also a consultation surface during `L1`, `L3`, and `L4`
- `L4` does not write directly into reusable memory without the `L3-R` return law

The most implementation-grounded form of that rule lives in:

- `knowledge_hub/layer_graph_support.py`

Current encoded edges are:

- `L0 -> L1`
- `L1 -> L0`
- `L1 -> L3-A`
- `L3-A -> L4`
- `L3-A -> L0`
- `L3-A -> L2` consultation
- `L4 -> L3-R` mandatory return
- `L4 -> L0`
- `L4 -> L2` consultation
- `L3-R -> L3-D`
- `L3-R -> L4`
- `L3-R -> L0`
- `L3-R -> L2` consultation
- `L3-D -> L2` distillation boundary
- `L3-D -> L4`
- `L3-D -> L0`
- `L2 -> L3-A` reuse return

So the current real model is:

- macro layers for epistemic placement
- `L3` subplanes for iterative middle-loop routing
- `runtime_mode` for operational envelope selection
- `transition_posture` for backedge/forward boundary behavior

## 6. What is genuinely implemented versus descriptive

### Implemented and machine-readable

- `runtime_mode`
- `active_submode`
- `mode_envelope`
- `transition_posture`
- `control_plane`
- `h_plane`
- `layer_graph`
- `L4 -> L3-R` mandatory return law

### Implemented but mostly descriptive

- `task_type`
- `lane`
- `research_mode`

These are real fields and do appear in runtime surfaces, but today they are
more explanatory than decisive.

### Not yet unified into one frozen switchboard

- task-type-driven runtime-mode selection
- one single public table that deterministically maps every task type and lane
  to one runtime mode
- a fully frozen orchestration template library for all task-type × lane pairs

## 7. Known drift and honesty notes

### Drift 1: `ROUTING_POLICY.md` still carries an old `L0` note

`ROUTING_POLICY.md` still says that `L0` is "not yet independently formalized".

That sentence is behind the current implementation and public layer map.
Today AITP already has:

- `research/knowledge-hub/source-layer/`
- `LAYER_MAP.md` treating that directory as the formal `L0` root
- runtime and acceptance flows that read and write `source-layer/...`

So the real state is:

- `L0` is implemented as a formal layer root
- the old note is documentation drift, not current truth

### Drift 2: task type is not the main runtime selector yet

The architecture and backlog correctly treat task type as important.
But the current runtime chooser does not primarily branch on task type.

Today the actual chooser branches on:

- idea-packet clarification state
- operator-checkpoint state
- selected action type
- selected action summary
- escalation trigger set

That is honest and implemented, but it means task type is not yet the master
control axis many readers might expect.

## 8. How to inspect a live topic

If you want to know what AITP is really doing on a real topic, inspect in this order:

1. `runtime/topics/<topic_slug>/topic_dashboard.md`
2. `runtime/topics/<topic_slug>/runtime_protocol.generated.json`
3. `runtime/topics/<topic_slug>/layer_graph.generated.md`
4. `runtime/topics/<topic_slug>/research_question.contract.md`
5. `runtime/topics/<topic_slug>/validation_review_bundle.active.md`

Interpret them like this:

- `control_plane.task_type` tells you the declared topic framing
- `control_plane.lane` / `research_mode` tells you the lane
- `control_plane.layer` tells you the current macro layer
- `runtime_mode` tells you the active operational envelope
- `transition_posture` tells you whether AITP should hold, backedge, or push a boundary
- `layer_graph.current_node_id` tells you where inside the iterative graph the topic currently sits

## 9. One-line summary

The real AITP operating model is not "one mode plus one layer".

It is:

- task type for semantic framing,
- lane/research mode for disciplinary posture,
- runtime mode for execution envelope,
- layer/subplane for epistemic placement,
- and transition posture for route change law.
