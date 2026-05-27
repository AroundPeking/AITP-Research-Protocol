"""Contracts for legacy needs-revision basis Obsidian view bundles."""

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


def validate_legacy_semantic_needs_revision_basis_obsidian_view_bundle(
    payload: dict[str, Any],
    *,
    path: str = "legacy_semantic_needs_revision_basis_obsidian_view_bundle",
) -> ContractResult:
    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    if payload.get("kind") != "legacy_semantic_needs_revision_basis_obsidian_view_bundle":
        result.add(f"{path}.kind", "must be 'legacy_semantic_needs_revision_basis_obsidian_view_bundle'")
    for key in ("view_dir", "migration_dir", "workspace", "derived_from"):
        _require_nonempty_str(payload, key, path, result)
    if payload.get("derived_from") != "legacy_semantic_needs_revision_basis_queue":
        result.add(f"{path}.derived_from", "must be legacy_semantic_needs_revision_basis_queue")
    _require_mapping(payload.get("files"), f"{path}.files", result)
    if isinstance(payload.get("files"), dict):
        _require_nonempty_str(payload["files"], "basis_worklist", f"{path}.files", result)
    if not isinstance(payload.get("basis_item_count"), int) or payload["basis_item_count"] < 0:
        result.add(f"{path}.basis_item_count", "must be a non-negative integer")
    for key in ("status_counts", "required_action_counts", "source_records"):
        _require_mapping(payload.get(key), f"{path}.{key}", result)
    if isinstance(payload.get("source_records"), dict):
        for key in ("topics", "active_claim_ids", "latest_review_ids"):
            _require_list(payload["source_records"].get(key), f"{path}.source_records.{key}", result)
    _require_list(payload.get("next_actions"), f"{path}.next_actions", result)
    for key, expected in (
        ("semantic_lossless_proven", False),
        ("semantic_review_required", True),
        ("truth_source", False),
        ("summary_inputs_trusted", False),
        ("orientation_only", True),
        ("can_update_kernel_state", False),
        ("can_update_claim_trust", False),
    ):
        _require_bool_value(payload.get(key), expected, f"{path}.{key}", result)
    return result


def require_valid_legacy_semantic_needs_revision_basis_obsidian_view_bundle(
    payload: dict[str, Any],
) -> dict[str, Any]:
    result = validate_legacy_semantic_needs_revision_basis_obsidian_view_bundle(payload)
    if not result.ok:
        raise ContractError(result)
    return payload
