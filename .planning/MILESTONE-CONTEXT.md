# Milestone Context Draft

Date: 2026-04-01
Source: post-topic-skill-projection ship
Status: draft

## Proposed Milestone

**Name:** Projection-First Formal-Theory Seed

**Goal:**
Extend `topic_skill_projection` beyond the TFIM `code_method` exemplar into one
bounded `formal_theory` seed lane, while preserving human-reviewed promotion
and explicit trust gates.

## Why this is the natural next step

The execution-projection milestone is now shipped:

- `topic_skill_projection` is a real L2 family
- runtime topics can materialize and surface projection artifacts
- TFIM proves the benchmark-first `code_method` seed lane
- human-reviewed promotion already lands in backend

The next unresolved question is no longer whether execution projections belong
in L2.
It is whether the same projection-first model survives a formal-theory lane
without collapsing trust boundaries.

The highest-value next step is therefore:

- keep the projection model
- seed it on one bounded formal-theory exemplar
- prove that the runtime stays honest when theorem-facing trust surfaces are the
  real gate

## Default Seed Candidate

- Jones Chapter 4 finite-product formal-closure acceptance
- current script surface:
  - `research/knowledge-hub/runtime/scripts/run_jones_chapter4_finite_product_formal_closure_acceptance.py`

Use Jones Chapter 4 as the default seed unless a cleaner bounded
`formal_theory` exemplar emerges during milestone definition.

## Target Features

- Allow `topic_skill_projection` to compile for one bounded `formal_theory`
  lane under stricter applicability rules than `code_method`
- Define the minimum formal-theory projection inputs:
  - reviewed theorem/candidate state
  - formal-theory review or equivalent trust ledger
  - strategy memory
  - explicit first-read / first-route guidance
- Expose the formal-theory projection through the same runtime read path used by
  TFIM, but without adapter/bootstrap auto-load
- Create one real formal-theory seed acceptance that:
  - generates the projection
  - creates the candidate ledger row
  - exercises human-reviewed promotion into backend
- Keep the projection explicitly separate from theorem truth claims or proof
  closure itself

## Candidate Scope Boundaries

- In scope:
  - formal-theory applicability rules for `topic_skill_projection`
  - runtime/compiler extensions needed for one bounded formal-theory seed
  - Jones Chapter 4 seed acceptance and promotion wiring
  - docs clarifying that a formal-theory projection is reusable execution memory,
    not a theorem certificate

- Out of scope:
  - adapter/bootstrap auto-load of formal-theory projections
  - broad multi-topic formal-theory generalization in one pass
  - auto-promotion of formal-theory projections
  - packaging-first product work

## Suggested First Requirements

- A bounded `formal_theory` topic can compile a `topic_skill_projection` only
  when its theorem-facing trust surfaces are explicitly ready.
- Non-ready formal-theory topics must return `blocked` or `not_applicable`
  honestly instead of manufacturing a reusable projection.
- Runtime status and must-read surfaces can expose the formal-theory projection
  once it is available.
- One real Jones Chapter 4 acceptance lane can generate and human-promote the
  projection into backend `units/topic-skill-projections/`.

## Notes

- This draft supersedes the previous topic-skill-projection milestone draft; that
  milestone is now shipped in code (`6445c59`).
- This is still a draft milestone context, not a locked roadmap.
- If priorities changed, adjust this file before running `gsd-new-milestone`.
