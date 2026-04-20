# AITP Physicist-Centered L1-L5 Research Flow Design

## Goal

Make AITP run like a disciplined theoretical-physics research workspace rather
than a collection of partially connected protocol fragments.

This design defines one umbrella contract for `L1-L5` from the perspective of
how a real theorist actually works:

1. read and compare sources,
2. bound the question and lock conventions,
3. derive or compute something explicit,
4. test it against known structure,
5. decide what survives as reusable knowledge,
6. write it clearly with provenance and caveats.

The result should make `brain` responsible for protocol progression while
keeping scientific judgment visible in durable artifacts rather than hidden in
Python heuristics.

## Problem

AITP already has strong ingredients:

- the Charter and SPEC keep evidence and promotion discipline explicit,
- `L1`, `L2`, `L3`, `L4`, and `L5` all have partial protocol surfaces,
- `L3` already has a five-subplane concept,
- progressive disclosure already exists as a runtime principle,
- `L2` already has real canonical families and retrieval surfaces.

But the current system still lacks one unified statement of how a real research
topic should move from provisional reading to validated, reusable, written
output.

Current problems:

- the layers exist, but the day-to-day research flow still feels fragmented,
- old mode ideas are still useful, but they are not yet cleanly separated from
  layer/state authority,
- `L1` still behaves too much like generic intake rather than a physicist's
  source-basis and notation-framing stage,
- `L4` still describes validation in abstract terms more often than as a real
  theoretical-physics adjudication notebook,
- `L5` still looks like a generic writing layer rather than a paper-building
  surface with equation and evidence provenance,
- `brain` still lacks one umbrella rule for what the current topic is doing
  across `L1-L5`.

The missing piece is not another local patch.
The missing piece is a unified research-flow spec.

## Approaches Considered

### Approach A: one umbrella spec with layers as hard stages and modes as posture

Keep `L1-L5` as the authoritative research-state machine.
Retain mode-like behavior, but demote it into a second axis that controls
context loading and operating style rather than truth status.

Pros:

- best fit to the Charter and existing layer model,
- easiest way to make `brain` genuinely executable,
- maps cleanly to real theoretical-physics work,
- keeps old mode ideas without letting them override epistemic state.

Cons:

- requires a clearer distinction between state, posture, and trigger,
- touches several existing protocol assumptions at once.

### Approach B: keep old mode system as the primary driver

Continue to treat modes as the main runtime state, then let layers appear as
supporting classifications underneath.

Pros:

- smaller conceptual migration from older brain designs,
- easier short-term compatibility with some acceptance surfaces.

Cons:

- too easy to mix scientific state with operating style,
- encourages "mode sounds right" over "artifact gate is satisfied,"
- weak fit for hard layer progression.

### Approach C: write five independent layer plans

Plan `L1`, `L2`, `L3`, `L4`, and `L5` separately without one umbrella model.

Pros:

- smallest local scope per document,
- easy to parallelize later.

Cons:

- high drift risk,
- weak answer to "how does a topic actually move end to end?",
- reproduces the existing fragmentation problem.

## Chosen Approach

Choose **Approach A**.

The right top-level design is:

- layers are the hard research-state machine,
- postures are the operating stance,
- lanes stay orthogonal,
- triggers control deeper protocol loading,
- and `brain` becomes the protocol kernel that checks advancement rather than a
  thin status echoer.

## Real-Research Spine

A realistic theoretical-physics workflow repeatedly answers six questions:

1. What is the exact bounded question, regime, and target object?
2. Which sources, assumptions, and notation choices define the starting basis?
3. What derivation, reconstruction, computation, or comparison is being done?
4. Which known constraints could falsify or narrow the result?
5. What survives as reusable knowledge beyond this one run?
6. What is honest to state in a paper or report, and with what caveats?

AITP should therefore look less like:

- "which generic runtime mode am I in?"

and more like:

- "which research stage am I in, what artifact is missing, what is the next
  honest scientific move?"

## Core Design

### 1. First axis: hard research stage

The authoritative stage progression remains:

```text
L0 -> L1 -> L3 -> L4 -> L2 -> L5
```

Where:

- `L0` is the source substrate and remains a prerequisite plane,
- `L1` is source-grounded framing and notation discipline,
- `L3` is the exploratory and derivational workspace,
- `L4` is adjudication,
- `L2` is reusable promoted memory,
- `L5` is communication and publication.

The key rule is:

- a topic advances because required artifacts exist and gates are satisfied,
- not because a mode label sounds plausible.

### 2. Second axis: operating posture

Retain the useful intent of old brain modes, but rename and relocate them as
operating postures:

- `read`
- `frame`
- `derive`
- `verify`
- `distill`
- `write`

These postures answer:

- what context is mandatory now,
- what should remain deferred,
- how the current step should be phrased,
- which triggers should force deeper protocol reads.

They do **not** decide:

- whether the topic may advance to the next layer,
- whether a claim is reusable,
- whether promotion is justified,
- whether validation is complete.

### 3. Third axis: lane

Retain lane as an orthogonal axis:

- `formal_theory`
- `toy_numeric`
- `code_method`
- future reserved: `theory_synthesis`

Lane changes the shape of required checks, not the layer meaning.

### 4. `brain` becomes the protocol kernel

`brain` should now own:

- current stage resolution,
- current posture resolution,
- current lane resolution,
- required artifact checks,
- gate status,
- trigger emission,
- execution-brief generation,
- backedge recording.

`brain` should **not** own:

- scientific truth judgments,
- proof-completeness judgments,
- hidden promotion shortcuts,
- silent weakening of validation criteria.

## Mapping Old Modes Into The New Model

The old brain-layer preset modes still have value, but only after being
reinterpreted.

### Older four-mode family

- `discussion` -> mostly `read` or `frame`
- `explore` -> `frame` plus early `derive`
- `verify` -> `verify`
- `promote` -> `distill` plus the `L4 -> L2` gate boundary

### Current three-mode family

- `explore` -> `read`, `frame`, and bounded early `derive`
- `learn` -> `read`, `frame`, `derive`, `verify` with source-reconstruction bias
- `implement` -> `derive`, `verify`, `distill` with novelty bias

This is the correct migration rule:

- keep the good intuition from old modes,
- stop using them as the top-level research-state machine.

## Recommended Topic Layout

```text
topics/<topic_slug>/
  state.md
  L1/
    question_contract.md
    source_basis.md
    convention_snapshot.md
    derivation_anchor_map.md
    contradiction_register.md
  L3/
    ideation/
    planning/
    analysis/
    result_integration/
    distillation/
    transitions/
  L4/
    validation_contract.md
    reviews/
    execution/
    gaps/
  L5_writing/
    outline.md
    claim_evidence_map.md
    equation_provenance.md
    figure_provenance.md
    limitations.md
    draft.tex
    references.bib
    figures/
    tables/
```

Global reusable memory remains outside the topic root in canonical `L2`.

## Knowledge-Base Operating Model

AITP should absorb the useful parts of an `LLM wiki` workflow, but reinterpret
them for disciplined theoretical-physics research instead of generic note
taking.

### Three-layer knowledge-base model

The right translation is:

- `raw sources` -> `L0` plus immutable source-linked execution artifacts
- `wiki` -> layered human-readable research surfaces across `L1`, `L3`, `L4`,
  and `L2`
- `schema` -> Charter, SPEC, protocols, artifact templates, and gate rules

The key AITP rule is:

- the system may use a wiki-like workflow,
- but it may not collapse source-grounded, derived, validated, and promoted
  content into one undifferentiated layer.

### Theoretical-physicist interpretation

A real theorist does not only want a bag of facts.
They need a knowledge workspace that answers:

- where did this equation or claim come from?
- which conventions and regime does it assume?
- what reconstruction or comparison produced it?
- what objections or failed routes remain?
- what is reusable across topics, and what is only locally provisional?

So the AITP knowledge base should behave less like:

- a general-purpose wiki of summaries

and more like:

- a layered research archive with source traces, derivation notebooks,
  adjudication records, reusable memory, and writing outputs.

### Core operations: ingest, query, lint

AITP should expose three first-class knowledge-base operations:

#### `ingest`

Bring new material into the research system without pretending it is already
understood.

Typical `ingest` outputs:

- `L0` source records,
- `L1` source-basis updates,
- new source anchors,
- updated contradiction and notation registers.

#### `query`

Answer a bounded scientific question against the layered knowledge base.

The result should be regime-aware and layer-aware:

- source-grounded answers should cite `L0/L1`,
- derivational answers should cite `L3`,
- adjudication answers should cite `L4`,
- reusable answers should cite `L2`.

`query` must not silently upgrade weak material into stronger authority.

#### `lint`

Inspect the knowledge base for structural and scientific hygiene failures.

Physics-relevant lint should include at least:

- unresolved notation tensions,
- contradiction records with no disposition,
- derivation anchors missing later reconstruction links,
- claims with missing regime statements,
- promoted units with broken provenance chains,
- stale reusable units contradicted by later evidence,
- missing non-claims or limitations,
- orphaned concepts/methods with no source or reuse links.

### Navigation surfaces: `index` and `log`

AITP should add two durable navigation surfaces at both topic and global
levels:

#### `index`

A content-oriented navigation map that answers:

- what concepts, methods, warnings, bridges, and claims exist?
- how are they grouped by regime, topic family, or method family?
- where should the human or agent read next?

#### `log`

A time-oriented evolution surface that answers:

- what changed in this topic or knowledge base?
- which question/answer/lint/promotion event caused the change?
- what scientific understanding moved forward, stalled, or was revised?

The index is for orientation.
The log is for continuity and audit.

### Query writeback rule

Useful query results should be allowed to write back into the knowledge base,
but only into the correct layer:

- source-grounded clarification -> `L1`
- derivation or route synthesis -> `L3`
- adjudication summary -> `L4`
- reusable promoted unit -> `L2` only after the normal gate

This preserves the productive part of a wiki workflow without weakening AITP's
epistemic discipline.

### Knowledge-base health rule

The knowledge base should be periodically linted the way a theorist would check
a notebook shelf:

- are the important things still findable?
- are contradictions visible rather than buried?
- are dead ends preserved as lessons?
- are notation and regime assumptions explicit?
- are reusable units actually reusable outside the original topic?

This should become an explicit runtime and maintenance surface, not an informal
hope.

## Stage Contracts

### `L1` Read-And-Frame Stage

#### Role

`L1` is where a theorist turns a pile of sources into a bounded research basis.
It is not merely intake.
It is the stage where the topic gains:

- a real question,
- a defined regime,
- a usable notation basis,
- and a map of where the later derivation work will start.

#### Required artifacts

- `question_contract.md`
- `source_basis.md`
- `convention_snapshot.md`
- `derivation_anchor_map.md`
- `contradiction_register.md`

#### Required contents

##### `question_contract.md`

Must include:

- bounded question,
- scope boundaries,
- target quantities or claim family,
- what does **not** count as success,
- current uncertainty markers.

##### `source_basis.md`

Must include:

- core sources,
- peripheral sources,
- source role per item,
- reading depth,
- why each source matters.

##### `convention_snapshot.md`

Must include:

- notation choices,
- unit conventions,
- sign conventions,
- metric/convention choices when relevant,
- unresolved notation tensions.

##### `derivation_anchor_map.md`

Must include:

- source-local theorem/equation/section anchors,
- missing-step markers,
- likely starting points for later reconstruction.

##### `contradiction_register.md`

Must include:

- unresolved source conflicts,
- regime mismatches,
- notation collisions,
- whether the contradiction blocks derivation.

#### Exit gate

`L1` may hand off to `L3` only when:

- the question is bounded,
- the source basis is explicit,
- conventions are locked enough for honest derivation,
- at least one derivation anchor exists,
- unresolved contradictions are either scoped or marked as blockers.

#### Real-physicist rule

A theorist does not start deriving seriously while still confused about what
symbols mean, which regime is being studied, or which paper actually supports
the starting formula.
`L1` must therefore act like a framing notebook, not a summary dump.

### `L3` Derive-And-Investigate Stage

#### Role

`L3` is the live scientific notebook:

- ideas,
- plans,
- derivations,
- computations,
- failed attempts,
- returned validation outcomes,
- and bounded distillation before promotion.

It remains the only detailed derivation home for a topic.

#### Required subplanes

`L3` progression is hard-gated:

```text
L3-I -> L3-P -> L3-A -> L3-R -> L3-D
```

Subplanes:

- `L3-I` ideation
- `L3-P` planning
- `L3-A` analysis
- `L3-R` result integration
- `L3-D` distillation

#### Required active artifacts

- `L3/ideation/active_idea.md`
- `L3/planning/active_plan.md`
- `L3/analysis/active_analysis.md`
- `L3/result_integration/active_integration.md`
- `L3/distillation/active_distillation.md`

#### Core gate rule

The topic may not:

- skip subplanes,
- promote directly from raw analysis,
- hide failures instead of recording them,
- or treat local coherence as validation.

#### Real-physicist rule

A careful theorist does not move directly from "I derived something" to
"therefore this is reusable knowledge."

They typically:

1. decide what they are trying to prove or compute,
2. make a plan,
3. work through the details,
4. compare with checks and objections,
5. rewrite the surviving claim in a cleaner bounded form.

That is exactly what `L3-I/P/A/R/D` should encode.

### `L4` Verify-And-Adjudicate Stage

#### Role

`L4` is where the topic asks:

- does this survive serious checking?

`L4` is not only execution.
It is the adjudication notebook for the candidate.

#### Required artifacts

- `validation_contract.md`
- `reviews/<candidate_id>.md`
- `execution/<candidate_id>.md` when non-trivial execution occurs
- `gaps/<candidate_id>.md` when blockers or contradictions remain

#### `validation_contract.md`

Must include:

- candidate under review,
- declared validation route,
- required checks,
- failure conditions,
- execution or proof surface if needed,
- which checks are mandatory vs optional.

#### Physics-specific mandatory checks

The exact checklist depends on lane, but `L4` should require explicit treatment
of the relevant items among:

- dimensional consistency,
- symmetry compatibility,
- conservation-law compatibility,
- limiting cases,
- correspondence principle,
- positivity / stability / unitarity when relevant,
- benchmark reproduction,
- finite-size / convergence behavior,
- notation-and-assumption consistency with `L1`.

#### Validation outcomes

Use the full six-outcome vocabulary:

- `pass`
- `partial_pass`
- `fail`
- `contradiction`
- `stuck`
- `timeout`

These outcomes must remain visible rather than collapsing into `ready/blocked`.

#### Exit gate

`L4` exits only by returning through `L3-R`.
It does not write directly to `L2`.

#### Real-physicist rule

Theoretical physics validation is rarely only "run the code and see."
It often means:

- check dimensions,
- examine limits,
- compare with known exact results,
- see whether the physical interpretation survives,
- and decide whether the mismatch is fatal, local, or unresolved.

`L4` should encode that discipline.

### `L2` Reusable-Physics-Memory Stage

#### Role

`L2` is the global reusable memory of the system.
It stores what survives beyond one topic.

It should represent the kinds of reusable objects a theorist actually wants to
reuse across problems:

- concepts,
- definitions,
- notations,
- conventions,
- methods,
- validation patterns,
- warning notes,
- negative lessons,
- bridges between topic families,
- and bounded promoted claims.

#### Global, not topic-local

`L2` should be global at the topics-root level.
Topics consult it and promote into it.
They do not own separate local canonical stores as the primary truth.

#### Recommended global families

- `canonical/`
- `notation/`
- `conventions/`
- `methods/`
- `validation_patterns/`
- `warning_notes/`
- `negative_results/`
- `bridges/`
- `physical_pictures/`

This may be realized as family directories or family tags, but the important
thing is that the reusable content is typed and regime-aware.

#### Required reusable fields

Each `L2` unit should carry at least:

- identity,
- unit type,
- bounded claim or content summary,
- trust class,
- regime/applicability,
- assumptions,
- provenance,
- validation receipts,
- origin topic refs,
- reuse refs,
- caveats and non-claims.

#### Trust classes

Recommended scientific trust classes:

- `exact`
- `rigorous`
- `established`
- `conjectural`
- `phenomenological`

These describe scientific standing.
They should remain distinct from workflow state such as `staged` or `promoted`.

#### Promotion boundary

`L2` accepts writes only from:

- `L3-D` bounded distillation,
- backed by `L4` review artifacts,
- with promotion trace,
- and with human approval when the policy requires it.

#### Real-physicist rule

Reusable memory in theoretical physics is not only theorems.
It also includes:

- convention locks that prevent repeated confusion,
- benchmark models that serve as sanity checks,
- warnings about false analogies,
- and negative lessons about routes that look elegant but fail.

`L2` should preserve that broader reusable scientific memory.

### `L5` Write-And-Communicate Stage

#### Role

`L5` is where the topic is turned into communicable scientific output:

- paper,
- report,
- slides,
- note,
- thesis fragment.

It is not a truth layer.
It is a communication layer built on prior truth surfaces.

#### Required artifacts

- `outline.md`
- `claim_evidence_map.md`
- `equation_provenance.md`
- `figure_provenance.md`
- `limitations.md`
- `draft.tex`
- `references.bib`

#### `claim_evidence_map.md`

Must include:

- each major paper claim,
- whether it comes from `L2` or remains preliminary from `L3`,
- the supporting `L4` artifact path,
- relevant caveats.

#### `equation_provenance.md`

Must include for numbered equations:

- whether the equation is source-derived, reconstructed, or newly derived,
- which `L1`/`L3`/`L4` artifacts support it,
- any omitted conditions or regime limits.

#### `figure_provenance.md`

Must include:

- figure source,
- script or generation path,
- validation relation,
- what the figure does and does not show.

#### `limitations.md`

Must include:

- unresolved assumptions,
- known weak spots,
- open contradictions,
- what would be needed before stronger claims are warranted.

#### Exit gate

External release requires human review.
`L5` does not silently certify correctness.

#### Real-physicist rule

A real theory paper is not just prose and equations.
It is an argument whose claims, derivations, figures, and caveats can be traced.
`L5` should therefore preserve provenance, not merely compile LaTeX.

## Posture Contracts

These are the renamed, useful descendants of older brain modes.

| Posture | Local task | Foreground layers | Typical result |
|---------|------------|------------------|----------------|
| `read` | inspect and compare source material | `L0`, `L1` | stronger source basis |
| `frame` | bound the question and lock conventions | `L1`, early `L3-I` | question/convention closure |
| `derive` | execute a derivation or computation route | `L3-P`, `L3-A` | bounded candidate output |
| `verify` | test and adjudicate the candidate | `L4`, `L3-R` | validation outcome |
| `distill` | rewrite surviving result into reusable bounded form | `L3-D`, `L2` boundary | promotion-ready packet |
| `write` | compile communicable output | `L5` | draft manuscript/report |

### Posture rule

Posture governs:

- minimum mandatory context,
- deferred context,
- top-level brief phrasing,
- trigger thresholds.

It does not govern:

- whether stage advancement is allowed,
- whether promotion is justified,
- whether a claim is scientifically mature.

## Progressive Disclosure Triggers

Across `L1-L5`, `brain` should emit stable trigger names such as:

- `source_basis_incomplete`
- `notation_lock_required`
- `contradiction_detected`
- `capability_gap_blocker`
- `numerical_execution_required`
- `formalization_required`
- `promotion_intent`
- `paper_release_boundary`

Default rule:

- load only what the current stage and posture require,
- attach deeper slices only when a trigger fires,
- never hide hard governance surfaces when they become mandatory.

## `brain` Output Contract

For any active topic, `brain` should be able to return a brief containing at
least:

- current layer,
- current `L3` subplane when applicable,
- current posture,
- current lane,
- gate status,
- required artifact path,
- missing requirements,
- immediate allowed work,
- immediate blocked work,
- next micro-skill or operation packet,
- deeper reads by trigger.

Short form:

- the agent should always know what stage it is in,
- what artifact is missing,
- and what scientific move is honest now.

## Backedge Rules

Backedges remain normal and healthy:

- `L1 -> L0` when source basis is insufficient,
- `L3 -> L1` when conventions or anchors are unstable,
- `L4 -> L1` when a claimed mismatch is really a framing or notation issue,
- `L4 -> L3` when a candidate needs revision,
- `L5 -> L3/L4` when writing exposes unsupported claims or gaps,
- narrow `L3/L4 -> L2` consultations when prior reusable knowledge is needed.

Every backedge must record:

- from-stage,
- to-stage,
- reason,
- blocking artifact,
- expected recovery artifact.

## What This Design Changes

This umbrella spec changes:

- `brain` from status announcer to protocol kernel,
- old modes from primary state to secondary posture,
- `L1` from generic intake to question/convention framing,
- `L4` from abstract validation to physics adjudication,
- `L2` from generic canonical store to reusable physicist memory,
- `L5` from generic writing output to claim/equation/figure provenance surface.

It keeps:

- the Charter,
- the layer ontology,
- the lane axis,
- progressive disclosure,
- human promotion checkpoints,
- the basic `L0 -> L1 -> L3 -> L4 -> L2` logic.

## Relationship To Earlier L3 Design

The focused document
`2026-04-20-l3-subplane-brain-gated-progressive-disclosure-design.md`
remains a valid detailed precursor for `L3`.

This umbrella spec supersedes it at the top-level architecture layer by placing
that `L3` design inside the broader `L1-L5` research-flow model.

If the two documents differ:

- this umbrella spec governs cross-layer architecture,
- the earlier document governs detailed `L3` subplane mechanics until a later
  merged revision is written.

## Implementation Order

Recommended rollout:

1. freeze the umbrella stage/posture model in docs,
2. refactor `brain` to emit layer + posture + gate status,
3. harden `L1` framing artifacts and notation lock,
4. land `L3` subplane gates,
5. upgrade `L4` into physics-specific adjudication bundles,
6. remodel `L2` as global reusable memory with trust-class and regime fields,
7. add `L5` claim/equation/figure provenance surfaces,
8. run real-topic end-to-end smoke tests on at least one formal-theory topic,
   one toy-model topic, and one code-method topic.

## Testing Strategy

Add coverage for:

- `L1` exit blocked when question, convention, or anchor surfaces are missing,
- `L3` subplane skipping rejected,
- `L4` validation artifacts carrying explicit outcomes and physics checks,
- `L2` writes rejected without proper promotion trace,
- `L5` claim/equation provenance surfaces required before completion,
- posture selection matching current stage,
- resume into the correct stage/posture pair after interruption.

Add end-to-end acceptance tests for real topics that verify:

- source basis and notation lock occur before deep derivation,
- contradictions remain visible,
- reusable memory is promoted only after explicit adjudication,
- final writing traces claims and equations to earlier artifacts.

## Risks

### 1. Turning the system into a form-filling bureaucracy

If every artifact becomes a dead template, AITP will lose actual research
intelligence.

Mitigation:

- keep forms minimal but gate-critical,
- let the agent reason freely inside the bounded artifact,
- use `brain` for checking structure, not for replacing thought.

### 2. Overloading `brain`

If `brain` starts deciding scientific truth rather than protocol progression,
the design will drift back into hidden heuristics.

Mitigation:

- keep `brain` responsible for state, gates, triggers, and briefs only.

### 3. L2 becoming unmanageably broad

If every useful note is promoted, `L2` will become cluttered.

Mitigation:

- require regime/applicability and non-claims,
- preserve negative lessons but keep them typed and bounded,
- rely on distillation before promotion.

### 4. L5 overstating weak results

If writing surfaces do not track provenance and limitations, polished drafts may
look stronger than the evidence warrants.

Mitigation:

- require claim/equation/figure provenance and explicit limitations artifacts.

## Success Criteria

This design is successful when:

- `brain` can report a topic's current layer, posture, gate status, and missing artifact,
- `L1` behaves like a source-basis and convention-framing stage,
- `L3` behaves like a real derivation notebook with hard subplane gates,
- `L4` records actual physics adjudication rather than vague pass/fail prose,
- `L2` stores reusable physicist memory with trust class and regime,
- `L5` can trace every major claim, equation, and figure to earlier artifacts,
- and a real topic can move from literature to draft without hidden stage jumps.

## One-Line Memory

AITP should behave like a careful theorist's workspace: frame the question,
lock the conventions, derive honestly, verify physically, distill what
survives, and only then write it up with provenance.
