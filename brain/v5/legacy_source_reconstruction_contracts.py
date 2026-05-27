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


def validate_legacy_source_reconstruction_manifest(
    payload: dict[str, Any],
    *,
    path: str = "legacy_source_reconstruction_manifest",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_source_reconstruction_manifest":
        result.add(f"{path}.kind", "must be 'legacy_source_reconstruction_manifest'")
    for key in ("run_id", "migration_dir", "truth_source"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("truth_source") != "typed_review_results_legacy_refs_and_source_reconstruction_audit":
        result.add(
            f"{path}.truth_source",
            "must be 'typed_review_results_legacy_refs_and_source_reconstruction_audit'",
        )
    for key in ("work_item_count", "proposed_repair_count"):
        if not isinstance(payload.get(key), int) or payload[key] < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    for key in ("repair_status_counts", "missing_component_counts", "required_action_counts"):
        _require_mapping(payload.get(key), f"{path}.{key}", result)
    _require_list(payload.get("items"), f"{path}.items", result)
    if isinstance(payload.get("items"), list):
        for index, item in enumerate(payload["items"]):
            _validate_manifest_item(item, f"{path}.items[{index}]", result)
    _require_list(payload.get("next_actions"), f"{path}.next_actions", result)
    for key in (
        "semantic_lossless_proven",
        "semantic_review_required",
        "summary_inputs_trusted",
        "orientation_only",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("semantic_lossless_proven"), False, f"{path}.semantic_lossless_proven", result)
    _require_bool_value(payload.get("semantic_review_required"), True, f"{path}.semantic_review_required", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_legacy_source_reconstruction_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_source_reconstruction_manifest(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_legacy_source_reconstruction_review_packet(
    payload: dict[str, Any],
    *,
    path: str = "legacy_source_reconstruction_review_packet",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_source_reconstruction_review_packet":
        result.add(f"{path}.kind", "must be 'legacy_source_reconstruction_review_packet'")
    for key in (
        "run_id",
        "migration_dir",
        "topic",
        "active_claim_id",
        "source_reconstruction_status",
        "review_result_cli",
        "truth_source",
    ):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("latest_review_id"), str):
        result.add(f"{path}.latest_review_id", "must be a string")
    _require_list(payload.get("missing_components"), f"{path}.missing_components", result)
    if isinstance(payload.get("missing_components"), list):
        for index, component in enumerate(payload["missing_components"]):
            if not isinstance(component, str) or not component:
                result.add(f"{path}.missing_components[{index}]", "must be a non-empty string")
    if not isinstance(payload.get("component_review_count"), int) or payload["component_review_count"] < 0:
        result.add(f"{path}.component_review_count", "must be a non-negative integer")
    if payload.get("truth_source") != "typed_review_results_legacy_refs_and_source_reconstruction_packet":
        result.add(f"{path}.truth_source", "must be 'typed_review_results_legacy_refs_and_source_reconstruction_packet'")
    _require_mapping(payload.get("latest_semantic_review"), f"{path}.latest_semantic_review", result)
    _require_mapping(payload.get("source_reconstruction_review_packet"), f"{path}.source_reconstruction_review_packet", result)
    _require_mapping(payload.get("legacy_refs"), f"{path}.legacy_refs", result)
    if isinstance(payload.get("legacy_refs"), dict):
        _require_list(payload["legacy_refs"].get("reviewed_legacy_refs"), f"{path}.legacy_refs.reviewed_legacy_refs", result)
        _require_list(payload["legacy_refs"].get("source_reconstruction_refs"), f"{path}.legacy_refs.source_reconstruction_refs", result)
        _require_mapping(payload["legacy_refs"].get("refs_by_prefix"), f"{path}.legacy_refs.refs_by_prefix", result)
    _require_list(payload.get("legacy_component_review_guidance"), f"{path}.legacy_component_review_guidance", result)
    if isinstance(payload.get("legacy_component_review_guidance"), list):
        for index, guidance in enumerate(payload["legacy_component_review_guidance"]):
            _validate_legacy_component_guidance(guidance, f"{path}.legacy_component_review_guidance[{index}]", result)
    _require_list(payload.get("recommended_actions"), f"{path}.recommended_actions", result)
    for key in (
        "semantic_lossless_proven",
        "summary_inputs_trusted",
        "orientation_only",
        "can_update_kernel_state",
        "can_update_claim_trust",
    ):
        if not isinstance(payload.get(key), bool):
            result.add(f"{path}.{key}", "must be a boolean")
    _require_bool_value(payload.get("semantic_lossless_proven"), False, f"{path}.semantic_lossless_proven", result)
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("orientation_only"), True, f"{path}.orientation_only", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    return result


def require_valid_legacy_source_reconstruction_review_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_source_reconstruction_review_packet(payload)
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


def _validate_manifest_item(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in (
        "topic",
        "active_claim_id",
        "latest_review_status",
        "source_reconstruction_status",
        "repair_status",
        "plan_cli",
        "plan_mcp",
        "plan_surface",
        "review_packet_cli",
        "review_packet_mcp",
        "review_packet_surface",
        "apply_mcp",
        "apply_surface",
    ):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("latest_review_id"), str):
        result.add(f"{path}.latest_review_id", "must be a string")
    if not isinstance(payload.get("apply_cli"), str):
        result.add(f"{path}.apply_cli", "must be a string")
    if payload.get("repair_status") not in {
        "proposed_repairs",
        "awaiting_needs_revision_review",
        "no_repair_candidates",
    }:
        result.add(f"{path}.repair_status", "must be an allowed repair status")
    if payload.get("source_reconstruction_status") != "incomplete":
        result.add(f"{path}.source_reconstruction_status", "must be incomplete")
    for key in (
        "missing_components",
        "source_reconstruction_recommended_actions",
        "source_refs",
        "proposed_repair_types",
        "required_actions",
    ):
        _require_list(payload.get(key), f"{path}.{key}", result)
    if not isinstance(payload.get("proposed_repair_count"), int) or payload["proposed_repair_count"] < 0:
        result.add(f"{path}.proposed_repair_count", "must be a non-negative integer")
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)


def _validate_legacy_component_guidance(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    for key in ("component", "review_decision", "record_result_cli"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("review_decision") != "record_passed_needs_revision_or_inconclusive":
        result.add(f"{path}.review_decision", "must be record_passed_needs_revision_or_inconclusive")
    _require_list(payload.get("legacy_refs_to_inspect"), f"{path}.legacy_refs_to_inspect", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
