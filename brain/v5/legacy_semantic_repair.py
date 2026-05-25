"""Read-only repair planning for reviewed legacy semantic migration gaps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.legacy_bridge import scan_legacy_topic
from brain.v5.legacy_semantic_review import build_legacy_semantic_review_queue
from brain.v5.legacy_semantic_review_packet import build_legacy_semantic_review_packet
from brain.v5.paths import WorkspacePaths


def build_legacy_semantic_repair_plan(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
    topic: str,
) -> dict[str, Any]:
    """Build a conservative, read-only repair plan from typed semantic reviews."""

    queue = build_legacy_semantic_review_queue(ws, migration_dir=migration_dir)
    item = _queue_item(queue, topic)
    packet = build_legacy_semantic_review_packet(ws, migration_dir=migration_dir, topic=topic)
    latest_review = item.get("latest_semantic_review") if isinstance(item.get("latest_semantic_review"), dict) else {}
    proposed_repairs = _proposed_repairs(
        legacy_root=Path(queue["legacy_root"]),
        topic=item["topic"],
        active_claim=packet.get("active_claim", {}),
        latest_review=latest_review,
    )
    return {
        "kind": "legacy_semantic_repair_plan",
        "run_id": queue["run_id"],
        "migration_dir": queue["migration_dir"],
        "topic": item["topic"],
        "active_claim_id": item["active_claim_id"],
        "repair_status": _repair_status(latest_review, proposed_repairs),
        "latest_semantic_review": latest_review,
        "proposed_repairs": proposed_repairs,
        "can_apply": False,
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "typed_review_results_and_legacy_refs",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _queue_item(queue: dict[str, Any], topic: str) -> dict[str, Any]:
    for item in queue["items"]:
        if item["topic"] == topic:
            return item
    raise ValueError(f"unknown semantic repair topic: {topic}")


def _proposed_repairs(
    *,
    legacy_root: Path,
    topic: str,
    active_claim: dict[str, Any],
    latest_review: dict[str, Any],
) -> list[dict[str, Any]]:
    if latest_review.get("status") != "needs_revision":
        return []
    claim_id = str(active_claim.get("claim_id") or "")
    if not claim_id or str(active_claim.get("statement") or ""):
        return []
    legacy_topic = legacy_root / topic
    if not (legacy_topic / "state.md").exists():
        return []
    question = scan_legacy_topic(legacy_topic).question
    if not question:
        return []
    basis_refs = _unique([
        *[str(ref) for ref in latest_review.get("reviewed_legacy_refs", []) if str(ref)],
        str(latest_review.get("review_id") or ""),
    ])
    return [
        {
            "repair_type": "claim_statement_backfill",
            "target_ref": claim_id,
            "current_value": "",
            "proposed_value": question,
            "basis_refs": basis_refs,
            "mutation_authority": "none_review_and_apply_separately",
        }
    ]


def _repair_status(latest_review: dict[str, Any], proposed_repairs: list[dict[str, Any]]) -> str:
    if proposed_repairs:
        return "proposed_repairs"
    if latest_review.get("status") != "needs_revision":
        return "awaiting_needs_revision_review"
    return "no_repair_candidates"


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
