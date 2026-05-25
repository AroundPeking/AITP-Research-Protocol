"""Contracts for legacy-review driven source reconstruction repairs."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractError, ContractResult, _require_bool_value, _require_list, _require_mapping, _require_nonempty_str

_REPAIR_TYPES = {"reconstruction_path_evidence_backfill"}


def validate_legacy_source_reconstruction_plan(
    payload: dict[str, Any],
    *,
    path: str = "legacy_source_reconstruction_plan",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_source_reconstruction_plan":
        result.add(f"{path}.kind", "must be 'legacy_source_reconstruction_plan'")
    for key in ("run_id", "migration_dir", "topic", "active_claim_id", "repair_status", "truth_source"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("repair_status") not in {
        "proposed_repairs",
        "awaiting_needs_revision_review",
        "no_repair_candidates",
    }:
        result.add(f"{path}.repair_status", "must be an allowed repair status")
    if payload.get("truth_source") != "typed_review_results_and_legacy_refs":
        result.add(f"{path}.truth_source", "must be 'typed_review_results_and_legacy_refs'")
    _require_mapping(payload.get("latest_semantic_review"), f"{path}.latest_semantic_review", result)
    _require_list(payload.get("proposed_repairs"), f"{path}.proposed_repairs", result)
    if isinstance(payload.get("proposed_repairs"), list):
        for index, repair in enumerate(payload["proposed_repairs"]):
            _validate_plan_repair(repair, f"{path}.proposed_repairs[{index}]", result)
    for key in (
        "can_apply",
        "semantic_lossless_proven",
        "summary_inputs_trusted",
        "orientation_only",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("can_apply"), False, f"{path}.can_apply", result)
    _require_bool_value(payload.get("semantic_lossless_proven"), False, f"{path}.semantic_lossless_proven", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_legacy_source_reconstruction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_source_reconstruction_plan(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_legacy_source_reconstruction_apply(
    payload: dict[str, Any],
    *,
    path: str = "legacy_source_reconstruction_apply",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_source_reconstruction_apply":
        result.add(f"{path}.kind", "must be 'legacy_source_reconstruction_apply'")
    for key in ("repair_id", "run_id", "migration_dir", "topic", "active_claim_id", "review_id", "repair_type"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("repair_type") not in _REPAIR_TYPES:
        result.add(f"{path}.repair_type", "must be an allowed repair type")
    if not isinstance(payload.get("evidence_id"), str):
        result.add(f"{path}.evidence_id", "must be a string")
    for key in ("basis_refs", "required_actions"):
        _require_list(payload.get(key), f"{path}.{key}", result)
    for key in (
        "applied",
        "semantic_lossless_proven",
        "summary_inputs_trusted",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("semantic_lossless_proven"), False, f"{path}.semantic_lossless_proven", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_legacy_source_reconstruction_apply(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_source_reconstruction_apply(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_plan_repair(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in (
        "repair_type",
        "target_ref",
        "current_missing_component",
        "proposed_evidence_type",
        "proposed_status",
        "mutation_authority",
    ):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("repair_type") not in _REPAIR_TYPES:
        result.add(f"{path}.repair_type", "must be an allowed repair type")
    if payload.get("current_missing_component") != "reconstruction_path":
        result.add(f"{path}.current_missing_component", "must be reconstruction_path")
    if payload.get("proposed_evidence_type") != "source_reconstruction":
        result.add(f"{path}.proposed_evidence_type", "must be source_reconstruction")
    if payload.get("mutation_authority") != "typed_review_and_apply_separately":
        result.add(f"{path}.mutation_authority", "must be typed_review_and_apply_separately")
    for key in ("proposed_supports_outputs", "source_refs", "basis_refs"):
        _require_list(payload.get(key), f"{path}.{key}", result)
