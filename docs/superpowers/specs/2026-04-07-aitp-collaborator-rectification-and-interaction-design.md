# AITP Collaborator Rectification And Interaction Design

Status: working design

Date: 2026-04-07

## Goal

Turn the current AITP kernel from a strong research control plane with weak
compounding memory into a system that can realistically grow into a
theoretical-physics collaborator:

- it should become more useful as literature, discussions, and validated
  routes accumulate;
- it should support real non-linear research motion across `L0/L1/L2/L3/L4`;
- it should expose its state, results, and human checkpoints in a form that a
  physicist can actually use.

This document is a design-level rectification map.
It does not define code tasks or implementation steps yet.

## Problem Statement

AITP already has unusually strong protocol discipline:

- explicit layer semantics,
- explicit runtime state,
- explicit promotion gates,
- explicit mode envelopes,
- explicit transition and backedge doctrine,
- and a coherent paired-backend doctrine.

But the system is still not yet a strong long-horizon collaborator.

The main mismatch is:

- control-plane strength is ahead of knowledge-plane strength;
- doctrine is ahead of operational memory growth;
- operator/runtime visibility is ahead of scientist-facing result presentation.

Short form:

- AITP can often say where a topic is,
- but it still cannot reliably accumulate enough reusable physics knowledge,
  route memory, and collaborator memory to become smarter through use.

## Design Objectives

The next architecture pass should satisfy all of the following.

### 1. Memory objective

AITP must accumulate reusable knowledge, not only runtime traces.

### 2. Research-flow objective

AITP must support real research motion as a graph, not only as one serialized
promotion pipeline with occasional allowed backedges.

### 3. Reading objective

AITP must read sources more like a physicist:

- assumptions,
- regimes,
- notation,
- proof status,
- contradiction,
- and source fidelity

must become durable objects rather than weak summary hints.

### 4. Validation objective

AITP must validate more like a physicist:

- limiting cases,
- dimensional checks,
- symmetry checks,
- source-consistency checks,
- and symbolic sanity checks

must become first-class validation families alongside existing execution and
formal-theory review paths.

### 5. Interaction objective

AITP must expose:

- what it knows,
- what changed,
- what it needs from the human,
- and why it stopped

without forcing the user to reconstruct internal state from logs or protocol
artifacts.

### 6. Collaboration objective

AITP must gradually learn the collaborator:

- route preferences,
- validation taste,
- preferred formalisms,
- known dead ends,
- and long-horizon research trajectory.

## Non-Goals

This design does not aim to:

- add more core layers unless forced by a genuine epistemic gap;
- turn every operation into a new top-level mode;
- collapse the human-readable backend and typed backend into one storage model;
- treat publication polish as the next primary milestone;
- claim full autonomy before the checkpoint and stop policy is made robust.

## Current Judgment

### What is already materially strong

- `layer / mode / transition` doctrine is now explicit enough to guide future
  work.
- The runtime shell already exposes a usable operator-facing control surface.
- The paired-backend doctrine is conceptually coherent.
- Promotion, consultation, and conformance surfaces are much more explicit than
  in most research-agent systems.

### What is still the central blocker

The central blocker is still `L2`.

The current canonical `L2` surface is not yet an operational knowledge network.
Without a populated graph, lightweight capture path, and real retrieval, AITP
does not become wiser through use.

## Rectification Map

The next round of design and implementation should be organized around eight
continuous rectification themes rather than a flat backlog.

### R1. Axis Semantic Closure

Repair semantic drift across:

- `lane`
- `research_mode`
- `template_mode`
- `runtime_mode`
- `transition`

Required outcomes:

- `first_principles` is no longer silently folded into `toy_numeric`;
- `theory_synthesis` gets an explicit bounded role;
- runtime artifacts cannot claim mutually inconsistent lane/mode identities;
- consultation, promotion, and backend alignment semantics become explicit
  rather than partly inferred from path conventions.

### R2. Research Flow As Graph, Not Just Pipeline

Treat real research motion as a graph over `L0/L1/L2/L3/L4`.

The existing default forward law remains useful:

`L0 -> L1 -> L3 -> L4 -> L2`

But AITP should no longer behave as if that serialized story is the natural
default of all serious work.

Required outcomes:

- `L1 -> L2` narrow consultation is recognized as normal early research work,
  not only as an edge-case doctrinal allowance;
- cross-layer context carrying is explicit;
- route branching, parking, return, and reintegration are ordinary runtime
  behavior;
- runtime state can represent several live sub-routes without pretending the
  topic has one linear narrative.

### R3. Layer 0 As Source Intelligence, Not Only Source Persistence

Current `L0` is a durable source substrate, but not yet a strong source
intelligence layer.

Required outcomes:

- global source identity across topics;
- source deduplication semantics;
- citation graph traversal;
- source fidelity grading;
- cross-topic source-family reuse;
- reading-depth breadcrumbs that later layers can consult.

### R4. Layer 1 As Physicist-Grade Intake

Current `L1` is still too close to preview and heuristic distillation.

Required outputs for source-backed intake packets should minimally include:

- main claims,
- assumptions,
- regime limits,
- notation bindings,
- proof status,
- evidence grade,
- reading depth,
- and tension with nearby sources.

These should support:

- shallow read,
- deeper read,
- comparison read,
- and contradiction-oriented read

without forcing one monolithic intake pass.

### R5. Layer 2 Knowledge-Network MVP

`L2` should start from a strict MVP rather than a fully expanded ontology.

#### MVP node families

- `concept`
- `theorem_card`
- `method`
- `assumption_card`
- `physical_picture`
- `warning_note`

#### Immediate next extension family

- `negative_result`

#### MVP edge families

- `depends_on`
- `uses_method`
- `valid_under`
- `warns_about`
- `contradicts`
- `analogy_to`
- `derived_from_source`

#### Required operational features

- lightweight capture into staging;
- review path from staging into canonical `L2`;
- first seeded graph direction with real data;
- graph traversal over actual edges;
- progressive-disclosure retrieval:
  index first, deeper packet only when needed.

The key rule is:

- the graph should start from real physics objects and real relations,
  not from ontology completeness theater.

### R6. Layer 3 And Layer 4 Research-Object Expansion

AITP currently over-privileges adjudicable candidates.

That misses too much real theoretical work.

Required `L3`-adjacent or reusable object families:

- `scratch_note`
- `physical_picture`
- `negative_result`
- `route_comparison`
- `partial_argument`
- `failed_check`

Required `L4` validation-family expansion:

- limiting-case validation,
- dimensional validation,
- symmetry validation,
- source-consistency validation,
- symbolic sanity validation.

Required `L4` output posture:

- allow `pass`,
- `partial`,
- `blocked`,
- `interesting_failure`,
- `regime_mismatch`,
- `needs_source_recovery`

without forcing every useful run into fake closure language.

### R7. Collaborator Memory

AITP must distinguish:

- topic state,
- reusable domain knowledge,
- and collaborator memory.

Required collaborator-memory surfaces:

- collaborator profile,
- research trajectory summaries,
- route history,
- negative-result retention,
- taste signals,
- and momentum / stuckness / surprise signals.

These should influence:

- route suggestion,
- retrieval ranking,
- lane choice,
- and checkpoint timing.

### R8. Human-Facing Surfaces

AITP already has a runtime shell, but it still leans too far toward control
surfaces and not far enough toward research presentation.

The human-facing surface model should be explicitly divided into four roles.

#### Operator view

Purpose:

- what is the system doing now,
- what is blocked,
- what is the next bounded step.

#### Research-state view

Purpose:

- what the topic currently claims,
- what is known,
- what remains open,
- what changed recently.

#### Validated-result view

Purpose:

- what result was obtained,
- why it is trusted,
- what its scope is,
- what it does not justify.

#### Collaborator-memory view

Purpose:

- how this topic connects to earlier work,
- which routes have already failed,
- what reusable ideas or warnings should be remembered now.

The runtime shell already partially covers the first role.
The next design pass should close the other three.

## Layer-Specific Improvement Summary

### L0

Upgrade from source registry to source intelligence.

### L1

Upgrade from heuristic distillation to assumption- and regime-aware reading.

### L2

Build the smallest real knowledge network that can support actual consultation.

### L3

Preserve scratch, route comparison, and negative-result memory rather than
only promotion-facing candidates.

### L4

Broaden validation to match theoretical-physics practice, not only execution
or formal-review discipline.

### Runtime

Keep the current shell discipline, but separate:

- runtime truth,
- research truth,
- and collaborator memory

more clearly.

## Workflow Routing Rule

This design should also make the operational division between
`Superpowers-style workflow shells`, `AITP`, and `GSD` explicit.

They should not be treated as three competing orchestrators.

They live at different levels.

### 1. Superpowers-style shell

Role:

- natural-language-first entry,
- workflow gating,
- progressive disclosure,
- and front-door routing into the correct deeper system.

It answers:

- how does the user enter the work naturally?

It must not become the durable source of truth for:

- research state,
- promotion state,
- or repo-development state.

### 2. AITP

Role:

- topic-governed research execution,
- research-state materialization,
- validation,
- checkpoints,
- and promotion-routing semantics.

It answers:

- where is this research topic now,
- what is the next bounded research action,
- what evidence exists,
- and what is trusted enough to reuse?

### 3. GSD

Role:

- repository implementation planning and execution for AITP itself.

It answers:

- how should this repository be changed, planned, verified, and summarized?

It must not replace:

- topic runtime state,
- topic validation state,
- or scientific trust state.

### 4. Default routing law

Use this routing order:

1. natural-language user entry first lands on the `Superpowers-style` shell;
2. if an explicit or implied research topic is active, `AITP` wins;
3. if the task is about changing the AITP repository itself, `GSD` wins.

Short form:

- `Superpowers` routes
- `AITP` governs research
- `GSD` governs implementation of AITP itself

### 5. Topic-first rule

If the next step needs any of the following, start in `AITP`:

- durable topic state,
- steering,
- validation-route choice,
- checkpoint semantics,
- promotion semantics,
- source recovery,
- or topic-governed code execution.

This remains true even when the immediate work includes code.

### 6. Code boundary rule

Code is not automatically `GSD`.

Distinguish:

- `code as research evidence`
- `code as repo maintenance`

#### Code as research evidence

Use `AITP` when code exists to:

- reproduce a benchmark,
- validate an observable,
- run a bounded implementation route inside a topic,
- record operation trust,
- or support a declared topic validation path.

In this case, success is judged by the topic contract.

#### Code as repo maintenance

Use `GSD` when code exists to:

- improve AITP runtime behavior generally,
- add tests, schemas, docs, or packaging,
- improve adapters or installs,
- or add capabilities that future topics may use.

In this case, success is judged by repository behavior.

### 7. Mixed-task rule

Some tasks genuinely have both layers.

When that happens:

- start in `AITP` if there is a real active research topic;
- record the actual research state and blocker there first;
- then capture the general product/runtime gap as `GSD` follow-up.

Typical pattern:

- topic-governed diagnosis or execution in `AITP`
- generalization into repo improvement in `GSD`

The reverse order should be rare and should happen only when the topic cannot
continue at all because a baseline repository/runtime surface is broken.

### 8. Anti-patterns

Do not:

- treat `GSD` summaries as the scientific source of truth for a topic;
- force every topic-governed coding task into repo-maintenance workflow;
- use `Superpowers-style` routing without durable AITP runtime materialization;
- let repository-maintenance work pollute active topic artifacts as if it were
  scientific progress.

### 9. Operational question sequence

When routing a mixed or ambiguous task, ask these questions in order:

1. Is there an explicit or implied active research topic?
2. Does the next honest step need topic state, validation, steering, or
   promotion semantics?
3. Is the code or document change part of topic evidence, or part of AITP
   product maintenance?
4. Where should the source of truth land:
   topic runtime artifacts or repository planning/execution artifacts?

Route like this:

- if `1` or `2` is yes, start in `AITP`
- if only `3` is yes and it is repo maintenance, use `GSD`
- always let `Superpowers-style` entry remain the front door instead of making
  the user choose protocol jargon first

## Human Interaction And Stop Policy

This is the main interaction contract required before claiming stronger AITP
autonomy.

AITP should not use one undifferentiated "assistant reply" pattern.
It should choose among four interaction classes.

### I1. Silent Continue

AITP continues without interrupting the human when:

- the current bounded route is already approved,
- the resource profile is already approved,
- the trust boundary is unchanged,
- and the next action does not materially change lane, scope, or cost.

This should be the default for ordinary bounded work.

### I2. Non-Blocking Update

AITP informs the human but does not pause the bounded loop when a meaningful
state change occurred and no decision is required.

Typical triggers:

- a new source cluster was registered or distilled;
- a new candidate or scratch object was formed;
- a validation result landed;
- a contradiction or negative result was recorded;
- a consultation changed terminology or route shape;
- a topic state changed from active to blocked, deferred, or promoted.

Required behavior:

- emit a concise result-aware summary;
- record the corresponding durable artifacts;
- do not force the user to answer unless a real checkpoint exists.

### I3. Checkpoint Question

AITP asks one bounded route-changing question and pauses the affected branch
when the answer materially changes the route.

Typical checkpoint families:

- scope ambiguity,
- novelty-direction choice,
- continue vs branch vs redirect,
- lane choice,
- benchmark or validation-route choice,
- contradiction adjudication,
- external execution target / resource class choice,
- promotion approval,
- paired-backend alignment choice when a real lossy tradeoff exists.

Required rules:

- one real route-changing question at a time;
- natural-language phrasing, not protocol jargon;
- durable checkpoint artifacts on disk;
- the checkpoint must say why continuation is blocked.

### I4. Hard Stop

AITP must stop when no honest automatic continuation path exists.

Typical hard-stop cases:

- an unresolved blocking human checkpoint exists;
- non-trivial execution lacks approved lane, target, or resource class;
- a high-impact trust move lacks approval;
- steering redirect has been detected but not yet materialized durably;
- required source or capability recovery cannot be completed automatically;
- continuing would only create fake progress.

Required stop payload:

- why the system stopped,
- which layer or boundary it stopped at,
- the most credible current result,
- what is missing,
- and the smallest next actionable question.

## When AITP Should Proactively Inform The Human

AITP should inform the human on event boundaries rather than on arbitrary loop
counts.

### Event family A: research-state change

Examples:

- topic reframing,
- route switch,
- important new blocker,
- new physical picture,
- meaningful route comparison.

### Event family B: evidence change

Examples:

- new validation result,
- benchmark mismatch,
- contradiction,
- negative result,
- stronger or weaker confidence state.

### Event family C: memory change

Examples:

- staging capture added,
- canonical `L2` updated,
- paired backend alignment debt introduced or resolved,
- reusable strategy memory recorded.

### Event family D: topic-state change

Examples:

- stage shift,
- blocked / deferred / promoted transition,
- active checkpoint appears or clears,
- topic completion or projection status changes.

## Human-Facing Result Shapes

The system should not expose one generic prose summary for every event.

It should materialize at least these distinct human-facing result shapes.

### 1. Status update

One-screen answer to:

- where are we now?

### 2. Result brief

One-screen answer to:

- what new result did this run produce,
- what evidence supports it,
- and what it still does not justify.

### 3. Checkpoint card

One-screen answer to:

- what decision is needed,
- why it matters,
- and what happens under each route.

### 4. Topic replay bundle

One-screen answer to:

- how should a returning human or agent re-enter this topic

without reopening the whole runtime tree blindly.

## Continuous Milestone Sequence

This design should become implementation work through five continuous
milestones.

### M1. Semantic Closure And Interaction Contract

Goals:

- close axis drift;
- define graph-first research-flow semantics;
- define the formal interaction and stop policy;
- define the `L2` MVP object/edge contract.

Why first:

- later implementation will harden the wrong semantics if this stays loose.

### M2. L2 Knowledge-Network MVP

Goals:

- build the staging and canonical MVP;
- seed one real direction;
- make retrieval and consultation non-empty.

Why second:

- without this, AITP still cannot become smarter through use.

### M3. Physicist-Grade Intake And Validation

Goals:

- assumption/regime/notation-aware `L1`;
- source fidelity and citation traversal in `L0`;
- analytical validation families in `L4`.

Why third:

- memory quality must improve once memory existence is no longer the blocker.

### M4. Collaborator Memory And Low-Bureaucracy Exploration

Goals:

- collaborator profile;
- trajectory memory;
- route-history learning;
- quick exploration path with promotion into the main topic graph.

Why fourth:

- these need the earlier knowledge and validation substrate to be meaningful.

### M5. Paired Backend Maturity And Theory-Synthesis Lane

Goals:

- paired-backend drift audit and rebuild policy;
- first-class `theory_synthesis` lane;
- cross-paper alignment and notation reconciliation workflows.

Why fifth:

- synthesis and backend maturity depend on the earlier graph, intake, and
  interaction work.

`L5 Publication Factory` should remain after these milestones, not before them.

## What Must Be Discussed Before Implementation

The following are still design decisions that should be finalized explicitly
before implementation planning.

### D1. Final lane set and lane boundaries

Especially:

- `first_principles`
- `toy_numeric`
- `theory_synthesis`
- `code_method`

### D2. Canonical versus staging boundary for new knowledge objects

Especially:

- `physical_picture`
- `negative_result`

### D3. Paired-backend alignment policy

Especially:

- what anchors shared identity,
- what counts as acceptable one-sided reduction,
- and when drift becomes blocking debt.

### D4. Collaborator-memory scope

Especially:

- what counts as durable scientific preference,
- what counts as transient session preference,
- and what should never enter collaborator memory.

## What Can Move Directly To Execution Once The Design Is Approved

The following are clear enough to become execution work after this design is
approved and converted into plans.

- repair mode/lane/route semantic drift;
- define and seed the `L2` MVP graph;
- implement lightweight knowledge capture into staging;
- extend `L1` with stronger source-packet scaffolds;
- add the first analytical validation families;
- harden checkpoint and stop behavior around route-changing choices;
- add scientist-facing result-brief surfaces on top of the existing runtime
  shell.

## One-Line Design Doctrine

AITP should evolve from a protocol-strong research control plane into a
memory-growing, graph-native, interaction-disciplined theoretical-physics
collaborator by prioritizing `L2` growth, physicist-grade reading and
validation, collaborator memory, and explicit human-facing checkpoint/result
surfaces before publication-layer polish.
