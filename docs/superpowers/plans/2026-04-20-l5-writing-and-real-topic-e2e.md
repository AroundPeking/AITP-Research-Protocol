# L5 Writing And Real-Topic E2E Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add provenance-heavy `L5` writing surfaces and real-topic end-to-end tests whose primary output check is the flow-end TeX notebook produced before paper writing.

**Architecture:** Keep the flow-end TeX notebook as the mandatory pre-paper archive of a completed research flow, then build `L5` on top of it with claim/equation/figure provenance maps. Real-topic acceptance should first inspect the flow notebook for scientific coherence and only then allow paper-writing checks.

**Tech Stack:** Python 3, LaTeX/XeLaTeX, Markdown + YAML frontmatter, real-topic fixtures, `unittest`.

---

## File map

- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-write.md`
- Create: `tests/test_l5_e2e.py`
- Create or modify: `scripts/render_flow_notebook.py`
- Create or modify: L5 helper/rendering scripts used by the repo

---

### Task 1: Add Provenance-Heavy L5 Scaffolds

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-write.md`
- Test: `tests/test_l5_e2e.py`

- [ ] **Step 1: Write failing tests for required L5 artifacts**

Add tests asserting that topic bootstrap or first write entry creates:

```text
L5_writing/outline.md
L5_writing/claim_evidence_map.md
L5_writing/equation_provenance.md
L5_writing/figure_provenance.md
L5_writing/limitations.md
```

- [ ] **Step 2: Create or scaffold the L5 artifacts**

These files must contain required sections, not just exist.

- [ ] **Step 3: Update `skill-write.md` to require them explicitly**

`skill-write.md` should block draft completion if provenance files are incomplete.

- [ ] **Step 4: Run the L5 scaffold tests**

Run:

```powershell
python -m unittest tests.test_l5_e2e -v
```

Expected:

- required L5 scaffold tests pass.

---

### Task 2: Make Flow-End TeX The Pre-Paper Gate

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-write.md`
- Test: `tests/test_l5_e2e.py`

- [ ] **Step 1: Write failing tests for the pre-paper TeX gate**

Add tests:

```python
def test_l5_write_is_blocked_if_flow_notebook_tex_missing(): ...
def test_l5_write_unblocks_after_flow_notebook_tex_exists(): ...
```

- [ ] **Step 2: Wire `aitp_get_execution_brief(...)` or write-entry logic to require flow TeX**

When `L5` is entered, block with:

```python
"gate_status": "blocked_missing_artifact"
"required_artifact_path": ".../L3/tex/flow_notebook.tex"
```

until the flow notebook exists.

- [ ] **Step 3: Run the TeX gate tests**

Run:

```powershell
python -m unittest tests.test_l5_e2e -v
```

Expected:

- pre-paper TeX gate tests pass.

---

### Task 3: Add Real-Topic E2E Fixtures

**Files:**
- Create or modify: fixture topics under `topics/` or fixture directories under `tests/fixtures/`
- Test: `tests/test_l5_e2e.py`

- [ ] **Step 1: Create three real-topic fixture families**

Use one topic each for:

- `formal_theory`
- `toy_numeric`
- `code_method`

Each fixture must include:

- L1 framing artifacts
- completed L3 flow artifacts
- at least one L4 review
- emitted flow notebook TeX

- [ ] **Step 2: Write failing e2e tests for each lane**

Add tests:

```python
def test_formal_theory_topic_emits_acceptable_flow_tex(): ...
def test_toy_numeric_topic_emits_acceptable_flow_tex(): ...
def test_code_method_topic_emits_acceptable_flow_tex(): ...
```

Acceptance should check the TeX for section presence:

- `Research Question`
- `Conventions And Regime`
- `Derivation Route`
- `Validation And Checks`
- `Current Claim Boundary`
- `Failures And Open Problems`

- [ ] **Step 3: Run the lane e2e tests to verify they fail before implementation is complete**

Run:

```powershell
python -m unittest tests.test_l5_e2e -v
```

Expected:

- at least one lane test fails until the fixtures and renderers are correct.

---

### Task 4: Add Final Paper-Writing Output Checks

**Files:**
- Modify: L5 writing renderer/helper
- Test: `tests/test_l5_e2e.py`

- [ ] **Step 1: Write failing tests for paper provenance**

Add tests asserting:

- every claim in `claim_evidence_map.md` points to an earlier `L2/L3/L4` artifact
- every equation in `equation_provenance.md` has a source classification
- `limitations.md` contains at least one explicit non-claim or unresolved issue

- [ ] **Step 2: Implement the provenance renderers**

Ensure the `L5` pipeline writes those provenance files before or alongside `draft.tex`.

- [ ] **Step 3: Run the full writing/e2e tests**

Run:

```powershell
python -m unittest tests.test_l5_e2e -v
```

Expected:

- writing and e2e tests pass across all three lanes.

---

### Task 5: Commit

- [ ] **Step 1: Run the full Wave 4 verification**

Run:

```powershell
python -m unittest tests.test_l5_e2e -v
```

Expected:

- all Wave 4 tests pass.

- [ ] **Step 2: Commit**

```powershell
git add brain/mcp_server.py `
  skills/skill-write.md `
  scripts/render_flow_notebook.py `
  tests/test_l5_e2e.py
git commit -m "feat: add l5 provenance and real-topic e2e gates"
```

---

## Verification checklist

- [ ] `L5` provenance files are required
- [ ] `flow_notebook.tex` is required before paper writing
- [ ] three real-topic lanes emit acceptable flow-end TeX
- [ ] paper provenance surfaces are explicit and test-backed
