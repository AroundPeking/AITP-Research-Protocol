from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .mode_registry import DEFAULT_RUNTIME_MODE, VALID_RUNTIME_MODES, normalize_runtime_mode


VALIDATION_REVIEW_VERDICTS = frozenset({"pass", "partial", "fail", "inconclusive"})
_VERDICT_ALIASES = {
    "passed": "pass",
    "failed": "fail",
    "blocked": "inconclusive",
    "needs_followup": "partial",
}
_MODE_VALIDATION_POLICY: dict[str, dict[str, Any]] = {
    "explore": {
        "validation_opportunity": False,
        "validation_required": False,
        "validation_recommended": False,
        "default_gate_status": "skipped",
    },
    "learn": {
        "validation_opportunity": True,
        "validation_required": False,
        "validation_recommended": True,
        "default_gate_status": "recommended",
    },
    "implement": {
        "validation_opportunity": True,
        "validation_required": True,
        "validation_recommended": True,
        "default_gate_status": "required",
    },
}
_DEFAULT_VALIDATION_OPTIONS: tuple[dict[str, str], ...] = (
    {
        "family_key": "limiting_case",
        "label": "Limiting-case check",
        "summary": "Check weak/strong coupling and temperature limits against known behavior.",
    },
    {
        "family_key": "dimensional_consistency",
        "label": "Dimensional analysis",
        "summary": "Check unit consistency, scaling, and dimensionless normalization.",
    },
    {
        "family_key": "symmetry",
        "label": "Symmetry check",
        "summary": "Check translation, rotation, time-reversal, or gauge symmetry expectations.",
    },
    {
        "family_key": "source_consistency",
        "label": "Source-consistency check",
        "summary": "Compare against trusted literature, benchmark values, or textbook limits.",
    },
    {
        "family_key": "derivation_step",
        "label": "Derivation-step check",
        "summary": "Review each derivation step and mark whether it is heuristic or rigorous.",
    },
)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _normalize_confidence(value: Any) -> float | None:
    if value is None or value == "":
        return None
    confidence = float(value)
    if confidence < 0:
        return 0.0
    if confidence > 1:
        return 1.0
    return confidence


def _normalized_verdict(value: Any) -> str:
    verdict = str(value or "").strip().lower()
    verdict = _VERDICT_ALIASES.get(verdict, verdict)
    if verdict not in VALIDATION_REVIEW_VERDICTS:
        raise ValueError(
            "validation review verdict must be one of: "
            + ", ".join(sorted(VALIDATION_REVIEW_VERDICTS))
        )
    return verdict


def _validation_policy(runtime_mode: str | None) -> tuple[str, dict[str, Any]]:
    canonical_mode = normalize_runtime_mode(runtime_mode or DEFAULT_RUNTIME_MODE)
    if canonical_mode not in VALID_RUNTIME_MODES:
        canonical_mode = DEFAULT_RUNTIME_MODE
    return canonical_mode, dict(_MODE_VALIDATION_POLICY[canonical_mode])


def _default_validation_options() -> list[dict[str, str]]:
    return [dict(row) for row in _DEFAULT_VALIDATION_OPTIONS]


def _summarize_submitted_reviews(submitted_reviews: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {verdict: 0 for verdict in VALIDATION_REVIEW_VERDICTS}
    for row in submitted_reviews:
        verdict = _normalized_verdict(row.get("verdict"))
        counts[verdict] += 1
    if not submitted_reviews:
        aggregate_status = "not_started"
    elif counts["fail"] > 0:
        aggregate_status = "fail"
    elif counts["partial"] > 0:
        aggregate_status = "partial"
    elif counts["inconclusive"] > 0 and counts["pass"] > 0:
        aggregate_status = "partial"
    elif counts["inconclusive"] > 0:
        aggregate_status = "inconclusive"
    else:
        aggregate_status = "pass"
    return {
        "aggregate_status": aggregate_status,
        "submitted_review_count": len(submitted_reviews),
        "status_counts": counts,
    }


def check_validation_gate(
    validation_review: dict[str, Any],
    *,
    runtime_mode: str | None = None,
) -> dict[str, Any]:
    canonical_mode, policy = _validation_policy(
        runtime_mode or validation_review.get("runtime_mode") or DEFAULT_RUNTIME_MODE
    )
    review_summary = _summarize_submitted_reviews(
        list(validation_review.get("submitted_reviews") or [])
    )
    aggregate_status = str(
        validation_review.get("aggregate_status")
        or review_summary.get("aggregate_status")
        or "not_started"
    ).strip()
    gate_status = str(policy.get("default_gate_status") or "unknown")
    gate_open = True
    reason = "Validation posture has not been computed yet."

    if canonical_mode == "explore":
        gate_status = "skipped"
        gate_open = True
        reason = "Explore mode keeps validation optional and may defer it entirely."
    elif canonical_mode == "learn":
        if aggregate_status == "fail":
            gate_status = "fail"
            gate_open = False
            reason = "Learn mode permits optional validation, but recorded failed reviews still block a validation gate."
        elif aggregate_status == "pass":
            gate_status = "pass"
            gate_open = True
            reason = "Learn mode review passed and the gate can remain open."
        elif aggregate_status == "partial":
            gate_status = "partial"
            gate_open = True
            reason = "Learn mode allows partial review closure while keeping next steps explicit."
        elif aggregate_status == "inconclusive":
            gate_status = "inconclusive"
            gate_open = True
            reason = "Learn mode can proceed with an inconclusive review, but follow-up validation is still recommended."
        else:
            gate_status = "recommended"
            gate_open = True
            reason = "Learn mode does not require validation, but review is recommended before stronger claims."
    else:
        if aggregate_status == "pass":
            gate_status = "pass"
            gate_open = True
            reason = "Implement mode requires validation and the recorded review has passed."
        elif aggregate_status == "partial":
            gate_status = "partial"
            gate_open = False
            reason = "Implement mode requires a full validation pass; partial closure is not enough."
        elif aggregate_status == "fail":
            gate_status = "fail"
            gate_open = False
            reason = "Implement mode requires validation and the recorded review has failed."
        elif aggregate_status == "inconclusive":
            gate_status = "inconclusive"
            gate_open = False
            reason = "Implement mode requires validation and the recorded review is still inconclusive."
        else:
            gate_status = "required"
            gate_open = False
            reason = "Implement mode requires at least one completed validation review before the gate can open."

    return {
        "runtime_mode": canonical_mode,
        "validation_opportunity": bool(policy["validation_opportunity"]),
        "validation_required": bool(policy["validation_required"]),
        "validation_recommended": bool(policy["validation_recommended"]),
        "aggregate_status": aggregate_status,
        "gate_status": gate_status,
        "gate_open": gate_open,
        "reason": reason,
        "submitted_review_count": int(review_summary["submitted_review_count"]),
        "status_counts": dict(review_summary["status_counts"]),
    }


def create_validation_review(
    *,
    topic_slug: str,
    runtime_mode: str | None = None,
    candidate_id: str | None = None,
    review_items: list[dict[str, Any]] | None = None,
    submitted_reviews: list[dict[str, Any]] | None = None,
    candidate_validation_options: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    now_iso: Callable[[], str] | None = None,
) -> dict[str, Any]:
    timestamp = (now_iso or _now_iso)()
    canonical_mode, policy = _validation_policy(runtime_mode or DEFAULT_RUNTIME_MODE)
    submitted_rows = [dict(row) for row in (submitted_reviews or [])]
    summary = _summarize_submitted_reviews(submitted_rows)
    payload = {
        "review_kind": "validation_review",
        "topic_slug": str(topic_slug or "").strip(),
        "candidate_id": str(candidate_id or "").strip() or None,
        "runtime_mode": canonical_mode,
        "validation_opportunity": bool(policy["validation_opportunity"]),
        "validation_required": bool(policy["validation_required"]),
        "validation_recommended": bool(policy["validation_recommended"]),
        "candidate_validation_options": [
            dict(row)
            for row in (
                candidate_validation_options
                if candidate_validation_options is not None
                else _default_validation_options()
            )
        ],
        "review_items": [dict(row) for row in (review_items or [])],
        "submitted_reviews": submitted_rows,
        "aggregate_status": str(summary["aggregate_status"]),
        "metadata": dict(metadata or {}),
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    payload["review_summary"] = {
        "submitted_review_count": int(summary["submitted_review_count"]),
        "status_counts": dict(summary["status_counts"]),
    }
    payload["validation_gate"] = check_validation_gate(payload, runtime_mode=canonical_mode)
    return payload


def submit_review(
    validation_review: dict[str, Any],
    *,
    reviewer: str,
    verdict: str,
    evidence: list[str] | None = None,
    confidence: float | None = None,
    notes: str | None = None,
    next_steps: list[str] | None = None,
    now_iso: Callable[[], str] | None = None,
) -> dict[str, Any]:
    updated = dict(validation_review)
    submitted_reviews = [dict(row) for row in (updated.get("submitted_reviews") or [])]
    submitted_reviews.append(
        {
            "reviewer": str(reviewer or "").strip() or "unknown",
            "verdict": _normalized_verdict(verdict),
            "evidence": _string_list(evidence),
            "confidence": _normalize_confidence(confidence),
            "notes": str(notes or "").strip(),
            "next_steps": _string_list(next_steps),
            "submitted_at": (now_iso or _now_iso)(),
        }
    )
    updated["submitted_reviews"] = submitted_reviews
    summary = _summarize_submitted_reviews(submitted_reviews)
    updated["aggregate_status"] = str(summary["aggregate_status"])
    updated["review_summary"] = {
        "submitted_review_count": int(summary["submitted_review_count"]),
        "status_counts": dict(summary["status_counts"]),
    }
    updated["updated_at"] = (now_iso or _now_iso)()
    updated["validation_gate"] = check_validation_gate(updated)
    return updated


def _string_list(values: Any) -> list[str]:
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


def analytical_cross_check_markdown_lines(surface: dict[str, Any]) -> list[str]:
    if not surface:
        return []
    lines = [
        "## Analytical cross-check surface",
        "",
        f"- Status: `{surface.get('status') or '(missing)'}`",
        f"- Candidate id: `{surface.get('candidate_id') or '(missing)'}`",
        f"- Candidate type: `{surface.get('candidate_type') or '(missing)'}`",
        f"- Review path: `{surface.get('path') or '(missing)'}`",
        f"- Check count: `{surface.get('check_count') or 0}`",
        f"- Passed: `{surface.get('passed_check_count') or 0}`",
        f"- Failed: `{surface.get('failed_check_count') or 0}`",
        f"- Blocked: `{surface.get('blocked_check_count') or 0}`",
        "",
        surface.get("summary") or "(missing)",
        "",
        "### Check rows",
        "",
    ]
    check_rows = surface.get("check_rows") or []
    if not check_rows:
        lines.append("- `(none)`")
    for row in check_rows:
        lines.append(
            f"- `{row.get('kind') or '(missing)'}` `{row.get('label') or '(missing)'}` "
            f"status=`{row.get('status') or '(missing)'}` depth=`{row.get('reading_depth') or '(missing)'}`"
        )
        lines.append(
            f"  anchors=`{', '.join(row.get('source_anchors') or []) or '(none)'}` "
            f"assumptions=`{', '.join(row.get('assumption_refs') or []) or '(none)'}`"
        )
        lines.append(
            f"  regime=`{row.get('regime_note') or '(none)'}` notes=`{row.get('notes') or '(none)'}`"
        )
    lines.extend(["", "### Blocking reasons", ""])
    for item in surface.get("blocking_reasons") or ["(none)"]:
        lines.append(f"- {item}")
    return lines


class ValidationReviewService:
    def __init__(
        self,
        service: Any,
        *,
        read_json: Callable[[Path], dict[str, Any] | None],
        now_iso: Callable[[], str],
    ) -> None:
        self._service = service
        self._read_json = read_json
        self._now_iso = now_iso

    def create_validation_review(
        self,
        *,
        topic_slug: str,
        runtime_mode: str | None = None,
        candidate_id: str | None = None,
        review_items: list[dict[str, Any]] | None = None,
        submitted_reviews: list[dict[str, Any]] | None = None,
        candidate_validation_options: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return create_validation_review(
            topic_slug=topic_slug,
            runtime_mode=runtime_mode,
            candidate_id=candidate_id,
            review_items=review_items,
            submitted_reviews=submitted_reviews,
            candidate_validation_options=candidate_validation_options,
            metadata=metadata,
            now_iso=self._now_iso,
        )

    def submit_review(
        self,
        validation_review: dict[str, Any],
        *,
        reviewer: str,
        verdict: str,
        evidence: list[str] | None = None,
        confidence: float | None = None,
        notes: str | None = None,
        next_steps: list[str] | None = None,
    ) -> dict[str, Any]:
        return submit_review(
            validation_review,
            reviewer=reviewer,
            verdict=verdict,
            evidence=evidence,
            confidence=confidence,
            notes=notes,
            next_steps=next_steps,
            now_iso=self._now_iso,
        )

    def check_validation_gate(
        self,
        validation_review: dict[str, Any],
        *,
        runtime_mode: str | None = None,
    ) -> dict[str, Any]:
        return check_validation_gate(validation_review, runtime_mode=runtime_mode)

    def review_artifact_status(self, artifact_kind: str, payload: dict[str, Any]) -> str:
        if artifact_kind == "coverage_ledger":
            return str(payload.get("coverage_status") or payload.get("status") or "unknown")
        if artifact_kind == "analytical_review":
            return str(payload.get("overall_status") or payload.get("status") or "unknown")
        if artifact_kind == "formal_theory_review":
            return str(payload.get("overall_status") or payload.get("status") or "unknown")
        if artifact_kind == "merge_report":
            return str(payload.get("merge_outcome") or payload.get("status") or "unknown")
        return str(payload.get("status") or "unknown")

    def collect_validation_review_artifacts(
        self,
        *,
        topic_slug: str,
        latest_run_id: str,
        candidate_rows: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        if not latest_run_id:
            return []
        artifact_rows: list[dict[str, str]] = []
        for row in candidate_rows:
            candidate_id = str(row.get("candidate_id") or "").strip()
            if not candidate_id:
                continue
            packet_paths = self._service._theory_packet_paths(topic_slug, latest_run_id, candidate_id)
            for artifact_kind in (
                "coverage_ledger",
                "agent_consensus",
                "regression_gate",
                "analytical_review",
                "faithfulness_review",
                "provenance_review",
                "prerequisite_closure_review",
                "formal_theory_review",
                "merge_report",
            ):
                artifact_path = packet_paths[artifact_kind]
                if not artifact_path.exists():
                    continue
                payload = self._read_json(artifact_path) or {}
                artifact_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "candidate_type": str(row.get("candidate_type") or ""),
                        "artifact_kind": artifact_kind,
                        "path": self._service._relativize(artifact_path),
                        "status": self.review_artifact_status(artifact_kind, payload),
                    }
                )
        deduped: list[dict[str, str]] = []
        seen: set[str] = set()
        for row in artifact_rows:
            key = f"{row['candidate_id']}::{row['artifact_kind']}::{row['path']}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    def derive_validation_review_bundle(
        self,
        *,
        topic_slug: str,
        latest_run_id: str,
        updated_by: str,
        validation_contract: dict[str, Any],
        promotion_readiness: dict[str, Any],
        open_gap_summary: dict[str, Any],
        topic_completion: dict[str, Any],
        candidate_rows: list[dict[str, Any]],
        promotion_gate: dict[str, Any],
    ) -> dict[str, Any]:
        artifact_rows = self.collect_validation_review_artifacts(
            topic_slug=topic_slug,
            latest_run_id=latest_run_id,
            candidate_rows=candidate_rows,
        )
        analytical_cross_check_surface = self._derive_analytical_cross_check_surface(
            topic_slug=topic_slug,
            latest_run_id=latest_run_id,
            candidate_rows=candidate_rows,
        )
        candidate_ids = self._service._dedupe_strings(
            [str(row.get("candidate_id") or "") for row in candidate_rows if str(row.get("candidate_id") or "").strip()]
        )
        artifact_kinds = {str(row.get("artifact_kind") or "") for row in artifact_rows}
        validation_mode = str(validation_contract.get("validation_mode") or "")
        if validation_mode == "analytical" and "analytical_review" in artifact_kinds:
            primary_review_kind = "analytical_review"
        elif "formal_theory_review" in artifact_kinds:
            primary_review_kind = "formal_theory_review"
        elif "analytical_review" in artifact_kinds:
            primary_review_kind = "analytical_review"
        elif artifact_kinds & {"regression_gate", "coverage_ledger", "agent_consensus"}:
            primary_review_kind = "promotion_readiness"
        else:
            primary_review_kind = "validation_contract"
        blockers = self._service._dedupe_strings(
            list(open_gap_summary.get("blockers") or [])
            + list(promotion_readiness.get("blockers") or [])
            + [
                f"{row['artifact_kind']}={row['status']}"
                for row in artifact_rows
                if str(row.get("status") or "").strip().lower()
                in {"blocked", "fail", "failed", "missing", "not_ready", "not_audited"}
            ]
        )
        if open_gap_summary.get("requires_l0_return"):
            status = "blocked"
        elif artifact_rows:
            status = "ready" if not blockers else "blocked"
        else:
            status = "not_materialized"
        summary = (
            f"Primary L4 review surface for topic `{topic_slug}` using `{primary_review_kind}` as the current review entry point."
        )
        if blockers:
            summary += f" Active blockers: {blockers[0]}"
        elif artifact_rows:
            summary += " Specialist review artifacts are available under this bundle."
        else:
            summary += " No specialist review artifacts are materialized for the active run yet."
        validation_paths = self._service._validation_contract_paths(topic_slug)
        topic_completion_paths = self._service._topic_completion_paths(topic_slug)
        promotion_gate_paths = self._service._promotion_gate_paths(topic_slug)
        entrypoints = {
            "validation_contract_path": self._service._relativize(validation_paths["json"]),
            "validation_contract_note_path": self._service._relativize(validation_paths["note"]),
            "promotion_readiness_path": self._service._relativize(self._service._runtime_root(topic_slug) / "promotion_readiness.json"),
            "promotion_readiness_note_path": self._service._relativize(self._service._promotion_readiness_path(topic_slug)),
            "topic_completion_path": self._service._relativize(topic_completion_paths["json"]),
            "topic_completion_note_path": self._service._relativize(topic_completion_paths["note"]),
            "gap_map_path": self._service._relativize(self._service._gap_map_path(topic_slug)),
            "promotion_gate_path": self._service._relativize(promotion_gate_paths["json"])
            if promotion_gate_paths["json"].exists()
            else None,
        }
        bundle = {
            "bundle_kind": "validation_review_bundle",
            "topic_slug": topic_slug,
            "run_id": latest_run_id,
            "status": status,
            "primary_review_kind": primary_review_kind,
            "candidate_ids": candidate_ids,
            "validation_mode": str(validation_contract.get("validation_mode") or ""),
            "promotion_readiness_status": str(promotion_readiness.get("status") or "not_ready"),
            "topic_completion_status": str(topic_completion.get("status") or "not_assessed"),
            "promotion_gate_status": str(promotion_gate.get("status") or "not_requested"),
            "blockers": blockers,
            "entrypoints": entrypoints,
            "specialist_artifacts": artifact_rows,
            "summary": summary,
            "updated_at": self._now_iso(),
            "updated_by": updated_by,
        }
        if analytical_cross_check_surface:
            bundle["analytical_cross_check_surface"] = analytical_cross_check_surface
        return bundle

    def _derive_analytical_cross_check_surface(
        self,
        *,
        topic_slug: str,
        latest_run_id: str,
        candidate_rows: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not latest_run_id:
            return None
        for row in candidate_rows:
            candidate_id = str(row.get("candidate_id") or "").strip()
            if not candidate_id:
                continue
            review_path = self._service._theory_packet_paths(topic_slug, latest_run_id, candidate_id)["analytical_review"]
            if not review_path.exists():
                continue
            payload = self._read_json(review_path) or {}
            if not payload:
                continue
            check_rows = [
                {
                    "kind": str(item.get("kind") or ""),
                    "label": str(item.get("label") or ""),
                    "status": str(item.get("status") or ""),
                    "notes": str(item.get("notes") or ""),
                    "source_anchors": _string_list(item.get("source_anchors")),
                    "assumption_refs": _string_list(item.get("assumption_refs")),
                    "regime_note": str(item.get("regime_note") or ""),
                    "reading_depth": str(item.get("reading_depth") or ""),
                }
                for item in (payload.get("checks") or [])
                if isinstance(item, dict)
            ]
            return {
                "status": str(payload.get("overall_status") or "unknown"),
                "candidate_id": candidate_id,
                "candidate_type": str(row.get("candidate_type") or ""),
                "path": self._service._relativize(review_path),
                "summary": str(payload.get("summary") or ""),
                "check_count": int(payload.get("check_count") or len(check_rows)),
                "passed_check_count": int(payload.get("passed_check_count") or 0),
                "failed_check_count": int(payload.get("failed_check_count") or 0),
                "blocked_check_count": int(payload.get("blocked_check_count") or 0),
                "blocking_reasons": _string_list(payload.get("blocking_reasons")),
                "check_rows": check_rows,
            }
        return None

    def render_validation_review_bundle_markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Validation review bundle",
            "",
            f"- Topic slug: `{payload.get('topic_slug') or '(missing)'}`",
            f"- Run id: `{payload.get('run_id') or '(missing)'}`",
            f"- Status: `{payload.get('status') or '(missing)'}`",
            f"- Primary review kind: `{payload.get('primary_review_kind') or '(missing)'}`",
            f"- Validation mode: `{payload.get('validation_mode') or '(missing)'}`",
            f"- Promotion readiness: `{payload.get('promotion_readiness_status') or '(missing)'}`",
            f"- Topic completion: `{payload.get('topic_completion_status') or '(missing)'}`",
            f"- Promotion gate: `{payload.get('promotion_gate_status') or '(missing)'}`",
            "",
            "## Summary",
            "",
            payload.get("summary") or "(missing)",
            "",
            "## Entry points",
            "",
        ]
        for key in (
            "validation_contract_path",
            "validation_contract_note_path",
            "promotion_readiness_path",
            "promotion_readiness_note_path",
            "topic_completion_path",
            "topic_completion_note_path",
            "gap_map_path",
            "promotion_gate_path",
        ):
            lines.append(f"- {key}: `{((payload.get('entrypoints') or {}).get(key) or '(missing)')}`")
        lines.extend(["", "## Candidate scope", ""])
        for item in payload.get("candidate_ids") or ["(none)"]:
            lines.append(f"- `{item}`")
        lines.extend(["", "## Blockers", ""])
        for item in payload.get("blockers") or ["(none)"]:
            lines.append(f"- {item}")
        lines.extend(["", *analytical_cross_check_markdown_lines(payload.get("analytical_cross_check_surface") or {})])
        lines.extend(["", "## Specialist artifacts", ""])
        if payload.get("specialist_artifacts"):
            for row in payload.get("specialist_artifacts") or []:
                lines.append(
                    f"- `{row.get('artifact_kind') or '(missing)'}` "
                    f"candidate=`{row.get('candidate_id') or '(missing)'}` "
                    f"status=`{row.get('status') or '(missing)'}` "
                    f"path=`{row.get('path') or '(missing)'}`"
                )
        else:
            lines.append("- `(none)`")
        return "\n".join(lines) + "\n"
