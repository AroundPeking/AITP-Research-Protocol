"""Contracts for legacy L2 typed migration review packets."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractError, ContractResult, _require_bool_value, _require_list, _require_mapping, _require_nonempty_str


def validate_legacy_l2_typed_migration_packet(
    payload: dict[str, Any],
    *,
    path: str = "legacy_l2_typed_migration_packet",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_l2_typed_migration_packet":
        result.add(f"{path}.kind", "must be 'legacy_l2_typed_migration_packet'")
    for key in ("legacy_l2_dir", "legacy_shape", "typed_migration_status", "truth_source"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("truth_source") != "legacy_l2_filesystem":
        result.add(f"{path}.truth_source", "must be 'legacy_l2_filesystem'")
    if payload.get("legacy_shape") not in {"global_l2_graph", "missing"}:
        result.add(f"{path}.legacy_shape", "must be global_l2_graph or missing")
    if payload.get("typed_migration_status") not in {"needs_review", "no_legacy_l2_work_items"}:
        result.add(f"{path}.typed_migration_status", "must be an allowed packet status")
    if not isinstance(payload.get("work_item_count"), int) or payload["work_item_count"] < 0:
        result.add(f"{path}.work_item_count", "must be a non-negative integer")
    _require_mapping(payload.get("work_item_counts_by_kind"), f"{path}.work_item_counts_by_kind", result)
    _require_list(payload.get("migration_work_items"), f"{path}.migration_work_items", result)
    if isinstance(payload.get("migration_work_items"), list):
        for index, item in enumerate(payload["migration_work_items"]):
            _validate_work_item(item, f"{path}.migration_work_items[{index}]", result)
    _require_mapping(payload.get("review_groups"), f"{path}.review_groups", result)
    if isinstance(payload.get("review_groups"), dict):
        for key, group in payload["review_groups"].items():
            _validate_review_group(group, f"{path}.review_groups.{key}", result)
    _require_mapping(payload.get("recommended_commands"), f"{path}.recommended_commands", result)
    if isinstance(payload.get("recommended_commands"), dict):
        for key, command in payload["recommended_commands"].items():
            _validate_command(command, f"{path}.recommended_commands.{key}", result)
    _require_list(payload.get("next_actions"), f"{path}.next_actions", result)
    for key in ("summary_inputs_trusted", "orientation_only", "can_update_kernel_state", "can_update_claim_trust"):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_legacy_l2_typed_migration_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_l2_typed_migration_packet(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_review_group(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    _require_nonempty_str(payload, "target_surface", path, result)
    if not isinstance(payload.get("count"), int) or payload["count"] < 0:
        result.add(f"{path}.count", "must be a non-negative integer")
    _require_list(payload.get("work_item_kinds"), f"{path}.work_item_kinds", result)
    _require_list(payload.get("sample_work_items"), f"{path}.sample_work_items", result)
    _require_list(payload.get("review_questions"), f"{path}.review_questions", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    if isinstance(payload.get("sample_work_items"), list):
        for index, item in enumerate(payload["sample_work_items"]):
            _validate_work_item(item, f"{path}.sample_work_items[{index}]", result)


def _validate_work_item(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in (
        "work_item_id",
        "work_item_kind",
        "legacy_id",
        "role",
        "status",
        "source_path",
        "recommended_target_surface",
        "migration_action",
    ):
        _require_nonempty_str(payload, key, path, result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)


def _validate_command(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("effect", "cli", "mcp"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("effect") not in {"review_only", "typed_record_write_after_review"}:
        result.add(f"{path}.effect", "must be review_only or typed_record_write_after_review")
    for key in ("can_update_kernel_state", "can_update_claim_trust"):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
