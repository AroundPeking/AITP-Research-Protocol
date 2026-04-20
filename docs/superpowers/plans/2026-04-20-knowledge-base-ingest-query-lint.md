# Knowledge-Base Ingest Query Lint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a knowledge-base operating loop to AITP that feels useful to a theoretical physicist: ingest new material, query the layered archive honestly, lint it for scientific and structural hygiene, and navigate it through `index` and `log` surfaces.

**Architecture:** Reuse AITP’s existing layer discipline instead of building a generic wiki. Treat `L0` as raw immutable source substrate, `L1/L3/L4/L2` as layered wiki-like research surfaces, and protocols/templates as the schema layer. Then add bounded `ingest`, `query`, `lint`, `index`, and `log` operations that always preserve authority boundaries.

**Tech Stack:** Python 3, Markdown + YAML frontmatter, `unittest`, topic runtime surfaces, global canonical memory surfaces.

---

## File map

### Core protocol-kernel changes

- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`

### Skills

- Modify: `skills/skill-read.md`
- Modify: `skills/skill-frame.md`
- Modify: `skills/skill-continuous.md`

### Topic-local knowledge-base surfaces

- Create or scaffold: `topics/<topic_slug>/runtime/index.md`
- Create or scaffold: `topics/<topic_slug>/runtime/log.md`

### Global knowledge-base surfaces

- Create or scaffold: `L2/index.md`
- Create or scaffold: `L2/log.md`

### Tests

- Create: `tests/test_knowledge_base_ops.py`

---

### Task 1: Add Topic-Level `index` And `log` Surfaces

**Files:**
- Modify: `brain/mcp_server.py`
- Test: `tests/test_knowledge_base_ops.py`

- [ ] **Step 1: Write failing tests for topic `index` and `log` scaffolds**

Add tests:

```python
def test_topic_runtime_index_is_materialized(): ...
def test_topic_runtime_log_is_materialized(): ...
def test_topic_index_links_l1_l3_l4_l5_surfaces(): ...
```

The expected paths are:

```text
topics/<slug>/runtime/index.md
topics/<slug>/runtime/log.md
```

- [ ] **Step 2: Run the tests to verify these surfaces do not exist yet**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- topic `index` / `log` tests fail.

- [ ] **Step 3: Materialize topic `index.md`**

The topic index should include sections like:

```markdown
# Topic Index

## Source Basis
- L0 sources
- L1 source basis

## Research Notebook
- L3 active artifacts

## Validation
- L4 contracts and reviews

## Reusable Results
- promoted or pending `L2`-relevant units

## Writing
- flow notebook TeX
- L5 writing surfaces
```

- [ ] **Step 4: Materialize topic `log.md`**

The topic log should record dated events such as:

- source ingested
- contradiction registered
- derivation advanced
- validation outcome returned
- promotion requested/resolved
- flow notebook rendered

- [ ] **Step 5: Run the topic-surface tests**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- topic `index` and `log` tests pass.

---

### Task 2: Add Global `L2` `index` And `log` Surfaces

**Files:**
- Modify: `brain/mcp_server.py`
- Test: `tests/test_knowledge_base_ops.py`

- [ ] **Step 1: Write failing tests for global `L2` index/log**

Add tests:

```python
def test_global_l2_index_is_materialized(): ...
def test_global_l2_log_is_materialized(): ...
def test_global_l2_index_groups_units_by_family_and_regime(): ...
```

- [ ] **Step 2: Run the tests to verify these global surfaces do not exist yet**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- global `L2` index/log tests fail.

- [ ] **Step 3: Build global `L2/index.md`**

It should group reusable material by:

- family,
- regime,
- warning/negative-result relevance,
- topic-family bridge relevance.

- [ ] **Step 4: Build global `L2/log.md`**

It should record:

- promoted units,
- conflict receipts,
- version/reuse receipts,
- lint warnings that materially affect reusable memory.

- [ ] **Step 5: Run the global-surface tests**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- global `L2` index/log tests pass.

---

### Task 3: Add First-Class `ingest` And `query` Operations

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-read.md`
- Modify: `skills/skill-frame.md`
- Test: `tests/test_knowledge_base_ops.py`

- [ ] **Step 1: Write failing tests for `ingest` and `query` tools**

Add tests:

```python
def test_ingest_updates_l1_source_basis_and_topic_log(): ...
def test_query_returns_layer_aware_answer_packet(): ...
def test_query_does_not_promote_material_across_authority_boundaries(): ...
```

- [ ] **Step 2: Add a bounded `aitp_ingest_knowledge(...)` tool**

The tool should:

- register or update source-linked material,
- refresh the relevant `L1` surfaces,
- append an event to the topic `log.md`,
- avoid silently writing to `L2`.

- [ ] **Step 3: Add a bounded `aitp_query_knowledge(...)` tool**

The returned packet should include:

```python
{
    "question": "...",
    "answer": "...",
    "basis_layer": "L1" | "L3" | "L4" | "L2",
    "artifact_refs": [...],
    "regime_notes": [...],
    "authority_warning": "...",
}
```

This keeps answers layer-aware and regime-aware.

- [ ] **Step 4: Update `skill-read.md` and `skill-frame.md`**

They should explicitly mention:

- use `ingest` when new material is being brought in,
- use `query` only as a bounded consultation aid,
- do not treat a query answer as stronger than its basis layer.

- [ ] **Step 5: Run the ingest/query tests**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- `ingest` and `query` tests pass.

---

### Task 4: Add Knowledge-Base `lint`

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-continuous.md`
- Test: `tests/test_knowledge_base_ops.py`

- [ ] **Step 1: Write failing tests for `lint` findings**

Add tests:

```python
def test_lint_finds_unresolved_contradiction_records(): ...
def test_lint_finds_missing_regime_or_nonclaims_in_reusable_units(): ...
def test_lint_finds_orphaned_units_without_provenance_or_reuse_links(): ...
```

- [ ] **Step 2: Add `aitp_lint_knowledge(...)`**

It should return findings such as:

```python
{
    "severity": "error" | "warning",
    "kind": "unresolved_contradiction" | "missing_regime" | "broken_provenance" | "orphaned_unit",
    "artifact_path": "...",
    "message": "...",
}
```

- [ ] **Step 3: Append lint runs to the topic/global `log.md` surfaces**

Only summarize the run and count/severity in the log, not the full report.

- [ ] **Step 4: Update `skill-continuous.md`**

Add a rule:

```markdown
If the topic is being resumed after a long gap or before promotion, run the
knowledge-base lint and read high-severity findings first.
```

- [ ] **Step 5: Run the lint tests**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- `lint` tests pass.

---

### Task 5: Add Query Writeback Discipline

**Files:**
- Modify: `brain/mcp_server.py`
- Test: `tests/test_knowledge_base_ops.py`

- [ ] **Step 1: Write failing tests for query-result writeback**

Add tests:

```python
def test_source_grounded_query_writes_back_only_to_l1(): ...
def test_derivational_query_writes_back_only_to_l3(): ...
def test_reusable_writeback_still_requires_l2_promotion_gate(): ...
```

- [ ] **Step 2: Add `aitp_writeback_query_result(...)`**

This tool should route writeback by declared basis layer:

- `L1` answer -> `L1` note or bridge
- `L3` answer -> `L3` note
- `L4` answer -> `L4` summary
- `L2` writeback only through the normal promotion machinery

- [ ] **Step 3: Run the writeback-discipline tests**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- writeback-discipline tests pass.

---

### Task 6: Commit

- [ ] **Step 1: Run the full knowledge-base wave verification**

Run:

```powershell
python -m unittest tests.test_knowledge_base_ops -v
```

Expected:

- all knowledge-base tests pass.

- [ ] **Step 2: Commit**

```powershell
git add brain/mcp_server.py `
  skills/skill-read.md `
  skills/skill-frame.md `
  skills/skill-continuous.md `
  tests/test_knowledge_base_ops.py
git commit -m "feat: add layered knowledge-base ingest query lint surfaces"
```

---

## Verification checklist

- [ ] topic and global `index` / `log` surfaces exist
- [ ] `ingest`, `query`, and `lint` are first-class tools
- [ ] query answers remain layer-aware and regime-aware
- [ ] query writeback cannot bypass `L2` promotion discipline
- [ ] lint can find contradictions, missing regime/non-claims, and orphaned units
