"""Per-topic packet for converting inconclusive legacy reviews into needs-revision basis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.legacy_semantic_needs_revision import build_legacy_semantic_needs_revision_basis_queue
from brain.v5.legacy_semantic_repair import build_legacy_semantic_repair_plan
from brain.v5.legacy_semantic_review_packet import build_legacy_semantic_review_packet
from brain.v5.legacy_semantic_review_worklist import build_legacy_semantic_review_worklist
from brain.v5.paths import WorkspacePaths


def build_legacy_semantic_needs_revision_basis_packet(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
    topic: str,
) -> dict[str, Any]:
    """Build a read-only basis packet for recording a specific needs-revision review."""

    topic_filter = topic.strip()
    queue = build_legacy_semantic_needs_revision_basis_queue(ws, migration_dir=migration_dir)
    worklist = build_legacy_semantic_review_worklist(ws, migration_dir=migration_dir)
    work_item = _topic_item(worklist["items"], topic_filter)
    semantic_packet = build_legacy_semantic_review_packet(
        ws,
        migration_dir=migration_dir,
        topic=topic_filter,
    )
    latest_review = (
        semantic_packet.get("latest_semantic_review")
        if isinstance(semantic_packet.get("latest_semantic_review"), dict)
        else {}
    )
    basis_item = _optional_topic_item(queue["items"], topic_filter)
    review_actions = [
        dict(command)
        for command in work_item.get("review_action_commands", [])
        if isinstance(command, dict)
    ]
    repair_plan = build_legacy_semantic_repair_plan(ws, migration_dir=migration_dir, topic=topic_filter)
    review_basis = _review_basis(latest_review, work_item)
    if basis_item is None:
        if str(work_item.get("review_status") or "") == "needs_revision":
            return _already_needs_revision_packet(
                ws,
                queue=queue,
                work_item=work_item,
                semantic_packet=semantic_packet,
                latest_review=latest_review,
                review_actions=review_actions,
                repair_plan=repair_plan,
                review_basis=review_basis,
            )
        raise ValueError(f"unknown legacy needs-revision basis topic: {topic_filter}")
    return {
        "kind": "legacy_semantic_needs_revision_basis_packet",
        "basis_packet_status": str(basis_item.get("basis_status") or "needs_revision_basis_required"),
        "run_id": queue["run_id"],
        "migration_dir": queue["migration_dir"],
        "workspace": queue["workspace"],
        "topic": basis_item["topic"],
        "active_claim_id": basis_item["active_claim_id"],
        "latest_review_id": basis_item["latest_review_id"],
        "review_status": basis_item["review_status"],
        "blocking_classes": list(basis_item.get("blocking_classes") or []),
        "pass_blockers": list(basis_item.get("pass_blockers") or []),
        "remaining_actions": list(basis_item.get("remaining_actions") or []),
        "required_actions": list(basis_item.get("required_actions") or []),
        "review_basis": review_basis,
        "legacy_review_refs": list(semantic_packet.get("legacy_review_refs") or []),
        "review_basis_refs": list(semantic_packet.get("review_basis_refs") or []),
        "review_action_commands": review_actions,
        "likely_repair_basis": _likely_repair_basis(basis_item, review_actions),
        "needs_revision_result_cli": _packet_needs_revision_result_cli(
            ws,
            migration_dir=queue["migration_dir"],
            basis_item=basis_item,
            review_basis=review_basis,
        ),
        "repair_plan": {
            "surface": "legacy_semantic_repair_plan",
            "repair_status": str(repair_plan.get("repair_status") or ""),
            "proposed_repair_count": len(repair_plan.get("proposed_repairs") or []),
            "required_actions": list(repair_plan.get("required_actions") or []),
            "cli": basis_item["repair_plan_cli"],
            "mcp": "aitp_v5_build_legacy_semantic_repair_plan",
            "can_update_claim_trust": False,
        },
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "legacy_semantic_needs_revision_basis_queue_and_review_packet",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _already_needs_revision_packet(
    ws: WorkspacePaths,
    *,
    queue: dict[str, Any],
    work_item: dict[str, Any],
    semantic_packet: dict[str, Any],
    latest_review: dict[str, Any],
    review_actions: list[dict[str, Any]],
    repair_plan: dict[str, Any],
    review_basis: dict[str, list[str]],
) -> dict[str, Any]:
    remaining_actions = _remaining_actions(work_item) or _clean_refs(latest_review.get("remaining_actions", []))
    latest_review_id = str(latest_review.get("review_id") or work_item.get("latest_review_id") or "")
    topic = str(work_item.get("topic") or "")
    return {
        "kind": "legacy_semantic_needs_revision_basis_packet",
        "basis_packet_status": "already_needs_revision",
        "run_id": queue["run_id"],
        "migration_dir": queue["migration_dir"],
        "workspace": queue["workspace"],
        "topic": topic,
        "active_claim_id": str(work_item.get("active_claim_id") or ""),
        "latest_review_id": latest_review_id,
        "review_status": "needs_revision",
        "blocking_classes": list(work_item.get("blocking_classes") or []),
        "pass_blockers": list(_pass_readiness(work_item).get("blockers") or []),
        "remaining_actions": remaining_actions,
        "required_actions": [
            "do_not_record_duplicate_needs_revision_basis",
            "use_legacy_semantic_repair_plan_or_executable_evidence_packet",
            "keep_semantic_review_blocking_until_remaining_actions_are_resolved",
        ],
        "review_basis": review_basis,
        "legacy_review_refs": list(semantic_packet.get("legacy_review_refs") or []),
        "review_basis_refs": list(semantic_packet.get("review_basis_refs") or []),
        "review_action_commands": review_actions,
        "likely_repair_basis": _likely_repair_basis(
            {**work_item, "remaining_actions": remaining_actions},
            review_actions,
        ),
        "needs_revision_result_cli": f"already_recorded:{latest_review_id}",
        "repair_plan": {
            "surface": "legacy_semantic_repair_plan",
            "repair_status": str(repair_plan.get("repair_status") or ""),
            "proposed_repair_count": len(repair_plan.get("proposed_repairs") or []),
            "required_actions": list(repair_plan.get("required_actions") or []),
            "cli": (
                f"aitp-v5 --base {ws.base} legacy semantic-repair-plan "
                f"--migration-dir {queue['migration_dir']} --topic {topic}"
            ),
            "mcp": "aitp_v5_build_legacy_semantic_repair_plan",
            "can_update_claim_trust": False,
        },
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "legacy_semantic_review_worklist_and_review_packet",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _optional_topic_item(items: list[dict[str, Any]], topic: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("topic") == topic:
            return item
    return None


def _topic_item(items: list[dict[str, Any]], topic: str) -> dict[str, Any]:
    for item in items:
        if item.get("topic") == topic:
            return item
    raise ValueError(f"unknown legacy needs-revision basis topic: {topic}")


def _review_basis(latest_review: dict[str, Any], work_item: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "reviewed_legacy_refs": _clean_refs(latest_review.get("reviewed_legacy_refs", [])),
        "reviewed_typed_refs": _clean_refs(latest_review.get("reviewed_typed_refs", [])),
        "evidence_refs": _clean_refs(latest_review.get("evidence_refs", [])),
        "validation_result_ids": _clean_refs(latest_review.get("validation_result_ids", [])),
        "source_reconstruction_review_refs": _clean_refs(
            work_item.get("source_reconstruction_review_refs", [])
        ),
        "open_checkpoint_refs": _clean_refs(work_item.get("open_human_checkpoint_refs", [])),
    }


def _likely_repair_basis(
    basis_item: dict[str, Any],
    review_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    commands_by_action = {
        str(command.get("action") or ""): command
        for command in review_actions
        if str(command.get("action") or "")
    }
    result: list[dict[str, Any]] = []
    for action in basis_item.get("remaining_actions") or []:
        action_text = str(action)
        candidate = commands_by_action.get(action_text)
        result.append(
            {
                "action": action_text,
                "basis_kind": _basis_kind(action_text, candidate),
                "candidate_command": dict(candidate) if candidate is not None else {},
                "can_update_claim_trust": False,
            }
        )
    return result


def _remaining_actions(work_item: dict[str, Any]) -> list[str]:
    readiness = _pass_readiness(work_item)
    return [str(action) for action in readiness.get("remaining_actions", []) if str(action)]


def _pass_readiness(work_item: dict[str, Any]) -> dict[str, Any]:
    value = work_item.get("pass_readiness")
    return value if isinstance(value, dict) else {}


def _basis_kind(action: str, command: dict[str, Any] | None) -> str:
    if command is not None:
        surface = str(command.get("surface") or "")
        if surface:
            return surface
    normalized = " ".join(action.lower().replace("_", " ").split())
    if "checkpoint" in normalized or "human topic question" in normalized:
        return "human_checkpoint_record"
    if "source reconstruction" in normalized or "reconstruction path" in normalized:
        return "source_reconstruction_review_result_record"
    return "legacy_semantic_review_result_record"


def _needs_revision_result_cli(
    ws: WorkspacePaths,
    *,
    migration_dir: str,
    topic: str,
    active_claim_id: str,
    review_basis: dict[str, list[str]],
    remaining_actions: list[str],
) -> str:
    parts = [
        f"aitp-v5 --base {ws.base} legacy semantic-review-result",
        f"--migration-dir {migration_dir}",
        f"--topic {topic}",
        "--status needs_revision",
    ]
    if active_claim_id:
        parts.append(f"--active-claim {active_claim_id}")
    parts.extend(f"--legacy-ref {ref}" for ref in review_basis["reviewed_legacy_refs"])
    parts.extend(f"--typed-ref {ref}" for ref in review_basis["reviewed_typed_refs"])
    parts.extend(f"--evidence-ref {ref}" for ref in review_basis["evidence_refs"])
    parts.extend(f"--validation-result-id {ref}" for ref in review_basis["validation_result_ids"])
    parts.extend(f"--typed-ref {ref}" for ref in review_basis["source_reconstruction_review_refs"])
    parts.extend(f"--remaining-action {action}" for action in remaining_actions if action)
    parts.append("--summary <specific repair basis and remaining semantic gaps>")
    return " ".join(parts)


def _packet_needs_revision_result_cli(
    ws: WorkspacePaths,
    *,
    migration_dir: str,
    basis_item: dict[str, Any],
    review_basis: dict[str, list[str]],
) -> str:
    if str(basis_item.get("basis_status") or "") == "human_checkpoint_only":
        return "not_applicable:human_checkpoint_only"
    return _needs_revision_result_cli(
        ws,
        migration_dir=migration_dir,
        topic=str(basis_item.get("topic") or ""),
        active_claim_id=str(basis_item.get("active_claim_id") or ""),
        review_basis=review_basis,
        remaining_actions=[str(action) for action in basis_item.get("remaining_actions", []) if str(action)],
    )


def _clean_refs(values: Any) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]
