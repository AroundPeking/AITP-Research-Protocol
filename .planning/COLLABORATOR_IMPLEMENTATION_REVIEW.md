# AITP Collaborator Implementation Review

Status: working review

## Purpose

This file records the current implementation review for AITP when judged
against the target of becoming a real theoretical-physics collaborator rather
than only a disciplined research control plane.

It is organized by active system surface:

- `L0`
- `L1`
- `L2`
- `L3`
- `L4`
- runtime / decision / long-horizon collaboration

## Executive summary

AITP is already strong at:

- explicit research control,
- runtime visibility,
- mode and backedge doctrine,
- and promotion-governed writeback boundaries.

AITP is currently weak at:

- growing reusable knowledge from real work,
- understanding literature at a physicist level,
- preserving scratch and negative-result memory,
- and learning the collaborator over time.

Short form:

- strong control plane
- weak compounding research memory

## L0: Source substrate

### What is already good

- `source-layer/` is now a real persistent layer root rather than an implicit
  intake side effect.
- Sources have explicit registration helpers and durable source snapshots.

### Main current weaknesses

- There is still no true global source deduplication engine.
- The same paper may still be registered separately under multiple topic slugs.
- Citation graph traversal and source-fidelity grading are not active system
  capabilities yet.
- Source-family and cross-topic source reuse are still too weak for real
  literature-driven theoretical work.

### Why this matters in actual use

In real theoretical-physics work, the same source often matters across many
topics:

- one review paper
- one classic theorem paper
- one numerical benchmark paper
- one private note or thesis chapter

If AITP cannot treat those as one durable source identity with different
topic-local uses, it will repeatedly "relearn" source context instead of
compounding understanding.

### Recommended changes

- Add global source identity and deduplication.
- Add citation graph and source-neighbor traversal.
- Add source fidelity metadata and ranking.
- Add source-family summaries for multi-topic reuse.

## L1: Intake and provisional understanding

### What is already good

- The source-distillation path exists and is source-backed rather than purely
  chat-based.
- AITP can already infer a first lane and first validation route from source
  material.

### Main current weaknesses

- Distillation is still too shallow and too heuristic.
- It is closer to preview / summary / keyword extraction than to real
  assumption-aware reading.
- There is no real reading-depth model.
- There is no real assumption extraction pipeline.
- There is no strong cross-paper contradiction or notation-alignment process.

### Why this matters in actual use

A theoretical physicist does not only ask:

- what is the paper about?

They ask:

- what assumptions does it make?
- which regime is it valid in?
- what is actually proved and what is heuristic?
- how deeply have we read it?
- how does it conflict with another source?

Without those, AITP cannot become a strong literature collaborator.

### Recommended changes

- Add reading-depth states.
- Add assumption extraction and regime tracking.
- Add explicit notation and terminology alignment.
- Add cross-source contradiction and compatibility checks.

## L2: Reusable knowledge and consultation

### What is already good

- The trust split between canonical / compiled / staging is already strong.
- The paired human-readable plus typed backend design is now coherent.
- Compiled, hygiene, and staging helper surfaces already exist as contracts.

### Main current weaknesses

- The canonical store is still effectively empty in practice.
- `index.jsonl` and `edges.jsonl` are still empty.
- The graph is designed but not operational.
- Consultation is structurally present but substantively underpowered because
  there is too little real reusable material to retrieve.
- There is not yet a real paired-backend alignment and drift-maintenance
  operation.

### Why this matters in actual use

This is the single biggest blocker to AITP becoming smarter over time.

Right now AITP can accumulate:

- topic runtime state,
- validation notes,
- and promotion contracts.

But it still cannot accumulate a rich enough reusable knowledge network to
behave like a collaborator with memory.

### Recommended changes

- Build an `L2` MVP around real data, not only ontology.
- Seed one real direction with 10-20 nodes and explicit edges.
- Add graph traversal and expansion.
- Add progressive-disclosure retrieval over actual knowledge packets.
- Add lightweight entry for reusable insights discovered in discussion.
- Add paired-backend drift audit and rebuild workflows.

## L3: Candidate formation and notebook work

### What is already good

- The candidate contract is explicit and disciplined.
- `L3 -> L4` handoff is much clearer than in many research-agent systems.
- Topic skill projection provides a useful reusable route capsule for some
  lanes.

### Main current weaknesses

- `L3` is still too formalized around adjudicable candidates.
- It lacks strong first-class support for:
  - scratch work
  - route comparisons
  - negative results
  - heuristic physical pictures
  - partial arguments that are worth remembering but not yet promotable

### Why this matters in actual use

Real theoretical progress is full of useful intermediate objects:

- "this route fails because the limit is singular"
- "this intuitive picture works only in weak coupling"
- "this derivation sketch suggests the right variable change"

Those should not disappear merely because they are not yet theorem cards or
promotion-ready candidates.

### Recommended changes

- Add `scratch` and `negative_result` object families.
- Add `physical_picture` as a first-class reusable structure.
- Add explicit route-comparison artifacts.
- Add demotion / retirement flow for dead-end candidates.

## L4: Validation and adjudication

### What is already good

- `L4` is not just prose; it has execution-task and result contracts.
- Formal-theory review, coverage, promotion gates, and Lean-bridge slices are
  much stronger than before.
- Execution-lane checkpoints and operator confirmation already exist.

### Main current weaknesses

- The protocol is ahead of the actual execution variety.
- Numerical and formal surfaces exist, but the broader theoretical-physics
  validation palette is still too narrow.
- Limiting-case checks, dimensional analysis, symmetry checks, analytical
  sanity checks, and source-consistency checks are not yet first-class
  everyday validators.
- Validation still relies too much on rigid route definitions rather than
  adaptive scientific judgment.

### Why this matters in actual use

A theoretical physicist often trusts a result because:

- it respects a symmetry,
- it matches a known limit,
- it has the right scaling,
- it agrees with a benchmark theorem,
- or it fails in a revealing way.

If AITP treats validation mainly as executable-task orchestration, it will
remain weaker than a real collaborator for analytical work.

### Recommended changes

- Add analytical validation families.
- Add symbolic replay and derivation-check routes.
- Add source-consistency and comparison validators.
- Let `L4` return rich partial outcomes without pretending every useful check
  is full closure.

## Runtime, decision, and collaboration memory

### What is already good

- Runtime mode, progressive disclosure, and backedge doctrine are already
  unusually strong.
- The operator checkpoint system is a real asset.
- The runtime bundle is rich enough to support bounded execution and review.

### Main current weaknesses

- Decision selection is still heuristic-heavy.
- Research momentum, stuckness, surprise, and collaborator preference are not
  yet durable decision inputs.
- There is no real collaborator profile yet.
- There is no real research trajectory memory yet.
- Quick, low-bureaucracy exploration is not yet a first-class path.

### Why this matters in actual use

This is the difference between:

- a system that can resume a topic,
- and a system that remembers how *you* think, what you care about, and which
  routes have already failed.

### Recommended changes

- Add collaborator profile and cross-session preference memory.
- Add research trajectory summaries and route history.
- Add stuckness / surprise / momentum-aware decision support.
- Add quick exploration mode with low artifact overhead.

## Cross-cutting issue: lane completeness

The current lane set is still not enough for all intended use cases.

Most importantly:

- `first_principles` exists as a research mode, but is still folded into
  `toy_numeric` at the lane level.
- `theory_synthesis` is acknowledged doctrinally but not implemented as a real
  working lane.

### Why this matters

For real use, these are distinct:

- toy-model benchmark work
- first-principles / ab initio / GW / QSGW / many-body numerics
- cross-paper and cross-framework theory synthesis

If AITP compresses them into the wrong lane, it will make the wrong choices
about:

- validation style
- artifact granularity
- reusable method memory
- and operator-facing next steps

### Recommended changes

- Split `first_principles` from `toy_numeric` as a real lane.
- Add `theory_synthesis` as a bounded but first-class lane.

## Priority judgment

If the goal is "become a real theoretical-physics collaborator", optimize in
this order:

1. make `L2` actually grow from real work
2. make `L1` read like a physicist
3. make `L4` validate like a physicist
4. make runtime decisions and memory collaborator-aware
5. only then spend major effort on publication polish

## One-line conclusion

AITP is already a serious research control plane, but to become a real
theoretical-physics collaborator it must shift emphasis from protocol strength
toward compounding knowledge, analytical judgment, and long-horizon
collaborative memory.
