"""Contracts for read-only record-ref lookup surfaces."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractError, ContractResult, _require_list, _require_mapping

_STATUSES = {"found", "not_found", "unsupported_kind", "malformed_ref"}


def validate_record_ref_lookup(payload: dict[str, Any], *, path: str = "record_ref_lookup") -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result

    if payload.get("kind") != "record_ref_lookup":
        result.add(f"{path}.kind", "must be 'record_ref_lookup'")
    if payload.get("lookup_scope") != "typed_record_existence_only":
        result.add(f"{path}.lookup_scope", "must be 'typed_record_existence_only'")
    if payload.get("read_surface_effect") != "record_existence_check_only":
        result.add(f"{path}.read_surface_effect", "must be 'record_existence_check_only'")
    for key in ("records_validation_result", "source_support_result", "evidence_created", "validation_created"):
        if payload.get(key) is not False:
            result.add(f"{path}.{key}", "must be false")
    if payload.get("claim_trust_mutation") != "none":
        result.add(f"{path}.claim_trust_mutation", "must be 'none'")
    if payload.get("can_update_claim_trust") is not False:
        result.add(f"{path}.can_update_claim_trust", "must be false")
    if payload.get("summary_inputs_trusted") is not False:
        result.add(f"{path}.summary_inputs_trusted", "must be false")
    if payload.get("orientation_only") is not True:
        result.add(f"{path}.orientation_only", "must be true")

    refs = payload.get("refs")
    _require_list(refs, f"{path}.refs", result)
    if isinstance(refs, list):
        _validate_counts(payload, refs, path, result)
        for index, item in enumerate(refs):
            _validate_lookup_item(item, f"{path}.refs[{index}]", result)
    _require_list(payload.get("supported_ref_kinds"), f"{path}.supported_ref_kinds", result)
    return result


def require_valid_record_ref_lookup(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_record_ref_lookup(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_counts(payload: dict[str, Any], refs: list[Any], path: str, result: ContractResult) -> None:
    expected = {
        "lookup_count": len(refs),
        "found_count": sum(1 for item in refs if isinstance(item, dict) and item.get("status") == "found"),
        "missing_count": sum(1 for item in refs if isinstance(item, dict) and item.get("status") == "not_found"),
        "unsupported_count": sum(1 for item in refs if isinstance(item, dict) and item.get("status") == "unsupported_kind"),
        "malformed_count": sum(1 for item in refs if isinstance(item, dict) and item.get("status") == "malformed_ref"),
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            result.add(f"{path}.{key}", "must match refs status counts")


def _validate_lookup_item(item: Any, path: str, result: ContractResult) -> None:
    _require_mapping(item, path, result)
    if not isinstance(item, dict):
        return
    for key in ("ref", "status", "read_surface_effect", "claim_trust_mutation"):
        if not isinstance(item.get(key), str) or not item.get(key):
            result.add(f"{path}.{key}", "must be a non-empty string")
    for key in (
        "suggested_next_operation",
        "suggested_next_entrypoint",
        "suggested_next_surface",
        "suggested_next_reason",
    ):
        if not isinstance(item.get(key), str):
            result.add(f"{path}.{key}", "must be a string")
    if item.get("status") not in _STATUSES:
        result.add(f"{path}.status", "must be a supported lookup status")
    if item.get("read_surface_effect") != "record_existence_check_only":
        result.add(f"{path}.read_surface_effect", "must be 'record_existence_check_only'")
    if item.get("claim_trust_mutation") != "none":
        result.add(f"{path}.claim_trust_mutation", "must be 'none'")
    for key in ("record_confirmed", "records_validation_result", "source_support_result", "can_update_claim_trust"):
        if not isinstance(item.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    if item.get("status") == "found" and item.get("record_confirmed") is not True:
        result.add(f"{path}.record_confirmed", "must be true when status is found")
    if item.get("status") != "found" and item.get("record_confirmed") is not False:
        result.add(f"{path}.record_confirmed", "must be false unless status is found")
    if item.get("records_validation_result") is not False:
        result.add(f"{path}.records_validation_result", "must be false")
    if item.get("source_support_result") is not False:
        result.add(f"{path}.source_support_result", "must be false")
    if item.get("can_update_claim_trust") is not False:
        result.add(f"{path}.can_update_claim_trust", "must be false")
    if item.get("can_update_record_claim_trust") is not False:
        result.add(f"{path}.can_update_record_claim_trust", "must be false")
