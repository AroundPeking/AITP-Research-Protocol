"""Semantic review queue for completed legacy-to-v5 migration runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.legacy_migration_audit import audit_legacy_migration_coverage
from brain.v5.models import ClaimRecord
from brain.v5.paths import WorkspacePaths
from brain.v5.source_reconstruction import audit_source_reconstruction_batch
from brain.v5.store import list_records


def build_legacy_semantic_review_queue(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build per-topic semantic review work items for a legacy migration run.

    This is an orientation-only review queue. It turns the existing accounting
    audit into concrete human/v5 review work without claiming semantic proof.
    """

    coverage = audit_legacy_migration_coverage(ws, migration_dir=migration_dir)
    claims = {claim.claim_id: claim for claim in list_records(ws.registry_dir("claims"), ClaimRecord)}
    claim_ids = [
        topic["active_claim_id"]
        for topic in coverage["topics"]
        if topic.get("active_claim_id") in claims
    ]
    source_audits = audit_source_reconstruction_batch(ws, claim_ids)
    items = [
        _review_item(topic, source_audits.get(topic.get("active_claim_id", "")), claims)
        for topic in coverage["topics"]
    ]
    priority_counts = _priority_counts(items)
    queue_status = "coverage_gaps_first" if coverage["coverage_status"] == "coverage_gaps" else "ready_for_semantic_review"

    return {
        "kind": "legacy_semantic_review_queue",
        "run_id": coverage["run_id"],
        "migration_dir": coverage["migration_dir"],
        "workspace": coverage["workspace"],
        "legacy_root": coverage["legacy_root"],
        "v5_root": coverage["v5_root"],
        "queue_status": queue_status,
        "topic_count": coverage["topic_count"],
        "legacy_file_count": coverage["legacy_file_count"],
        "review_item_count": len(items),
        "priority_counts": priority_counts,
        "items": items,
        "coverage_audit": {
            "coverage_status": coverage["coverage_status"],
            "gap_topic_count": coverage["gap_topic_count"],
            "gap_topics": coverage["gap_topics"],
            "file_preservation_ok": coverage["file_preservation"]["ok"],
            "archive_reference_coverage_ok": coverage["archive_reference_coverage"]["ok"],
            "markdown_readability_ok": coverage["markdown_readability"]["ok"],
        },
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "semantic_review_reason": (
            "This queue operationalizes semantic review; it does not prove that "
            "legacy physics claims were interpreted correctly."
        ),
        "truth_source": "migration_manifests_and_typed_records",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _review_item(
    topic: dict[str, Any],
    source_audit: dict[str, Any] | None,
    claims: dict[str, ClaimRecord],
) -> dict[str, Any]:
    active_claim_id = str(topic.get("active_claim_id") or "")
    source_review = _source_review(active_claim_id, source_audit, claims)
    reasons = _review_reasons(topic, source_review)
    actions = _recommended_actions(topic, source_review)
    return {
        "topic": str(topic.get("topic") or ""),
        "legacy_shape": str(topic.get("legacy_shape") or ""),
        "active_claim_id": active_claim_id,
        "coverage_status": str(topic.get("coverage_status") or ""),
        "file_count": int(topic.get("file_count") or 0),
        "structured_file_count": int(topic.get("structured_file_count") or 0),
        "archive_reference_count": int(topic.get("archive_reference_count") or 0),
        "preserved_source_refs": int(topic.get("preserved_source_refs") or 0),
        "written_records": dict(topic.get("written_records") or {}),
        "source_reconstruction": source_review,
        "semantic_review_required": True,
        "review_priority": _review_priority(topic, source_review),
        "review_reasons": reasons,
        "recommended_actions": actions,
        "can_update_claim_trust": False,
    }


def _source_review(
    claim_id: str,
    source_audit: dict[str, Any] | None,
    claims: dict[str, ClaimRecord],
) -> dict[str, Any]:
    if not claim_id:
        return {
            "status": "missing_claim_id",
            "complete": False,
            "missing_components": ["active_claim_id"],
            "source_refs": [],
        }
    if claim_id not in claims:
        return {
            "status": "missing_claim_record",
            "complete": False,
            "missing_components": ["claim_record"],
            "source_refs": [],
        }
    if source_audit is None:
        return {
            "status": "not_audited",
            "complete": False,
            "missing_components": ["source_reconstruction_audit"],
            "source_refs": [],
        }
    complete = bool(source_audit.get("complete") is True)
    return {
        "status": "complete" if complete else "incomplete",
        "complete": complete,
        "missing_components": [
            str(component) for component in source_audit.get("missing_components", []) if str(component)
        ],
        "source_refs": [str(ref) for ref in source_audit.get("source_refs", []) if str(ref)],
    }


def _review_priority(topic: dict[str, Any], source_review: dict[str, Any]) -> str:
    if topic.get("coverage_status") == "coverage_gaps" or int(topic.get("unaccounted_file_count") or 0) > 0:
        return "critical"
    if source_review["status"] in {"missing_claim_id", "missing_claim_record"}:
        return "critical"
    if topic.get("legacy_shape") != "canonical_topic" or not source_review["complete"]:
        return "high"
    if int(topic.get("archive_reference_count") or 0) > 0:
        return "medium"
    return "low"


def _review_reasons(topic: dict[str, Any], source_review: dict[str, Any]) -> list[str]:
    reasons = ["semantic_lossless_not_proven"]
    if topic.get("coverage_status") == "coverage_gaps":
        reasons.append("coverage_gaps")
    if topic.get("legacy_shape") != "canonical_topic":
        reasons.append("noncanonical_legacy_seed")
    if int(topic.get("archive_reference_count") or 0) > 0:
        reasons.append("archive_only_records_require_sampling")
    if source_review["status"] != "complete":
        reasons.append(f"source_reconstruction_{source_review['status']}")
    return _unique(reasons)


def _recommended_actions(topic: dict[str, Any], source_review: dict[str, Any]) -> list[str]:
    actions = ["review_claim_statement_against_legacy_sources"]
    if topic.get("coverage_status") == "coverage_gaps":
        actions.append("resolve_file_accounting_or_archive_reference_gaps")
    if topic.get("legacy_shape") != "canonical_topic":
        actions.append("classify_noncanonical_seed_before_promotion")
    if int(topic.get("archive_reference_count") or 0) > 0:
        actions.append("sample_archive_reference_readback")
    if not source_review["complete"]:
        actions.append("complete_source_reconstruction")
    actions.extend([
        "record_validation_or_failure_modes",
        "decide_human_checkpoint_before_promotion",
    ])
    return _unique(actions)


def _priority_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for item in items:
        counts[item["review_priority"]] += 1
    return counts


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
