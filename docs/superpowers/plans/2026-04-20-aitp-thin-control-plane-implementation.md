# AITP Thin Control Plane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a thin cross-topic control plane to AITP with a derived dashboard/blocker queue, notebook-obligation remediation tasks, and a minimal unified dispatch contract without flattening `L0/L1/L2/L3/L4`.

**Architecture:** Reuse existing topic-local truth surfaces as the only scientific authority, then derive three thin layers around them: a cross-topic control index, topic-local remediation task ledgers, and dispatch target contracts. Keep new writable state small and file-backed; orchestration and adapter scripts should only point at or write back to topic-owned runtime artifacts.

**Tech Stack:** Python 3.10+, `pytest`, existing `knowledge_hub` runtime helpers, Markdown/JSON runtime artifacts, OpenClaw adapter scripts

---

## Scope Guard

This plan implements only the thin control plane described in the approved spec.

It does **not**:

- replace `active_topics.json` with a database,
- replace AITP layer semantics with generic workflow stages,
- add a web UI,
- add a new long-term memory substrate,
- or redesign the OpenClaw execution lane beyond the dispatch contract needed here.

## File Structure

### New files

- `research/knowledge-hub/knowledge_hub/control_plane_index_support.py`
  - derive and render `runtime/control_plane/topic_control_index.{json,md}` and `blocker_queue.{json,md}`
- `research/knowledge-hub/knowledge_hub/remediation_task_support.py`
  - materialize topic-local `remediation_tasks.{json,md}` from notebook/report obligation gaps
- `research/knowledge-hub/knowledge_hub/dispatch_target_support.py`
  - define thin dispatch-target payloads and write `runtime/control_plane/dispatch_targets.json`
- `research/knowledge-hub/tests/test_control_plane_index_support.py`
  - focused unit tests for cross-topic summary derivation and blocker ordering

### Existing files to modify

- `research/knowledge-hub/knowledge_hub/aitp_service.py`
  - expose control-plane materialization methods and return control-plane paths from active-topic/status flows
- `research/knowledge-hub/runtime/scripts/orchestrate_topic.py`
  - refresh topic-local and cross-topic control-plane surfaces after orchestration
- `research/knowledge-hub/runtime/scripts/decide_next_action.py`
  - persist dispatch-target surfaces for the selected action and derived remediation tasks
- `research/knowledge-hub/knowledge_hub/research_report_support.py`
  - generate remediation ledgers alongside `unfinished_work` merges and publish them in the report payload
- `research/knowledge-hub/knowledge_hub/research_notebook_support.py`
  - render remediation tasks in the notebook/open-problems section
- `research/adapters/openclaw/scripts/dispatch_action_queue.py`
  - consume the thin dispatch target payload instead of ad hoc queue-only metadata where available
- `research/adapters/openclaw/scripts/dispatch_execution_task.py`
  - record `dispatch_target_id` and writeback expectations into execution handoff receipts
- `research/knowledge-hub/tests/test_research_report_support.py`
  - lock remediation task generation and deduplication
- `research/knowledge-hub/tests/test_research_notebook_support.py`
  - lock notebook rendering of remediation tasks and open-problem summaries
- `research/knowledge-hub/tests/test_runtime_scripts.py`
  - lock orchestrator/next-action generation of control-plane surfaces
- `research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py`
  - lock adapter-side use of the dispatch target contract
- `research/knowledge-hub/tests/test_aitp_service.py`
  - lock service-level control-plane path publication and status payloads
- `docs/PROJECT_INDEX.md`
  - document the new control-plane and remediation surfaces
- `research/knowledge-hub/runtime/README.md`
  - add the new control-plane artifact inventory

## Task 1: Build The Cross-Topic Control Index

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/control_plane_index_support.py`
- Test: `research/knowledge-hub/tests/test_control_plane_index_support.py`

- [ ] **Step 1: Write the failing control-plane index test**

```python
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from knowledge_hub.control_plane_index_support import materialize_control_plane_index


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_materialize_control_plane_index_summarizes_topics_and_blockers() -> None:
    with tempfile.TemporaryDirectory() as td:
        kernel_root = Path(td)
        runtime_root = kernel_root / "runtime"
        control_root = runtime_root / "control_plane"
        blocked_runtime = kernel_root / "topics" / "blocked-topic" / "runtime"
        ready_runtime = kernel_root / "topics" / "ready-topic" / "runtime"

        _write_json(
            runtime_root / "active_topics.json",
            {
                "focused_topic_slug": "blocked-topic",
                "topics": [
                    {"topic_slug": "blocked-topic", "operator_status": "ready", "focus_state": "focused"},
                    {"topic_slug": "ready-topic", "operator_status": "ready", "focus_state": "background"},
                ],
            },
        )
        _write_json(
            blocked_runtime / "topic_state.json",
            {"topic_slug": "blocked-topic", "resume_stage": "L4", "latest_run_id": "run-001"},
        )
        _write_json(
            blocked_runtime / "next_action_decision.json",
            {
                "selected_action": {
                    "action_id": "action:blocked-topic:repair",
                    "action_type": "dispatch_execution_task",
                    "summary": "Repair the missing anomaly analysis.",
                    "auto_runnable": True,
                }
            },
        )
        _write_json(
            blocked_runtime / "pending_decisions.json",
            {"pending_count": 1, "items": [{"decision_id": "decision:blocked-topic:route"}]},
        )
        _write_json(
            blocked_runtime / "unfinished_work.json",
            {"items": [{"summary": "Repair notebook obligation", "status": "pending"}]},
        )
        _write_json(
            blocked_runtime / "remediation_tasks.json",
            {
                "items": [
                    {
                        "task_id": "remediation:blocked-topic:anomaly",
                        "status": "pending",
                        "blocks_claim_use": True,
                        "summary": "Add anomaly analysis for iteration-001.",
                    }
                ]
            },
        )
        _write_json(
            blocked_runtime / "research_report.active.json",
            {"current_best_statements": [], "open_obligations": [{"summary": "Missing anomaly analysis."}]},
        )
        _write_json(
            ready_runtime / "topic_state.json",
            {"topic_slug": "ready-topic", "resume_stage": "L3", "latest_run_id": "run-002"},
        )
        _write_json(
            ready_runtime / "next_action_decision.json",
            {
                "selected_action": {
                    "action_id": "action:ready-topic:continue",
                    "action_type": "continue_topic",
                    "summary": "Continue the bounded derivation.",
                    "auto_runnable": True,
                }
            },
        )
        _write_json(ready_runtime / "pending_decisions.json", {"pending_count": 0, "items": []})
        _write_json(ready_runtime / "unfinished_work.json", {"items": []})
        _write_json(ready_runtime / "research_report.active.json", {"current_best_statements": []})

        payload = materialize_control_plane_index(
            kernel_root=kernel_root,
            updated_by="pytest",
            active_topics_path=runtime_root / "active_topics.json",
            output_root=control_root,
        )

        assert payload["topic_count"] == 2
        assert payload["topics"][0]["topic_slug"] == "blocked-topic"
        assert payload["topics"][0]["remediation_count"] == 1
        assert payload["topics"][0]["open_decision_count"] == 1
        assert payload["blocker_queue"][0]["topic_slug"] == "blocked-topic"
        assert payload["blocker_queue"][0]["source_kind"] == "remediation_task"
        assert (control_root / "topic_control_index.json").exists()
        assert (control_root / "blocker_queue.md").exists()
```

- [ ] **Step 2: Run the test to verify the helper does not exist yet**

Run: `python -m pytest research/knowledge-hub/tests/test_control_plane_index_support.py -q`

Expected: FAIL with `ModuleNotFoundError` or `ImportError` for `knowledge_hub.control_plane_index_support`

- [ ] **Step 3: Implement the new control-plane index helper**

```python
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_topic_control_row(*, kernel_root: Path, registry_row: dict[str, Any]) -> dict[str, Any]:
    topic_slug = str(registry_row.get("topic_slug") or "").strip()
    runtime_root = kernel_root / "topics" / topic_slug / "runtime"
    topic_state = _read_json(runtime_root / "topic_state.json") or {}
    next_action = _read_json(runtime_root / "next_action_decision.json") or {}
    unfinished = _read_json(runtime_root / "unfinished_work.json") or {}
    pending_decisions = _read_json(runtime_root / "pending_decisions.json") or {}
    remediation = _read_json(runtime_root / "remediation_tasks.json") or {}

    remediation_items = remediation.get("items") or []
    unfinished_items = unfinished.get("items") or []
    selected_action = (next_action.get("selected_action") or {}) if isinstance(next_action.get("selected_action"), dict) else {}
    blocked = bool(
        any(bool(item.get("blocks_claim_use")) for item in remediation_items)
        or any(str(item.get("status") or "").strip() == "blocked" for item in unfinished_items)
    )
    return {
        "topic_slug": topic_slug,
        "focus_state": registry_row.get("focus_state") or "background",
        "operator_status": registry_row.get("operator_status") or "ready",
        "resume_stage": topic_state.get("resume_stage") or "",
        "latest_run_id": topic_state.get("latest_run_id") or "",
        "selected_action_id": selected_action.get("action_id"),
        "selected_action_type": selected_action.get("action_type"),
        "selected_action_summary": selected_action.get("summary"),
        "open_decision_count": len(pending_decisions.get("items") or []),
        "unfinished_count": len(unfinished_items),
        "remediation_count": len(remediation_items),
        "blocked": blocked,
        "runtime_root": runtime_root.as_posix(),
    }


def build_blocker_queue(topic_rows: list[dict[str, Any]], *, kernel_root: Path) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for row in topic_rows:
        runtime_root = kernel_root / "topics" / str(row["topic_slug"]) / "runtime"
        remediation = _read_json(runtime_root / "remediation_tasks.json") or {}
        for item in remediation.get("items") or []:
            if str(item.get("status") or "pending") not in {"pending", "blocked"}:
                continue
            queue.append(
                {
                    "topic_slug": row["topic_slug"],
                    "source_kind": "remediation_task",
                    "source_id": item.get("task_id"),
                    "summary": item.get("summary"),
                    "blocks_claim_use": bool(item.get("blocks_claim_use")),
                    "recommended_round_type": item.get("recommended_round_type"),
                }
            )
    queue.sort(key=lambda item: (not bool(item["blocks_claim_use"]), item["topic_slug"], str(item["source_id"] or "")))
    return queue


def materialize_control_plane_index(
    *,
    kernel_root: Path,
    updated_by: str,
    active_topics_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    registry = _read_json(active_topics_path) or {"topics": []}
    topic_rows = [build_topic_control_row(kernel_root=kernel_root, registry_row=row) for row in (registry.get("topics") or [])]
    blocker_queue = build_blocker_queue(topic_rows, kernel_root=kernel_root)
    payload = {
        "status": "available",
        "updated_at": _now_iso(),
        "updated_by": updated_by,
        "focused_topic_slug": str(registry.get("focused_topic_slug") or "").strip(),
        "topic_count": len(topic_rows),
        "topics": topic_rows,
        "blocker_queue": blocker_queue,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "topic_control_index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "topic_control_index.md").write_text(
        "# Topic Control Index\n\n"
        + "\n".join(
            f"- `{row['topic_slug']}` stage=`{row['resume_stage'] or '(missing)'}` blocked=`{str(bool(row['blocked'])).lower()}` remediation=`{row['remediation_count']}`"
            for row in topic_rows
        )
        + "\n",
        encoding="utf-8",
    )
    (output_root / "blocker_queue.json").write_text(json.dumps({"items": blocker_queue}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "blocker_queue.md").write_text(
        "# Blocker Queue\n\n"
        + ("\n".join(f"- `{item['topic_slug']}`: {item['summary']}" for item in blocker_queue) or "- (none)")
        + "\n",
        encoding="utf-8",
    )
    return payload
```

- [ ] **Step 4: Run the focused helper test**

Run: `python -m pytest research/knowledge-hub/tests/test_control_plane_index_support.py -q`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add research/knowledge-hub/knowledge_hub/control_plane_index_support.py research/knowledge-hub/tests/test_control_plane_index_support.py
git commit -m "feat: add thin control plane index support"
```

## Task 2: Integrate Control-Plane Index Into Service And Orchestration

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/runtime/scripts/orchestrate_topic.py`
- Modify: `research/knowledge-hub/tests/test_aitp_service.py`
- Modify: `research/knowledge-hub/tests/test_runtime_scripts.py`

- [ ] **Step 1: Write failing service and orchestrator regressions**

```python
def test_list_active_topics_publishes_control_plane_paths(self) -> None:
    payload = self.service.list_active_topics(updated_by="pytest")
    self.assertIn("control_plane_index_path", payload)
    self.assertIn("blocker_queue_path", payload)
    self.assertTrue(Path(payload["control_plane_index_path"]).exists())


def test_orchestrate_topic_refreshes_runtime_control_plane_surfaces(self) -> None:
    topic_slug = "demo-topic"
    self.orchestrate_topic.main(
        [
            "--topic-slug",
            topic_slug,
            "--updated-by",
            "pytest",
        ]
    )
    control_root = self.knowledge_root / "runtime" / "control_plane"
    self.assertTrue((control_root / "topic_control_index.json").exists())
    self.assertTrue((control_root / "blocker_queue.json").exists())
```

- [ ] **Step 2: Run the targeted tests to verify the paths are not wired yet**

Run: `python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k control_plane_index -q`

Expected: FAIL because `list_active_topics()` does not yet return `control_plane_index_path`

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k control_plane -q`

Expected: FAIL because `orchestrate_topic.py` does not yet refresh `runtime/control_plane/*`

- [ ] **Step 3: Wire the helper through `AITPService` and the orchestration script**

```python
from .control_plane_index_support import (
    materialize_control_plane_index as materialize_control_plane_index_surface,
)


def _control_plane_root(self) -> Path:
    return self.kernel_root / "runtime" / "control_plane"


def materialize_control_plane_index(
    self,
    *,
    updated_by: str = "aitp-cli",
) -> dict[str, Any]:
    return materialize_control_plane_index_surface(
        kernel_root=self.kernel_root,
        updated_by=updated_by,
        active_topics_path=self._active_topics_registry_paths()["json"],
        output_root=self._control_plane_root(),
    )


def list_active_topics(self, *, updated_by: str = "aitp-cli") -> dict[str, Any]:
    ...
    control_plane = self.materialize_control_plane_index(updated_by=updated_by)
    return {
        ...
        "control_plane_index_path": str(self._control_plane_root() / "topic_control_index.json"),
        "control_plane_index_note_path": str(self._control_plane_root() / "topic_control_index.md"),
        "blocker_queue_path": str(self._control_plane_root() / "blocker_queue.json"),
        "blocker_queue_note_path": str(self._control_plane_root() / "blocker_queue.md"),
        "control_plane_summary": {
            "topic_count": control_plane.get("topic_count", 0),
            "blocker_count": len(control_plane.get("blocker_queue") or []),
        },
    }
```

And in `orchestrate_topic.py`, after writing topic-local runtime surfaces:

```python
service = AITPService(...)
service.materialize_control_plane_index(updated_by=args.updated_by)
```

- [ ] **Step 4: Re-run the targeted integration tests**

Run: `python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k control_plane_index -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k control_plane -q`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add research/knowledge-hub/knowledge_hub/aitp_service.py research/knowledge-hub/runtime/scripts/orchestrate_topic.py research/knowledge-hub/tests/test_aitp_service.py research/knowledge-hub/tests/test_runtime_scripts.py
git commit -m "feat: wire thin control plane into service and orchestration"
```

## Task 3: Materialize Remediation Tasks From Notebook Obligations

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/remediation_task_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/research_report_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/research_notebook_support.py`
- Modify: `research/knowledge-hub/tests/test_research_report_support.py`
- Modify: `research/knowledge-hub/tests/test_research_notebook_support.py`

- [ ] **Step 1: Add failing remediation-task tests**

```python
def test_materialize_research_report_writes_remediation_task_ledger_for_missing_blocks() -> None:
    service, topic_slug, run_id, runtime_root = _build_service_fixture(
        round_type="numerical_or_benchmark_round",
        plan_overrides={"observable_definition": ""},
        l4_return_overrides={},
        synthesis_overrides={},
    )

    payload = service.materialize_research_report(
        topic_slug=topic_slug,
        run_id=run_id,
        updated_by="pytest",
    )

    remediation_path = runtime_root / "remediation_tasks.json"
    assert remediation_path.exists()
    remediation = json.loads(remediation_path.read_text(encoding="utf-8"))
    assert remediation["items"][0]["missing_block"] == "observable_definition"
    assert remediation["items"][0]["recommended_round_type"] == "numerical_or_benchmark_round"
    assert payload["remediation_tasks"][0]["blocks_claim_use"] is True


def test_topic_notebook_renders_remediation_tasks_section() -> None:
    notebook.compile_notebook(topic_root / "L3")
    tex_path = topic_root / "L3" / "research_notebook.tex"
    rendered = tex_path.read_text(encoding="utf-8")
    assert "Remediation Tasks" in rendered
    assert "observable definition" in rendered.lower()
```

- [ ] **Step 2: Run the report/notebook tests to confirm the new ledger is absent**

Run: `python -m pytest research/knowledge-hub/tests/test_research_report_support.py -k remediation -q`

Expected: FAIL because `remediation_tasks.json` is not written and `payload["remediation_tasks"]` is missing

Run: `python -m pytest research/knowledge-hub/tests/test_research_notebook_support.py -k remediation -q`

Expected: FAIL because the notebook has no remediation section

- [ ] **Step 3: Implement the remediation-task helper and connect it to report generation**

```python
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_remediation_tasks(*, topic_slug: str, round_rows: list[dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for round_row in round_rows:
        round_id = str(round_row.get("iteration_id") or "").strip()
        hard_blocks = set(round_row.get("hard_blocking_gaps") or [])
        for missing_block in round_row.get("missing_blocks") or []:
            key = (round_id, str(missing_block))
            if key in seen:
                continue
            seen.add(key)
            items.append(
                {
                    "task_id": f"remediation:{topic_slug}:{round_id}:{missing_block}",
                    "status": "pending",
                    "topic_slug": topic_slug,
                    "source_round_id": round_id,
                    "round_type": round_row.get("round_type"),
                    "missing_block": missing_block,
                    "blocks_claim_use": missing_block in hard_blocks,
                    "recommended_round_type": round_row.get("round_type"),
                    "summary": f"Repair notebook obligation '{missing_block}' for {round_id}.",
                    "expected_writeback_paths": [
                        f"topics/{topic_slug}/runtime/research_report.active.json",
                        f"topics/{topic_slug}/runtime/unfinished_work.json",
                    ],
                }
            )
    return {
        "status": "available",
        "topic_slug": topic_slug,
        "updated_at": _now_iso(),
        "items": items,
    }


def write_remediation_tasks(runtime_root: Path, payload: dict[str, Any]) -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "remediation_tasks.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (runtime_root / "remediation_tasks.md").write_text(
        "# Remediation Tasks\n\n"
        + ("\n".join(f"- `{item['task_id']}`: {item['summary']}" for item in payload.get("items") or []) or "- (none)")
        + "\n",
        encoding="utf-8",
    )
```

Then in `research_report_support.py`, after `_merge_unfinished_items(...)`:

```python
from .remediation_task_support import build_remediation_tasks, write_remediation_tasks

remediation_tasks = build_remediation_tasks(
    topic_slug=topic_slug,
    round_rows=round_development,
)
write_remediation_tasks(runtime_root, remediation_tasks)
payload["remediation_tasks"] = remediation_tasks.get("items") or []
```

And in `research_notebook_support.py`, extend `_render_open_problems_section(...)` with:

```python
remediation = _read_json(topic_paths["runtime_root"] / "remediation_tasks.json") or {}
for row in _dict_list(remediation.get("items")):
    items.append(f"{row.get('summary')} [{row.get('status') or 'pending'}]")
```

- [ ] **Step 4: Re-run the focused report/notebook tests**

Run: `python -m pytest research/knowledge-hub/tests/test_research_report_support.py -k remediation -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_research_notebook_support.py -k remediation -q`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add research/knowledge-hub/knowledge_hub/remediation_task_support.py research/knowledge-hub/knowledge_hub/research_report_support.py research/knowledge-hub/knowledge_hub/research_notebook_support.py research/knowledge-hub/tests/test_research_report_support.py research/knowledge-hub/tests/test_research_notebook_support.py
git commit -m "feat: materialize remediation tasks from notebook obligations"
```

## Task 4: Add The Thin Dispatch Contract And Adapter Writeback

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/dispatch_target_support.py`
- Modify: `research/knowledge-hub/runtime/scripts/decide_next_action.py`
- Modify: `research/adapters/openclaw/scripts/dispatch_action_queue.py`
- Modify: `research/adapters/openclaw/scripts/dispatch_execution_task.py`
- Modify: `research/knowledge-hub/tests/test_runtime_scripts.py`
- Modify: `research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py`
- Modify: `docs/PROJECT_INDEX.md`
- Modify: `research/knowledge-hub/runtime/README.md`

- [ ] **Step 1: Add failing dispatch-contract tests**

```python
def test_decide_next_action_writes_dispatch_targets_for_selected_action(self) -> None:
    self._rewrite_action_queue(
        "dispatch_execution_task",
        "Dispatch the bounded benchmark repair.",
        handler_args={"run_id": "run-001"},
    )
    self.decide_next_action.main(
        [
            "--topic-slug",
            "demo-topic",
            "--updated-by",
            "pytest",
        ]
    )
    dispatch_targets = json.loads((self.runtime_root / "control_plane" / "dispatch_targets.json").read_text(encoding="utf-8"))
    assert dispatch_targets["items"][0]["target_kind"] == "selected_action"
    assert dispatch_targets["items"][0]["action_ref"].endswith("action_queue.jsonl#action:demo-topic")


def test_dispatch_execution_task_receipt_records_dispatch_target_id(self) -> None:
    ...
    self.assertEqual(receipt_rows[0]["dispatch_target_id"], "dispatch:demo-topic:repair")
    self.assertIn("expected_writeback_paths", receipt_rows[0])
```

- [ ] **Step 2: Run the dispatch-focused tests to verify the contract is missing**

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k dispatch_targets -q`

Expected: FAIL because `runtime/control_plane/dispatch_targets.json` is not written

Run: `python -m pytest research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py -k dispatch_target -q`

Expected: FAIL because receipts do not yet include `dispatch_target_id`

- [ ] **Step 3: Implement dispatch-target payload generation and adapter consumption**

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_selected_action_dispatch_target(*, topic_slug: str, selected_action: dict[str, Any], runtime_root: Path) -> dict[str, Any]:
    action_id = str(selected_action.get("action_id") or "").strip()
    return {
        "dispatch_target_id": f"dispatch:{topic_slug}:{action_id.split(':')[-1] or 'action'}",
        "target_kind": "selected_action",
        "topic_slug": topic_slug,
        "action_ref": f"topics/{topic_slug}/runtime/action_queue.jsonl#{action_id}",
        "task_ref": None,
        "dispatch_surface": "action_queue",
        "session_ref": f"topics/{topic_slug}/runtime/next_action_decision.json",
        "writeback_paths": [
            f"topics/{topic_slug}/runtime/next_action_decision.json",
            f"topics/{topic_slug}/runtime/unfinished_work.json",
        ],
        "reply_required": bool(selected_action.get("auto_runnable")),
        "retry_policy": {"mode": "manual"},
        "cooldown_policy": {"seconds": 0},
    }


def write_dispatch_targets(control_root: Path, items: list[dict[str, Any]]) -> None:
    control_root.mkdir(parents=True, exist_ok=True)
    (control_root / "dispatch_targets.json").write_text(
        json.dumps({"items": items}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

Then in `decide_next_action.py`, after building `next_action`:

```python
from knowledge_hub.dispatch_target_support import (
    build_selected_action_dispatch_target,
    write_dispatch_targets,
)

selected_action = next_action.get("selected_action") or {}
dispatch_targets = []
if selected_action:
    dispatch_targets.append(
        build_selected_action_dispatch_target(
            topic_slug=topic_slug,
            selected_action=selected_action,
            runtime_root=topic_runtime_root,
        )
    )
write_dispatch_targets(topic_runtime_root / "control_plane", dispatch_targets)
```

And in `dispatch_execution_task.py`, before appending the receipt:

```python
dispatch_targets = read_json(runtime_root / "control_plane" / "dispatch_targets.json") or {"items": []}
matching_target = next(
    (
        item
        for item in (dispatch_targets.get("items") or [])
        if str(item.get("topic_slug") or "") == topic_slug
    ),
    None,
)
if matching_target:
    receipt["dispatch_target_id"] = matching_target.get("dispatch_target_id")
    receipt["expected_writeback_paths"] = list(matching_target.get("writeback_paths") or [])
```

And in `dispatch_action_queue.py`, prefer the persisted dispatch target when the
selected queue action matches:

```python
dispatch_targets = read_json(runtime_root / "control_plane" / "dispatch_targets.json") or {"items": []}
selected_target = next(
    (
        item
        for item in (dispatch_targets.get("items") or [])
        if str(item.get("action_ref") or "").endswith(f"#{selected_action_id}")
    ),
    None,
)
if selected_target is not None:
    receipt["dispatch_target_id"] = selected_target.get("dispatch_target_id")
```

- [ ] **Step 4: Re-run the targeted dispatch tests**

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k dispatch_targets -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py -k dispatch_target -q`

Expected: PASS

- [ ] **Step 5: Update docs and commit**

```markdown
In `docs/PROJECT_INDEX.md`, add:

| **Control plane index** | `runtime/control_plane/topic_control_index.json` | Cross-topic operator summary | Human, Agent |
| **Blocker queue** | `runtime/control_plane/blocker_queue.json` | Derived actionable blockers across topics | Human, Agent |
| **Dispatch targets** | `topics/<slug>/runtime/control_plane/dispatch_targets.json` | Thin dispatch routing contract for selected actions and remediation work | Agent |
| **Remediation tasks** | `topics/<slug>/runtime/remediation_tasks.json` | Actionable notebook/report gap repairs | Human, Agent |
```

Run:

`python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k 'dispatch_targets or control_plane' -q`

Expected: PASS

Commit:

```bash
git add research/knowledge-hub/knowledge_hub/dispatch_target_support.py research/knowledge-hub/runtime/scripts/decide_next_action.py research/adapters/openclaw/scripts/dispatch_action_queue.py research/adapters/openclaw/scripts/dispatch_execution_task.py research/knowledge-hub/tests/test_runtime_scripts.py research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py docs/PROJECT_INDEX.md research/knowledge-hub/runtime/README.md
git commit -m "feat: add thin dispatch contract surfaces"
```

## Final Verification

- [ ] **Step 1: Run the focused thin-control-plane suite**

Run:

`python -m pytest research/knowledge-hub/tests/test_control_plane_index_support.py research/knowledge-hub/tests/test_research_report_support.py research/knowledge-hub/tests/test_research_notebook_support.py research/knowledge-hub/tests/test_runtime_scripts.py research/knowledge-hub/tests/test_openclaw_dispatch_runtime.py research/knowledge-hub/tests/test_aitp_service.py -k 'control_plane or remediation or dispatch_target' -q`

Expected: PASS with the new thin-control-plane coverage

- [ ] **Step 2: Run one broader regression slice around topic status**

Run:

`python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k 'topic_status or active_topics' -q`

Expected: PASS; active-topic/status surfaces still publish existing fields plus the new control-plane paths

- [ ] **Step 3: Final commit if verification changed snapshots or docs**

```bash
git status --short
git add -A
git commit -m "test: verify thin control plane integration"
```
