"""Contracts for read-only failure-mode review packets."""

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


def validate_failure_mode_review_packet(
    payload: dict[str, Any], *, path: str = "failure_mode_review_packet"
) -> ContractResult:
    """Validate a public, read-only physical adequacy review packet."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result
    for key in (
        "ok",
        "kind",
        "claim_id",
        "topic_id",
        "truth_source",
        "summary_inputs_trusted",
        "can_update_kernel_state",
        "can_update_claim_trust",
        "review_scope",
        "coverage_status",
        "requires_human_or_adversarial_review",
        "review_items",
        "recommended_actions",
    ):
        if key not in payload:
            result.add(f"{path}.{key}", "missing required failure-mode review key")
    _require_bool_value(payload.get("ok"), True, f"{path}.ok", result)
    if payload.get("kind") != "failure_mode_review_packet":
        result.add(f"{path}.kind", "must be 'failure_mode_review_packet'")
    _require_nonempty_str(payload, "claim_id", path, result)
    _require_nonempty_str(payload, "topic_id", path, result)
    if payload.get("truth_source") != "typed_records":
        result.add(f"{path}.truth_source", "must be 'typed_records'")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_kernel_state"), False, f"{path}.can_update_kernel_state", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    if payload.get("review_scope") != "physical_adequacy_before_promotion":
        result.add(f"{path}.review_scope", "must be 'physical_adequacy_before_promotion'")
    if payload.get("coverage_status") not in {"covered", "gap"}:
        result.add(f"{path}.coverage_status", "must be 'covered' or 'gap'")
    if not isinstance(payload.get("requires_human_or_adversarial_review"), bool):
        result.add(f"{path}.requires_human_or_adversarial_review", "must be a bool")
    _require_list(payload.get("review_items"), f"{path}.review_items", result)
    _require_list(payload.get("recommended_actions"), f"{path}.recommended_actions", result)
    for index, item in enumerate(payload.get("review_items", [])):
        _validate_review_item(item, f"{path}.review_items[{index}]", result)
    return result


def require_valid_failure_mode_review_packet(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a failure-mode review packet or raise a contract error."""

    result = validate_failure_mode_review_packet(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_review_item(item: Any, path: str, result: ContractResult) -> None:
    _require_mapping(item, path, result)
    if not isinstance(item, dict):
        return
    _require_nonempty_str(item, "failure_mode", path, result)
    _require_list(item.get("sources"), f"{path}.sources", result)
    _require_list(item.get("review_questions"), f"{path}.review_questions", result)
    if item.get("coverage") not in {"covered_by_promotion_packet", "promotion_packet_only", "uncovered"}:
        result.add(f"{path}.coverage", "has unsupported coverage label")
