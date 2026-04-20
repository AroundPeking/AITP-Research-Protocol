from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.control_plane_index_support import materialize_control_plane_index


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
                    {
                        "topic_slug": "blocked-topic",
                        "operator_status": "ready",
                        "focus_state": "focused",
                    },
                    {
                        "topic_slug": "ready-topic",
                        "operator_status": "ready",
                        "focus_state": "background",
                    },
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
