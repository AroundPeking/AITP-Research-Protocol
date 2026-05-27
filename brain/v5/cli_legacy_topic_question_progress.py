"""Compact CLI progress payload for legacy topic-question backfill blockers."""

from __future__ import annotations

from typing import Any


def compact_legacy_topic_question_backfill_packet(payload: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in payload.get("items", []) if isinstance(item, dict)]
    open_items = [
        item
        for item in items
        if isinstance(item.get("checkpoint"), dict)
        and item["checkpoint"].get("mode") == "decide_open_checkpoint"
    ][:5]
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "legacy_topic_question_backfill_packet_progress",
        "source_surface": "legacy_topic_question_backfill_packet",
        "run_id": str(payload.get("run_id") or ""),
        "migration_dir": str(payload.get("migration_dir") or ""),
        "workspace": str(payload.get("workspace") or ""),
        "backfill_item_count": int(payload.get("backfill_item_count") or 0),
        "open_decision_count": int(payload.get("open_decision_count") or 0),
        "pending_request_count": int(payload.get("pending_request_count") or 0),
        "top_topics": [str(item.get("topic") or "") for item in items[:5] if str(item.get("topic") or "")],
        "top_active_claim_ids": [
            str(item.get("active_claim_id") or "")
            for item in items[:5]
            if str(item.get("active_claim_id") or "")
        ],
        "open_checkpoint_refs": [
            f"human_checkpoint:{checkpoint_id}"
            for checkpoint_id in [
                str(item.get("checkpoint", {}).get("checkpoint_id") or "")
                for item in open_items
            ]
            if checkpoint_id
        ],
        "next_action_count": len(payload.get("next_actions") or []),
        "next_action_refs": _limited_strings(payload.get("next_actions")),
        "auto_backfill_allowed": bool(payload.get("auto_backfill_allowed", False)),
        "semantic_lossless_proven": bool(payload.get("semantic_lossless_proven", False)),
        "semantic_review_required": bool(payload.get("semantic_review_required", True)),
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def _limited_strings(value: Any, *, limit: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value[:limit] if str(item)]
