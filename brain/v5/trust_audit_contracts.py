"""Contracts for read-only claim trust audit surfaces."""

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


_SUPPORT_STATES = {"unsupported", "evidence_only", "validated", "validated_memory_backed"}


def validate_claim_trust_audit(payload: dict[str, Any], *, path: str = "claim_trust_audit") -> ContractResult:
    """Validate a public, read-only claim trust audit payload."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result

    for key in (
        "ok",
        "kind",
        "claim_id",
        "topic_id",
        "confidence_state",
        "evidence_profile",
        "support_state",
        "supporting_evidence_refs",
        "challenging_evidence_refs",
        "passed_validation_result_ids",
        "failed_validation_result_ids",
        "l2_memory_entry_ids",
        "code_state_ids",
        "trust_update_record_ids",
        "review_actions",
        "mutation_history_available",
        "truth_source",
        "summary_inputs_trusted",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if key not in payload:
            result.add(f"{path}.{key}", "missing required claim trust audit key")

    _require_bool_value(payload.get("ok"), True, f"{path}.ok", result)
    if payload.get("kind") != "claim_trust_audit":
        result.add(f"{path}.kind", "must be 'claim_trust_audit'")
    for key in ("claim_id", "topic_id", "confidence_state", "evidence_profile"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("support_state") not in _SUPPORT_STATES:
        result.add(f"{path}.support_state", f"must be one of {sorted(_SUPPORT_STATES)}")
    for key in (
        "supporting_evidence_refs",
        "challenging_evidence_refs",
        "passed_validation_result_ids",
        "failed_validation_result_ids",
        "l2_memory_entry_ids",
        "code_state_ids",
        "trust_update_record_ids",
        "review_actions",
    ):
        _require_list(payload.get(key), f"{path}.{key}", result)
    if not isinstance(payload.get("mutation_history_available"), bool):
        result.add(f"{path}.mutation_history_available", "must be a boolean")
    if payload.get("truth_source") != "typed_records":
        result.add(f"{path}.truth_source", "must be 'typed_records'")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_claim_trust_audit(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a claim trust audit payload or raise a contract error."""

    result = validate_claim_trust_audit(payload)
    if not result.ok:
        raise ContractError(result)
    return payload
