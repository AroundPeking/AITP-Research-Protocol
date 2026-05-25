"""Guarded source-reconstruction repairs derived from legacy semantic reviews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.evidence import record_evidence
from brain.v5.legacy_semantic_review import build_legacy_semantic_review_queue
from brain.v5.paths import WorkspacePaths

_RECONSTRUCTION_REF_PREFIXES = ("legacy_candidate:", "legacy_l3_process:")
_REPAIR_TYPE = "reconstruction_path_evidence_backfill"


def build_legacy_source_reconstruction_plan(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
    topic: str,
) -> dict[str, Any]:
    """Plan reconstruction-path evidence backfills without mutating state."""

    queue = build_legacy_semantic_review_queue(ws, migration_dir=migration_dir)
    item = _queue_item(queue, topic)
    latest_review = item.get("latest_semantic_review") if isinstance(item.get("latest_semantic_review"), dict) else {}
    proposed_repairs = _proposed_repairs(item, latest_review)
    return {
        "kind": "legacy_source_reconstruction_plan",
        "run_id": queue["run_id"],
        "migration_dir": queue["migration_dir"],
        "topic": item["topic"],
        "active_claim_id": item["active_claim_id"],
        "repair_status": _repair_status(latest_review, proposed_repairs),
        "latest_semantic_review": latest_review,
        "proposed_repairs": proposed_repairs,
        "can_apply": False,
        "semantic_lossless_proven": False,
        "truth_source": "typed_review_results_and_legacy_refs",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def apply_legacy_source_reconstruction_repair(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
    topic: str,
    repair_type: str,
    review_id: str,
) -> dict[str, Any]:
    """Apply a single guarded reconstruction-path evidence backfill."""

    plan = build_legacy_source_reconstruction_plan(ws, migration_dir=migration_dir, topic=topic)
    repair = _matching_repair(plan, repair_type=repair_type)
    if repair is None:
        return _apply_payload(
            plan,
            repair_type=repair_type,
            review_id=review_id,
            evidence_id="",
            applied=False,
            required_actions=["select_available_repair"],
            basis_refs=[],
        )
    if review_id != plan["latest_semantic_review"].get("review_id"):
        return _apply_payload(
            plan,
            repair_type=repair_type,
            review_id=review_id,
            evidence_id="",
            applied=False,
            required_actions=["match_latest_needs_revision_review_id"],
            basis_refs=repair["basis_refs"],
        )
    summary = f"Reviewed legacy reconstruction path for {plan['topic']} from {len(repair['source_refs'])} L3/candidate refs."
    evidence = record_evidence(
        ws,
        topic_id=plan["topic"],
        claim_id=plan["active_claim_id"],
        evidence_type=repair["proposed_evidence_type"],
        status=repair["proposed_status"],
        summary=summary,
        supports_outputs=repair["proposed_supports_outputs"],
        source_refs=repair["source_refs"],
        body=_evidence_body(plan, repair, summary),
    )
    return _apply_payload(
        plan,
        repair_type=repair_type,
        review_id=review_id,
        evidence_id=evidence.evidence_id,
        applied=True,
        required_actions=[],
        basis_refs=repair["basis_refs"],
    )


def _queue_item(queue: dict[str, Any], topic: str) -> dict[str, Any]:
    for item in queue["items"]:
        if item["topic"] == topic:
            return item
    raise ValueError(f"unknown legacy source reconstruction topic: {topic}")


def _proposed_repairs(item: dict[str, Any], latest_review: dict[str, Any]) -> list[dict[str, Any]]:
    if latest_review.get("status") != "needs_revision":
        return []
    if "complete_source_reconstruction" not in _source_reconstruction_action_tokens(
        latest_review.get("remaining_actions", [])
    ):
        return []
    missing_components = set(item.get("source_reconstruction", {}).get("missing_components", []))
    if "reconstruction_path" not in missing_components:
        return []
    source_refs = [
        ref
        for ref in _clean_refs(latest_review.get("reviewed_legacy_refs", []))
        if ref.startswith(_RECONSTRUCTION_REF_PREFIXES)
    ]
    if not source_refs:
        return []
    basis_refs = _unique([*source_refs, str(latest_review.get("review_id") or "")])
    return [
        {
            "repair_type": _REPAIR_TYPE,
            "target_ref": str(item.get("active_claim_id") or ""),
            "current_missing_component": "reconstruction_path",
            "proposed_evidence_type": "source_reconstruction",
            "proposed_status": "supports",
            "proposed_supports_outputs": ["reconstruction_path"],
            "source_refs": source_refs,
            "basis_refs": basis_refs,
            "mutation_authority": "typed_review_and_apply_separately",
        }
    ]


def _repair_status(latest_review: dict[str, Any], proposed_repairs: list[dict[str, Any]]) -> str:
    if proposed_repairs:
        return "proposed_repairs"
    if latest_review.get("status") != "needs_revision":
        return "awaiting_needs_revision_review"
    return "no_repair_candidates"


def _source_reconstruction_action_tokens(raw_actions: list[str] | None) -> set[str]:
    tokens: set[str] = set()
    for action in raw_actions or []:
        text = str(action).strip()
        if not text:
            continue
        tokens.add(text)
        normalized = " ".join(text.lower().replace("_", " ").split())
        if "source reconstruction" in normalized or "reconstruction path" in normalized:
            tokens.add("complete_source_reconstruction")
    return tokens


def _matching_repair(plan: dict[str, Any], *, repair_type: str) -> dict[str, Any] | None:
    for repair in plan["proposed_repairs"]:
        if repair["repair_type"] == repair_type:
            return repair
    return None


def _apply_payload(
    plan: dict[str, Any],
    *,
    repair_type: str,
    review_id: str,
    evidence_id: str,
    applied: bool,
    required_actions: list[str],
    basis_refs: list[str],
) -> dict[str, Any]:
    return {
        "kind": "legacy_source_reconstruction_apply",
        "run_id": plan["run_id"],
        "migration_dir": plan["migration_dir"],
        "topic": plan["topic"],
        "active_claim_id": plan["active_claim_id"],
        "review_id": review_id,
        "repair_type": repair_type,
        "evidence_id": evidence_id,
        "basis_refs": list(basis_refs),
        "applied": applied,
        "required_actions": list(required_actions),
        "semantic_lossless_proven": False,
        "summary_inputs_trusted": False,
        "can_update_kernel_state": applied,
        "can_update_claim_trust": False,
    }


def _evidence_body(plan: dict[str, Any], repair: dict[str, Any], summary: str) -> str:
    lines = [
        "# Legacy Source Reconstruction Evidence",
        "",
        summary,
        "",
        "## Reviewed Legacy Reconstruction Refs",
        "",
    ]
    lines.extend(f"- `{ref}`" for ref in repair["source_refs"])
    lines.extend([
        "",
        "## Review Basis",
        "",
    ])
    lines.extend(f"- `{ref}`" for ref in repair["basis_refs"])
    lines.extend([
        "",
        "## Trust Boundary",
        "",
        "This evidence records a reconstruction-path pointer only; it does not prove semantic losslessness or update claim trust.",
    ])
    return "\n".join(lines) + "\n"


def _clean_refs(values: list[str] | None) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
