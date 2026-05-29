"""Compact CLI progress payloads for legacy migration coverage surfaces."""

from __future__ import annotations

from collections import Counter
from typing import Any


def compact_legacy_migration_coverage_audit(payload: dict[str, Any]) -> dict[str, Any]:
    topics = [item for item in payload.get("topics", []) if isinstance(item, dict)]
    file_preservation = payload.get("file_preservation") if isinstance(payload.get("file_preservation"), dict) else {}
    archive_reference = (
        payload.get("archive_reference_coverage")
        if isinstance(payload.get("archive_reference_coverage"), dict)
        else {}
    )
    markdown_readability = (
        payload.get("markdown_readability") if isinstance(payload.get("markdown_readability"), dict) else {}
    )
    return {
        "ok": bool(payload.get("ok", True)),
        "kind": "legacy_migration_coverage_audit_progress",
        "source_surface": "legacy_migration_coverage_audit",
        "run_id": str(payload.get("run_id") or ""),
        "migration_dir": str(payload.get("migration_dir") or ""),
        "workspace": str(payload.get("workspace") or ""),
        "coverage_status": str(payload.get("coverage_status") or ""),
        "topic_count": int(payload.get("topic_count") or 0),
        "legacy_file_count": int(payload.get("legacy_file_count") or 0),
        "file_preservation_ok": bool(file_preservation.get("ok", False)),
        "archive_reference_coverage_ok": bool(archive_reference.get("ok", False)),
        "markdown_readability_ok": bool(markdown_readability.get("ok", False)),
        "gap_topic_count": int(payload.get("gap_topic_count") or 0),
        "gap_topics": _limited_strings(payload.get("gap_topics"), limit=10),
        "topic_coverage_status_counts": _status_counts(topics, key="coverage_status"),
        "semantic_lossless_proven": bool(payload.get("semantic_lossless_proven", False)),
        "semantic_review_required": bool(payload.get("semantic_review_required", True)),
        "truth_source": str(payload.get("truth_source") or ""),
        "summary_inputs_trusted": bool(payload.get("summary_inputs_trusted", False)),
        "orientation_only": bool(payload.get("orientation_only", True)),
        "can_update_kernel_state": bool(payload.get("can_update_kernel_state", False)),
        "can_update_claim_trust": bool(payload.get("can_update_claim_trust", False)),
    }


def _status_counts(items: list[dict[str, Any]], *, key: str) -> dict[str, int]:
    counts = Counter(str(item.get(key) or "") for item in items if str(item.get(key) or ""))
    return dict(sorted(counts.items()))


def _limited_strings(value: Any, *, limit: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value[:limit] if str(item)]
