"""Compact CLI progress payloads for high-volume audit surfaces."""

from __future__ import annotations

from typing import Any

from brain.v5.cli_final_readiness_progress import compact_final_readiness


def compact_source_reconstruction_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    incomplete_items = [
        item
        for item in payload.get("items", [])
        if isinstance(item, dict) and item.get("status") == "incomplete"
    ][:5]
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "source_reconstruction_manifest_progress",
        "source_surface": "source_reconstruction_manifest",
        "claim_count": int(payload.get("claim_count") or 0),
        "complete_claim_count": int(payload.get("complete_claim_count") or 0),
        "incomplete_claim_count": int(payload.get("incomplete_claim_count") or 0),
        "missing_component_counts": dict(payload.get("missing_component_counts") or {}),
        "next_action_count": len(payload.get("next_actions") or []),
        "next_action_refs": _limited_strings(payload.get("next_actions")),
        "top_incomplete_claim_refs": [
            f"source_reconstruction:{claim_id}"
            for claim_id in [str(item.get("claim_id") or "") for item in incomplete_items]
            if claim_id
        ],
        "top_incomplete_claim_topics": [
            str(item.get("topic_id") or "")
            for item in incomplete_items
            if str(item.get("topic_id") or "")
        ],
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def compact_source_reconstruction_review_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    progress = dict(payload.get("review_progress") or {})
    top_review_items = [
        item
        for item in payload.get("items", [])
        if isinstance(item, dict)
        and item.get("review_status") in {"pending", "needs_revision", "inconclusive"}
    ][:5]
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "source_reconstruction_review_manifest_progress",
        "source_surface": "source_reconstruction_review_manifest",
        "claim_count": int(payload.get("claim_count") or 0),
        "review_progress": progress,
        "pending_review_count": int(progress.get("pending") or 0),
        "needs_revision_count": int(progress.get("needs_revision") or 0),
        "inconclusive_count": int(progress.get("inconclusive") or 0),
        "passed_count": int(progress.get("passed") or 0),
        "next_action_count": len(payload.get("next_actions") or []),
        "next_action_refs": _limited_strings(payload.get("next_actions")),
        "top_review_claim_refs": [
            f"source_reconstruction_review:{claim_id}"
            for claim_id in [str(item.get("claim_id") or "") for item in top_review_items]
            if claim_id
        ],
        "top_review_claim_topics": [
            str(item.get("topic_id") or "")
            for item in top_review_items
            if str(item.get("topic_id") or "")
        ],
        "top_review_statuses": [
            str(item.get("review_status") or "")
            for item in top_review_items
            if str(item.get("review_status") or "")
        ],
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def compact_source_stack_coverage_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    top_gap_items = [
        item
        for item in payload.get("items", [])
        if isinstance(item, dict) and item.get("coverage_status") != "complete"
    ][:5]
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "source_stack_coverage_manifest_progress",
        "source_surface": "source_stack_coverage_manifest",
        "claim_count": int(payload.get("claim_count") or 0),
        "coverage_status_counts": dict(payload.get("coverage_status_counts") or {}),
        "missing_required_output_counts": dict(payload.get("missing_required_output_counts") or {}),
        "source_component_gap_counts": dict(payload.get("source_component_gap_counts") or {}),
        "source_review_status_counts": dict(payload.get("source_review_status_counts") or {}),
        "next_action_count": len(payload.get("next_actions") or []),
        "next_action_refs": _limited_strings(payload.get("next_actions")),
        "top_gap_claim_refs": [
            f"source_stack_coverage:{claim_id}"
            for claim_id in [str(item.get("claim_id") or "") for item in top_gap_items]
            if claim_id
        ],
        "top_gap_claim_topics": [
            str(item.get("topic_id") or "")
            for item in top_gap_items
            if str(item.get("topic_id") or "")
        ],
        "top_gap_statuses": [
            str(item.get("coverage_status") or "")
            for item in top_gap_items
            if str(item.get("coverage_status") or "")
        ],
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def compact_source_reconstruction_review_packet(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _limited_strings(payload.get("missing_components"), limit=10)
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "source_reconstruction_review_packet_progress",
        "source_surface": "source_reconstruction_review_packet",
        "topic_id": str(payload.get("topic_id") or ""),
        "claim_id": str(payload.get("claim_id") or ""),
        "source_reconstruction_status": "incomplete" if missing else "complete",
        "missing_components": missing,
        "satisfied_components": _limited_strings(payload.get("satisfied_components"), limit=10),
        "component_review_count": len(payload.get("component_reviews") or []),
        "review_result_cli": (
            f"aitp-v5 source reconstruction-review-result --claim {payload.get('claim_id') or ''} "
            "--status <passed|needs_revision|inconclusive> "
            "--reviewed-component <component> --basis-ref <typed-or-source-ref> "
            "--summary <source reconstruction review basis>"
        ),
        "requires_human_or_adversarial_review": bool(
            payload.get("requires_human_or_adversarial_review", False)
        ),
        "recommended_actions": _limited_strings(payload.get("recommended_actions")),
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def _limited_strings(value: Any, *, limit: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value[:limit] if str(item)]
