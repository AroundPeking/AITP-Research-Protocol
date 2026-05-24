"""Contracts for legacy migration coverage audits."""

from __future__ import annotations

from typing import Any

from brain.v5.contracts import ContractError, ContractResult


def validate_legacy_migration_coverage_audit(
    payload: dict[str, Any],
    *,
    path: str = "legacy_migration_coverage_audit",
) -> ContractResult:
    result = ContractResult()
    if not isinstance(payload, dict):
        result.add(path, "must be a mapping")
        return result

    for key in ("kind", "run_id", "migration_dir", "coverage_status", "truth_source"):
        if not isinstance(payload.get(key), str) or not payload.get(key):
            result.add(f"{path}.{key}", "must be a non-empty string")
    if payload.get("kind") != "legacy_migration_coverage_audit":
        result.add(f"{path}.kind", "must be 'legacy_migration_coverage_audit'")
    if payload.get("coverage_status") not in {"accounted_needs_review", "coverage_gaps"}:
        result.add(f"{path}.coverage_status", "must be an allowed coverage status")
    for key in (
        "summary_inputs_trusted",
        "orientation_only",
        "can_update_kernel_state",
        "can_update_claim_trust",
        "semantic_lossless_proven",
    ):
        if payload.get(key) not in {False, True}:
            result.add(f"{path}.{key}", "must be a boolean")
    if payload.get("summary_inputs_trusted") is not False:
        result.add(f"{path}.summary_inputs_trusted", "must be false")
    if payload.get("orientation_only") is not True:
        result.add(f"{path}.orientation_only", "must be true")
    if payload.get("can_update_kernel_state") is not False:
        result.add(f"{path}.can_update_kernel_state", "must be false")
    if payload.get("can_update_claim_trust") is not False:
        result.add(f"{path}.can_update_claim_trust", "must be false")
    if payload.get("semantic_lossless_proven") is not False:
        result.add(f"{path}.semantic_lossless_proven", "must be false")
    _validate_block(payload.get("file_preservation"), f"{path}.file_preservation", result)
    _validate_block(payload.get("archive_reference_coverage"), f"{path}.archive_reference_coverage", result)
    _validate_block(payload.get("markdown_readability"), f"{path}.markdown_readability", result)
    topics = payload.get("topics")
    if not isinstance(topics, list):
        result.add(f"{path}.topics", "must be a list")
    else:
        for index, topic in enumerate(topics):
            _validate_topic(topic, f"{path}.topics[{index}]", result)
    for key in ("topic_count", "legacy_file_count", "gap_topic_count"):
        if not isinstance(payload.get(key), int) or payload.get(key) < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    return result


def require_valid_legacy_migration_coverage_audit(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_legacy_migration_coverage_audit(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_block(payload: Any, path: str, result: ContractResult) -> None:
    if not isinstance(payload, dict):
        result.add(path, "must be a mapping")
        return
    if not isinstance(payload.get("ok"), bool):
        result.add(f"{path}.ok", "must be a boolean")


def _validate_topic(payload: Any, path: str, result: ContractResult) -> None:
    if not isinstance(payload, dict):
        result.add(path, "must be a mapping")
        return
    for key in ("topic", "status", "coverage_status", "legacy_shape"):
        if not isinstance(payload.get(key), str):
            result.add(f"{path}.{key}", "must be a string")
    if payload.get("coverage_status") not in {"accounted_needs_review", "coverage_gaps"}:
        result.add(f"{path}.coverage_status", "must be an allowed coverage status")
    for key in (
        "file_count",
        "accounted_file_count",
        "unaccounted_file_count",
        "structured_file_count",
        "archive_reference_count",
        "audit_mapped_file_count",
        "preserved_source_refs",
    ):
        if not isinstance(payload.get(key), int) or payload.get(key) < 0:
            result.add(f"{path}.{key}", "must be a non-negative integer")
    if not isinstance(payload.get("missing_expected_paths"), list):
        result.add(f"{path}.missing_expected_paths", "must be a list")
    if not isinstance(payload.get("written_records"), dict):
        result.add(f"{path}.written_records", "must be a mapping")
    if payload.get("semantic_review_required") is not True:
        result.add(f"{path}.semantic_review_required", "must be true")
