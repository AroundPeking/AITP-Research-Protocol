"""Risk and action-budget contracts for AITP v5 protocol weight."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import (
    ContractResult,
    _require_level,
    _require_list,
    _require_mapping,
    _require_nonempty_str,
)


_MAX_QUESTIONS_BY_LEVEL = {
    "fluid": 1,
    "guided": 3,
    "rigorous": 3,
    "adversarial": 3,
}


def validate_risk_assessment(payload: dict[str, Any], *, path: str = "risk_assessment") -> ContractResult:
    """Validate a risk assessment payload."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    _require_level(payload.get("level"), f"{path}.level", result)
    if not isinstance(payload.get("score"), int):
        result.add(f"{path}.score", "must be an integer")
    if payload.get("score", 0) < 0:
        result.add(f"{path}.score", "must be non-negative")

    signals = payload.get("signals")
    _require_list(signals, f"{path}.signals", result)
    if isinstance(signals, list):
        for index, signal in enumerate(signals):
            _validate_risk_signal(signal, f"{path}.signals[{index}]", result)

    if "trust_reductions" in payload:
        _require_list(payload["trust_reductions"], f"{path}.trust_reductions", result)

    if "action_budget" in payload:
        result.extend(validate_action_budget(payload["action_budget"], path=f"{path}.action_budget"))
        if isinstance(payload["action_budget"], dict) and payload["action_budget"].get("level") != payload.get("level"):
            result.add(f"{path}.action_budget.level", "must match risk assessment level")

    if not isinstance(payload.get("human_checkpoint_needed"), bool):
        result.add(f"{path}.human_checkpoint_needed", "must be a boolean")
    _require_nonempty_str(payload, "summary", path, result)

    return result


def validate_action_budget(payload: dict[str, Any], *, path: str = "action_budget") -> ContractResult:
    """Validate an action-budget payload."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    level = payload.get("level")
    _require_level(level, f"{path}.level", result)

    max_questions = payload.get("max_questions")
    if not isinstance(max_questions, int):
        result.add(f"{path}.max_questions", "must be an integer")
    elif isinstance(level, str) and level in _MAX_QUESTIONS_BY_LEVEL:
        allowed = _MAX_QUESTIONS_BY_LEVEL[level]
        if max_questions > allowed:
            result.add(f"{path}.max_questions", f"{level} budget max_questions must be <= {allowed}")
        if max_questions < 0:
            result.add(f"{path}.max_questions", "must be non-negative")

    for key in ("required_outputs", "allowed_actions"):
        _require_list(payload.get(key), f"{path}.{key}", result)
        if isinstance(payload.get(key), list) and any(not isinstance(item, str) or not item for item in payload[key]):
            result.add(f"{path}.{key}", "must contain non-empty strings")

    if not isinstance(payload.get("requires_human_checkpoint"), bool):
        result.add(f"{path}.requires_human_checkpoint", "must be a boolean")

    return result


def _validate_risk_signal(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("kind", "reason", "evidence_ref", "suggested_action"):
        _require_nonempty_str(payload, key, path, result)
    severity = payload.get("severity")
    if not isinstance(severity, int):
        result.add(f"{path}.severity", "must be an integer")
    elif severity <= 0:
        result.add(f"{path}.severity", "must be positive")
