"""Contracts for vNext research-intent and steering surfaces."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import (
    ContractError,
    ContractResult,
    _require_bool_value,
    _require_list,
    _require_nonempty_str,
)

_INTENT_STATUSES = {"needs_clarification", "approved_for_execution", "deferred"}
_STEERING_STATUSES = {"active", "superseded", "cancelled"}


def validate_research_intent_packet(payload: dict[str, Any], *, path: str = "research_intent_packet") -> ContractResult:
    result = ContractResult()
    _validate_common(payload, path, result, kind="research_intent_packet")
    if not isinstance(payload, dict):
        return result
    for key in ("intent_id", "topic_id", "initial_idea", "status"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("status") not in _INTENT_STATUSES:
        result.add(f"{path}.status", f"must be one of {sorted(_INTENT_STATUSES)}")
    if not isinstance(payload.get("execution_ready"), bool):
        result.add(f"{path}.execution_ready", "must be a boolean")
    if payload.get("status") != "approved_for_execution" and payload.get("execution_ready") is not False:
        result.add(f"{path}.execution_ready", "must be false unless status is approved_for_execution")
    for key in ("non_goals", "clarification_questions"):
        _require_list(payload.get(key), f"{path}.{key}", result)
    return result


def require_valid_research_intent_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_research_intent_packet(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_steering_decision_record(payload: dict[str, Any], *, path: str = "steering_decision_record") -> ContractResult:
    result = ContractResult()
    _validate_common(payload, path, result, kind="steering_decision")
    if not isinstance(payload, dict):
        return result
    for key in ("decision_id", "topic_id", "steering_text", "novelty_target", "scope", "acceptance_posture", "status"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("status") not in _STEERING_STATUSES:
        result.add(f"{path}.status", f"must be one of {sorted(_STEERING_STATUSES)}")
    return result


def require_valid_steering_decision_record(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_steering_decision_record(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_common(payload: Any, path: str, result: ContractResult, *, kind: str) -> None:
    if not isinstance(payload, dict):
        result.add(path, "must be a mapping")
        return
    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != kind:
        result.add(f"{path}.kind", f"must be {kind!r}")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
