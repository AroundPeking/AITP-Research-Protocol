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
    selected_action = (
        (next_action.get("selected_action") or {})
        if isinstance(next_action.get("selected_action"), dict)
        else {}
    )
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
    topic_rows = [
        build_topic_control_row(kernel_root=kernel_root, registry_row=row)
        for row in (registry.get("topics") or [])
    ]
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
    (output_root / "topic_control_index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_root / "topic_control_index.md").write_text(
        "# Topic Control Index\n\n"
        + "\n".join(
            f"- `{row['topic_slug']}` stage=`{row['resume_stage'] or '(missing)'}` blocked=`{str(bool(row['blocked'])).lower()}` remediation=`{row['remediation_count']}`"
            for row in topic_rows
        )
        + "\n",
        encoding="utf-8",
    )
    (output_root / "blocker_queue.json").write_text(
        json.dumps({"items": blocker_queue}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_root / "blocker_queue.md").write_text(
        "# Blocker Queue\n\n"
        + ("\n".join(f"- `{item['topic_slug']}`: {item['summary']}" for item in blocker_queue) or "- (none)")
        + "\n",
        encoding="utf-8",
    )
    return payload
