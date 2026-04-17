from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ALLOWED_ANALYTICAL_CHECK_KINDS = {
    "limiting_case",
    "dimensional_consistency",
    "symmetry",
    "self_consistency",
    "source_cross_reference",
    "derivation_step",
}
ALLOWED_ANALYTICAL_CHECK_STATUSES = {
    "passed",
    "failed",
    "blocked",
    "not_run",
    "needs_followup",
}
ALLOWED_READING_DEPTHS = {"skim", "targeted", "deep"}
ALLOWED_REVIEW_ITEM_STATUSES = {
    "queued",
    "in_progress",
    "pass",
    "partial",
    "fail",
    "inconclusive",
    "blocked",
    "skipped",
}
ALLOWED_REVIEW_ITEM_PRIORITIES = {"high", "medium", "low"}
ALLOWED_STEP_RIGOR = {"heuristic", "rigorous", "mixed", "unspecified"}
_ANALYTICAL_KIND_ALIASES = {
    "dimensional_analysis": "dimensional_consistency",
    "source_consistency": "source_cross_reference",
    "derivation_check": "derivation_step",
}
_REVIEW_ITEM_STATUS_ALIASES = {
    "pending": "queued",
    "open": "queued",
    "passed": "pass",
    "failed": "fail",
    "needs_followup": "partial",
    "not_run": "queued",
}
_REVIEW_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _dedupe_strings(values: Any) -> list[str]:
    if isinstance(values, (str, bytes)):
        values = [values]
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _slugify(text: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower())
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "review-item"


def _canonical_analytical_kind(kind: str | None) -> str:
    normalized = str(kind or "").strip().lower()
    normalized = _ANALYTICAL_KIND_ALIASES.get(normalized, normalized)
    if normalized not in ALLOWED_ANALYTICAL_CHECK_KINDS:
        raise ValueError(
            "analytical check kind must be one of: "
            + ", ".join(sorted(ALLOWED_ANALYTICAL_CHECK_KINDS))
        )
    return normalized


def _normalize_review_item_status(status: str | None) -> str:
    normalized = str(status or "").strip().lower() or "queued"
    normalized = _REVIEW_ITEM_STATUS_ALIASES.get(normalized, normalized)
    if normalized not in ALLOWED_REVIEW_ITEM_STATUSES:
        raise ValueError(
            "review item status must be one of: "
            + ", ".join(sorted(ALLOWED_REVIEW_ITEM_STATUSES))
        )
    return normalized


def _normalize_review_priority(priority: str | None) -> str:
    normalized = str(priority or "").strip().lower() or "medium"
    if normalized not in ALLOWED_REVIEW_ITEM_PRIORITIES:
        raise ValueError(
            "priority must be one of: "
            + ", ".join(sorted(ALLOWED_REVIEW_ITEM_PRIORITIES))
        )
    return normalized


def _normalize_step_rigor(step_rigor: str | None) -> str:
    normalized = str(step_rigor or "").strip().lower() or "unspecified"
    if normalized not in ALLOWED_STEP_RIGOR:
        raise ValueError(
            "step_rigor must be one of: " + ", ".join(sorted(ALLOWED_STEP_RIGOR))
        )
    return normalized


def _normalize_confidence(value: Any) -> float | None:
    if value is None or value == "":
        return None
    confidence = float(value)
    if confidence < 0:
        return 0.0
    if confidence > 1:
        return 1.0
    return confidence


def create_review_item(
    *,
    kind: str,
    label: str,
    prompt: str | None = None,
    status: str = "queued",
    priority: str = "medium",
    source_anchors: list[str] | None = None,
    assumption_refs: list[str] | None = None,
    regime_note: str | None = None,
    reading_depth: str | None = None,
    notes: str | None = None,
    evidence: list[str] | None = None,
    confidence: float | None = None,
    next_steps: list[str] | None = None,
    step_rigor: str | None = None,
    metadata: dict[str, Any] | None = None,
    item_id: str | None = None,
) -> dict[str, Any]:
    normalized_kind = _canonical_analytical_kind(kind)
    normalized_label = str(label or "").strip()
    if not normalized_label:
        raise ValueError("review item label must not be empty")
    timestamp = _now_iso()
    return {
        "item_id": str(item_id or f"review_item:{_slugify(f'{normalized_kind}-{normalized_label}')}")
        .strip(),
        "kind": normalized_kind,
        "label": normalized_label,
        "prompt": str(prompt or "").strip() or normalized_label,
        "status": _normalize_review_item_status(status),
        "priority": _normalize_review_priority(priority),
        "source_anchors": _dedupe_strings(source_anchors),
        "assumption_refs": _dedupe_strings(assumption_refs),
        "regime_note": str(regime_note or "").strip(),
        "reading_depth": _normalize_reading_depth(reading_depth),
        "notes": str(notes or "").strip(),
        "evidence": _dedupe_strings(evidence),
        "confidence": _normalize_confidence(confidence),
        "next_steps": _dedupe_strings(next_steps),
        "step_rigor": _normalize_step_rigor(step_rigor),
        "metadata": dict(metadata or {}),
        "updated_at": timestamp,
    }


def update_review_status(
    review_item: dict[str, Any],
    *,
    status: str,
    notes: str | None = None,
    evidence: list[str] | None = None,
    confidence: float | None = None,
    next_steps: list[str] | None = None,
    step_rigor: str | None = None,
) -> dict[str, Any]:
    updated = dict(review_item)
    updated["status"] = _normalize_review_item_status(status)
    if notes is not None:
        updated["notes"] = str(notes or "").strip()
    if evidence is not None:
        updated["evidence"] = _dedupe_strings(evidence)
    if confidence is not None:
        updated["confidence"] = _normalize_confidence(confidence)
    if next_steps is not None:
        updated["next_steps"] = _dedupe_strings(next_steps)
    if step_rigor is not None:
        updated["step_rigor"] = _normalize_step_rigor(step_rigor)
    updated["updated_at"] = _now_iso()
    return updated


def get_review_agenda(
    review_items: list[dict[str, Any]] | None,
    *,
    include_completed: bool = False,
) -> dict[str, Any]:
    normalized_items = []
    for row in review_items or []:
        normalized = create_review_item(
            kind=str(row.get("kind") or ""),
            label=str(row.get("label") or ""),
            prompt=row.get("prompt"),
            status=str(row.get("status") or "queued"),
            priority=str(row.get("priority") or "medium"),
            source_anchors=row.get("source_anchors"),
            assumption_refs=row.get("assumption_refs"),
            regime_note=row.get("regime_note"),
            reading_depth=row.get("reading_depth"),
            notes=row.get("notes"),
            evidence=row.get("evidence"),
            confidence=row.get("confidence"),
            next_steps=row.get("next_steps"),
            step_rigor=row.get("step_rigor"),
            metadata=row.get("metadata"),
            item_id=row.get("item_id"),
        )
        normalized_items.append(normalized)
    completed_statuses = {"pass", "skipped"}
    agenda_items = (
        normalized_items
        if include_completed
        else [row for row in normalized_items if row["status"] not in completed_statuses]
    )
    agenda_items.sort(
        key=lambda row: (
            _REVIEW_PRIORITY_ORDER.get(str(row.get("priority") or "medium"), 1),
            str(row.get("kind") or ""),
            str(row.get("label") or ""),
        )
    )
    status_counts: dict[str, int] = {}
    for row in normalized_items:
        current_status = str(row.get("status") or "queued")
        status_counts[current_status] = status_counts.get(current_status, 0) + 1
    return {
        "agenda_kind": "analytical_review_agenda",
        "item_count": len(normalized_items),
        "open_item_count": sum(
            1 for row in normalized_items if row["status"] not in completed_statuses
        ),
        "completed_item_count": sum(
            1 for row in normalized_items if row["status"] in completed_statuses
        ),
        "status_counts": status_counts,
        "items": agenda_items,
        "updated_at": _now_iso(),
    }


def _normalize_checks(
    checks: list[dict[str, Any]] | None,
    *,
    default_source_anchors: list[str],
    default_assumption_refs: list[str],
    default_regime_note: str,
    default_reading_depth: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in checks or []:
        kind = _canonical_analytical_kind(row.get("kind"))
        label = str(row.get("label") or "").strip()
        status = str(row.get("status") or "").strip().lower()
        notes = str(row.get("notes") or "").strip()
        if not kind or not label or not status:
            raise ValueError("analytical checks must include kind, label, and status")
        if status not in ALLOWED_ANALYTICAL_CHECK_STATUSES:
            raise ValueError(
                "analytical check status must be one of: "
                + ", ".join(sorted(ALLOWED_ANALYTICAL_CHECK_STATUSES))
            )
        normalized.append(
            {
                "kind": kind,
                "label": label,
                "status": status,
                "notes": notes,
                "source_anchors": _dedupe_strings(row.get("source_anchors"))
                or list(default_source_anchors),
                "assumption_refs": _dedupe_strings(row.get("assumption_refs"))
                or list(default_assumption_refs),
                "regime_note": str(row.get("regime_note") or "").strip() or default_regime_note,
                "reading_depth": _normalize_reading_depth(
                    str(row.get("reading_depth") or "").strip() or default_reading_depth
                ),
                "evidence": _dedupe_strings(row.get("evidence")),
                "confidence": _normalize_confidence(row.get("confidence")),
                "next_steps": _dedupe_strings(row.get("next_steps")),
                "step_rigor": _normalize_step_rigor(row.get("step_rigor")),
            }
        )
    return normalized


def _normalize_reading_depth(reading_depth: str | None) -> str:
    normalized = str(reading_depth or "").strip().lower() or "targeted"
    if normalized not in ALLOWED_READING_DEPTHS:
        raise ValueError("reading_depth must be one of: skim, targeted, deep")
    return normalized


def _compute_blocking_reasons(
    *,
    checks: list[dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    if not checks:
        blockers.append("missing_analytical_checks")
    if any(not row.get("source_anchors") for row in checks):
        blockers.append("missing_source_anchors")
    if any(not row.get("assumption_refs") and not row.get("regime_note") for row in checks):
        blockers.append("missing_assumption_or_regime_context")
    if not any(row["status"] == "passed" for row in checks):
        blockers.append("no_passed_analytical_check")
    for row in checks:
        if row["status"] in {"failed", "blocked"}:
            blockers.append(f"{row['kind']}:{row['label']}={row['status']}")
    deduped: list[str] = []
    seen: set[str] = set()
    for item in blockers:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _default_summary(
    *,
    overall_status: str,
    checks: list[dict[str, Any]],
    source_anchors: list[str],
) -> str:
    if checks:
        first_check = checks[0]
        return (
            f"Analytical review is `{overall_status}` with `{first_check['kind']}` "
            f"check `{first_check['label']}` and {len(source_anchors)} source anchor(s)."
        )
    return "Analytical review is blocked because no durable analytical checks were recorded."


def _rollup_source_anchors(checks: list[dict[str, Any]]) -> list[str]:
    anchors: list[str] = []
    for row in checks:
        anchors.extend(_dedupe_strings(row.get("source_anchors")))
    return _dedupe_strings(anchors)


def _rollup_assumption_refs(checks: list[dict[str, Any]]) -> list[str]:
    assumptions: list[str] = []
    for row in checks:
        assumptions.extend(_dedupe_strings(row.get("assumption_refs")))
    return _dedupe_strings(assumptions)


def _rollup_regime_note(checks: list[dict[str, Any]]) -> str:
    notes = [
        str(row.get("regime_note") or "").strip()
        for row in checks
        if str(row.get("regime_note") or "").strip()
    ]
    return "; ".join(_dedupe_strings(notes))


def _rollup_reading_depth(checks: list[dict[str, Any]], *, fallback: str) -> str:
    reading_depths = [
        str(row.get("reading_depth") or "").strip()
        for row in checks
        if str(row.get("reading_depth") or "").strip()
    ]
    deduped = _dedupe_strings(reading_depths)
    return deduped[0] if deduped else fallback


def _update_candidate_after_review(
    self,
    *,
    topic_slug: str,
    resolved_run_id: str,
    candidate_id: str,
    candidate: dict[str, Any],
    packet_paths: dict[str, Path],
    overall_status: str,
    checks: list[dict[str, Any]],
    source_anchors: list[str],
) -> None:
    updated_candidate = dict(candidate)
    updated_candidate["analytical_review_overall_status"] = overall_status
    updated_candidate["analytical_check_kinds"] = self._dedupe_strings(
        [row["kind"] for row in checks]
    )
    updated_candidate["analytical_source_anchors"] = self._dedupe_strings(source_anchors)
    theory_packet_refs = dict(updated_candidate.get("theory_packet_refs") or {})
    theory_packet_refs["analytical_review"] = self._relativize(packet_paths["analytical_review"])
    updated_candidate["theory_packet_refs"] = theory_packet_refs
    self._replace_candidate_row(topic_slug, resolved_run_id, candidate_id, updated_candidate)


def audit_analytical_review(
    self,
    *,
    topic_slug: str,
    candidate_id: str,
    run_id: str | None = None,
    updated_by: str = "aitp-cli",
    checks: list[dict[str, Any]] | None = None,
    source_anchors: list[str] | None = None,
    assumption_refs: list[str] | None = None,
    regime_note: str | None = None,
    reading_depth: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    resolved_run_id = self._resolve_run_id(topic_slug, run_id)
    if not resolved_run_id:
        raise FileNotFoundError(f"Unable to resolve a validation run for topic {topic_slug}")

    candidate = self._load_candidate(topic_slug, resolved_run_id, candidate_id)
    normalized_source_anchors = self._dedupe_strings(source_anchors)
    normalized_assumption_refs = self._dedupe_strings(assumption_refs)
    normalized_regime_note = str(regime_note or "").strip()
    normalized_reading_depth = _normalize_reading_depth(reading_depth)
    normalized_checks = _normalize_checks(
        checks,
        default_source_anchors=normalized_source_anchors,
        default_assumption_refs=normalized_assumption_refs,
        default_regime_note=normalized_regime_note,
        default_reading_depth=normalized_reading_depth,
    )
    normalized_source_anchors = _rollup_source_anchors(normalized_checks)
    normalized_assumption_refs = _rollup_assumption_refs(normalized_checks)
    normalized_regime_note = _rollup_regime_note(normalized_checks)
    normalized_reading_depth = _rollup_reading_depth(
        normalized_checks,
        fallback=normalized_reading_depth,
    )
    blocking_reasons = _compute_blocking_reasons(
        checks=normalized_checks,
    )
    overall_status = "ready" if not blocking_reasons else "blocked"
    updated_at = _now_iso()
    packet_paths = self._theory_packet_paths(topic_slug, resolved_run_id, candidate_id)
    analytical_review = {
        "schema_version": 1,
        "topic_slug": topic_slug,
        "run_id": resolved_run_id,
        "candidate_id": candidate_id,
        "candidate_type": str(candidate.get("candidate_type") or ""),
        "overall_status": overall_status,
        "blocking_reasons": blocking_reasons,
        "check_count": len(normalized_checks),
        "check_kinds": self._dedupe_strings([row["kind"] for row in normalized_checks]),
        "passed_check_count": sum(1 for row in normalized_checks if row["status"] == "passed"),
        "failed_check_count": sum(1 for row in normalized_checks if row["status"] == "failed"),
        "blocked_check_count": sum(1 for row in normalized_checks if row["status"] == "blocked"),
        "reading_depth": normalized_reading_depth,
        "source_anchors": normalized_source_anchors,
        "assumption_refs": normalized_assumption_refs,
        "regime_note": normalized_regime_note,
        "checks": normalized_checks,
        "summary": str(summary or "").strip()
        or _default_summary(
            overall_status=overall_status,
            checks=normalized_checks,
            source_anchors=normalized_source_anchors,
        ),
        "analytical_review_path": self._relativize(packet_paths["analytical_review"]),
        "updated_at": updated_at,
        "updated_by": updated_by,
    }
    _write_json(packet_paths["analytical_review"], analytical_review)
    _update_candidate_after_review(
        self,
        topic_slug=topic_slug,
        resolved_run_id=resolved_run_id,
        candidate_id=candidate_id,
        candidate=candidate,
        packet_paths=packet_paths,
        overall_status=overall_status,
        checks=normalized_checks,
        source_anchors=normalized_source_anchors,
    )
    return {
        "topic_slug": topic_slug,
        "run_id": resolved_run_id,
        "candidate_id": candidate_id,
        "candidate_type": str(candidate.get("candidate_type") or ""),
        "overall_status": overall_status,
        "blocking_reasons": blocking_reasons,
        "paths": {
            "analytical_review": str(packet_paths["analytical_review"]),
        },
        "artifacts": {
            "analytical_review": analytical_review,
        },
    }
