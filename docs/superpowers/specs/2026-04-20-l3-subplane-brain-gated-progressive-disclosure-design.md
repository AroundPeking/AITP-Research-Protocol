# L3 Subplane Brain-Gated Progressive Disclosure Design

## Goal

Make `brain` the executable protocol kernel for `L3` so AITP can enforce the
top-level architecture instead of merely hinting at it through large skills.

This design introduces three linked changes:

1. `brain` explicitly manages `L3-I -> L3-P -> L3-A -> L3-R -> L3-D` as real
   subplane states.
2. each `L3` subplane must leave a Markdown-first required artifact before the
   topic may advance.
3. skills become bounded micro-skills injected through progressive disclosure,
   so the agent reads only the slice required for the current subplane and
   trigger surface.

## Problem

The current v2 direction correctly simplifies the public workflow, but it still
leaves a key protocol gap inside `L3`.

Current pain points:

- `L3` is described as five sub-planes in protocol docs, but the minimal v2
  surface still collapses them into a coarse derive/validate/promotion flow.
- the agent is told what good behavior looks like, but `brain` does not yet
  gate advancement using durable subplane artifacts.
- session continuity can tell an agent which large skill to read, but it cannot
  reliably answer:
  - which `L3` subplane the topic is currently in,
  - which required artifact is missing,
  - what exact work is allowed now,
  - what deeper protocol slices become mandatory when risk rises.
- the current skill shape is too broad for honest context control: one skill
  tends to include both immediate instructions and edge-case governance.

This weakens conformance to the Charter's "durable artifact" rule and makes it
too easy for an agent to advance because its prose sounds plausible rather than
because protocol gates were actually satisfied.

## Approved Direction

Adopt a hard-gated `L3` subplane model:

- `brain` is the authority on current `L3` subplane position and gate status.
- each subplane has a required Markdown artifact contract.
- advancement is blocked until the artifact exists and satisfies minimal
  structure checks.
- the agent receives a small current-step brief plus one micro-skill, not one
  monolithic mode skill.
- deeper protocol material is disclosed only when trigger conditions fire.

Short form:

- protocol state lives in `brain`
- research judgment stays in durable Markdown artifacts
- skills become current-step operating instructions
- progressive disclosure controls protocol depth, not protocol force

## Core Model

### 1. `brain` owns `L3` subplane state

For any topic in `L3`, `brain` must expose at least:

- `layer: L3`
- `l3_subplane: ideation | planning | analysis | result_integration | distillation`
- `gate_status: ready | blocked_missing_artifact | blocked_missing_field | blocked_trigger_read | blocked_human_decision`
- `required_artifact_kind`
- `required_artifact_path`
- `next_allowed_transition`
- `backedge_options`

This state is protocol truth for the agent. The agent does not infer its own
subplane from intuition alone.

### 2. `L3` progression uses hard gates

The required progression is:

```text
L3-I -> L3-P -> L3-A -> L3-R -> L3-D
```

The default rule is strict:

- no skipping subplanes,
- no direct `L3-I -> L3-A`,
- no direct `L3-A -> L3-D`,
- no promotion routing from `L3-A` without `L3-R` and `L3-D`.

Backward transitions are allowed, but they must be explicit and durable:

- `L3-P -> L3-I` when the plan target is underspecified,
- `L3-A -> L3-P` when the plan is underconstrained,
- `L3-R -> L3-A` when validation requires revision,
- `L3-D -> L3-A` when distillation reveals a claim-boundary problem.

Every backedge must record a reason in the active subplane artifact or an
associated transition receipt.

### 3. Required artifacts are Markdown-first forms

The human authority for each `L3` subplane is one Markdown artifact with:

1. YAML frontmatter for stable fields,
2. fixed required headings,
3. optional freeform notes in explicitly non-authoritative sections.

`brain` may generate machine-readable indexes or summaries, but those are
derived companions. The gate checks the Markdown truth surface.

## `L3` Required Artifact Contracts

Recommended per-topic layout:

```text
topics/<topic_slug>/L3/
  ideation/
    active_idea.md
  planning/
    active_plan.md
  analysis/
    active_analysis.md
  result_integration/
    active_integration.md
  distillation/
    active_distillation.md
  transitions/
    l3_transition_log.md
```

One active artifact per subplane keeps the current execution surface legible.
Historical snapshots may later be copied into `history/` or versioned by run id,
but the gate should have one canonical current file to inspect.

### `L3-I` ideation artifact

Path:

- `topics/<topic_slug>/L3/ideation/active_idea.md`

Required frontmatter:

- `artifact_kind: l3_ideation`
- `topic_slug`
- `l3_subplane: ideation`
- `status`
- `question_focus`
- `idea_id`
- `updated_at`

Required sections:

- `## Current Question`
- `## Observation Or Prompt`
- `## Candidate Directions`
- `## Existing Knowledge Touchpoints`
- `## Why This Is Worth Pursuing`
- `## Exit Criteria`

Gate to enter `L3-P`:

- at least one bounded direction is named,
- the question focus is explicit,
- related `L0`/`L1`/`L2` touchpoints are named,
- exit criteria describe what would count as a plan-ready direction.

### `L3-P` planning artifact

Path:

- `topics/<topic_slug>/L3/planning/active_plan.md`

Required frontmatter:

- `artifact_kind: l3_plan`
- `topic_slug`
- `l3_subplane: planning`
- `plan_id`
- `target_claim_scope`
- `required_inputs`
- `updated_at`

Required sections:

- `## Plan Objective`
- `## Inputs And Dependencies`
- `## Planned Steps`
- `## Tool Or Capability Needs`
- `## Validation Preview`
- `## Stop Conditions`

Gate to enter `L3-A`:

- the objective is bounded,
- required inputs are named,
- at least one concrete step sequence exists,
- capability needs are explicit,
- stop conditions forbid open-ended wandering.

### `L3-A` analysis artifact

Path:

- `topics/<topic_slug>/L3/analysis/active_analysis.md`

Required frontmatter:

- `artifact_kind: l3_analysis`
- `topic_slug`
- `l3_subplane: analysis`
- `analysis_id`
- `plan_id`
- `analysis_kind`
- `updated_at`

Required sections:

- `## Starting Point`
- `## Steps Taken`
- `## Assumptions`
- `## Approximations And Regime`
- `## Notation And Conventions`
- `## Intermediate Results`
- `## Failures And Unresolved Gaps`
- `## Candidate Output`

Gate to enter `L3-R`:

- the work references its originating plan,
- assumptions are explicit,
- approximations and regime limits are explicit,
- failures are preserved rather than omitted,
- there is a bounded output to interpret.

### `L3-R` result integration artifact

Path:

- `topics/<topic_slug>/L3/result_integration/active_integration.md`

Required frontmatter:

- `artifact_kind: l3_result_integration`
- `topic_slug`
- `l3_subplane: result_integration`
- `integration_id`
- `analysis_id`
- `validation_state`
- `updated_at`

Required sections:

- `## Returned Evidence`
- `## What Passed`
- `## What Failed`
- `## Contradictions Or Tensions`
- `## Decision`
- `## Required Backedge Or Forward Path`

Gate to enter `L3-D`:

- returned evidence is summarized,
- failures and contradictions remain visible,
- a bounded integration decision is made,
- the decision explicitly states forward vs backedge route.

### `L3-D` distillation artifact

Path:

- `topics/<topic_slug>/L3/distillation/active_distillation.md`

Required frontmatter:

- `artifact_kind: l3_distillation`
- `topic_slug`
- `l3_subplane: distillation`
- `distillation_id`
- `claim_scope`
- `promotion_readiness`
- `updated_at`

Required sections:

- `## Distilled Claim`
- `## Evidence Summary`
- `## Scope Limits`
- `## Reuse Suitability`
- `## Remaining Risks`
- `## Promotion Recommendation`

Gate to exit toward promotion:

- the claim is bounded,
- evidence is summarized without hiding limits,
- reuse suitability is explicit,
- remaining risks are explicit,
- promotion recommendation is recorded as a durable judgment artifact.

## Micro-Skill Model

Replace the coarse `skill-derive` style with micro-skills aligned to the active
subplane:

- `skill-l3-ideate`
- `skill-l3-plan`
- `skill-l3-analyze`
- `skill-l3-integrate`
- `skill-l3-distill`

Role of each micro-skill:

- tell the agent what to do now,
- remind it which artifact it must update,
- name the current gate and transition rule,
- point to deeper reads when a trigger fires.

Micro-skills should not restate the entire protocol tree. They are operating
instructions for one bounded state.

## Progressive Disclosure Model

`brain` should emit an `L3` execution brief with four tiers consistent with the
existing progressive disclosure protocol.

### Tier 1: minimal execution brief

Always include:

- current subplane,
- current gate status,
- required artifact path,
- immediate allowed work,
- immediate blocked work,
- next micro-skill,
- exact deeper file paths when relevant.

Example shape:

```text
Current subplane: L3-P
Gate status: blocked_missing_field
Required artifact: topics/demo/L3/planning/active_plan.md
Missing: Tool Or Capability Needs
Allowed now: refine the active plan artifact
Blocked now: analysis, candidate submission, promotion
Inject: skill-l3-plan
```

### Tier 2: trigger rules

Stable triggers for `L3` should include at least:

- `promotion_intent`
- `contradiction_detected`
- `notation_lock_required`
- `capability_gap_blocker`
- `trust_missing`
- `verification_route_selection`

### Tier 3: protocol slice

When a trigger fires, `brain` attaches only the relevant slice:

- promotion slice,
- contradiction slice,
- notation/convention slice,
- capability slice,
- validation route slice.

### Tier 4: full governance

Full protocol remains available for audits and disputes, but it is not injected
by default into the active step bundle.

## `brain` Responsibilities

`brain` should now do five protocol-kernel jobs for `L3`:

1. resolve the current active `L3` subplane,
2. validate the required Markdown artifact structure,
3. decide whether the current transition is blocked or allowed,
4. select the micro-skill for the current state,
5. attach deeper protocol slices only when triggers fire.

`brain` should not decide:

- whether the physics is correct,
- whether a proof is truly complete,
- whether weak evidence is scientifically sufficient,
- whether a claim deserves promotion despite unresolved scope.

Those remain research judgments recorded in the artifacts and checked through
the proper validation and human-gate surfaces.

## Proposed Tool Surface Changes

Minimal direction:

- keep `aitp_get_status`, but extend it to include `l3_subplane`,
  `gate_status`, `required_artifact_path`, and `missing_requirements`.
- add `aitp_get_execution_brief(topic_slug)` to return the progressive current
  step bundle.
- add `aitp_check_l3_gate(topic_slug)` to evaluate the active subplane artifact.
- add `aitp_advance_l3_subplane(topic_slug)` to move only when gate checks pass.
- add `aitp_record_l3_transition(topic_slug, from_subplane, to_subplane, reason)`
  to preserve forward and backward moves.

Optional later additions:

- `aitp_get_protocol_slice(topic_slug, trigger_name)`
- `aitp_list_missing_fields(topic_slug, artifact_kind)`

The key point is that advancement should stop being a free-form status edit and
become a checked transition.

## Relationship To Existing Protocol Surface

This design does not replace the top-level `L3` protocol. It operationalizes it.

It keeps:

- the five-subplane `L3` architecture,
- the progressive disclosure model,
- the Charter requirement that meaningful research steps leave durable artifacts.

It changes:

- who is authoritative about current `L3` state,
- how advancement is gated,
- how much of the protocol is injected at once,
- how narrowly skills are scoped.

## Error Handling

When the active artifact is missing or incomplete:

- `brain` must return `blocked_missing_artifact` or `blocked_missing_field`,
- the brief must list the exact missing file or section,
- the agent must be blocked from advancing further.

When contradiction or notation tension appears:

- `brain` must keep the topic in the current or previous safe subplane,
- fire the relevant trigger,
- attach the deeper required reads,
- prevent silent forward progress.

When human input is required:

- `brain` must return `blocked_human_decision`,
- expose the durable decision artifact path,
- block promotion or other high-impact transitions until resolved.

## Testing Strategy

Add protocol-level tests for:

- subplane inference from topic state and active artifacts,
- gate failure when required files are missing,
- gate failure when required sections are absent,
- successful forward transition only after gate satisfaction,
- explicit backedge transition recording,
- progressive execution brief selection per subplane,
- trigger-driven deeper slice attachment,
- prevention of direct `L3-A -> L3-D` and similar skips.

Add integration tests for:

- resume after session restart into the correct `L3` subplane,
- blocked `L3` topics reporting exact missing fields,
- micro-skill selection matching current subplane,
- promotion surfaces remaining unavailable until `L3-D` is complete.

## Risks

### 1. Overloading `brain`

If `brain` starts deciding scientific maturity rather than validating contract
shape and transition legality, the design will drift back into hidden heuristics.

Mitigation:

- keep `brain` limited to state, gate, trigger, and disclosure decisions.

### 2. Markdown drift

If subplane artifacts become free-form notes, gate checks become subjective.

Mitigation:

- fixed headings,
- required frontmatter keys,
- structure validation in `brain`.

### 3. Too many micro-skills

If every tiny edge case becomes its own skill, the system becomes harder to
maintain than the problem it solves.

Mitigation:

- one skill per subplane,
- deeper protocol slices for triggers,
- no separate skills for every error case.

### 4. Historical clutter

If every revision produces a new top-level artifact without a current/archived
distinction, the agent may not know which file is authoritative.

Mitigation:

- one canonical active artifact path per subplane,
- optional archived snapshots in a separate history area later.

## Recommended Implementation Order

1. freeze the `L3` subplane artifact contract in protocol docs,
2. teach `brain` to report `l3_subplane` and `gate_status`,
3. add gate checks for artifact existence and required sections,
4. add execution-brief generation,
5. split coarse `L3` skills into subplane micro-skills,
6. add trigger-driven protocol-slice attachment,
7. wire resume/session continuity to the new subplane-aware brief.

## Success Criteria

This design is successful when:

- an `L3` topic always has one explicit current subplane,
- the agent cannot advance without the required Markdown artifact,
- the brief tells the agent exactly what is missing,
- skills are scoped to the current subplane rather than the whole workflow,
- deeper reads are attached by trigger instead of always-on dumping,
- session resume restores the current `L3` subplane and gate status correctly.

## One-Line Memory

`brain` runs the `L3` state machine, Markdown artifacts are the gates, and
micro-skills are the bounded instructions for the current subplane only.
