"""Contracts for legacy topic-question backfill packets."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import (
    ContractError,
    ContractResult,
    _require_bool_value,
    _require_list,
    _require_mapping,
    _require_nonempty_str,
)


def validate_legacy_topic_question_backfill_packet(
    payload: dict[str, Any],
    *,
    path: str = "legacy_topic_question_backfill_packet",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_topic_question_backfill_packet":
        result.add(f"{path}.kind", "must be 'legacy_topic_question_backfill_packet'")
    for key in ("run_id", "migration_dir", "workspace", "truth_source"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("truth_source") != "legacy_semantic_review_worklist_topic_question_commands":
        result.add(f"{path}.truth_source", "must be 'legacy_semantic_review_worklist_topic_question_commands'")
    for key in ("backfill_item_count", "open_decision_count", "pending_request_count"):
        if not isinstance(payload.get(key), int) or payload[key] < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    _require_list(payload.get("items"), f"{path}.items", result)
    if isinstance(payload.get("items"), list):
        if payload.get("backfill_item_count") != len(payload["items"]):
            result.add(f"{path}.backfill_item_count", "must match items length")
        open_count = 0
        pending_count = 0
        for index, item in enumerate(payload["items"]):
            _validate_item(item, f"{path}.items[{index}]", result)
            if isinstance(item, dict):
                checkpoint = item.get("checkpoint") if isinstance(item.get("checkpoint"), dict) else {}
                if checkpoint.get("mode") == "decide_open_checkpoint":
                    open_count += 1
                if checkpoint.get("mode") == "request_checkpoint":
                    pending_count += 1
        if payload.get("open_decision_count") != open_count:
            result.add(f"{path}.open_decision_count", "must match open checkpoint items")
        if payload.get("pending_request_count") != pending_count:
            result.add(f"{path}.pending_request_count", "must match pending checkpoint items")
    _require_list(payload.get("next_actions"), f"{path}.next_actions", result)
    for key, expected in (
        ("auto_backfill_allowed", False),
        ("semantic_lossless_proven", False),
        ("semantic_review_required", True),
        ("summary_inputs_trusted", False),
        ("orientation_only", True),
        ("can_update_kernel_state", False),
        ("can_update_claim_trust", False),
    ):
        _require_bool_value(payload.get(key), expected, f"{path}.{key}", result)
    return result


def require_valid_legacy_topic_question_backfill_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_topic_question_backfill_packet(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_item(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in (
        "topic",
        "active_claim_id",
        "latest_review_id",
        "review_status",
        "needs_revision_result_cli",
    ):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("review_status") not in {"pending", "needs_revision", "inconclusive"}:
        result.add(f"{path}.review_status", "must be a backlog review status")
    _require_bool_value(payload.get("claim_statement_present"), False, f"{path}.claim_statement_present", result)
    _require_bool_value(payload.get("auto_backfill_allowed"), False, f"{path}.auto_backfill_allowed", result)
    for key in ("required_actions", "guardrails"):
        _require_list(payload.get(key), f"{path}.{key}", result)
    _validate_review_basis(payload.get("review_basis"), f"{path}.review_basis", result)
    _validate_checkpoint(payload.get("checkpoint"), f"{path}.checkpoint", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)


def _validate_review_basis(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("reviewed_legacy_refs", "reviewed_typed_refs", "open_checkpoint_refs"):
        _require_list(payload.get(key), f"{path}.{key}", result)


def _validate_checkpoint(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("mode", "reason"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("mode") not in {"decide_open_checkpoint", "request_checkpoint"}:
        result.add(f"{path}.mode", "must be decide_open_checkpoint or request_checkpoint")
    if payload.get("mode") == "decide_open_checkpoint":
        _require_nonempty_str(payload, "checkpoint_id", path, result)
        _require_nonempty_str(payload, "checkpoint_ref", path, result)
    if payload.get("mode") == "request_checkpoint":
        if not isinstance(payload.get("checkpoint_id"), str):
            result.add(f"{path}.checkpoint_id", "must be a string")
        if not isinstance(payload.get("checkpoint_ref"), str):
            result.add(f"{path}.checkpoint_ref", "must be a string")
    _require_list(payload.get("options"), f"{path}.options", result)
    _require_mapping(payload.get("command"), f"{path}.command", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
