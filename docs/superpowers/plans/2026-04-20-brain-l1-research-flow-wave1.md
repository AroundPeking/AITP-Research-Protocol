# Brain + L1 Research Flow Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first working slice of the new AITP research-flow kernel by adding stage/posture-aware brain state, L1 framing artifact scaffolds, L1 gate checks, and hook/skill wiring that points the agent at `read` and `frame` work instead of the old coarse status-only flow.

**Architecture:** Keep the current minimal `brain/` + `hooks/` + `skills/` footprint, but extract a shared state-model helper so the MCP server and hooks agree on topic-root resolution, `stage/posture/lane/gate_status` inference, and L1 gate evaluation. Preserve old `status` for compatibility while introducing new `state.md` fields and a new execution-brief tool that treats L1 as the first hard research stage.

**Tech Stack:** Python 3 standard library, `fastmcp`, `pyyaml`, Markdown-with-YAML-frontmatter protocol artifacts, `unittest`, PowerShell commands.

---

## Scope note

This umbrella spec is too broad for one safe code wave. This plan intentionally
covers **Wave 1 only**:

- shared stage/posture state model,
- compatibility-safe topic-root resolution,
- `L1` artifact scaffolding,
- `L1` gate checks,
- execution brief generation,
- hook output based on the new brief,
- `read` / `frame` posture skills.

Later waves should separately implement:

- `L3` hard subplane gates,
- `L4` physics-specific adjudication bundles,
- global `L2` memory remodeling,
- `L5` provenance-heavy writing surfaces.

## File map

### Core state model

- Create: `brain/__init__.py`
- Create: `brain/state_model.py`
- Modify: `brain/mcp_server.py`

### Hooks

- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`

### Skills

- Create: `skills/skill-read.md`
- Create: `skills/skill-frame.md`
- Modify: `skills/skill-continuous.md`

### Tests

- Create: `tests/__init__.py`
- Create: `tests/test_state_model.py`
- Create: `tests/test_hooks.py`

---

### Task 1: Extract A Shared Stage/Path State Model

**Files:**
- Create: `brain/__init__.py`
- Create: `brain/state_model.py`
- Create: `tests/__init__.py`
- Create: `tests/test_state_model.py`
- Modify: `brain/mcp_server.py`

- [ ] **Step 1: Write the failing path-resolution tests**

Create `tests/test_state_model.py` with these first tests:

```python
import tempfile
import unittest
from pathlib import Path

from brain import state_model


class TopicRootResolutionTests(unittest.TestCase):
    def test_repo_root_with_topics_dir_resolves_topic_inside_topics_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics" / "demo-topic").mkdir(parents=True)

            resolved = state_model.topic_root(repo_root, "demo-topic")

            self.assertEqual(resolved, repo_root / "topics" / "demo-topic")

    def test_direct_topics_root_still_resolves_existing_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            topics_root = Path(tmp)
            (topics_root / "demo-topic").mkdir()

            resolved = state_model.topic_root(topics_root, "demo-topic")

            self.assertEqual(resolved, topics_root / "demo-topic")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
python -m unittest tests.test_state_model -v
```

Expected:

- `ImportError` for `brain.state_model`, or
- `AttributeError` because `topic_root` is not defined yet.

- [ ] **Step 3: Create the shared state-model module**

Add `brain/__init__.py`:

```python
"""Brain package for shared stage/posture helpers."""
```

Create `brain/state_model.py` with the initial shared helpers:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StageSnapshot:
    stage: str
    posture: str
    lane: str
    gate_status: str
    required_artifact_path: str = ""
    missing_requirements: list[str] = field(default_factory=list)
    next_allowed_transition: str = ""
    skill: str = "skill-continuous"


def topics_dir(topics_root: str | Path) -> Path:
    root = Path(topics_root)
    nested = root / "topics"
    return nested if nested.is_dir() else root


def topic_root(topics_root: str | Path, topic_slug: str) -> Path:
    root = topics_dir(topics_root) / topic_slug
    if not root.is_dir():
        raise FileNotFoundError(f"Topic not found: {topic_slug}")
    return root
```

- [ ] **Step 4: Switch `brain/mcp_server.py` to use the shared helper**

Replace the local topic-root logic with an import from the new helper:

```python
from brain.state_model import topic_root as resolve_topic_root
```

Then update the local helper:

```python
def _topic_root(topics_root: str, topic_slug: str) -> Path:
    return resolve_topic_root(topics_root, topic_slug)
```

- [ ] **Step 5: Run the tests to verify the new helper works**

Run:

```powershell
python -m unittest tests.test_state_model -v
```

Expected:

- both `TopicRootResolutionTests` pass.

---

### Task 2: Bootstrap The New L1 Scaffolds And Compatibility-Safe State Fields

**Files:**
- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Modify: `tests/test_state_model.py`

- [ ] **Step 1: Write the failing bootstrap test**

Extend `tests/test_state_model.py` with:

```python
from brain import mcp_server


class BootstrapL1ScaffoldTests(unittest.TestCase):
    def test_bootstrap_topic_creates_l1_artifacts_and_new_state_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics").mkdir()

            mcp_server.aitp_bootstrap_topic(
                str(repo_root),
                "demo-topic",
                "Demo Topic",
                "What is the bounded question?",
            )

            topic_root = repo_root / "topics" / "demo-topic"
            self.assertTrue((topic_root / "L1" / "question_contract.md").exists())
            self.assertTrue((topic_root / "L1" / "source_basis.md").exists())
            self.assertTrue((topic_root / "L1" / "convention_snapshot.md").exists())
            self.assertTrue((topic_root / "L1" / "derivation_anchor_map.md").exists())
            self.assertTrue((topic_root / "L1" / "contradiction_register.md").exists())

            fm, _ = mcp_server._parse_md(topic_root / "state.md")
            self.assertEqual(fm["status"], "new")
            self.assertEqual(fm["stage"], "L1")
            self.assertEqual(fm["posture"], "read")
            self.assertEqual(fm["lane"], "unspecified")
```

- [ ] **Step 2: Run the tests to verify the new scaffolds are missing**

Run:

```powershell
python -m unittest tests.test_state_model.BootstrapL1ScaffoldTests -v
```

Expected:

- failure because the new `L1/*.md` files and `stage/posture/lane` fields do not exist yet.

- [ ] **Step 3: Add the L1 scaffold templates to `brain/state_model.py`**

Add a constant like this:

```python
L1_ARTIFACT_TEMPLATES = {
    "question_contract.md": (
        {
            "artifact_kind": "l1_question_contract",
            "stage": "L1",
            "required_fields": ["bounded_question", "scope_boundaries", "target_quantities"],
            "bounded_question": "",
            "scope_boundaries": "",
            "target_quantities": "",
        },
        "# Question Contract\n\n## Bounded Question\n\n## Scope Boundaries\n\n## Target Quantities Or Claims\n\n## Non-Success Conditions\n\n## Uncertainty Markers\n",
    ),
    "source_basis.md": (
        {
            "artifact_kind": "l1_source_basis",
            "stage": "L1",
            "required_fields": ["core_sources", "peripheral_sources"],
            "core_sources": "",
            "peripheral_sources": "",
        },
        "# Source Basis\n\n## Core Sources\n\n## Peripheral Sources\n\n## Source Roles\n\n## Reading Depth\n\n## Why Each Source Matters\n",
    ),
    "convention_snapshot.md": (
        {
            "artifact_kind": "l1_convention_snapshot",
            "stage": "L1",
            "required_fields": ["notation_choices", "unit_conventions"],
            "notation_choices": "",
            "unit_conventions": "",
        },
        "# Convention Snapshot\n\n## Notation Choices\n\n## Unit Conventions\n\n## Sign Conventions\n\n## Metric Or Coordinate Conventions\n\n## Unresolved Tensions\n",
    ),
    "derivation_anchor_map.md": (
        {
            "artifact_kind": "l1_derivation_anchor_map",
            "stage": "L1",
            "required_fields": ["starting_anchors"],
            "starting_anchors": "",
        },
        "# Derivation Anchor Map\n\n## Source Anchors\n\n## Missing Steps\n\n## Candidate Starting Points\n",
    ),
    "contradiction_register.md": (
        {
            "artifact_kind": "l1_contradiction_register",
            "stage": "L1",
            "required_fields": ["blocking_contradictions"],
            "blocking_contradictions": "",
        },
        "# Contradiction Register\n\n## Unresolved Source Conflicts\n\n## Regime Mismatches\n\n## Notation Collisions\n\n## Blocking Status\n",
    ),
}
```

- [ ] **Step 4: Update `aitp_bootstrap_topic(...)` to create the L1 scaffolds and new fields**

Modify the bootstrap path logic to use `topics_dir(...)`, then write the L1 files:

```python
topics_root_path = topics_dir(topics_root)
root = topics_root_path / topic_slug
```

Keep the existing directories, but add:

```python
for rel_name, (artifact_fm, artifact_body) in L1_ARTIFACT_TEMPLATES.items():
    _write_md(root / "L1" / rel_name, artifact_fm, artifact_body)
```

Also extend `state.md` frontmatter:

```python
fm = {
    "topic_slug": topic_slug,
    "title": title,
    "status": "new",
    "layer": "L1",
    "stage": "L1",
    "posture": "read",
    "lane": "unspecified",
    "gate_status": "blocked_missing_field",
    "created_at": _now(),
    "updated_at": _now(),
}
```

- [ ] **Step 5: Run the bootstrap tests to verify the new scaffolds exist**

Run:

```powershell
python -m unittest tests.test_state_model.BootstrapL1ScaffoldTests -v
```

Expected:

- the scaffold files exist,
- `state.md` carries `stage/posture/lane`,
- existing `status` remains `new`.

---

### Task 3: Add L1 Gate Evaluation And A Stage/Posture Execution Brief

**Files:**
- Modify: `brain/state_model.py`
- Modify: `brain/mcp_server.py`
- Modify: `tests/test_state_model.py`

- [ ] **Step 1: Write the failing gate-and-brief tests**

Add these tests to `tests/test_state_model.py`:

```python
class L1GateTests(unittest.TestCase):
    def test_execution_brief_blocks_on_first_missing_l1_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics").mkdir()
            mcp_server.aitp_bootstrap_topic(
                str(repo_root),
                "demo-topic",
                "Demo Topic",
                "What is the bounded question?",
            )

            brief = mcp_server.aitp_get_execution_brief(str(repo_root), "demo-topic")

            self.assertEqual(brief["stage"], "L1")
            self.assertEqual(brief["posture"], "read")
            self.assertEqual(brief["gate_status"], "blocked_missing_field")
            self.assertTrue(brief["required_artifact_path"].endswith("question_contract.md"))
            self.assertIn("bounded_question", brief["missing_requirements"])

    def test_execution_brief_turns_ready_after_all_l1_artifacts_are_filled(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics").mkdir()
            mcp_server.aitp_bootstrap_topic(
                str(repo_root),
                "demo-topic",
                "Demo Topic",
                "What is the bounded question?",
            )

            topic_root = repo_root / "topics" / "demo-topic"
            mcp_server._write_md(
                topic_root / "L1" / "question_contract.md",
                {
                    "artifact_kind": "l1_question_contract",
                    "stage": "L1",
                    "bounded_question": "What quantity is bounded here?",
                    "scope_boundaries": "One model, one regime.",
                    "target_quantities": "Gap and symmetry sector.",
                },
                "# Question Contract\n\n## Bounded Question\nWhat quantity is bounded here?\n\n## Scope Boundaries\nOne model, one regime.\n\n## Target Quantities Or Claims\nGap and symmetry sector.\n\n## Non-Success Conditions\nNo broad universality claim.\n\n## Uncertainty Markers\nFinite-size risk.\n",
            )
            mcp_server._write_md(
                topic_root / "L1" / "source_basis.md",
                {
                    "artifact_kind": "l1_source_basis",
                    "stage": "L1",
                    "core_sources": "paper-a",
                    "peripheral_sources": "note-b",
                },
                "# Source Basis\n\n## Core Sources\npaper-a\n\n## Peripheral Sources\nnote-b\n\n## Source Roles\npaper-a is the main derivation source.\n\n## Reading Depth\nfull_read for paper-a.\n\n## Why Each Source Matters\npaper-a defines the bounded route.\n",
            )
            mcp_server._write_md(
                topic_root / "L1" / "convention_snapshot.md",
                {
                    "artifact_kind": "l1_convention_snapshot",
                    "stage": "L1",
                    "notation_choices": "Use source-a symbols.",
                    "unit_conventions": "Natural units.",
                },
                "# Convention Snapshot\n\n## Notation Choices\nUse source-a symbols.\n\n## Unit Conventions\nNatural units.\n\n## Sign Conventions\nHamiltonian sign fixed.\n\n## Metric Or Coordinate Conventions\nEuclidean.\n\n## Unresolved Tensions\nNone blocking.\n",
            )
            mcp_server._write_md(
                topic_root / "L1" / "derivation_anchor_map.md",
                {
                    "artifact_kind": "l1_derivation_anchor_map",
                    "stage": "L1",
                    "starting_anchors": "eq-12",
                },
                "# Derivation Anchor Map\n\n## Source Anchors\neq-12\n\n## Missing Steps\nOne omitted algebra step.\n\n## Candidate Starting Points\neq-12 to eq-14.\n",
            )
            mcp_server._write_md(
                topic_root / "L1" / "contradiction_register.md",
                {
                    "artifact_kind": "l1_contradiction_register",
                    "stage": "L1",
                    "blocking_contradictions": "none",
                },
                "# Contradiction Register\n\n## Unresolved Source Conflicts\nNone.\n\n## Regime Mismatches\nNone blocking.\n\n## Notation Collisions\nTracked and resolved.\n\n## Blocking Status\nnone\n",
            )

            brief = mcp_server.aitp_get_execution_brief(str(repo_root), "demo-topic")

            self.assertEqual(brief["stage"], "L1")
            self.assertEqual(brief["posture"], "frame")
            self.assertEqual(brief["gate_status"], "ready")
            self.assertEqual(brief["next_allowed_transition"], "L3")
            self.assertEqual(brief["skill"], "skill-frame")
```

- [ ] **Step 2: Run the tests to verify the brief API does not exist yet**

Run:

```powershell
python -m unittest tests.test_state_model.L1GateTests -v
```

Expected:

- failure because `aitp_get_execution_brief` and L1 gate inference do not exist yet.

- [ ] **Step 3: Implement the L1 gate logic in `brain/state_model.py`**

Add helper functions like:

```python
def missing_frontmatter_keys(frontmatter: dict[str, object], required: list[str]) -> list[str]:
    return [key for key in required if not str(frontmatter.get(key, "")).strip()]


def missing_required_headings(body: str, headings: list[str]) -> list[str]:
    return [heading for heading in headings if heading not in body]


def evaluate_l1_stage(parse_md, topic_root: Path, lane: str = "unspecified") -> StageSnapshot:
    contracts = [
        (
            "question_contract.md",
            "read",
            ["bounded_question", "scope_boundaries", "target_quantities"],
            ["## Bounded Question", "## Scope Boundaries", "## Target Quantities Or Claims"],
        ),
        (
            "source_basis.md",
            "read",
            ["core_sources", "peripheral_sources"],
            ["## Core Sources", "## Peripheral Sources", "## Why Each Source Matters"],
        ),
        (
            "convention_snapshot.md",
            "frame",
            ["notation_choices", "unit_conventions"],
            ["## Notation Choices", "## Unit Conventions", "## Unresolved Tensions"],
        ),
        (
            "derivation_anchor_map.md",
            "frame",
            ["starting_anchors"],
            ["## Source Anchors", "## Candidate Starting Points"],
        ),
        (
            "contradiction_register.md",
            "frame",
            ["blocking_contradictions"],
            ["## Unresolved Source Conflicts", "## Blocking Status"],
        ),
    ]

    for name, posture, fields, headings in contracts:
        path = topic_root / "L1" / name
        if not path.exists():
            return StageSnapshot(
                stage="L1",
                posture=posture,
                lane=lane,
                gate_status="blocked_missing_artifact",
                required_artifact_path=str(path),
                missing_requirements=[name],
                next_allowed_transition="L1",
                skill=f"skill-{posture}",
            )

        fm, body = parse_md(path)
        missing = missing_frontmatter_keys(fm, fields) + missing_required_headings(body, headings)
        if missing:
            return StageSnapshot(
                stage="L1",
                posture=posture,
                lane=lane,
                gate_status="blocked_missing_field",
                required_artifact_path=str(path),
                missing_requirements=missing,
                next_allowed_transition="L1",
                skill=f"skill-{posture}",
            )

    return StageSnapshot(
        stage="L1",
        posture="frame",
        lane=lane,
        gate_status="ready",
        next_allowed_transition="L3",
        skill="skill-frame",
    )
```

- [ ] **Step 4: Expose the brief in `brain/mcp_server.py`**

Extend `aitp_get_status(...)` to return:

```python
snapshot = evaluate_l1_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
```

and include:

```python
"stage": fm.get("stage", snapshot.stage),
"posture": fm.get("posture", snapshot.posture),
"lane": fm.get("lane", snapshot.lane),
"gate_status": snapshot.gate_status,
"required_artifact_path": snapshot.required_artifact_path,
"missing_requirements": snapshot.missing_requirements,
```

Then add a new MCP tool:

```python
@mcp.tool()
def aitp_get_execution_brief(topics_root: str, topic_slug: str) -> dict[str, Any]:
    root = _topic_root(topics_root, topic_slug)
    fm, _ = _parse_md(root / "state.md")
    snapshot = evaluate_l1_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    return {
        "topic_slug": topic_slug,
        "stage": snapshot.stage,
        "posture": snapshot.posture,
        "lane": snapshot.lane,
        "gate_status": snapshot.gate_status,
        "required_artifact_path": snapshot.required_artifact_path,
        "missing_requirements": snapshot.missing_requirements,
        "next_allowed_transition": snapshot.next_allowed_transition,
        "skill": snapshot.skill,
        "immediate_allowed_work": [f"edit {snapshot.required_artifact_path}" if snapshot.required_artifact_path else "prepare transition to L3"],
        "immediate_blocked_work": ["L3 derivation", "L4 validation", "L2 promotion"],
    }
```

- [ ] **Step 5: Run the state-model tests to verify the gate and brief**

Run:

```powershell
python -m unittest tests.test_state_model -v
```

Expected:

- topic-root tests pass,
- bootstrap scaffold tests pass,
- both L1 gate tests pass.

---

### Task 4: Make Hooks Print Stage/Posture-Aware Guidance

**Files:**
- Modify: `hooks/session_start.py`
- Modify: `hooks/compact.py`
- Create: `tests/test_hooks.py`

- [ ] **Step 1: Write failing hook-output tests**

Create `tests/test_hooks.py` with:

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from brain import mcp_server


REPO_ROOT = Path(__file__).resolve().parents[1]


class HookOutputTests(unittest.TestCase):
    def test_session_start_prints_stage_posture_and_required_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics").mkdir()
            mcp_server.aitp_bootstrap_topic(
                str(repo_root),
                "demo-topic",
                "Demo Topic",
                "What is the bounded question?",
            )

            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / "hooks" / "session_start.py")],
                cwd=repo_root,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("stage: L1", completed.stdout)
            self.assertIn("posture: read", completed.stdout)
            self.assertIn("question_contract.md", completed.stdout)
            self.assertIn("skill-read.md", completed.stdout)

    def test_compact_prints_same_stage_posture_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "topics").mkdir()
            mcp_server.aitp_bootstrap_topic(
                str(repo_root),
                "demo-topic",
                "Demo Topic",
                "What is the bounded question?",
            )

            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / "hooks" / "compact.py")],
                cwd=repo_root,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("stage: L1", completed.stdout)
            self.assertIn("posture: read", completed.stdout)
            self.assertIn("skill-read.md", completed.stdout)
```

- [ ] **Step 2: Run the hook tests to verify the current scripts are too shallow**

Run:

```powershell
python -m unittest tests.test_hooks -v
```

Expected:

- failure because the hooks only print old status/skill messages.

- [ ] **Step 3: Update `hooks/session_start.py` to use the shared state model**

Import the new helper:

```python
from brain.state_model import evaluate_l1_stage, topic_root
```

Then replace the old `_SKILL_MAP`-driven output with:

```python
def _load_snapshot(topics_root: str, topic_slug: str):
    root = topic_root(topics_root, topic_slug)
    fm, _ = _parse_md(root / "state.md")
    return evaluate_l1_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
```

and print:

```python
print(
    f"AITP: Active topic '{topic_slug}' "
    f"(stage: {snapshot.stage}, posture: {snapshot.posture}, gate: {snapshot.gate_status})."
)
if snapshot.required_artifact_path:
    print(f"AITP: Fill {snapshot.required_artifact_path} before advancing.")
print(f"AITP: Read and follow skills/{snapshot.skill}.md before continuing.")
```

Add a Markdown parser helper so the hook can reuse the same gate evaluator:

```python
def _parse_md(path: Path) -> tuple[dict, str]:
    ...
```

- [ ] **Step 4: Update `hooks/compact.py` to mirror the same stage/posture summary**

Keep the compact-specific preface, but use the same snapshot fields:

```python
print(
    f"AITP: Context was compacted. Resuming topic '{topic_slug}' "
    f"(stage: {snapshot.stage}, posture: {snapshot.posture}, gate: {snapshot.gate_status})."
)
if snapshot.required_artifact_path:
    print(f"AITP: Complete {snapshot.required_artifact_path} before advancing.")
print(f"AITP: Read skills/{snapshot.skill}.md to restore your workflow context.")
```

- [ ] **Step 5: Run the hook tests to verify the new guidance**

Run:

```powershell
python -m unittest tests.test_hooks -v
```

Expected:

- both hook-output tests pass.

---

### Task 5: Add `read` / `frame` Micro-Skills And Rewire Resume Guidance

**Files:**
- Create: `skills/skill-read.md`
- Create: `skills/skill-frame.md`
- Modify: `skills/skill-continuous.md`

- [ ] **Step 1: Create `skills/skill-read.md`**

Add:

```markdown
---
name: skill-read
description: Read posture — build the source basis before framing or derivation.
trigger: posture == "read"
---

# Read Posture

You are building the topic's source-grounded basis.

## Required artifacts

- `L1/source_basis.md`
- `L1/question_contract.md`

## What to do now

1. Register or inspect the source basis.
2. Fill the bounded question if it is still blank.
3. Record source roles and reading depth.
4. Do not start L3 derivation yet.

## Exit condition

Move on only after the source basis and bounded question are explicit.
```

- [ ] **Step 2: Create `skills/skill-frame.md`**

Add:

```markdown
---
name: skill-frame
description: Frame posture — lock conventions, anchors, and contradictions before derivation.
trigger: posture == "frame"
---

# Frame Posture

You are preparing the topic for honest derivation.

## Required artifacts

- `L1/convention_snapshot.md`
- `L1/derivation_anchor_map.md`
- `L1/contradiction_register.md`

## What to do now

1. Lock notation, unit, sign, and metric conventions.
2. Record derivation anchors from the source basis.
3. Make contradictions explicit and mark whether they block derivation.
4. Do not advance to `L3` while these artifacts are incomplete.

## Exit condition

Move on only when the topic has a usable convention snapshot, at least one derivation anchor, and scoped contradictions.
```

- [ ] **Step 3: Update `skills/skill-continuous.md` to use the execution brief**

Replace the old popup-driven resume opening with a brief-driven one:

```markdown
1. Read the current execution brief:
   `aitp_get_execution_brief(topics_root, topic_slug)`

2. Inspect:
   - `stage`
   - `posture`
   - `gate_status`
   - `required_artifact_path`
   - `missing_requirements`

3. Read the posture skill named by the brief.

4. Do not advance if the brief says the topic is blocked.
```

Also remove the stale `aitp_get_popup(...)` reference entirely.

- [ ] **Step 4: Verify the new skills are wired in**

Run:

```powershell
rg -n "name: skill-read|name: skill-frame|aitp_get_execution_brief|aitp_get_popup" skills
```

Expected:

- `skill-read.md` exists,
- `skill-frame.md` exists,
- `skill-continuous.md` references `aitp_get_execution_brief`,
- no skill file references `aitp_get_popup`.

- [ ] **Step 5: Run the whole Wave 1 verification slice**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected:

- all state-model tests pass,
- all hook tests pass.

- [ ] **Step 6: Commit**

```powershell
git add brain/__init__.py `
  brain/state_model.py `
  brain/mcp_server.py `
  hooks/session_start.py `
  hooks/compact.py `
  skills/skill-read.md `
  skills/skill-frame.md `
  skills/skill-continuous.md `
  tests/__init__.py `
  tests/test_state_model.py `
  tests/test_hooks.py
git commit -m "feat: add stage-aware brain kernel and L1 gates"
```

---

## Verification checklist

- [ ] `brain` resolves both repo-root-with-`topics/` and direct-topics-root layouts
- [ ] bootstrap creates the five required `L1` scaffold files
- [ ] `state.md` now carries `stage`, `posture`, `lane`, and `gate_status`
- [ ] `aitp_get_execution_brief(...)` reports blocked-vs-ready `L1` state
- [ ] hooks print stage/posture/gate guidance instead of old coarse status-only text
- [ ] `read` and `frame` skills exist and `skill-continuous` points at the execution brief

## Spec coverage self-review

- [ ] Stage/posture split: covered by Tasks 1-4
- [ ] `brain` as protocol kernel: covered by Tasks 1-4
- [ ] `L1` framing artifacts and notation lock scaffolds: covered by Tasks 2-3 and Task 5
- [ ] Triggered posture skills (`read`, `frame`): covered by Task 5
- [ ] Compatibility with existing `status` field: covered by Task 2
- [ ] Out-of-scope later layers (`L3-L5`) intentionally deferred to later wave plans

## Recommended execution order

1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5

This wave is intentionally sequential because each later task depends on the
shared state model introduced earlier.
