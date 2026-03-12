# Kernel for an AI Theoretical Physicist

> A human-in-the-loop research kernel for theoretical physics, built toward a human-AI collaborative theoretical physicist.

## Overview

This repository is an attempt to build the research core of a future **human-AI collaborative theoretical physicist**.

The goal is **not** to build a paper summarizer, a chat-only assistant, or a system that merely imitates the language of research. The goal is to build a disciplined research kernel that helps a human researcher and an AI system work together on real theoretical-physics problems.

In practical terms, that means combining:
- a callable source substrate for papers, notes, web material, and transcripts,
- provisional understanding before canonicalization,
- a canonical reusable knowledge base that acts as active memory,
- exploratory candidate formation from active investigation,
- explicit validation and adjudication,
- execution or handoff when deeper checking is required,
- structured writeback rather than one-off chat output,
- and human checkpoints at high-impact decisions.

The long-term target is ambitious:

> build toward a system that behaves less like a generic assistant and more like a human-AI collaborative theoretical-physics researcher.

But the current project is still a **research kernel**, not a finished AI physicist.

---

## Why this project exists

Modern AI systems can already produce fluent summaries, plausible derivations, and confident-sounding research talk. That is not enough.

What is often missing is:
- epistemic separation between evidence, interpretation, and speculation,
- durable artifacts rather than chat-only memory,
- reusable knowledge that compounds across topics,
- explicit validation routes,
- structured communication between stages,
- structured handling of uncertainty,
- and a disciplined loop from source acquisition -> understanding -> investigation -> evaluation -> writeback.

This project exists to address that gap.

---

## What the repository is trying to build

The repository aims to support a research workflow that can:

1. ingest sources,
2. extract and structure claims,
3. build reusable knowledge,
4. scaffold arguments or derivations,
5. design validation routes,
6. carry out or hand off deeper investigation,
7. evaluate what should be kept,
8. write back stable outcomes,
9. preserve uncertainty where uncertainty is real.

This is intended to support research tasks such as:
- literature mapping,
- theory comparison,
- concept clarification,
- claim tracking,
- idea evaluation,
- derivation scaffolding,
- validation planning,
- and eventually theory-to-execution closure.

---

## Core architecture

The current public baseline is an **L0-L4 research architecture**.

### Layer 0 — Source Substrate
This layer handles source acquisition, source identity, source reopening, and source expansion.

Examples:
- papers and PDFs,
- URLs and web pages,
- videos and transcripts,
- conversations and local notes.

Purpose:
- keep source provenance explicit,
- allow later stages to reopen evidence,
- support citation chasing and source expansion when new gaps appear.

### Layer 1 — Intake / Provisional Understanding
This layer stores source-bound, not-yet-canonical material.

Examples:
- paper intake,
- transcript chunks,
- reading notes,
- provisional claims,
- extraction fragments,
- unresolved source ambiguities.

Purpose:
- preserve provenance before abstraction,
- allow ambiguity and partial understanding,
- avoid premature canonicalization.

### Layer 2 — Canonical Reusable Knowledge and Active Memory
This is the center of gravity of the system.

It stores reusable research knowledge such as:
- concepts,
- claim cards,
- derivation objects,
- methods,
- workflows,
- bridge notes,
- validation patterns,
- warning notes,
- and transitional atomic notes where needed.

Purpose:
- accumulate reusable research memory,
- support cross-topic reuse,
- act as an active comparison surface during later reasoning,
- allow the system to compound over time.

### Layer 3 — Research Candidate / Exploratory Notebook
This layer stores active research output that is still uncertain or too local to canonicalize.

Examples:
- conjectures,
- failed attempts,
- partial derivations,
- anomalies,
- negative results,
- candidate objects,
- run-local interpretations,
- open technical questions.

Purpose:
- preserve high-value uncertainty,
- support active investigation,
- form explicit candidates for later adjudication,
- prevent exploratory material from polluting the canonical layer too early.

### Layer 4 — Execution-Backed Validation Surface
This layer judges whether Layer 3 candidates are ready to enter the canonical layer.

Examples:
- validation plans,
- contradiction checks,
- benchmark or reproduction records,
- execution tasks,
- promotion / revise / reject / defer decisions.

Purpose:
- make non-trivial acceptance decisions explicit,
- connect reasoning to execution or handoff when deeper checks are required,
- keep promotion into Layer 2 auditable rather than implicit.

Earlier internal drafts used a three-layer knowledge view. The current baseline keeps that epistemic separation but makes the source substrate and the validation surface explicit.

---

## Flow logic

The default route for non-trivial research material is:

`L0 -> L1 -> L3 -> L4 -> L2`

The low-risk exception route is:

`L0 -> L1 -> L2`

Three additional constraints matter:
- `L2` is not only the final writeback target; it should also be consulted during `L1`, `L3`, and `L4`.
- `L4` is not just a synonym for execution; it is the execution-backed validation surface that can dispatch execution or handoff when needed.
- direct `L1 -> L4 -> L2` should not replace explicit candidate formation in `L3`.

This separation is not cosmetic. It is the main way the project tries to avoid collapsing source traces, reusable knowledge, uncertain research output, and validation records into one mixed notebook.

---

## Design principles

1. **Human-in-the-loop, not fake autonomy**  
   Important framing, claim acceptance, validation choices, and interpretation checkpoints should remain visible to the human researcher.

2. **Evidence before speculation**  
   The system should distinguish what a source explicitly states, what follows by local reasoning, what is plausible but not established, and what is genuinely conjectural.

3. **Reusable knowledge over chat residue**  
   If something is worth keeping, it should become a durable artifact rather than remaining trapped in conversation history.

4. **Structure before fluency**  
   Good research support requires typed claims, provenance, assumptions, regimes, unresolved gaps, and validation routes—not just fluent paragraphs.

5. **Uncertainty should be preserved, not erased**  
   Failed attempts, anomalies, partial derivations, and unresolved contradictions may be valuable and should not be hidden.

6. **The system should compound over time**  
   The aim is not just to answer one prompt, but to accumulate reusable workflows, notes, methods, and research patterns that improve future work.

For a more explicit statement, see [`docs/design-principles.md`](docs/design-principles.md).

---

## Current status

This project is currently in an **early architecture-build phase**.

What already exists conceptually:
- an L0-L4 architecture baseline,
- Layer 2 as the center of gravity and active memory surface,
- a human-in-the-loop research posture,
- a draft closed-loop research workflow,
- the idea of canonical promotion from intake and feedback through explicit validation,
- and an emphasis on epistemic discipline.

What does **not** yet exist in mature public form:
- a complete stable implementation,
- polished public scripts,
- broad worked examples,
- standardized execution adapters,
- a fully mature result-writeback loop.

So the honest description is:

> this repository is building the kernel of a future human-AI collaborative theoretical-physics research system.

The public repository is intentionally cleaner and higher-level than the current internal working environment. That is deliberate: public wording should stay stable and honest while deeper schemas, examples, and adapters continue to harden.

---

## What this project is not

This project is not:
- a generic paper summarizer,
- a one-shot literature review generator,
- a fully autonomous theorem prover,
- a replacement for human research judgment,
- or a claim that AI can already do serious theoretical physics on its own.

---

## Repository structure

```text
AI-Theoretical-Physicist-Kernel/
  README.md
  LICENSE
  docs/
    architecture.md
    roadmap.md
    benchmark-cases.md
    design-principles.md
```

The public repository is intentionally minimal in its first release. The goal is to keep the public surface clean, legible, and honest while the deeper implementation is still being stabilized.

---

## Documentation map

- [`docs/architecture.md`](docs/architecture.md) — current architectural picture
- [`docs/roadmap.md`](docs/roadmap.md) — staged near- and medium-term development plan
- [`docs/benchmark-cases.md`](docs/benchmark-cases.md) — candidate benchmark-style research cases
- [`docs/design-principles.md`](docs/design-principles.md) — epistemic and workflow principles

---

## Near-term roadmap

### Phase 1 — Public kernel release
- publish the architecture and core ideas,
- clean the repository surface,
- export the first stable docs,
- provide a minimal public structure.

### Phase 2 — Stronger layer contracts and canonical memory
- improve canonical schemas,
- strengthen ids, linking, and provenance,
- define clearer handoff objects between layers,
- strengthen typed research artifacts.

### Phase 3 — Validation and writeback closure
- connect validation routes to execution or handoff,
- standardize result evaluation,
- improve promotion / revise / reject / defer decisions,
- improve writeback from exploratory runs into canonical knowledge.

### Phase 4 — Benchmark-style research cases
- literature-to-knowledge case,
- idea-evaluation case,
- theory-to-numerics case,
- theory-to-formalization case.

See [`docs/roadmap.md`](docs/roadmap.md) for the fuller version.

---

## Who this is for

This project is for people interested in:
- theoretical-physics research workflows,
- human-AI collaboration in deep technical domains,
- epistemically disciplined knowledge systems,
- structured scientific note-making,
- and systems that aim beyond chat-only assistance.

---

## Suggested GitHub description

**A human-in-the-loop research kernel for theoretical physics, built toward a human-AI collaborative theoretical physicist.**

---

## Suggested GitHub topics

- theoretical-physics
- ai-research
- human-ai-collaboration
- research-workflow
- knowledge-base
- scientific-reasoning
- physics
- llm
- epistemic-tools

---

## Status note

Early-stage architecture and workflow project. Public development should prioritize clarity, honesty, and a clean kernel over breadth.
