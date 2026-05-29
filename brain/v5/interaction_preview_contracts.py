"""Contracts for interaction recording previews."""

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
    "session_id",
    "topic_id",
    "active_claim",
    "interaction_profile",
    "risk_level",
    "flow_profile",
    "can_stay_lightweight",
    "max_questions",
    "mandatory_question_count",
    "natural_workflow",
    "recording_decision",
    "recommended_records",
    "deferred_records",
    "heavier_triggers",
    "boundary_notes",
    "forbidden_now",
    "source_brief_ref",
    "truth_source",
    "summary_inputs_trusted",
    "orientation_only",
    "can_update_kernel_state",
    "can_update_claim_trust",
)


def validate_interaction_recording_preview(
    payload: dict[str, Any],
    *,
    path: str = "interaction_recording_preview",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result

    for key in _REQUIRED_KEYS:
        if key not in payload:
            result.add(f"{path}.{key}", "missing required interaction preview key")

    if payload.get("kind") != "interaction_recording_preview":
        result.add(f"{path}.kind", "must be 'interaction_recording_preview'")
    for key in ("session_id", "topic_id", "risk_level", "flow_profile", "source_brief_ref"):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("active_claim"), str):
        result.add(f"{path}.active_claim", "must be a string")
    _require_mapping(payload.get("interaction_profile"), f"{path}.interaction_profile", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    if payload.get("truth_source") != "typed_records":
        result.add(f"{path}.truth_source", "must be 'typed_records'")
    if not isinstance(payload.get("can_stay_lightweight"), bool):
        result.add(f"{path}.can_stay_lightweight", "must be a bool")
    _validate_recording_decision(payload.get("recording_decision"), f"{path}.recording_decision", result)
    _validate_question_counts(payload, path, result)
    for key in ("natural_workflow", "recommended_records", "deferred_records", "heavier_triggers", "boundary_notes", "forbidden_now"):
        _require_list(payload.get(key), f"{path}.{key}", result)
    for index, item in enumerate(payload.get("recommended_records", [])):
        _validate_record_advice(item, f"{path}.recommended_records[{index}]", result)
    for index, item in enumerate(payload.get("deferred_records", [])):
        _validate_deferred_record(item, f"{path}.deferred_records[{index}]", result)
    return result


def require_valid_interaction_recording_preview(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_interaction_recording_preview(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_question_counts(payload: dict[str, Any], path: str, result: ContractResult) -> None:
    max_questions = payload.get("max_questions")
    count = payload.get("mandatory_question_count")
    if not isinstance(max_questions, int) or max_questions < 0:
        result.add(f"{path}.max_questions", "must be a non-negative integer")
    if not isinstance(count, int) or count < 0:
        result.add(f"{path}.mandatory_question_count", "must be a non-negative integer")
    if isinstance(max_questions, int) and isinstance(count, int) and count > max_questions:
        result.add(f"{path}.mandatory_question_count", "cannot exceed max_questions")


def _validate_record_advice(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("record_type", "timing", "reason"):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("required_now"), bool):
        result.add(f"{path}.required_now", "must be a bool")


def _validate_recording_decision(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    if payload.get("mode") not in {"lightweight_trace", "guarded_recording", "trust_boundary_checkpoint"}:
        result.add(f"{path}.mode", "must be a supported recording decision mode")
    if not isinstance(payload.get("can_continue_without_kernel_write"), bool):
        result.add(f"{path}.can_continue_without_kernel_write", "must be a bool")
    if not isinstance(payload.get("next_kernel_entrypoint"), str):
        result.add(f"{path}.next_kernel_entrypoint", "must be a string")
    _require_list(payload.get("required_before_trust_change"), f"{path}.required_before_trust_change", result)
    _require_nonempty_str(payload, "why", path, result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)


def _validate_deferred_record(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("record_type", "until", "reason"):
        _require_nonempty_str(payload, key, path, result)
    if "required_now" in payload and not isinstance(payload["required_now"], bool):
        result.add(f"{path}.required_now", "must be a bool")
