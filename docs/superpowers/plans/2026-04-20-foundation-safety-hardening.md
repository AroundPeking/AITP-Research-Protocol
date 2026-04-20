# Foundation Safety Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the E2E-blocking safety and contract bugs before any higher-level research-flow work proceeds.

**Architecture:** First harden the minimal kernel around path resolution, slug validation, and file writes. Then restore a real promotion gate so the agent cannot directly promote by mutating candidate status. Finally, fix hook/session continuity so stop/resume operations affect only the active topic and preserve stable runtime behavior.

**Tech Stack:** Python 3 standard library, `fastmcp`, `pyyaml`, Markdown frontmatter files, `unittest`.

---

## File map

- Modify: `brain/mcp_server.py`
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`
- Modify: `hooks/stop.py`
- Create: `brain/__init__.py`
- Create: `brain/state_model.py`
- Create: `tests/__init__.py`
- Create: `tests/test_foundation_safety.py`

---

### Task 1: Unify Topic-Root Resolution And Block Path Traversal

**Files:**
- Create: `brain/__init__.py`
- Create: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`
- Test: `tests/test_foundation_safety.py`

- [ ] **Step 1: Write failing tests for topic-root resolution and slug rejection**

Add tests covering:

```python
def test_repo_root_topics_layout_resolves_inside_topics_dir(): ...
def test_direct_topics_root_layout_resolves_direct_child(): ...
def test_slug_with_parent_traversal_is_rejected(): ...
def test_slug_with_absolute_path_is_rejected(): ...
```

Use bad slugs such as:

```python
"..\\evil"
"/tmp/evil"
"C:\\\\temp\\\\evil"
"demo/../../oops"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- path-resolution and slug-validation tests fail because the shared helper does not exist yet.

- [ ] **Step 3: Implement shared safe topic helpers**

Create `brain/state_model.py` with:

```python
from pathlib import Path, PurePath


def topics_dir(topics_root: str | Path) -> Path:
    root = Path(topics_root)
    nested = root / "topics"
    return nested if nested.is_dir() else root


def validate_topic_slug(topic_slug: str) -> str:
    slug = topic_slug.strip()
    if not slug:
        raise ValueError("topic_slug must be non-empty")
    pure = PurePath(slug)
    if pure.is_absolute():
        raise ValueError("topic_slug must be relative")
    if any(part in {"..", "."} for part in pure.parts):
        raise ValueError("topic_slug contains unsafe path traversal")
    if len(pure.parts) != 1:
        raise ValueError("topic_slug must be a single path component")
    return slug


def topic_root(topics_root: str | Path, topic_slug: str) -> Path:
    safe_slug = validate_topic_slug(topic_slug)
    root = topics_dir(topics_root) / safe_slug
    if not root.is_dir():
        raise FileNotFoundError(f"Topic not found: {safe_slug}")
    return root
```

- [ ] **Step 4: Update `brain/mcp_server.py` and hooks to use the shared safe helper**

In `brain/mcp_server.py`:

```python
from brain.state_model import topic_root as resolve_topic_root, topics_dir, validate_topic_slug
```

Use:

```python
def _topic_root(topics_root: str, topic_slug: str) -> Path:
    return resolve_topic_root(topics_root, topic_slug)
```

And in bootstrap:

```python
safe_slug = validate_topic_slug(topic_slug)
root = topics_dir(topics_root) / safe_slug
```

Update hooks to resolve the active topic through the same helpers.

- [ ] **Step 5: Run the foundation tests again**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- path-resolution and slug-rejection tests pass.

---

### Task 2: Make File Writes Atomic

**Files:**
- Modify: `brain/mcp_server.py`
- Test: `tests/test_foundation_safety.py`

- [ ] **Step 1: Write failing tests for atomic write semantics**

Add tests for:

```python
def test_write_md_replaces_file_contents_cleanly(): ...
def test_append_section_preserves_existing_text_without_truncation(): ...
```

The tests should assert:

- the resulting file exists,
- the file content is exactly the expected final content,
- no duplicated partial fragments appear.

- [ ] **Step 2: Run the tests to verify current helpers are simple direct writes**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- the new atomic-write tests fail or expose the old direct-write behavior.

- [ ] **Step 3: Add a temp-file-and-replace helper**

Inside `brain/mcp_server.py`, add:

```python
import os
import tempfile


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as handle:
        handle.write(text)
        tmp_name = handle.name
    os.replace(tmp_name, path)
```

Refactor `_write_md(...)` and `_append_section(...)` to call `_atomic_write_text(...)`.

- [ ] **Step 4: Run the tests to verify the write helpers still behave correctly**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- all current foundation tests pass.

---

### Task 3: Restore A Real Promotion Gate And Remove Direct Promote Bypass

**Files:**
- Modify: `brain/mcp_server.py`
- Modify: `skills/skill-promote.md`
- Test: `tests/test_foundation_safety.py`

- [ ] **Step 1: Write failing tests for the promotion gate lifecycle**

Add tests for:

```python
def test_request_promotion_marks_candidate_pending_approval(): ...
def test_promote_candidate_rejects_nonapproved_candidates(): ...
def test_resolve_promotion_gate_approve_writes_l2_copy(): ...
```

The desired contract is:

- validated candidate -> `aitp_request_promotion(...)` -> `pending_approval`
- only explicit approval resolution may write to `L2`
- `aitp_promote_candidate(...)` must refuse to promote unless the gate is approved

- [ ] **Step 2: Run the tests to verify current direct-promote behavior is unsafe**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- tests fail because direct promote bypasses approval.

- [ ] **Step 3: Reintroduce request/resolve gate tools and tighten `aitp_promote_candidate(...)`**

In `brain/mcp_server.py`, restore:

```python
@mcp.tool()
def aitp_request_promotion(...): ...

@mcp.tool()
def aitp_resolve_promotion_gate(...): ...
```

Use statuses:

- `validated`
- `pending_approval`
- `approved_for_promotion`
- `promoted`

And make direct promotion require:

```python
if fm.get("status") != "approved_for_promotion":
    return "Candidate ... is not approved_for_promotion."
```

- [ ] **Step 4: Update `skills/skill-promote.md` to match the restored gate contract**

Replace direct `aitp_promote_candidate(...)` as the first post-question step with:

```markdown
1. `aitp_request_promotion(...)`
2. Ask the human
3. `aitp_resolve_promotion_gate(..., decision=\"approve\")`
4. `aitp_promote_candidate(...)`
```

- [ ] **Step 5: Run the promotion-gate tests**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- promotion gate tests pass,
- direct bypass is gone.

---

### Task 4: Make Stop/Resume Topic-Safe

**Files:**
- Modify: `hooks/stop.py`
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`
- Test: `tests/test_foundation_safety.py`

- [ ] **Step 1: Write failing tests for stop-hook scope**

Add tests:

```python
def test_stop_hook_only_updates_active_topic(): ...
def test_session_start_prefers_safe_current_topic_choice(): ...
```

Use two topics and assert stop does **not** append to both.

- [ ] **Step 2: Run the tests to verify current stop behavior touches all topics**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- stop-hook scope test fails because current code appends to every topic.

- [ ] **Step 3: Introduce a small active-topic pointer and use it in hooks**

Prefer a runtime file such as:

```python
topics/<slug>/runtime/current_topic.marker
```

or a single root-level:

```python
topics/current_topic.txt
```

Implement a helper that:

- uses the explicit current-topic pointer if present,
- otherwise falls back to most recently updated topic.

Make `stop.py` only append to that topic's `state.md` or, preferably, write a
separate runtime chronicle note for that topic.

- [ ] **Step 4: Run the hook-safety tests**

Run:

```powershell
python -m unittest tests.test_foundation_safety -v
```

Expected:

- stop now affects only the active topic,
- session start / compact still find a topic safely.

- [ ] **Step 5: Commit**

```powershell
git add brain/__init__.py `
  brain/state_model.py `
  brain/mcp_server.py `
  hooks/session_start.py `
  hooks/compact.py `
  hooks/stop.py `
  skills/skill-promote.md `
  tests/__init__.py `
  tests/test_foundation_safety.py
git commit -m "fix: harden foundation safety and promotion gates"
```

---

## Verification checklist

- [ ] topic roots resolve consistently
- [ ] unsafe slugs are rejected
- [ ] writes are atomic
- [ ] promotion requires explicit approval
- [ ] stop hook updates only the active topic

