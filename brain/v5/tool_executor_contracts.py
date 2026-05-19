"""Contracts for safe tool-executor catalog surfaces."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractError, ContractResult, _require_bool_value, _require_list, _require_mapping


def validate_tool_executor_catalog(payload: dict[str, Any], *, path: str = "tool_executor_catalog") -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != "tool_executor_catalog":
        result.add(f"{path}.kind", "must be 'tool_executor_catalog'")
    if payload.get("truth_source") != "builtin_executor_registry":
        result.add(f"{path}.truth_source", "must be 'builtin_executor_registry'")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_list(payload.get("executors"), f"{path}.executors", result)
    if isinstance(payload.get("executor_count"), int) and isinstance(payload.get("executors"), list):
        if payload["executor_count"] != len(payload["executors"]):
            result.add(f"{path}.executor_count", "must match number of executors")
    elif "executor_count" in payload:
        result.add(f"{path}.executor_count", "must be an integer")
    if isinstance(payload.get("executors"), list):
        for index, executor in enumerate(payload["executors"]):
            _validate_executor(executor, f"{path}.executors[{index}]", result)
    return result


def require_valid_tool_executor_catalog(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_tool_executor_catalog(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_executor(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("executor_id", "tool_family", "tool_name", "execution_mode", "version", "purpose"):
        if not isinstance(payload.get(key), str) or not payload[key]:
            result.add(f"{path}.{key}", "must be a non-empty string")
    _require_list(payload.get("evidence_profiles"), f"{path}.evidence_profiles", result)
    _require_mapping(payload.get("input_schema"), f"{path}.input_schema", result)
    _require_mapping(payload.get("output_schema"), f"{path}.output_schema", result)
