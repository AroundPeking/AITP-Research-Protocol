"""Workspace replay contract helpers for legacy topic-question backfill blockers."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractResult, _require_bool_value, _require_list, _require_mapping, _require_nonempty_str


def validate_legacy_topic_question_backfill_backlog(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    if payload.get("surface") != "legacy_topic_question_backfill_packet":
        result.add(f"{path}.surface", "must be legacy_topic_question_backfill_packet")
    _require_nonempty_str(payload, "migration_dir", path, result)
    for key in ("backfill_item_count", "open_decision_count", "pending_request_count"):
        if not isinstance(payload.get(key), int) or payload[key] < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    _require_list(payload.get("top_backfill_items"), f"{path}.top_backfill_items", result)
    if isinstance(payload.get("top_backfill_items"), list):
        for index, item in enumerate(payload["top_backfill_items"]):
            _validate_item(item, f"{path}.top_backfill_items[{index}]", result)
    for key in (
        "auto_backfill_allowed",
        "summary_inputs_trusted",
        "orientation_only",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("auto_backfill_allowed"), False, f"{path}.auto_backfill_allowed", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)


def _validate_item(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in (
        "topic",
        "active_claim_id",
        "latest_review_id",
        "review_status",
        "mode",
        "reason",
        "cli",
        "mcp",
    ):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("mode") == "decide_open_checkpoint":
        _require_nonempty_str(payload, "checkpoint_id", path, result)
    elif not isinstance(payload.get("checkpoint_id"), str):
        result.add(f"{path}.checkpoint_id", "must be a string")
    _require_list(payload.get("options"), f"{path}.options", result)
    _require_bool_value(payload.get("auto_backfill_allowed"), False, f"{path}.auto_backfill_allowed", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
