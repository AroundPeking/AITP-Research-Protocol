"""Contracts for natural interaction recording worklists."""

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


_REQUIRED_KEYS = (
    "kind",
    "session_count",
    "work_item_count",
    "required_now_count",
    "decision_mode_counts",
    "items",
    "source_preview_refs",
    "source_records",
    "derived_from",
    "truth_source",
    "summary_inputs_trusted",
    "orientation_only",
    "adapter_rule",
    "can_update_kernel_state",
    "can_update_claim_trust",
)
_DECISION_MODES = {"lightweight_trace", "guarded_recording", "trust_boundary_checkpoint"}
_ACTION_KINDS = {
    "keep_lightweight_until_claim_binding",
    "optional_sensemaking_trace_before_trust",
    "record_sensemaking_then_evidence_before_trust",
    "request_checkpoint_before_natural_recording",
}


def validate_interaction_recording_worklist(
    payload: dict[str, Any],
    *,
    path: str = "interaction_recording_worklist",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    for key in _REQUIRED_KEYS:
        if key not in payload:
            result.add(f"{path}.{key}", "missing required interaction worklist key")
    if payload.get("kind") != "interaction_recording_worklist":
        result.add(f"{path}.kind", "must be 'interaction_recording_worklist'")
    if payload.get("derived_from") != "workspace_interaction_preview_bundle":
        result.add(f"{path}.derived_from", "must be 'workspace_interaction_preview_bundle'")
    if payload.get("truth_source") != "typed_records":
        result.add(f"{path}.truth_source", "must be 'typed_records'")
    if payload.get("adapter_rule") != "read_for_orientation_then_call_kernel_before_trust_updates":
        result.add(f"{path}.adapter_rule", "must be the orientation adapter rule")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    _require_list(payload.get("items"), f"{path}.items", result)
    _require_list(payload.get("source_preview_refs"), f"{path}.source_preview_refs", result)
    _require_mapping(payload.get("source_records"), f"{path}.source_records", result)
    _validate_counts(payload, path, result)
    for index, item in enumerate(payload.get("items") or []):
        _validate_item(item, f"{path}.items[{index}]", result)
    return result


def require_valid_interaction_recording_worklist(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_interaction_recording_worklist(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_counts(payload: dict[str, Any], path: str, result: ContractResult) -> None:
    for key in ("session_count", "work_item_count", "required_now_count"):
        if not isinstance(payload.get(key), int) or payload[key] < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    items = payload.get("items")
    if isinstance(items, list):
        if isinstance(payload.get("work_item_count"), int) and payload["work_item_count"] != len(items):
            result.add(f"{path}.work_item_count", "must equal the number of worklist items")
        if isinstance(payload.get("session_count"), int) and payload["session_count"] != len(items):
            result.add(f"{path}.session_count", "must equal the number of worklist items")
        if isinstance(payload.get("required_now_count"), int):
            required = sum(1 for item in items if isinstance(item, dict) and item.get("required_now") is True)
            if payload["required_now_count"] != required:
                result.add(f"{path}.required_now_count", "must equal required-now item count")
    counts = payload.get("decision_mode_counts")
    _require_mapping(counts, f"{path}.decision_mode_counts", result)
    if isinstance(counts, dict):
        for key, value in counts.items():
            if key not in _DECISION_MODES:
                result.add(f"{path}.decision_mode_counts.{key}", "must be a supported recording decision mode")
            if not isinstance(value, int) or value < 0:
                result.add(f"{path}.decision_mode_counts.{key}", "must be a non-negative integer")


def _validate_item(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("session_id", "topic_id", "recording_mode", "action_kind", "source_preview_ref"):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("active_claim"), str):
        result.add(f"{path}.active_claim", "must be a string")
    if payload.get("recording_mode") not in _DECISION_MODES:
        result.add(f"{path}.recording_mode", "must be a supported recording decision mode")
    if payload.get("action_kind") not in _ACTION_KINDS:
        result.add(f"{path}.action_kind", "must be a supported interaction action kind")
    if not isinstance(payload.get("required_now"), bool):
        result.add(f"{path}.required_now", "must be a bool")
    if not isinstance(payload.get("can_continue_without_kernel_write"), bool):
        result.add(f"{path}.can_continue_without_kernel_write", "must be a bool")
    if not isinstance(payload.get("max_questions"), int) or payload["max_questions"] < 0:
        result.add(f"{path}.max_questions", "must be a non-negative integer")
    if not isinstance(payload.get("next_kernel_entrypoint"), str):
        result.add(f"{path}.next_kernel_entrypoint", "must be a string")
    for key in ("heavier_triggers", "mcp_entrypoints", "cli_templates", "before_trust_change"):
        _require_list(payload.get(key), f"{path}.{key}", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
