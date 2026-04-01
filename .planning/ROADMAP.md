# Roadmap: AITP Runtime And Execution Projections

## Milestones

- ✅ **v1.0 Runtime Hardening** — Phases 1-5 (shipped 2026-03-31)
- ✅ **v1.1 L2 Topic-Skill Projection** — retrospective ship capture in commit `6445c59` (shipped 2026-04-01)
- ✅ **v1.2 Projection-First Formal-Theory Seed** — Phases 06-09 (shipped 2026-04-01)

## Overview

The next milestone should not expand packaging or adapter auto-load first.
It should prove that the projection-first model survives one bounded
`formal_theory` lane under honest trust gates, using Jones Chapter 4 as the
default seed exemplar.

## Phases

- [x] **Phase 1: Topic-Start Hardening** - Shipped in v1.0.
- [x] **Phase 2: Steering And Checkpoint Durability** - Shipped in v1.0.
- [x] **Phase 3: Strategy Memory Integration** - Shipped in v1.0.
- [x] **Phase 4: Code-Backed Acceptance Lane** - Shipped in v1.0.
- [x] **Phase 5: AITP x GSD Workflow Contract** - Shipped in v1.0.
- [x] **Phase 06: Formal-Theory Projection Contract** - Define the applicability, payload semantics, and trust gates for a bounded `formal_theory` projection.
- [x] **Phase 07: Runtime Read-Path Extension** - Extend compiler/runtime surfaces so a ready formal-theory projection appears in existing read paths without changing adapter auto-load.
- [x] **Phase 08: Jones Seed Exemplar And Promotion** - Make the Jones Chapter 4 lane generate, surface, and human-promote the formal-theory projection.
- [x] **Phase 09: Docs And Regression Closure** - Lock the milestone with docs and regression coverage that keep projection semantics honest.

## Phase Details

### Phase 06: Formal-Theory Projection Contract
**Goal**: Define when a `formal_theory` topic may materialize a reusable execution projection and what that projection is allowed to claim.
**Depends on**: v1.1 topic-skill projection ship
**Requirements**: [FTS-01, FTS-02, FTS-03]
**Success Criteria** (what must be TRUE):
  1. `formal_theory` projection applicability is tied to explicit run-local trust artifacts instead of heuristic optimism.
  2. Non-ready theorem-facing topics return `blocked` or `not_applicable` honestly and do not create promotion-ready projection candidates.
  3. Projection payload semantics distinguish reusable execution guidance from theorem truth claims or proof closure.
**Plans**: 2 plans

Plans:
- [x] 06-01: Define the formal-theory applicability contract and payload semantics for `topic_skill_projection`.
- [x] 06-02: Update service and schema gates so non-ready formal-theory topics fail honestly without writing false candidates.

### Phase 07: Runtime Read-Path Extension
**Goal**: Surface the formal-theory projection through the existing runtime read path while leaving adapter/bootstrap behavior unchanged.
**Depends on**: Phase 06
**Requirements**: [RTS-01, RTS-02]
**Success Criteria** (what must be TRUE):
  1. `topic_status()`, `topic_next()`, runtime protocol, and dashboard expose the formal-theory projection when it is `available`.
  2. `must_read_now` includes the projection only when it is truly readable and ready.
  3. Adapter/bootstrap auto-load remains untouched in this milestone.
**Plans**: 1 plan

Plans:
- [x] 07-01: Extend the runtime read-path and dashboard surfaces for formal-theory projections without changing bootstrap behavior.

### Phase 08: Jones Seed Exemplar And Promotion
**Goal**: Prove the formal-theory seed lane on one bounded real topic, with the same human-reviewed promotion path used by TFIM.
**Depends on**: Phase 07
**Requirements**: [JNS-01, JNS-02]
**Success Criteria** (what must be TRUE):
  1. The Jones Chapter 4 acceptance lane can generate a formal-theory `topic_skill_projection`.
  2. The acceptance flow writes the projection candidate row and exercises request/approve/promote without pretending auto-promotion is allowed.
  3. The promoted unit lands in backend `units/topic-skill-projections/` with provenance back to the Jones seed inputs.
**Plans**: 1 plan

Plans:
- [x] 08-01: Wire the Jones Chapter 4 acceptance lane through formal-theory projection generation, candidate sync, and human-reviewed promotion.

### Phase 09: Docs And Regression Closure
**Goal**: Lock the formal-theory seed milestone with docs and tests that keep projection semantics honest and discoverable.
**Depends on**: Phase 08
**Requirements**: [DOC-01]
**Success Criteria** (what must be TRUE):
  1. Docs explain that a formal-theory projection is reusable execution memory rather than theorem certification.
  2. Tests cover schema/runtime/promotion behavior for the formal-theory seed lane.
  3. The next milestone can build on this seed without re-opening the basic trust-boundary question.
**Plans**: 1 plan

Plans:
- [x] 09-01: Add milestone docs and regression coverage for projection-first formal-theory seed semantics.

## Archived Phase Details

<details>
<summary>v1.0 Runtime Hardening (Phases 1-5)</summary>

### Phase 1: Topic-Start Hardening
**Goal**: Convert source-heavy starts into sharper `idea_packet` defaults and truthful runtime status surfaces.
**Depends on**: Nothing (first phase)
**Requirements**: [START-01, START-02, START-03, STAT-01, STAT-02, STAT-03]
**Plans**: 3 plans, all complete

### Phase 2: Steering And Checkpoint Durability
**Goal**: Make true human choices durable and authoritative before the loop continues.
**Depends on**: Phase 1
**Requirements**: [STEER-01, STEER-02]
**Plans**: 1 plan, complete

### Phase 3: Strategy Memory Integration
**Goal**: Capture and reuse bounded route lessons from runs without overstating scientific certainty.
**Depends on**: Phase 2
**Requirements**: [MEM-01, MEM-02]
**Plans**: 1 plan, complete

### Phase 4: Code-Backed Acceptance Lane
**Goal**: Demonstrate that AITP can govern a real code-backed research topic with benchmark-first discipline.
**Depends on**: Phase 3
**Requirements**: [ACC-01]
**Plans**: 1 plan, complete

### Phase 5: AITP x GSD Workflow Contract
**Goal**: Make the repo's everyday execution model explicit: when GSD drives repo work and when AITP runtime governs the task.
**Depends on**: Phase 4
**Requirements**: [ACC-02]
**Plans**: 1 plan, complete

</details>

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Topic-Start Hardening | 3/3 | Complete | 2026-03-31 |
| 2. Steering And Checkpoint Durability | 1/1 | Complete | 2026-03-31 |
| 3. Strategy Memory Integration | 1/1 | Complete | 2026-03-31 |
| 4. Code-Backed Acceptance Lane | 1/1 | Complete | 2026-03-31 |
| 5. AITP x GSD Workflow Contract | 1/1 | Complete | 2026-03-31 |
| 6. Formal-Theory Projection Contract | 0/2 | Not started | - |
| 7. Runtime Read-Path Extension | 1/1 | Complete | 2026-04-01 |
| 8. Jones Seed Exemplar And Promotion | 1/1 | Complete | 2026-04-01 |
| 9. Docs And Regression Closure | 1/1 | Complete | 2026-04-01 |
