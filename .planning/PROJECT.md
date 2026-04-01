# AITP vNext Runtime Hardening

## What This Is

This is the brownfield GSD planning layer for the canonical `AITP-Research-Protocol` repository. It turns the current AITP runtime-hardening push into explicit phases so protocol work, runtime changes, acceptance cases, and product-facing routing decisions can be executed and reviewed without losing the protocol-first character of the repo.

## Core Value

AITP must turn vague but meaningful research starts into bounded, durable, and explainable runtime state without pretending uncertainty is already resolved.

## Current Milestone: v1.2 Projection-First Formal-Theory Seed

**Goal:** Extend `topic_skill_projection` beyond the TFIM `code_method` exemplar into one bounded `formal_theory` seed lane with explicit trust gates and human-reviewed promotion.

**Target features:**
- formal-theory applicability rules for `topic_skill_projection`
- Jones Chapter 4 finite-product seed acceptance
- runtime read-path exposure without adapter/bootstrap auto-load
- docs that keep execution projection separate from theorem truth claims

## Requirements

### Validated

- [x] Phase 6 decision points, traces, chronicles, and lightweight runtime exist in the protocol/runtime surface.
- [x] Current-topic memory and topic resume surfaces are already durable across sessions.
- [x] Natural-language-first bootstrap exists across Codex, Claude Code, OpenCode, and OpenClaw adapters.
- [x] Source-heavy starts now prefer source-grounded `idea_packet`, research-question, and validation-route defaults over generic request text or heuristic queue blur.
- [x] Runtime status explainability now answers why a topic is here, what the route is, what the last evidence return was, and what human need remains.
- [x] Steering checkpoints can now materialize durable steering artifacts when the answer itself changes route semantics.
- [x] Run-local strategy memory can now be written, surfaced in runtime status, and consulted as bounded route guidance.
- [x] A real code-backed benchmark-first acceptance lane exists for the TFIM exact-diagonalization helper.
- [x] The repo now has an explicit AITP x GSD workflow contract for everyday use.
- [x] `topic_skill_projection` now exists as a first-class L2 family with runtime projection artifacts, TFIM seed acceptance, and human-reviewed promotion into backend `units/topic-skill-projections/`. - v1.1

### Active

- [ ] Define the next milestone as a projection-first formal-theory seed lane instead of another packaging-only cycle.
- [ ] Decide and scope the first formal-theory seed exemplar for `topic_skill_projection`, with Jones Chapter 4 finite-product closure as the current default candidate.
- [ ] Keep adapter/bootstrap auto-load out of scope until a non-`code_method` projection seed closes honestly.

### Out of Scope

- Replacing AITP's `L0 -> L1 -> L3 -> L4 -> L2` model with generic software-project milestones — the runtime remains authoritative for research state.
- Marketplace-grade packaging in this milestone — local convergence matters more than public polish right now.
- Broad feature expansion before topic-start sharpness improves — the bottleneck is the first bounded question, not more surface area.

## Context

- The canonical public/protocol repo is `D:\BaiduSyncdisk\repos\AITP-Research-Protocol`; this is the checkout where protocol and runtime changes should be developed.
- Existing handoff notes on `2026-03-28` and `2026-03-29` identify the main bottleneck as source/thesis-to-question distillation, especially for formal-theory starts.
- Commit `6445c59` shipped the `topic_skill_projection` milestone: schema, runtime compiler path, TFIM seed acceptance, and human-reviewed promotion are now live in the codebase.
- The current local planning gap is no longer whether execution projections belong in L2; it is whether the same projection-first model can survive a bounded `formal_theory` seed without weakening trust gates.
- `research/knowledge-hub/` is the installable runtime surface; repo changes should preserve adapter compatibility and protocol honesty.

## Constraints

- **Protocol**: Keep AITP protocol-first — GSD organizes execution, but AITP runtime artifacts remain the source of truth for research state.
- **Compatibility**: Do not break existing CLI, adapters, or runtime artifacts that already back current-topic continuation.
- **Brownfield**: Work with the existing dirty tree carefully; do not overwrite unrelated user changes.
- **Scientific Trust**: Prefer bounded, honest defaults over aggressive inference when source evidence is weak.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use GSD as a planning overlay for this repo | The codebase has active work but no phase/project scaffold yet | ✓ Good |
| Anchor the current milestone on topic-start sharpness and status explainability | Prior handoff notes identify this as the highest-value bottleneck | ✓ Good |
| Preserve protocol docs as the authority and use implementation-focused phases in GSD | Execution tracking should reflect real repo work without rewriting protocol semantics | ✓ Good |
| Treat source-grounded topic starts as higher priority than generic human-request defaults | The real bottleneck was thesis/paper to bounded question, not more protocol surface area | ✓ Good |
| Treat steering answers as durable route changes when they express continue/branch/redirect semantics | Answered checkpoints were otherwise archived without changing the loop | ✓ Good |
| Keep strategy memory non-promotional and surface it through runtime guidance instead of hidden heuristics | Route memory should influence bounded choices without pretending to be scientific truth | ✓ Good |
| Prove the code-method lane with a benchmark-first acceptance script instead of a synthetic stub | Code-backed work needed a real bounded exemplar to validate the lane model | ✓ Good |
| Write an explicit AITP x GSD coexistence note | The repo needed a durable answer to when coding belongs to AITP topics versus GSD repo execution | ✓ Good |
| Treat reusable execution memory as a real L2 family instead of leaving it hidden inside runtime state | `topic_skill_projection` needed to be promotable, reviewable, and backend-addressable rather than a local heuristic only | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? Move them to Out of Scope with reason.
2. Requirements validated? Move them to Validated with a phase or milestone reference.
3. New requirements emerged? Add them to Active.
4. Decisions worth preserving? Append them to Key Decisions.
5. If the product meaning drifted, update "What This Is" before more execution work lands.

**After each milestone:**
1. Review the whole document against what actually shipped.
2. Re-check Core Value against what the repo is now optimizing for.
3. Move shipped requirements to Validated and prune stale Active items.
4. Refresh Context with the real codebase state and the next milestone gap.

---
*Last updated: 2026-04-01 after shipping `topic_skill_projection` and resetting next-milestone direction*
