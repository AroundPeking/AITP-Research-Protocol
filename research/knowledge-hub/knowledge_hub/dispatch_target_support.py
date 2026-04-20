from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _dispatch_target_id(topic_slug: str, raw_ref: str) -> str:
    suffix = str(raw_ref or "").strip().split(":")[-1] or "target"
    return f"dispatch:{topic_slug}:{suffix}"


def _selected_action_expected_writebacks(topic_slug: str, selected_action: dict[str, Any]) -> list[str]:
    action_type = str(selected_action.get("action_type") or "").strip()
    if action_type != "dispatch_execution_task":
        return []
    handler_args = selected_action.get("handler_args") or {}
    run_id = str(handler_args.get("run_id") or "").strip()
    expected = [f"topics/{topic_slug}/runtime/execution_task.json"]
    if run_id:
        expected.append(
            f"validation/topics/{topic_slug}/runs/{run_id}/returned_execution_result.json"
        )
    return expected


def _selected_action_dispatch_target(
    *,
    topic_slug: str,
    selected_action: dict[str, Any] | None,
    auto_dispatch_allowed: bool,
) -> dict[str, Any] | None:
    if not isinstance(selected_action, dict):
        return None
    action_id = str(selected_action.get("action_id") or "").strip()
    if not action_id:
        return None
    return {
        "dispatch_target_id": _dispatch_target_id(topic_slug, action_id),
        "topic_slug": topic_slug,
        "target_kind": "selected_action",
        "action_id": action_id,
        "action_ref": f"topics/{topic_slug}/runtime/action_queue.jsonl#{action_id}",
        "action_type": selected_action.get("action_type"),
        "handler": selected_action.get("handler"),
        "handler_args": selected_action.get("handler_args") or {},
        "summary": selected_action.get("summary"),
        "auto_dispatch_allowed": bool(auto_dispatch_allowed),
        "expected_writeback_paths": _selected_action_expected_writebacks(topic_slug, selected_action),
    }


def _remediation_dispatch_targets(topic_slug: str, runtime_root: Path) -> list[dict[str, Any]]:
    remediation = _read_json(runtime_root / "remediation_tasks.json") or {}
    targets: list[dict[str, Any]] = []
    for item in remediation.get("items") or []:
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("task_id") or "").strip()
        if not task_id:
            continue
        targets.append(
            {
                "dispatch_target_id": _dispatch_target_id(topic_slug, task_id),
                "topic_slug": topic_slug,
                "target_kind": "remediation_task",
                "source_id": task_id,
                "action_ref": f"topics/{topic_slug}/runtime/remediation_tasks.json#{task_id}",
                "summary": item.get("summary"),
                "status": item.get("status"),
                "blocks_claim_use": bool(item.get("blocks_claim_use")),
                "recommended_round_type": item.get("recommended_round_type"),
                "expected_writeback_paths": list(item.get("expected_writeback_paths") or []),
            }
        )
    return targets


def materialize_dispatch_targets(
    *,
    knowledge_root: Path,
    topic_slug: str,
    runtime_root: Path,
    next_action_decision: dict[str, Any],
    updated_by: str,
) -> dict[str, Any]:
    output_root = knowledge_root / "runtime" / "control_plane"
    existing = _read_json(output_root / "dispatch_targets.json") or {}
    items = [
        item
        for item in (existing.get("items") or [])
        if isinstance(item, dict) and str(item.get("topic_slug") or "").strip() != topic_slug
    ]

    selected_target = _selected_action_dispatch_target(
        topic_slug=topic_slug,
        selected_action=next_action_decision.get("selected_action"),
        auto_dispatch_allowed=bool(next_action_decision.get("auto_dispatch_allowed")),
    )
    if selected_target is not None:
        items.append(selected_target)
    items.extend(_remediation_dispatch_targets(topic_slug, runtime_root))
    items.sort(
        key=lambda item: (
            str(item.get("topic_slug") or ""),
            str(item.get("target_kind") or ""),
            str(item.get("dispatch_target_id") or ""),
        )
    )

    payload = {
        "status": "available",
        "updated_at": _now_iso(),
        "updated_by": updated_by,
        "items": items,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "dispatch_targets.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_root / "dispatch_targets.md").write_text(
        "# Dispatch Targets\n\n"
        + (
            "\n".join(
                f"- `{item['dispatch_target_id']}` kind=`{item.get('target_kind') or '(missing)'}` ref=`{item.get('action_ref') or '(missing)'}`"
                for item in items
            )
            or "- (none)"
        )
        + "\n",
        encoding="utf-8",
    )
    return payload
