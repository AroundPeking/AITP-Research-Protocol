# Backlog Parking Lot: AITP Runtime And Knowledge Foundations

These items are parked between milestones.

- They are not active GSD phases.
- Their accumulated context lives under `.planning/backlog/`.
- When one is selected, promote it into the next milestone and create a fresh
  `.planning/REQUIREMENTS.md` plus `.planning/ROADMAP.md`.

## Recommended Milestone Sequence

The backlog should not be promoted as a flat list.
The intended next sequence is:

1. **Control-plane and paired-backend closure**
   - stabilize the unified architecture
   - make paired backend alignment and drift semantics explicit in runtime and
     maintenance workflows
   - keep `L2` trust surfaces distinct from downstream human-readable versus
     typed realizations
2. **L2 knowledge-network MVP**
   - define the minimum useful knowledge object subset
   - add `physical_picture`
   - add lightweight knowledge entry
   - seed one small real knowledge direction with nodes and edges
3. **Graph retrieval and consultation maturity**
   - graph traversal and search
   - progressive-disclosure retrieval
   - consultation that actually expands structured context instead of returning
     an empty library surface
4. **Document understanding and source intelligence**
   - source fidelity grading
   - citation graph traversal
   - assumption extraction and reading-depth tracking
   - better cross-paper comparison and contradiction handling
5. **Research judgment and theoretical validation**
   - symbolic / analytical reasoning path
   - analytical validation beyond numerical execution
   - decision-making that uses momentum, stuckness, and surprise rather than
     only heuristics
6. **Long-term collaborator memory**
   - collaborator profile
   - research trajectory memory
   - negative-result retention
   - cross-session continuity
7. **Low-bureaucracy exploration**
   - quick exploration mode
   - reduced artifact footprint
   - promotion path from quick exploration into full topic work
8. **Engineering polish and reliability**
   - CLI readability
   - Windows startup reliability
   - E2E and test quality
   - documentation repair
   - dependency pinning
9. **Publication/output layer**
   - `L5 Publication Factory` only after the research-collaborator core is
     genuinely stronger

## Near-Term Stabilization

### 999.1: L5 Publication Factory

**Goal:** Add a final `L5` publication/output layer that turns a completed
topic into a paper-grade writing package without changing scientific truth.
**Requirements:** `PUB-01`, `PUB-02`, `PUB-03`
**Context:** `.planning/backlog/999.1-l5-publication-factory/`

### 999.2: Fix CLI Human-Readable Output

**Goal:** `_emit()` in `aitp_cli.py:22-26` always outputs JSON regardless of
the `--json` flag. Implement a human-readable default output path so users get
actionable status summaries instead of raw JSON.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.2-fix-cli-human-readable-output/`

### 999.3: Add End-to-End Integration Tests

**Goal:** Add at least one subprocess-based E2E test that exercises
`aitp bootstrap -> aitp loop -> aitp status` against real temp-topic outputs.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.3-add-e2e-integration-tests/`

### 999.4: Fix SessionStart Windows Silent Failure

**Goal:** `hooks/run-hook.cmd:25` exits successfully when bash is missing on
Windows. Emit a warning so users can see that AITP session initialization did
not actually run.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.4-fix-sessionstart-windows-silent-failure/`

### 999.5: Add Complete Demo Topic For Onboarding

**Goal:** Add one worked demo topic, including transcript/history, that shows
the full `L0 -> L1 -> L3 -> L4 -> L2` lifecycle through natural user
interaction.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.5-add-complete-demo-topic/`

### 999.6: Service God Class Cleanup

**Goal:** `aitp_service.py` is still large and contains many one-line wrapper
methods. Remove thin wrappers where callers can use the extracted support
modules directly.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.6-service-god-class-cleanup/`

### 999.7: Decision Script Quality Fixes

**Goal:** Document and improve `decide_next_action.py` scoring, including the
hardcoded scoring constants and the duplicate `policy_ranked_pending`
definition.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.7-decision-script-quality/`

### 999.8: Schema And Contract Consistency

**Goal:** Fix the `follow_up_actions` contract/schema mismatch and document the
relationship between the root `schemas/` tree and
`research/knowledge-hub/schemas/`.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.8-schema-contract-consistency/`

### 999.9: Documentation Fixes

**Goal:** Repair the broken roadmap link, document the Python version
requirement, and consolidate scattered install guidance.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.9-documentation-fixes/`

### 999.10: Dependency Pinning

**Goal:** Add compatible upper bounds or a lockfile for currently open-ended
dependencies such as `mcp` and `jsonschema`.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.10-dependency-pinning/`

### 999.11: User Experience Friction Reduction

**Goal:** Reduce operator friction around excessive state files, lossy
subprocess errors, planning noise, and leaked Windows paths in runtime state.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.11-user-experience-friction/`

### 999.12: Test Suite Quality Improvement

**Goal:** Separate structural integrity checks from behavioral tests, remove
duplicated bootstrap fixtures, and upgrade critical CLI tests from mocks to
real service paths.
**Source:** User-perspective audit 2026-04-07
**Context:** `.planning/backlog/999.12-test-suite-quality/`

## L2 Knowledge Graph Evolution

These items were captured during the 2026-04-07 conceptual audit of the empty
L2 knowledge base and its overbuilt ontology surface.

### 999.13: Implement Graph Traversal And Search

**Goal:** Add graph expansion, dependency-edge traversal, and token-budgeted
knowledge-packet retrieval on top of the current empty `edges.jsonl` / tag-only
consultation path.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.13-implement-graph-traversal-and-search/`

### 999.14: Add Physical Picture Object Type

**Goal:** Add a first-class `physical_picture` knowledge object so AITP can
store physics intuition, heuristic arguments, formal analogs, and known
limitations rather than only formal concepts/theorems.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.14-add-physical-picture-object-type/`

### 999.15: Define MVP Type Subset For Knowledge Graph Seed

**Goal:** Define a smaller core subset of `concept`, `theorem_card`, `method`,
`assumption_card`, `physical_picture`, and `warning_note` so the graph can
start from real data before carrying the full 22-type ontology.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.15-define-mvp-type-subset-for-knowledge-graph-seed/`

### 999.16: Add Lightweight Knowledge Entry Path

**Goal:** Add a lightweight staging/CLI path for recording concepts outside the
full `L3 -> L4 -> L2` promotion bureaucracy, with later review into trusted
knowledge.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.16-add-lightweight-knowledge-entry-path/`

### 999.17: Implement Progressive Disclosure Retrieval For AI Context

**Goal:** Make AI retrieve an index first and request deeper knowledge payloads
on demand, rather than loading the full knowledge base into context.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.17-implement-progressive-disclosure-retrieval-for-ai-context/`

### 999.18: Seed First Direction Knowledge Graph

**Goal:** Seed one small real knowledge graph direction with 10-20 nodes and
dependency edges, then use it as the regression baseline for later L2 work.
**Source:** L2 knowledge graph conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.18-seed-first-direction-knowledge-graph/`

## Conceptual Gaps

These items came from the theoretical-physics collaborator audit of AITP's
current research loop.

### 999.19: Add Symbolic And Analytical Reasoning Path

**Goal:** Extend validation beyond executable numerical scripts to symbolic and
analytical work such as SymPy/Mathematica lanes, dimensional analysis, limiting
cases, and proof-sketch sanity checks.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.19-symbolic-analytical-reasoning-path/`

### 999.20: Add Research Judgment To Decision-Making

**Goal:** Replace purely keyword-and-score action routing with momentum,
stuckness, surprise capture, and lightweight research-judgment signals.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.20-research-judgment-in-decision-making/`

### 999.21: Make Layer Model Flexible For Real Research Iteration

**Goal:** Treat the AITP layer model more like a graph with iteration edges and
exploratory loops, not only as a serialized promotion pipeline.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.21-flexible-layer-model/`

### 999.22: Model Creativity, Taste, And Physical Intuition

**Goal:** Give the operator/research loop a place to represent elegance,
physical taste, preferred formalisms, and intuition-driven surprise handling.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.22-creativity-taste-and-physical-intuition/`

### 999.23: Cross-Session Collaborator Learning

**Goal:** Persist collaborator preferences, long-horizon concerns, and research
trajectory memory across sessions and across related topics.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.23-cross-session-collaborator-learning/`

### 999.24: Quick Exploration Mode With Low Bureaucracy

**Goal:** Add a lightweight `aitp explore` path that skips full topic bootstrap
and heavy artifact generation for short speculative sessions.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.24-quick-exploration-mode/`

### 999.25: Source Fidelity Grading

**Goal:** Distinguish peer-reviewed papers, arXiv preprints, blog posts,
informal notes, and verbal claims so evidence weight is visible and promotion
logic can use fidelity.
**Source:** Conceptual audit 2026-04-07
**Context:** `.planning/backlog/999.25-source-fidelity-grading/`

## L0-L4 Layer Audit

These items are the layer-specific follow-ups from the 2026-04-07 audit.

### 999.26: L0 Citation Graph Traversal And BibTeX Support

**Goal:** Add citation traversal, related-work suggestions, and BibTeX import /
export so literature navigation matches how physicists actually work.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.26-l0-citation-graph-and-bibtex/`

### 999.27: L1 Assumption Extraction And Reading Depth Model

**Goal:** Make intake track assumptions, reading depth, method specificity, and
contradictory assumptions instead of shallow keyword extraction alone.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.27-l1-assumption-extraction-reading-depth/`

### 999.28: L3 Scratch Mode And Negative Results Documentation

**Goal:** Add scratch notes, negative-result memory, candidate demotion, and
intermediate calculation logs so exploratory dead ends become durable knowledge
instead of disappearing.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.28-l3-scratch-mode-negative-results/`

### 999.29: L4 Analytical Validation Beyond Numerical Execution

**Goal:** Add limiting-case, dimensional, symmetry, cross-reference, and
self-consistency validation modes alongside current numerical execution checks.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.29-l4-analytical-validation/`

### 999.30: Cross-Layer Parallel Research And Context Carrying

**Goal:** Support parallel research actions, backward context carrying after
failed validation, cross-topic reuse, and pause/resume with richer continuity.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.30-cross-layer-parallel-research-context/`

### 999.31: Artifact Footprint Reduction

**Goal:** Audit and reduce the 14+ artifacts and 7+ subprocess calls produced
by a single topic step, aiming for a much smaller essential surface.
**Source:** L0-L4 layer audit 2026-04-07
**Context:** `.planning/backlog/999.31-artifact-footprint-reduction/`

### 999.32: Research Trajectory Recording And Mode Learning

**Goal:** Record what research modes the operator actually uses and learn from
full research arcs, rather than assuming a fixed predetermined pipeline.
**Source:** Research workflow learning discussion 2026-04-07
**Context:** `.planning/backlog/999.32-research-trajectory-recording-and-mode-learning/`

## Legacy Note

### Legacy: L2 Knowledge Compiler And Hygiene

**Status:** Retained for reference only.
**Why kept:** This older backlog note predates the shipped `v1.5` milestone and
the later conceptual L2 graph audit. It is now superseded by the newer L2
backlog cluster above, but its context may still be useful when selecting a
future milestone.
**Context:** `.planning/backlog/legacy-l2-knowledge-compiler-and-hygiene/`
