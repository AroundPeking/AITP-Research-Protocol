# Formal Theory Automation Workflow

This file defines the current end-to-end AITP workflow for formal-theory and
semi-formal theory research.

It answers one practical question:

When a topic is mathematical or theoretical enough that future Lean export is
part of the plan, what exact workflow should AITP follow today, before full
theorem-prover closure is available?

## 1. Current target state

AITP is not yet at "whole-paper one-shot Leanization".

The current target state is:

- source-grounded sectionization,
- semi-formal theorem and derivation packets,
- compile-checked local Lean shadows for bounded sections,
- explicit proof and source gaps,
- regression-backed topic control,
- and promotion only for packets that remain honest about their trust boundary.

This is strong enough for controlled research assistance and bounded
autoformalization work.
It is not yet full autonomous theorem-prover completion for arbitrary physics
literature.

## 2. The three operating lanes

Formal-theory automation should usually be decomposed into three lanes.

### Lane A: concrete theorem-level package

Goal:

- build the concrete representation-dependent route into a theorem-level Lean
  package

Typical examples:

- concrete von Neumann algebras in `B(H)`
- topology-dependent closure theorems
- explicit operator-algebra definitions and bundled consequences

Required outputs:

- section source maps
- theorem statements
- proof obligations
- compile-checked local Lean modules
- section regressions

### Lane B: abstract/concrete equivalence route

Goal:

- connect the abstract backend-facing notion to the concrete theorem package
  without silently identifying them too early

Typical examples:

- `WStarAlgebra` versus `VonNeumannAlgebra`
- abstract tensor-categorical notions versus concrete model realizations

Required outputs:

- explicit equivalence target
- bridge-oriented `open_gap`
- cited-source recovery route
- separate regression prompts that punish category errors

### Lane C: examples and flagship models

Goal:

- formalize worked examples, canonical models, and physically meaningful test
  cases after the relevant concrete theorem packet is already stable

Typical examples:

- multiplication-operator / masa examples
- topological-phase toy models
- bounded Hamiltonian exemplars

Required outputs:

- example source packet
- explicit dependency on the concrete theorem line
- example-specific source recovery if the original source is too terse
- no fake closure from a mere compile-clean stub

## 3. The stage machine

AITP should move a formal-theory topic through these stages.

### Stage 0: source registration

Layers:

- `L0`

Deliverables:

- source manifest
- section map
- provenance and locator registration

### Stage 1: semi-formal packet shaping

Layers:

- `L1`
- `L3`

Deliverables:

- definitions
- theorem cards
- derivation steps
- proof obligations
- notation maps
- open gaps
- follow-up source tasks

Exit rule:

- the bounded packet must be source-grounded and split-honest

### Stage 2: local Lean shadow

Layers:

- `L3`
- `L4`

Deliverables:

- compile-checked local Lean modules
- declaration headers aligned with current upstream names
- explicit statement of what remains unproved

Exit rule:

- compilation success is necessary but not sufficient for promotion

### Stage 3: theorem-level package

Layers:

- `L3`
- `L4`
- optional `L2_auto`

Deliverables:

- theorem-level local package
- section regressions
- blocker-clear review
- split/gap honesty

Exit rule:

- only bounded, review-ready packets may move toward `L2_auto`

### Stage 4: bridge and example closure

Layers:

- `L0`
- `L1`
- `L3`
- `L4`

Deliverables:

- abstract/concrete bridge route
- example formalization route
- additional cited-source recovery where needed

This stage is usually slower and should remain explicitly separate from the
concrete theorem lane.

## 4. Required artifacts by lane

For each active lane, AITP should be able to point to:

- one active queue
- one regression surface
- one current source map or family leader
- one current Lean shadow path if Lean work has started
- one trust-boundary statement

If those pointers do not exist, the lane is not yet operationally mature.

## 5. What counts as "automation-ready" today

AITP is ready for bounded automated formal-theory research when it can do all
of the following on a topic:

- split the source by section or bounded family
- materialize semi-formal packets
- preserve explicit proof and source gaps
- compile-check local Lean shadows for bounded packets
- run regression questions that detect drift
- keep runtime and backend writeback auditable

AITP is not yet ready to claim:

- arbitrary whole-paper autonomous Lean closure
- proof-complete export from informal prose without packet shaping
- example completion when the example route is still under-sourced

## 6. Jones exemplar as the current benchmark

The Jones 2015 operator-algebra branch should currently be read through the
three-lane model:

- Lane A:
  - concrete commutant / topology / bicommutant / concrete-definition route
- Lane B:
  - abstract `WStarAlgebra` versus concrete `VonNeumannAlgebra` bridge
- Lane C:
  - multiplication-operator / masa example route

AITP should treat success on this exemplar as:

- a theorem-level package for Lane A,
- an explicit open bridge plan for Lane B,
- and an explicit example backlog or closure route for Lane C.

## 7. Decision rule for operators

If an operator asks "is the topic automated now?", answer by lane:

- Lane A automated enough for bounded theorem-level progress?
- Lane B automated enough for equivalence work?
- Lane C automated enough for examples?

Do not answer with one undifferentiated yes/no unless all three lanes are
actually at the same maturity.
