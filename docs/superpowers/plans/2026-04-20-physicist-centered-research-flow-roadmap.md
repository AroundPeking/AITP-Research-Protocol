# Physicist-Centered Research Flow Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the umbrella AITP research-flow spec into a sequence of executable waves that Claude can implement safely and incrementally.

**Architecture:** Treat the overall program as six waves: foundation hardening, `brain + L1`, `L3 + flow TeX`, knowledge-base operations, `L4 + global L2`, and `L5 + real-topic e2e`. Each wave ends with a usable protocol surface and a verification gate, so later waves build on stable interfaces instead of rewriting moving targets.

**Tech Stack:** Python 3, `fastmcp`, `pyyaml`, Markdown + YAML frontmatter, LaTeX/XeLaTeX, `unittest`, real-topic fixture directories under `topics/`.

---

## Scope Check

The umbrella spec spans several independent but related subsystems:

- foundation safety and protocol-kernel hardening,
- stage/posture modeling and `L1` framing,
- `L3` subplane workflow and flow-end TeX archive output,
- knowledge-base `ingest/query/lint/index/log` operations,
- `L4` physics adjudication and `L2` promotion/memory,
- `L5` paper-writing and end-to-end acceptance.

These should **not** be executed as one giant plan.
Claude should execute them as separate wave plans in the order below.

## Execution Order

1. `docs/superpowers/plans/2026-04-20-foundation-safety-hardening.md`
2. `docs/superpowers/plans/2026-04-20-brain-l1-research-flow-wave1.md`
3. `docs/superpowers/plans/2026-04-20-l3-subplanes-and-flow-tex.md`
4. `docs/superpowers/plans/2026-04-20-knowledge-base-ingest-query-lint.md`
5. `docs/superpowers/plans/2026-04-20-l4-l2-physics-adjudication-and-memory.md`
6. `docs/superpowers/plans/2026-04-20-l5-writing-and-real-topic-e2e.md`

## Critical Bug Mapping

### P0 blockers

- Path contract inconsistency:
  fixed in Wave 0, then reused by Wave 1+
- Promotion gate bypass:
  fixed in Wave 0, extended in Wave 3
- `topic_slug` path traversal:
  fixed in Wave 0

### P1 work

- `_infer_status` incompleteness:
  replaced gradually by stage/gate evaluation in Waves 1-3
- missing transition tools:
  introduced in Waves 1-3
- session continuity fragility:
  fixed in Waves 0-1
- non-atomic file I/O:
  fixed in Wave 0
- non-normalized L2 promote:
  fixed in Wave 3
- global L2 merge/conflict/versioning:
  first usable implementation in Wave 3

### P2 cleanup

- stale `aitp_get_popup` references:
  removed in Wave 1
- duplicated YAML parse and skill maps:
  reduced in Waves 0-1
- append-only derivation log scalability:
  replaced by `L3` active-artifact + history structure in Wave 2
- trust classification redesign:
  introduced in Wave 3 as `basis x scope`

## Wave Contracts

### Wave 0: Foundation Safety Hardening

Outcome:

- safe topic-root resolution,
- safe slug handling,
- safe write semantics,
- promotion gate can no longer be bypassed by direct status mutation,
- stop/session continuity become topic-safe.

### Wave 1: Brain + L1 Stage Kernel

Outcome:

- `brain` reports `stage/posture/lane/gate_status`,
- `L1` question/source/convention/anchor/contradiction artifacts exist,
- `read` and `frame` postures are real.

### Wave 2: L3 Subplanes + Flow TeX

Outcome:

- `L3-I/P/A/R/D` hard gates exist,
- every research flow leaves a flow-end TeX notebook in the old `L3` spirit,
- TeX is emitted after research-flow completion, before paper writing.

### Wave 3: Knowledge-Base Ingest / Query / Lint

Outcome:

- AITP exposes first-class `ingest`, `query`, and `lint` operations,
- topic and global `index` and `log` surfaces exist,
- query results write back into the correct layer instead of a generic wiki,
- knowledge-base lint can surface contradictions, orphaned units, stale claims,
  missing provenance, and missing non-claims.

### Wave 4: L4 Physics Adjudication + Global L2 Memory

Outcome:

- six-outcome `L4`,
- physics-specific mandatory checks,
- global `L2` memory with version/conflict handling,
- safe promotion boundary and 2D trust classification.

### Wave 5: L5 Writing + Real-Topic E2E

Outcome:

- claim/equation/figure provenance surfaces,
- writing pipeline that consumes `L2/L3/L4` honestly,
- real-topic e2e tests that use the flow-end TeX output as the main quality gate.

## File Ownership Map

### Foundation and brain kernel

- `brain/`
- `hooks/`
- `skills/skill-continuous.md`

### Stage artifacts and L3 flow

- `skills/`
- `topics/<slug>/L1/`
- `topics/<slug>/L3/`

### Validation and reusable memory

- `topics/<slug>/L4/`
- global `canonical/` / `research/knowledge-hub/canonical/`-aligned surfaces
- promotion trace helpers

### Knowledge-base operations

- topic and global `index.md` / `log.md` surfaces
- query/writeback helpers
- lint and hygiene helpers
- consultation and retrieval glue

### Writing and e2e

- `topics/<slug>/L5_writing/`
- LaTeX helpers / templates
- e2e fixture topics and test runners

## Acceptance Gates

Claude should not start the next wave until the current wave passes its gate:

- Wave 0 gate: path, slug, promotion, and stop-hook tests green
- Wave 1 gate: `L1` brief/gate/hook/skill tests green
- Wave 2 gate: `L3` subplane tests green and flow-end TeX renders
- Wave 3 gate: `ingest/query/lint` tests green and index/log surfaces render
- Wave 4 gate: `L4` outcome tests green and `L2` promotion conflict tests green
- Wave 5 gate: one real topic per lane completes and emits acceptable flow-end TeX

## Coordination Rule For Claude

Claude should treat this roadmap as authoritative sequencing only.
For implementation details, it should open the specific wave plan and execute
that wave task-by-task.

## Verification Checklist

- [ ] Wave ordering is explicit
- [ ] P0/P1/P2 bugs are mapped to concrete waves
- [ ] The old-`L3`-style TeX archive output is explicitly part of Wave 2 and Wave 4
- [ ] Real-topic e2e with TeX output checking is explicitly part of Wave 4
- [ ] Knowledge-base `ingest/query/lint/index/log` is explicitly part of the roadmap
