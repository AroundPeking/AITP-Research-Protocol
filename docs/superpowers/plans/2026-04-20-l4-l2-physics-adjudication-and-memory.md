# L4 + Global L2 Physics Adjudication And Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `L4` behave like a real theoretical-physics adjudication layer and `L2` behave like safe global reusable memory rather than a local copy bucket.

**Architecture:** First expand `L4` from `ready/blocked` to the full six-outcome model with explicit validation contracts and physics-specific check fields. Then remodel `L2` promotion as a global memory write with normalization, versioning, conflict detection, and a two-dimensional trust classification (`basis x scope`) instead of a single flat trust label.

**Tech Stack:** Python 3, Markdown + YAML frontmatter, global canonical directories, `unittest`.

---

## File map

- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-validate.md`
- Modify: `skills/skill-promote.md`
- Create: `tests/test_l4_l2_memory.py`
- Create: `docs/protocols/L4_validation_protocol.md` follow-up update if needed
- Create or modify global canonical family directories under the repo’s chosen `L2` root

---

### Task 1: Implement Full L4 Validation Contract And Outcome Vocabulary

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-validate.md`
- Test: `tests/test_l4_l2_memory.py`

- [ ] **Step 1: Write failing tests for six validation outcomes**

Add tests:

```python
def test_validation_contract_requires_explicit_checks(): ...
def test_review_can_end_in_partial_pass(): ...
def test_review_can_end_in_contradiction(): ...
def test_review_can_end_in_stuck(): ...
```

- [ ] **Step 2: Add a first-class validation contract artifact**

Require:

```text
topics/<slug>/L4/validation_contract.md
```

with fields:

- `candidate_id`
- `validation_route`
- `mandatory_checks`
- `failure_conditions`

- [ ] **Step 3: Replace `ready/blocked` with six outcomes**

The MCP/tooling path should support:

- `pass`
- `partial_pass`
- `fail`
- `contradiction`
- `stuck`
- `timeout`

and return the result only through `L3-R`.

- [ ] **Step 4: Run the L4 outcome tests**

Run:

```powershell
python -m unittest tests.test_l4_l2_memory -v
```

Expected:

- six-outcome tests pass.

---

### Task 2: Add Physics-Specific Mandatory Check Fields

**Files:**
- Modify: `skills/skill-validate.md`
- Modify: `brain/mcp_server.py`
- Test: `tests/test_l4_l2_memory.py`

- [ ] **Step 1: Write failing tests for required physics checks**

Add tests asserting the validation contract or review artifact can require:

- `dimensional_consistency`
- `symmetry_compatibility`
- `limiting_case_check`
- `conservation_check`
- `correspondence_check`

- [ ] **Step 2: Extend validation artifacts and brief output**

The relevant paths should surface missing checks explicitly in the execution brief.

- [ ] **Step 3: Run the tests**

Run:

```powershell
python -m unittest tests.test_l4_l2_memory -v
```

Expected:

- physics-check tests pass.

---

### Task 3: Move Promotion Into Global L2 With Conflict And Version Handling

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-promote.md`
- Test: `tests/test_l4_l2_memory.py`

- [ ] **Step 1: Write failing tests for global promotion behavior**

Add tests:

```python
def test_promote_writes_to_global_l2_root_not_topic_local_copy(): ...
def test_conflicting_existing_unit_creates_conflict_record(): ...
def test_repeat_promotion_creates_new_version_or_reuse_receipt(): ...
```

- [ ] **Step 2: Normalize the promotion target**

Use a single global root such as:

```python
topics_dir(topics_root).parent / "L2"
```

or the repository’s chosen canonical root.

Promotions should no longer blindly copy into `topics/<slug>/L2/canonical/`.

- [ ] **Step 3: Add conflict/version receipts**

Before writing the promoted unit:

- compare normalized identity + scope,
- if incompatible content exists, write a conflict receipt and block promotion,
- if compatible content exists, create a version or reuse receipt.

- [ ] **Step 4: Run the promotion-memory tests**

Run:

```powershell
python -m unittest tests.test_l4_l2_memory -v
```

Expected:

- global-promotion, conflict, and version tests pass.

---

### Task 4: Replace Flat Trust Class With `basis x scope`

**Files:**
- Modify: `brain/mcp_server.py`
- Test: `tests/test_l4_l2_memory.py`

- [ ] **Step 1: Write failing tests for 2D trust classification**

Add tests for fields:

```python
"trust_basis": "source" | "derived" | "validated" | "human_approved"
"trust_scope": "local" | "bounded_reusable" | "cross_topic_reusable"
```

- [ ] **Step 2: Persist both dimensions in promoted units**

For example:

```python
{
    "trust_basis": "validated",
    "trust_scope": "bounded_reusable",
}
```

Do not rely only on one flat label.

- [ ] **Step 3: Run the trust tests**

Run:

```powershell
python -m unittest tests.test_l4_l2_memory -v
```

Expected:

- 2D trust tests pass.

---

### Task 5: Commit

- [ ] **Step 1: Run the full L4/L2 verification**

Run:

```powershell
python -m unittest tests.test_l4_l2_memory -v
```

Expected:

- all L4/L2 tests pass.

- [ ] **Step 2: Commit**

```powershell
git add brain/mcp_server.py `
  skills/skill-validate.md `
  skills/skill-promote.md `
  tests/test_l4_l2_memory.py
git commit -m "feat: add physics adjudication and global l2 memory"
```

---

## Verification checklist

- [ ] `L4` uses six outcomes
- [ ] physics checks are first-class
- [ ] promotion writes to global `L2`
- [ ] conflicts/versioning are explicit
- [ ] trust is classified as `basis x scope`

