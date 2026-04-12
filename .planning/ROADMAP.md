# Roadmap: v1.91 Real Topic L0 To L2 End-To-End Validation

## Result

`v1.91` is active.

## Strategic Framework: 5-Axis Advancement Model

All future AITP work is organized along five axes. Every backlog item (999.x)
and every new phase must declare which axis it belongs to.

```
AITP Advancement Model (v1.91+)
├── Axis 1: Layer-Internal Optimization
│   ├── L0 (Source): PDF/TeX parsing, default download-source, citation graph
│   ├── L1 (Intake): LLM replacing regex, content-aware chunking
│   ├── L2 (Canonical): knowledge population incentive, hygiene auto-fix
│   ├── L3 (Candidate): coverage audit completeness
│   ├── L4 (Adjudication): trust gate strictness calibration
│   ├── L5 (Publication): output factory
│   └── Human (HCI): status rendering, onboarding, jargon cleanup
│
├── Axis 2: Inter-Layer Connection Optimization
│   ├── L0→L1: source projection automation
│   ├── L1→L2: literature-intake fast path (Phase 165.2)
│   ├── L3→L4: coverage + trust audit pipeline
│   ├── L4→L2: promotion gate + auto-promote relaxation
│   └── L5←L2: publication from canonical knowledge
│
├── Axis 3: Layer-Internal Data Recording
│   ├── Schema evolution (topic_state, operation manifests)
│   ├── JSONL metrics collection (self-evolution loop)
│   └── Manifest-as-truth-source (integrity checks)
│
├── Axis 4: Global Infrastructure
│   ├── Protocol skeleton: crash recovery, state machine,
│   │   checkpoint-restore, deep pause
│   ├── Human experience: session summary, change diff,
│   │   progress indicator, progressive disclosure, feedback mechanism
│   └── Execution strategy: mode dispatch, escalation sensitivity,
│       loop detection, derivation retry intervention
│
└── Axis 5: AI Agent Integration
    ├── Agent governance: schema-level isolation, context injection
    │   with dedup, gatekeeper, deploy-guard equivalents
    └── Agent interface: natural-language steering, MCP routing,
        feedback mechanism, mechanical-first verification
```

### Backlog Mapping to Axes

| Axis | Backlog items |
|------|---------------|
| Axis 1 — Layer-Internal | 999.14, 999.15, 999.16, 999.17, 999.18, 999.19, 999.20, 999.1, 999.60, 999.61, 999.62, 999.63, 999.79, 999.80, 999.81, 999.84 |
| Axis 2 — Inter-Layer | 999.6 (Phase 165.2), 999.12 (Phase 165.2), 999.28, 999.29, 999.30, 999.82, 999.83 |
| Axis 3 — Data Recording | 999.7, 999.76, 999.78, 999.85 |
| Axis 4 — Global Infra | 999.8, 999.9, 999.10, 999.11, 999.13, 999.21, 999.22, 999.23, 999.24, 999.73, 999.77 |
| Axis 5 — Agent Integration | 999.5, 999.64, 999.74, 999.75 |

### Recommended Priority Sequence

1. **Axis 4 (Human experience) first** — without readable status, onboarding,
   and jargon cleanup, users cannot benefit from anything else.
2. **Axis 5 (Agent governance) second** — mechanical checks and agent isolation
   make the protocol trustworthy before adding more features.
3. **Axis 1 (Layer-internal) third** — once humans and agents can interact
   reliably, improve each layer's capability.
4. **Axis 2 (Inter-layer) fourth** — connect improved layers with optimized
   paths.
5. **Axis 3 (Data recording) cross-cutting** — self-evolution and integrity
   checks run in parallel with all other work.

### wow-harness Reference

Several backlog items (999.73–999.78) are directly inspired by the wow-harness
project (https://github.com/NatureBlueee/wow-harness), which governs AI coding
agents through mechanical hooks rather than prompt instructions. Key borrowable
insight: "use mechanical checks first, LLM evaluation only when mechanical
passes." See `BACKLOG.md` Tier 5 for details.

## Phases

- [ ] **Phase 165: Real Topic L0 To L2 End-To-End Validation**
- [ ] **Phase 165.1: Proof Engineering Knowledge Layer — Schema + Bootstrap**
- [ ] **Phase 165.2: Mode Envelope Runtime Enforcement + Literature Intake Fast Path**
- [ ] **Phase 165.3: HCI Foundation — Human-Readable Surfaces + Onboarding** *(Axis 4)*
- [ ] **Phase 165.4: Agent Governance — Mechanical Verification + Schema Isolation** *(Axis 5)*
- [ ] **Phase 165.5: L0/L1 Integration — DeepXiv Progressive Reading + Graphify Concept Graph** *(Axis 1 + Axis 2)*

## Target Outcome

- one real-topic run from an initial idea through the current public AITP
  entry surfaces
- one durable postmortem naming where the protocol helped, where it created
  friction, and what bounded outcome was actually reached
- one explicit issue ledger that routes discovered problems into GSD-visible
  follow-up work instead of leaving them implicit
- mode envelope enforcement that actually controls runtime behavior per mode
- a literature-intake fast path that lets papers deposit knowledge into L2
  staging without the full formal-theory audit pipeline
- human-readable status/next rendering as the default CLI output
- mechanical-first verification before expensive LLM evaluation

## Next Step

Execute Phase `165`.

### Phase 165: Real Topic L0 To L2 End-To-End Validation
**Axis:** all (diagnostic)

**Goal:** Close the next post-`v1.90` maturity gap by proving whether the
current AITP implementation is genuinely useful on a real topic from an
initial idea through one honest bounded research outcome.
**Requirements:**
- one real topic must run through the current public AITP entry surfaces from
  an initial idea
- the run must leave a durable postmortem and artifact-backed outcome
- every discovered issue must be converted into explicit GSD-tracked follow-up
  work
- the milestone must stay honest about whether the topic reached `L2`,
  `promotion-ready`, or a blocked / deferred state
**Depends on:** v1.90 completion
**Plans:** 1 plan

Plans:
- [ ] `165-01` Execute one real-topic E2E route and capture all findings into
  GSD-visible artifacts

### Phase 165.1: Proof Engineering Knowledge Layer — Schema + Bootstrap
**Axis:** Axis 1 (L2 internal) + Axis 3 (schema evolution)

**Goal:** Define the `proof_fragment` canonical schema, seed `strategy_memory.jsonl`
with Jones-topic discoveries, and create the first proof_fragment instance as
proof of concept.
**Requirements:**
- `schemas/proof-fragment.schema.json` must define `construction_steps`,
  `common_pitfalls`, `reuse_conditions`, `do_not_apply_when` fields
- `strategy_memory.jsonl` must be seeded with at least 6 rows from the Jones
  Lean formalization (codRestrict pattern, CoeFun workaround, sub_eq_zero
  direction, starProjection instance inference, ker bridge, show goal mismatch)
- one canonical `proof_fragment` instance must be created for the
  codRestrict-comp-subtype construction recipe
- `LAYER2_OBJECT_FAMILIES.md` must be updated with proof_fragment payload
  contract
**Depends on:** Phase 165 completion
**Plans:** 1 plan

Plans:
- [ ] `165.1-01` Define proof_fragment schema + seed strategy_memory + create
  first instance

### Phase 165.2: Mode Envelope Runtime Enforcement + Literature Intake Fast Path
**Axis:** Axis 4 (execution strategy) + Axis 2 (L1→L2 connection)

**Goal:** Make the 4 AITP operating modes (discussion, explore, verify, promote)
actually control runtime behavior instead of being decorative metadata, and add
a lightweight literature-intake fast path so papers can deposit useful knowledge
into L2 without the full formal-theory audit pipeline.

**Motivation:**
- `mode_envelope_support.py` already defines 4 modes and auto-selects the right
  one, but `runtime_bundle_support.py` does not actually vary context loading,
  escalation trigger sensitivity, or human-checkpoint gating by mode.
- There is no lightweight "read a paper → extract reusable knowledge → deposit
  into L2" path. Every topic must go through the full L0→L1→L3→L4→L2 pipeline
  even when the user just wants to capture literature notes as reusable memory.
- The L1 vault (raw/wiki/output) exists but nothing bridges it to L2 without
  formal coverage + formal-theory audit.

**Requirements:**

1. **Mode-aware runtime bundle generation:**
   - `runtime_bundle_support.py` must consult the selected mode when building
     `must_read_now` and `may_defer_until_trigger` lists.
   - Discussion mode: load only topic synopsis + research question + minimal
     source subset. Defer full L2 retrieval, promotion surfaces, validation
     bundles.
   - Explore mode: load research question + active candidate + relevant L1/L3
     artifacts. Defer promotion package, unrelated historical logs, broad L2.
   - Verify mode: load validation contract + selected candidate + execution
     surface. Defer unrelated L2 bodies and topic history.
   - Promote mode: load gate state + candidate + target backend + supporting
     artifacts. Defer unrelated topic history and future publication surfaces.

2. **Mode-aware human-checkpoint gating:**
   - `runtime_protocol.generated.md` must include the mode name and its
     human-checkpoint policy so agents can respect it without guessing.
   - The `mode_envelope` section in the runtime bundle must be top-level, not
     buried inside a sub-object, so progressive-disclosure readers hit it early.

3. **Literature-intake fast path (`literature` submode under `explore`):**
   - A new `literature` submode that activates when:
     - the topic lane is `formal_theory` or mixed, AND
     - the action involves source intake / reading / note extraction, AND
     - there is no active benchmark or proof obligation.
   - This submode enables a streamlined promotion path:
     - L0 source registration (existing)
     - L1 vault extraction: raw → wiki → output (existing)
     - L1→L2 provisional deposit: concepts, physical_pictures, methods, and
       warning_notes extracted from the source can be staged into L2 staging
       without full coverage audit or formal-theory audit.
     - Staged items get a `provenance.literature_intake_fast_path: true` tag.
     - A later full audit can promote them from staging to canonical, but the
       knowledge is immediately searchable in L2 consultation.
   - Entry: `aitp loop --topic-slug <slug> --human-request "Read and extract
     reusable knowledge from this paper" --skill-query "literature intake"`
   - Exit: when all extractable units from the current source are staged.

4. **`aitp intake-literature` CLI command (optional, for Phase 165.3):**
   - A dedicated entry point that combines source registration + L1 vault
     extraction + L2 staging in one call.
   - This is a convenience wrapper, not a bypass of the layer model.

5. **Mode-aware escalation trigger sensitivity:**
   - Discussion mode: escalation triggers fire on `direction_ambiguity` and
     `scope_change` only.
   - Explore mode: escalation triggers fire on `candidate_ready`, `route_change`,
     and `source_gap`.
   - Verify mode: escalation triggers fire on `validation_complete`,
     `contradiction_detected`, and `proof_obligation_resolved`.
   - Promote mode: escalation triggers fire on `gate_passed`, `gate_rejected`,
     and `human_override`.

6. **Acceptance test:**
   - A new acceptance script `run_mode_enforcement_acceptance.py` that:
     - bootstraps a topic, runs a discussion-mode loop, verifies the runtime
       bundle has discussion-mode context loading (minimal must_read, deferred
       validation).
     - advances to explore mode, verifies expanded context.
     - triggers verify mode, verifies L4-foreground loading.
     - triggers promote mode, verifies gate-state loading.
     - runs a literature-intake fast-path loop, verifies that L2 staging
       receives extractable units without full coverage audit.
   - All checks on isolated temp kernel root.

**Depends on:** Phase 165 completion (uses the real-topic E2E findings to
validate mode design against real friction).

**Plans:** 2 plans

Plans:
- [ ] `165.2-01` Implement mode-aware runtime bundle generation + mode-aware
  escalation trigger sensitivity + mode section promotion in runtime protocol
  markdown
- [ ] `165.2-02` Implement literature-intake fast-path submode + L2 staging
  bridge + acceptance test

### Phase 165.3: HCI Foundation — Human-Readable Surfaces + Onboarding
**Axis:** Axis 4 (human experience)

**Goal:** Make AITP usable by a physics researcher who has never seen it before.
Replace machine-first rendering with human-first defaults.

**Motivation:**
- HCI gap analysis (2026-04-13) identified 30 issues; 12 are pure HCI problems
  in Tier 1 and Tier 2.
- Dashboard outputs 40+ sections with no visual hierarchy.
- No onboarding, no tutorial, no getting-started.
- Jargon leaks into checkpoint questions despite explicit rules.
- 60+ CLI commands are flat with no grouping.

**Requirements:**

1. **Human-readable status/next rendering (999.60):**
   - Default `aitp status` output ≤10 lines: topic name, current mode, last
     action, next step, blocked items.
   - Full dashboard available via `--full` flag.
   - `aitp next` shows one actionable step, not a wall of context.

2. **First-run onboarding (999.61):**
   - `aitp hello` command: install check → create demo topic → show status →
     register a paper.
   - Runs in <2 minutes on a fresh install.
   - Zero jargon in all onboarding text.

3. **Jargon cleanup (999.62):**
   - Audit all checkpoint_questions templates.
   - Replace: "adjudication route" → "how to judge this", "L0 recovery" →
     "restart from source intake", "promotion approval" → "ready to save as
     reusable knowledge", "bounded route" → "chosen approach".
   - Add jargon-regex gate to CI.

4. **Progressive disclosure for CLI commands (999.63):**
   - `aitp help` shows Core (5 commands): session-start, status, next, work,
     consult-l2.
   - `aitp help --all` shows all 60+ commands with grouping.

5. **Natural-language steering (999.64):**
   - `aitp steer-topic --text "我想换个方向做X"` parses free text into
     structured steering internally.

6. **Error messages for humans (999.70):**
   - All subprocess failures produce actionable messages with suggested fixes.
   - No Python tracebacks in user-facing output.

**Depends on:** Phase 165 completion (uses real-topic friction findings).
**Plans:** TBD during discuss phase.

### Phase 165.4: Agent Governance — Mechanical Verification + Schema Isolation
**Axis:** Axis 5 (agent governance + agent interface)

**Goal:** Replace prompt-level constraints with mechanical enforcement where
possible. Make agent behavior deterministic for trust-critical operations.

**Motivation:**
- wow-harness demonstrated: "CLAUDE.md instruction compliance: ~20% / Hook
  enforcement: 100%"
- AITP's Skeptic-D relies on prompt-level "do not edit" — easily violated.
- AITP invokes LLM evaluation even for trivially checkable mechanical conditions.
- No observability into recurring agent behavior patterns across topics.

**Requirements:**

1. **Mechanical completion verification (999.73):**
   - Before LLM conformance audit: zero-cost check that all operations have
     `baseline_status: confirmed`, no unresolved gaps, no pending follow-ups.
   - Only invoke LLM if mechanical check passes.

2. **Schema-level agent isolation (999.75):**
   - Review/Skeptic agents' MCP tool manifests physically exclude write
     operations.
   - Not "please don't edit" — "you cannot edit".

3. **Context injection with dedup (999.74):**
   - Path-scoped fragment injection when agents edit theory artifacts.
   - Auto-inject notation bindings, prerequisite status, relevant L2 units.
   - Session-scoped dedup (1-hour TTL) to prevent token waste.

4. **JSONL metrics → self-evolution (999.76):**
   - Log all theory operations as append-only JSONL.
   - Periodic offline analysis for systematic patterns.
   - Surface actionable proposals with confidence scores.

5. **Derivation loop detection (999.77):**
   - Per-artifact retry counting within topic loop.
   - Inject strategy change suggestion after N retries on same approach.

6. **Manifest-as-truth-source (999.78):**
   - Declare what artifacts must exist at each topic state.
   - Enable integrity checks: "topic claims verify mode but
     validation_contract.md is missing".

**Depends on:** Phase 165.3 completion (human surfaces must exist first so
  agent governance improvements are visible to users).
**Plans:** TBD during discuss phase.

### Phase 165.5: L0/L1 Integration — DeepXiv Progressive Reading + Graphify Concept Graph
**Axis:** Axis 1 (L0 + L1 internal) + Axis 2 (L0→L1 connection)

**Goal:** Integrate design patterns from DeepXiv SDK (progressive arXiv reading)
and Graphify (knowledge graph construction from documents) into AITP's L0 source
layer and L1 intake layer, adapting them from a theoretical physicist's research
perspective. The integration borrows core logic and adapts it into AITP's existing
codebase — not a shallow `pip install`, but a deep internalization of their design
patterns with physics-specific extensions.

**Motivation:**
- L0 source registration currently stores papers as metadata-only (title, authors,
  abstract URL). No PDF parsing, no TeX parsing, no figure extraction. The 200–500
  character preview is the only content AITP ever sees.
- L1 intake runs 8 hardcoded regex patterns on that preview to extract assumptions,
  regimes, notation candidates, and contradictions. This is far too shallow for
  real physics research.
- DeepXiv SDK provides a 5-level progressive reading chain (brief → head → section
  → preview → raw) that is perfectly suited to AITP's mode-aware context loading.
  Currently integrated as a shallow `subprocess.run("deepxiv search ...")` fallback
  in `discover_and_register.py` — only search, no brief/head/section/TLDR.
- Graphify provides a complete local knowledge graph pipeline (LLM extraction →
  NetworkX construction → Leiden community detection → MCP query tools) with an
  LLM extraction prompt that includes 3-tier confidence (EXTRACTED/INFERRED/AMBIGUOUS)
  + numeric scores — directly usable for AITP's evidence-vs-speculation separation.
- Both tools are MIT License — copyright attribution in source files + NOTICE entry.

**External references:**
- Graphify v0.4.5: https://github.com/safishamsi/graphify
- DeepXiv SDK v0.2.4: https://github.com/DeepXiv/deepxiv_sdk

**Integration Architecture (3 layers):**

```
discover_and_register.py  (search candidates — existing)
        ↓
register_arxiv_source.py  (standard registration → source.json + snapshot.md — existing)
        ↓
[NEW] enrich_with_deepxiv.py  (use brief/head to fill provenance)
        ↓ enriched source with TLDR, section structure, keywords
[NEW] build_concept_graph.py  (use adapted Graphify LLM prompt → graph pipeline)
        ↓ concept_graph.json (nodes + edges + hyperedges + communities)
        ↓
L1 distillation  (source_distillation_support.py reads graph — existing, enhanced)
```

**Requirements:**

1. **Post-registration enrichment (`enrich_with_deepxiv.py`):**
   - After `register_arxiv_source.py` completes, run enrichment step that calls
     DeepXiv `brief()` for a ~200-token paper summary and `head()` for structured
     section list with `{name, idx, tldr, token_count}` per section.
   - Store enriched data in `provenance` sub-object of source.json (free-form,
     safe to extend without schema change).
   - Fields: `provenance.deepxiv_tldr`, `provenance.deepxiv_keywords`,
     `provenance.deepxiv_sections[]`, `provenance.deepxiv_github_url`.
   - Reuse DeepXiv SDK's `PaperInfo` TypedDict schema and section fuzzy matching
     (`_match_section_name()`) pattern.
   - Reuse exponential backoff retry pattern from DeepXiv SDK's `_retry()` method.
   - Graceful degradation: if DeepXiv cloud API is unavailable, proceed with
     metadata-only registration (existing behavior preserved).

2. **Concept graph construction (`build_concept_graph.py`):**
   - Adapt Graphify's LLM extraction prompt (skill.md ~L253-303) with
     physics-specific extensions:
     - **Node types**: `theorem`, `definition`, `conjecture`, `regime`,
       `approximation`, `notation_system`, `proof`, `equation`, `observable`
       (in addition to Graphify's existing `concept`, `method`, `finding`).
     - **Relation types**: `assumes`, `valid_in`, `contradicts`, `derives`,
       `notation_for`, `generalizes`, `special_case_of`, `implies`
       (in addition to Graphify's existing `depends_on`, `related_to`).
     - **Extraction targets**: assumptions (with validity conditions), notation
       conventions, approximation regimes, theorem-proof pairs, equation-observable
       links.
   - Preserve Graphify's 3-tier confidence model (EXTRACTED/INFERRED/AMBIGUOUS)
     with numeric scores — maps directly to AITP's evidence-vs-speculation separation.
   - Use Graphify's 3-layer dedup from `build.py` (exact → fuzzy → LLM-verified).
   - Use Graphify's Leiden community detection from `cluster.py` for automatic
     topic clustering.
   - Support hyperedges (3+ node relationships) for physics patterns like
     "theorem + assumption + approximation → conclusion".
   - Store output as `concept_graph.json` alongside source.json in the source directory.
   - Use Graphify's SHA256 per-file caching to avoid redundant LLM calls on
     re-processing.
   - Reuse Graphify's `extract_pdf_text()` (pypdf wrapper) for PDF-based sources.

3. **Progressive reading in L1 distillation:**
   - Replace brute-force preview truncation (currently 200–500 chars) with
     section-aware loading:
     - `brief()` (~200 tokens) → initial assessment
     - `head()` (~2K tokens) → section structure, decide what to read
     - `section()` (targeted) → specific sections relevant to research question
     - `raw()` (full paper) → only when deep analysis needed
   - Token-budget-aware loading by AITP mode (feeds into Phase 165.2's mode-aware
     runtime bundle):
     - Discussion mode: brief only
     - Explore mode: brief + head
     - Verify mode: brief + head + relevant sections
     - Promote mode: full access as needed
   - Reuse DeepXiv agent submodule's LangGraph ReAct pattern for token-budget
     management — agent decides whether to load more context based on research
     question relevance.

4. **Graph-based L1 intake extension:**
   - Add `concept_graph` key to L1 intake dict (safe extension — existing consumers
     ignore unknown keys).
   - Contents: `{nodes[], edges[], hyperedges[], communities[], god_nodes[]}`.
   - `god_nodes[]` uses Graphify's `god_nodes()` function to identify foundational
     concepts that many other concepts depend on — maps to AITP's prerequisite
     detection.
   - Preserve all 8 existing required L1 keys (`source_count`, `assumption_rows`,
     `regime_rows`, `reading_depth_rows`, `method_specificity_rows`,
     `notation_rows`, `contradiction_candidates`, `notation_tension_candidates`).
   - The graph data augments (does not replace) the regex patterns — the 8 regex
     fields remain populated as before, with graph data providing richer context.

5. **Analysis tools for L1→L2 connection:**
   - Adapt Graphify's `analyze.py` functions:
     - `surprising_connections()` → cross-domain links between sources
     - `suggest_questions()` → auto-generate research questions from graph structure
     - `graph_diff()` → track knowledge evolution across topic iterations
   - These feed into Phase 165.2's literature-intake fast path for L2 staging.

6. **Obsidian export path:**
   - Adapt Graphify's Obsidian vault export for direct compatibility with the
     theoretical-physics brain.
   - Export concept graph nodes as Obsidian notes with wikilinks for edges.
   - Community clusters map to Obsidian folders.

7. **MIT attribution:**
   - Copyright notice comments in all files that borrow code or patterns from
     Graphify or DeepXiv SDK.
   - Entry in AITP's NOTICE/LICENSE file listing both projects with MIT license
     text.

**Contract safety:**
- `source-item.schema.json` has `additionalProperties: false` at top level — new
  data goes into `provenance` and `locator` sub-objects (free-form, safe to extend).
- L1 intake dict accepts new keys without breaking downstream consumers.
- Existing pipeline continues to work if DeepXiv cloud API or graph construction
  is unavailable (graceful degradation).

**Depends on:** Phase 165.2 (mode-aware runtime must exist for progressive reading
  to vary by mode). Phase 165.5 can start L0 enrichment work immediately but
  progressive reading integration requires 165.2's mode dispatch.

**Plans:** 3 plans

Plans:
- [ ] `165.5-01` Implement post-registration enrichment (`enrich_with_deepxiv.py`)
  + concept graph construction (`build_concept_graph.py`) + MIT attribution
- [ ] `165.5-02` Implement progressive reading in L1 distillation + graph-based
  L1 intake extension + analysis tools for L1→L2 connection
- [ ] `165.5-03` Implement Obsidian export path + acceptance tests for full
  enrichment → graph → distillation pipeline
