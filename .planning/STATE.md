---
gsd_state_version: 1.0
milestone: v1.91
milestone_name: Real Topic L0 To L2 End-To-End Validation
status: milestone_active
stopped_at: "Added Phase 165.5 (L0/L1 Deep Integration: DeepXiv + Graphify) with 7 backlog items 999.79–999.85"
last_updated: "2026-04-14T12:00:00+08:00"
last_activity: 2026-04-14
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 5
  completed_plans: 0
  percent: 0
---

# Project State

## Current Position

Status: milestone `v1.91` active; Phase 165.5 (L0/L1 Deep Integration) added to
  ROADMAP with 3 plans covering DeepXiv progressive reading enrichment,
  Graphify-adapted concept graph construction, progressive reading in L1
  distillation, graph-based intake extension, analysis tools for L1→L2, Obsidian
  export, and MIT attribution. Backlog items 999.79–999.85 created.

## Immediate Next Step

- current milestone: `v1.91` `Real Topic L0 To L2 End-To-End Validation`
- next phase boundary: execute Phase `165`, then `165.1`, `165.2`, `165.3`,
  `165.4`, `165.5`

## Accumulated Context

### 5-Axis Advancement Framework (2026-04-13)

**Canonical reference**: `.planning/AXIS_TAXONOMY.md` — contains axis
definitions, intent-signal keywords, decision tree, and complete
backlog-to-axis mapping (999.1–999.78 + all ROADMAP phases). GSD agents
MUST consult this file when classifying new work.

All future AITP work is organized along five axes:

1. **Layer-Internal Optimization** — improve each layer's capability (L0 PDF
   parsing, L1 LLM extraction, L2 population, Human HCI)
2. **Inter-Layer Connection Optimization** — optimize paths between layers
   (L0→L1, L1→L2 fast path, L3→L4, L4→L2, L5←L2)
3. **Layer-Internal Data Recording** — schema evolution, JSONL metrics,
   manifest-as-truth-source
4. **Global Infrastructure** — protocol skeleton, human experience, execution
   strategy (mode dispatch, loop detection)
5. **AI Agent Integration** — agent governance (schema isolation, context
   injection) and agent interface (natural-language steering, MCP routing)

Priority sequence: Axis 4 (human experience) → Axis 5 (agent governance) →
Axis 1 (layer capability) → Axis 2 (inter-layer) → Axis 3 (data recording,
cross-cutting).

### Roadmap Evolution

- `v1.90` is now archived after shipping explicit hypothesis-aware route
  transition-authority visibility
- Phase `165` is promoted into the new active milestone `v1.91`
- `v1.91` centers the next scope on real-topic utility validation and explicit
  GSD issue capture instead of inventing more local protocol surface first
- Comprehensive HCI gap analysis (2026-04-13) identified 30 issues across 6
  tiers; all captured as 999.60–999.70 in BACKLOG.md
- wow-harness comparison (2026-04-13) identified 6 borrowable patterns; all
  captured as 999.73–999.78 in BACKLOG.md

### Protected Closed Scope

- keep the shipped route-transition and adoption surfaces closed unless a fresh
  regression appears
- use the current public entry surfaces first instead of bypassing them with
  seeded hidden artifacts
- do not assume GSD will auto-discover arbitrary issues from runtime artifacts
  alone; capture them explicitly during the milestone

### Mode Envelope Context

- `docs/AITP_MODE_ENVELOPE_PROTOCOL.md` defines the 4 modes (discussion,
  explore, verify, promote) with draft working doctrine status
- `mode_envelope_support.py` already has mode specs, auto-selection, and
  markdown rendering
- The gap: runtime bundle generation does not actually vary context loading
  by mode, and there is no lightweight literature-intake fast path
- Phase 165.2 addresses both gaps after Phase 165 validates real-topic friction

### wow-harness Reference

- wow-harness (https://github.com/NatureBlueee/wow-harness) governs AI coding
  agents through mechanical hooks rather than prompt instructions
- Core insight: "CLAUDE.md instruction compliance: ~20% / Hook enforcement:
  100%" — mechanical constraints beat prompt constraints
- Key borrowable patterns: mechanical-first verification, context injection
  with dedup, schema-level agent isolation, JSONL self-evolution, loop
  detection, manifest-as-truth-source
- See BACKLOG.md Tier 5 (999.73–999.78) for details

### DeepXiv SDK + Graphify Integration (2026-04-14)

**DeepXiv SDK** (MIT, v0.2.4): Cloud API client for progressive arXiv reading.
Key borrowable patterns: 5-level reading chain (brief→head→section→preview→raw),
`PaperInfo` TypedDict schema, token-budget-aware agent mode (LangGraph ReAct),
section fuzzy matching, exponential backoff retry. Currently integrated as
shallow `subprocess.run("deepxiv search ...")` fallback — only search, no
brief/head/section/TLDR. What's cloud-only: search index, trending signals, all
paper parsing. What's borrowable locally: progressive reading paradigm, schema,
token-budget pattern, exception hierarchy, retry logic.

**Graphify** (MIT, v0.4.5): Local Python library for knowledge graph construction.
Key borrowable patterns: LLM extraction prompt with 3-tier confidence
(EXTRACTED/INFERRED/AMBIGUOUS) + numeric scores, 3-layer dedup (exact→fuzzy→LLM),
Leiden community detection, `analyze.py` functions (god_nodes,
surprising_connections, suggest_questions, graph_diff), hyperedge support, SHA256
caching, Obsidian export, PDF text extraction. What needs adaptation for physics:
add physics-specific relation/node types, extraction targets (assumptions,
validity regimes, notation conventions).

**Integration architecture:**
```
register_arxiv_source.py → enrich_with_deepxiv.py → build_concept_graph.py → L1
```
Phase 165.5 covers this with 3 plans and 7 backlog items (999.79–999.85).
Depends on Phase 165.2 (mode-aware runtime) for progressive reading integration.
