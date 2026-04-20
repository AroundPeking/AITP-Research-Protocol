# L3 Subplanes And Flow TeX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement hard-gated `L3-I/P/A/R/D` workflow plus an old-`L3`-style TeX notebook that is emitted after each completed research flow, before any paper-writing begins.

**Architecture:** Build `L3` around active Markdown artifacts and execution-brief gating rather than a single append-only derivation log. Then add a dedicated flow-end notebook compiler that turns the completed research flow into a TeX artifact for inspection, separate from `L5` paper-writing.

**Tech Stack:** Python 3, Markdown + YAML frontmatter, LaTeX/XeLaTeX, `unittest`, topic fixture directories.

---

## File map

- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`
- Create: `skills/skill-l3-ideate.md`
- Create: `skills/skill-l3-plan.md`
- Create: `skills/skill-l3-analyze.md`
- Create: `skills/skill-l3-integrate.md`
- Create: `skills/skill-l3-distill.md`
- Create: `tests/test_l3_subplanes.py`
- Create: `scripts/render_flow_notebook.py`
- Create: `topics/<topic_slug>/L3/tex/README.md` support path via bootstrap/templates

---

### Task 1: Introduce Hard-Gated L3 Subplanes

**Files:**
- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Test: `tests/test_l3_subplanes.py`

- [ ] **Step 1: Write failing subplane tests**

Add tests for:

```python
def test_new_l3_topic_starts_in_ideation_when_l1_is_complete(): ...
def test_l3_cannot_skip_from_ideation_to_analysis(): ...
def test_l3_requires_active_artifact_per_subplane(): ...
```

- [ ] **Step 2: Implement `L3-I/P/A/R/D` active-artifact evaluation**

Add active paths:

```python
L3/ideation/active_idea.md
L3/planning/active_plan.md
L3/analysis/active_analysis.md
L3/result_integration/active_integration.md
L3/distillation/active_distillation.md
```

Return subplane-aware brief data:

```python
"stage": "L3",
"l3_subplane": "ideation",
"gate_status": "blocked_missing_field",
...
```

- [ ] **Step 3: Add explicit transition tools**

Introduce:

```python
aitp_check_l3_gate(...)
aitp_advance_l3_subplane(...)
aitp_record_l3_transition(...)
```

and prevent direct `L3-I -> L3-A` or `L3-A -> L3-D`.

- [ ] **Step 4: Run the L3 subplane tests**

Run:

```powershell
python -m unittest tests.test_l3_subplanes -v
```

Expected:

- subplane-gating tests pass.

---

### Task 2: Replace Coarse Derive Skill With Micro-Skills

**Files:**
- Create: `skills/skill-l3-ideate.md`
- Create: `skills/skill-l3-plan.md`
- Create: `skills/skill-l3-analyze.md`
- Create: `skills/skill-l3-integrate.md`
- Create: `skills/skill-l3-distill.md`
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`

- [ ] **Step 1: Create the five micro-skills**

Each skill must:

- name the active artifact,
- state blocked work,
- define the exit condition,
- explicitly mention when backedges are correct.

- [ ] **Step 2: Update hook output to mention the active `L3` subplane skill**

When the brief says:

```python
"stage": "L3", "l3_subplane": "planning"
```

the hooks should point at:

```text
skills/skill-l3-plan.md
```

- [ ] **Step 3: Verify skill selection**

Run:

```powershell
rg -n "name: skill-l3-" skills
python -m unittest tests.test_l3_subplanes -v
```

Expected:

- five micro-skills exist,
- hook/subplane tests still pass.

---

### Task 3: Emit Flow-End TeX After Any Completed Research Flow

**Files:**
- Create: `scripts/render_flow_notebook.py`
- Modify: `brain/mcp_server.py`
- Modify: `tests/test_l3_subplanes.py`

- [ ] **Step 1: Write failing flow-TeX tests**

Add tests:

```python
def test_completed_l3_flow_emits_tex_notebook_path(): ...
def test_flow_tex_includes_question_conventions_derivation_checks_and_limits(): ...
```

The TeX output should be expected at:

```text
topics/<slug>/L3/tex/flow_notebook.tex
```

- [ ] **Step 2: Implement a simple flow-notebook renderer**

Create `scripts/render_flow_notebook.py` that reads:

- `L1/question_contract.md`
- `L1/convention_snapshot.md`
- active or archived `L3` artifacts
- `L4/reviews/*.md`

and emits sections:

```text
Research Question
Conventions And Regime
Derivation Route
Validation And Checks
Current Claim Boundary
Failures And Open Problems
```

- [ ] **Step 3: Add a brain tool or command surface to trigger notebook emission**

Add:

```python
aitp_render_flow_notebook(...)
```

It should be callable after an `L3/L4` flow closes and before `L5` starts.

- [ ] **Step 4: Run the flow-TeX tests**

Run:

```powershell
python -m unittest tests.test_l3_subplanes -v
```

Expected:

- flow notebook tests pass,
- `flow_notebook.tex` exists and contains the expected section names.

---

### Task 4: Commit

**Files:**
- All changed files from Tasks 1-3

- [ ] **Step 1: Run the full L3 wave verification**

Run:

```powershell
python -m unittest tests.test_l3_subplanes -v
```

Expected:

- all L3 tests pass.

- [ ] **Step 2: Commit**

```powershell
git add brain/state_model.py `
  brain/mcp_server.py `
  hooks/session_start.py `
  hooks/compact.py `
  skills/skill-l3-ideate.md `
  skills/skill-l3-plan.md `
  skills/skill-l3-analyze.md `
  skills/skill-l3-integrate.md `
  skills/skill-l3-distill.md `
  scripts/render_flow_notebook.py `
  tests/test_l3_subplanes.py
git commit -m "feat: add hard-gated l3 subplanes and flow tex output"
```

---

## Verification checklist

- [ ] `L3` has five active subplanes
- [ ] subplanes cannot be skipped
- [ ] hooks point to the current micro-skill
- [ ] every finished research flow can emit `L3/tex/flow_notebook.tex`

