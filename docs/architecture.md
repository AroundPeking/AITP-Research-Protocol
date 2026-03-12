# Architecture

## Core objective

Build a human-in-the-loop research kernel for theoretical physics that can evolve toward a human-AI collaborative theoretical physicist.

The project is not trying to imitate a finished autonomous researcher. It is trying to provide the research structure needed for serious human-AI collaboration in theoretical physics.

---

## Public baseline: L0-L4

The current public baseline is an **L0-L4 architecture**.

Earlier internal notes sometimes described a three-layer knowledge architecture. That view is still useful as a sub-view, but it is no longer the public baseline because it leaves out two crucial surfaces:
- the source substrate,
- the validation surface.

### Layer 0 — Source substrate

Purpose:
- register sources,
- preserve source identity,
- reopen evidence later,
- expand the source set when new gaps appear.

Typical contents:
- papers and PDFs,
- URLs and web pages,
- videos and transcripts,
- conversations and local notes,
- source snapshots or durable pointers.

### Layer 1 — Intake / provisional understanding

Purpose:
- store source-bound, not-yet-canonical material,
- preserve provenance before abstraction,
- allow provisional extraction and ambiguity.

Typical contents:
- source registrations,
- raw notes,
- provisional claims,
- transcript fragments,
- intake maps.

### Layer 2 — Canonical reusable knowledge and active memory

Purpose:
- store reusable research memory,
- accumulate typed concepts, claim cards, derivation objects, methods, workflows, bridges, validation patterns, and warning notes,
- support cross-topic reuse,
- act as the active comparison surface for later stages.

This is the center of gravity of the system.

### Layer 3 — Research candidate / exploratory notebook

Purpose:
- store active research outputs that are still uncertain or too local to canonicalize,
- form explicit candidates for later adjudication,
- support exploratory work without polluting the canonical layer too early.

Typical contents:
- conjectures,
- failed attempts,
- partial derivations,
- anomalies,
- negative results,
- candidate objects,
- run-local interpretations,
- open technical questions.

### Layer 4 — Execution-backed validation surface

Purpose:
- judge whether Layer 3 candidates are ready to enter Layer 2,
- connect reasoning to execution or handoff when deeper checks are needed,
- preserve explicit keep / revise / reject / defer decisions.

Typical contents:
- validation plans,
- contradiction checks,
- benchmark or reproduction records,
- execution tasks,
- promotion decisions.

Layer 4 should be read as an **execution-backed validation surface**, not as a pure execution layer. Its role is to decide what must be checked, collect the evidence, and issue the verdict.

---

## Flow logic

The default route for non-trivial research material is:

`L0 -> L1 -> L3 -> L4 -> L2`

The low-risk exception route is:

`L0 -> L1 -> L2`

Three additional rules matter:
- `L2` is not only the end of the route; it should also be consulted during `L1`, `L3`, and `L4`.
- `L4` comes after explicit candidate formation, not instead of it.
- the system should pass typed references and explicit decisions between layers rather than copying whole artifacts everywhere.

This separation is essential. The system should not collapse source traces, canonical knowledge, exploratory research output, and validation records into one undifferentiated notebook.

---

## Research loop

The long-term research loop is:

1. source acquisition and registration,
2. provisional understanding and claim extraction,
3. candidate formation and exploratory work,
4. validation design and execution or handoff,
5. result evaluation,
6. structured writeback,
7. preservation of uncertainty where uncertainty remains real.

A complete version of the system should support explicit keep / revise / discard / defer decisions for non-trivial research outputs.

---

## Active memory and retrieval

The architecture is not meant to behave like a passive archive plus a chat layer.

`L2` should act as active memory:
- `L1` consults `L2` to normalize terminology and catch known traps,
- `L3` consults `L2` to reuse methods, derivation routes, workflows, and warnings,
- `L4` consults `L2` to choose validation patterns and compare against prior accepted knowledge.

This is one reason the project is not reducible to ordinary note-taking or ordinary RAG. The system needs stage-aware retrieval of typed research objects, not only text similarity.

---

## Human checkpoints

The project is explicitly human-in-the-loop.

Important checkpoints include:
- framing the research question,
- accepting high-impact claims,
- correcting scaffold structure,
- choosing a validation route,
- deciding how to treat results.

This is a deliberate design choice. The aim is not performative autonomy, but disciplined research collaboration.

---

## Current public implementation posture

At the current stage, the internal architecture is more mature than the public implementation.

What already exists at the public-architecture level:
- an L0-L4 baseline,
- artifact-first workflow,
- Layer 2 as canonical active memory,
- validation-aware promotion logic,
- explicit human checkpoints.

What still needs stronger public implementation:
- stable public schemas,
- cleaned helper scripts,
- broader worked examples,
- clearer adapter surfaces,
- stronger writeback discipline.

That gap is intentional. The public repository should stay honest and legible while deeper implementation details continue to stabilize.

---

## Design principles

1. **Evidence before speculation**
2. **Durable artifacts over chat-only output**
3. **Reusable knowledge over local residue**
4. **Layer 2 should function as active memory, not passive storage**
5. **Uncertainty should be preserved, not hidden**
6. **Human judgment remains central at high-impact points**
7. **The system should improve by compounding reusable research structure over time**
