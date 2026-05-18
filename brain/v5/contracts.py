"""Lightweight payload contracts for AITP v5 interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from brain.v5.runtime_entrypoints import runtime_entrypoints, validate_runtime_entrypoints

@dataclass
class ContractIssue:
    path: str
    message: str


@dataclass
class ContractResult:
    issues: list[ContractIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues

    def add(self, path: str, message: str) -> None:
        self.issues.append(ContractIssue(path=path, message=message))

    def extend(self, other: "ContractResult") -> None:
        self.issues.extend(other.issues)


class ContractError(ValueError):
    """Raised when a v5 payload violates a required contract."""

    def __init__(self, result: ContractResult):
        self.result = result
        summary = "; ".join(f"{issue.path}: {issue.message}" for issue in result.issues)
        super().__init__(summary or "contract validation failed")


_BRIEF_REQUIRED_KEYS = (
    "session",
    "current_focus",
    "flow_profile",
    "risk_assessment",
    "action_budget",
    "known_context",
    "mandatory_reflection",
    "next_action_candidates",
    "forbidden_now",
    "human_checkpoint",
)
_RISK_LEVELS = {"fluid", "guided", "rigorous", "adversarial"}
_MAX_QUESTIONS_BY_LEVEL = {
    "fluid": 1,
    "guided": 3,
    "rigorous": 3,
    "adversarial": 3,
}


def validate_execution_brief(payload: dict[str, Any], *, path: str = "brief") -> ContractResult:
    """Validate the public execution-brief payload."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    for key in _BRIEF_REQUIRED_KEYS:
        if key not in payload:
            result.add(key, "missing required execution brief key")

    if "session" in payload:
        _require_mapping(payload["session"], f"{path}.session", result)
        if isinstance(payload["session"], dict):
            _require_nonempty_str(payload["session"], "session_id", f"{path}.session", result)
            _require_nonempty_str(payload["session"], "topic_id", f"{path}.session", result)
            _require_nonempty_str(payload["session"], "context_id", f"{path}.session", result)

    if "flow_profile" in payload:
        _validate_flow_profile(payload["flow_profile"], f"{path}.flow_profile", result)

    if "risk_assessment" in payload:
        result.extend(validate_risk_assessment(payload["risk_assessment"], path=f"{path}.risk_assessment"))

    if "action_budget" in payload:
        result.extend(validate_action_budget(payload["action_budget"], path=f"{path}.action_budget"))

    if isinstance(payload.get("risk_assessment"), dict) and isinstance(payload.get("action_budget"), dict):
        risk_level = payload["risk_assessment"].get("level")
        budget_level = payload["action_budget"].get("level")
        if risk_level != budget_level:
            result.add(
                f"{path}.action_budget.level",
                f"must match risk_assessment.level ({risk_level!r}), got {budget_level!r}",
            )

    if "mandatory_reflection" in payload:
        _require_list(payload["mandatory_reflection"], f"{path}.mandatory_reflection", result)
        budget = payload.get("action_budget")
        if isinstance(budget, dict) and isinstance(payload["mandatory_reflection"], list):
            max_questions = budget.get("max_questions")
            if isinstance(max_questions, int) and len(payload["mandatory_reflection"]) > max_questions:
                result.add(
                    f"{path}.mandatory_reflection",
                    "contains more questions than action_budget.max_questions",
                )

    if "human_checkpoint" in payload:
        _require_mapping(payload["human_checkpoint"], f"{path}.human_checkpoint", result)
        if isinstance(payload["human_checkpoint"], dict) and not isinstance(payload["human_checkpoint"].get("needed"), bool):
            result.add(f"{path}.human_checkpoint.needed", "must be a boolean")

    for key in ("next_action_candidates", "forbidden_now"):
        if key in payload:
            _require_list(payload[key], f"{path}.{key}", result)

    return result


def require_valid_execution_brief(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a brief payload or raise a contract error."""

    result = validate_execution_brief(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_adapter_packet(payload: dict[str, Any], *, path: str = "adapter") -> ContractResult:
    """Validate the public runtime adapter packet."""

    from brain.v5.adapter_contracts import validate_adapter_packet as _validate_adapter_packet

    return _validate_adapter_packet(payload, path=path)


def require_valid_adapter_packet(payload: dict[str, Any]) -> dict[str, Any]:
    """Return an adapter packet or raise a contract error."""

    from brain.v5.adapter_contracts import require_valid_adapter_packet as _require_valid_adapter_packet

    return _require_valid_adapter_packet(payload)


def validate_adapter_protocol_registry(
    payload: dict[str, Any],
    *,
    path: str = "adapter_protocol_registry",
) -> ContractResult:
    """Validate the public adapter protocol registry payload."""

    from brain.v5.adapter_contracts import validate_adapter_protocol_registry as _validate_adapter_protocol_registry

    return _validate_adapter_protocol_registry(payload, path=path)


def require_valid_adapter_protocol_registry(payload: dict[str, Any]) -> dict[str, Any]:
    """Return an adapter protocol registry payload or raise a contract error."""

    from brain.v5.adapter_contracts import (
        require_valid_adapter_protocol_registry as _require_valid_adapter_protocol_registry,
    )

    return _require_valid_adapter_protocol_registry(payload)


def validate_summary_orientation(payload: dict[str, Any], *, path: str = "summary_orientation") -> ContractResult:
    """Validate a public orientation-only summary view."""

    from brain.v5.summary_contracts import validate_summary_orientation as _validate_summary_orientation

    return _validate_summary_orientation(payload, path=path)


def require_valid_summary_orientation(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a summary orientation payload or raise a contract error."""

    from brain.v5.summary_contracts import require_valid_summary_orientation as _require_valid_summary_orientation

    return _require_valid_summary_orientation(payload)


def validate_session_summary_bundle(payload: dict[str, Any], *, path: str = "session_summary_bundle") -> ContractResult:
    """Validate a public session-summary write result."""

    from brain.v5.summary_contracts import validate_session_summary_bundle as _validate_session_summary_bundle

    return _validate_session_summary_bundle(payload, path=path)


def require_valid_session_summary_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a session-summary bundle payload or raise a contract error."""

    from brain.v5.summary_contracts import (
        require_valid_session_summary_bundle as _require_valid_session_summary_bundle,
    )

    return _require_valid_session_summary_bundle(payload)


def validate_trust_update_preflight(payload: dict[str, Any], *, path: str = "trust_preflight") -> ContractResult:
    """Validate a public trust-update preflight payload."""

    from brain.v5.trust_contracts import validate_trust_update_preflight as _validate_trust_update_preflight

    return _validate_trust_update_preflight(payload, path=path)


def require_valid_trust_update_preflight(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a trust-update preflight payload or raise a contract error."""

    from brain.v5.trust_contracts import require_valid_trust_update_preflight as _require_valid_trust_update_preflight

    return _require_valid_trust_update_preflight(payload)


def validate_trust_update_apply(payload: dict[str, Any], *, path: str = "trust_apply") -> ContractResult:
    """Validate a public trust-update apply payload."""

    from brain.v5.trust_contracts import validate_trust_update_apply as _validate_trust_update_apply

    return _validate_trust_update_apply(payload, path=path)


def require_valid_trust_update_apply(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a trust-update apply payload or raise a contract error."""

    from brain.v5.trust_contracts import require_valid_trust_update_apply as _require_valid_trust_update_apply

    return _require_valid_trust_update_apply(payload)


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


def _validate_flow_profile(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    _require_level(payload.get("profile"), f"{path}.profile", result)
    _require_nonempty_str(payload, "reason", path, result)
    _require_list(payload.get("escalation_triggers"), f"{path}.escalation_triggers", result)
    risk_level = payload.get("risk_level")
    if risk_level:
        _require_level(risk_level, f"{path}.risk_level", result)


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


def _require_mapping(value: Any, path: str, result: ContractResult) -> None:
    if not isinstance(value, dict):
        result.add(path, "must be a mapping")


def _require_list(value: Any, path: str, result: ContractResult) -> None:
    if not isinstance(value, list):
        result.add(path, "must be a list")


def _require_nonempty_str(payload: dict[str, Any], key: str, path: str, result: ContractResult) -> None:
    if not isinstance(payload.get(key), str) or not payload.get(key):
        result.add(f"{path}.{key}", "must be a non-empty string")


def _require_bool_value(value: Any, expected: bool, path: str, result: ContractResult) -> None:
    if value is not expected:
        result.add(path, f"must be {expected}")


def _require_level(value: Any, path: str, result: ContractResult) -> None:
    if value not in _RISK_LEVELS:
        result.add(path, f"must be one of {sorted(_RISK_LEVELS)}")
