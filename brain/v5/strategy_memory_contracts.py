"""Contracts for non-promotional strategy memory records."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import (
    ContractError,
    ContractResult,
    _require_bool_value,
    _require_list,
    _require_nonempty_str,
)

_STRATEGY_TYPES = {"search_route", "verification_guardrail", "debug_pattern", "resource_plan", "scope_control"}
_OUTCOMES = {"helped", "failed", "neutral"}


def validate_strategy_memory_record(payload: dict[str, Any], *, path: str = "strategy_memory_record") -> ContractResult:
    result = ContractResult()
    if not isinstance(payload, dict):
        result.add(path, "must be a mapping")
        return result
    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != "strategy_memory":
        result.add(f"{path}.kind", "must be 'strategy_memory'")
    for key in ("memory_id", "topic_id", "run_id", "strategy_type", "outcome", "lesson", "next_time_rule", "status"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("strategy_type") not in _STRATEGY_TYPES:
        result.add(f"{path}.strategy_type", f"must be one of {sorted(_STRATEGY_TYPES)}")
    if payload.get("outcome") not in _OUTCOMES:
        result.add(f"{path}.outcome", f"must be one of {sorted(_OUTCOMES)}")
    if payload.get("status") not in {"active", "superseded", "archived"}:
        result.add(f"{path}.status", "must be active, superseded, or archived")
    _require_list(payload.get("source_refs"), f"{path}.source_refs", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_strategy_memory_record(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_strategy_memory_record(payload)
    if not result.ok:
        raise ContractError(result)
    return payload
