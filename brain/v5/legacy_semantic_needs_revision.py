"""Read-only queue for converting inconclusive legacy reviews into specific needs-revision basis."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from brain.v5.legacy_semantic_review_worklist import build_legacy_semantic_review_worklist
from brain.v5.paths import WorkspacePaths

_DEFAULT_REQUIRED_ACTIONS = [
    "record_needs_revision_review_with_specific_repair_basis",
    "keep_semantic_review_blocking_until_typed_review_basis_exists",
]
_HUMAN_CHECKPOINT_ONLY_ACTIONS = [
    "resolve_human_checkpoint_before_promotion",
    "do_not_record_needs_revision_without_specific_semantic_gap",
]
_CHECKPOINT_ONLY_BLOCKERS = {
    "latest_review_remaining_actions",
    "open_human_checkpoint_pending",
}


def build_legacy_semantic_needs_revision_basis_queue(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
) -> dict[str, Any]:
    """List inconclusive semantic reviews that need a concrete needs-revision basis."""

    worklist = build_legacy_semantic_review_worklist(ws, migration_dir=migration_dir)
    return legacy_semantic_needs_revision_basis_queue_from_worklist(ws, worklist)


def legacy_semantic_needs_revision_basis_queue_from_worklist(
    ws: WorkspacePaths,
    worklist: dict[str, Any],
) -> dict[str, Any]:
    """Build the needs-revision basis surface from an already-loaded semantic worklist."""

    items = [
        _basis_item(ws, worklist, item)
        for item in worklist["items"]
        if item.get("review_status") == "inconclusive"
    ]
    return {
        "kind": "legacy_semantic_needs_revision_basis_queue",
        "run_id": worklist["run_id"],
        "migration_dir": worklist["migration_dir"],
        "workspace": worklist["workspace"],
        "basis_item_count": len(items),
        "basis_status_counts": dict(Counter(item["basis_status"] for item in items)),
        "status_counts": dict(Counter(item["review_status"] for item in items)),
        "required_action_counts": _required_action_counts(items),
        "items": items,
        "next_actions": [item["next_action_ref"] for item in items],
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "legacy_semantic_review_worklist",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _basis_item(ws: WorkspacePaths, worklist: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    pass_readiness = item.get("pass_readiness") if isinstance(item.get("pass_readiness"), dict) else {}
    remaining_actions = [
        str(action) for action in pass_readiness.get("remaining_actions", []) if str(action)
    ]
    basis_status = _basis_status(item, pass_readiness, remaining_actions)
    required_actions = _required_actions(item, remaining_actions, basis_status=basis_status)
    topic = str(item.get("topic") or "")
    needs_revision_result_cli = _needs_revision_result_cli(
        ws,
        worklist=worklist,
        topic=topic,
        basis_status=basis_status,
    )
    return {
        "topic": topic,
        "active_claim_id": str(item.get("active_claim_id") or ""),
        "latest_review_id": str(item.get("latest_review_id") or ""),
        "review_status": str(item.get("review_status") or ""),
        "basis_status": basis_status,
        "blocking_classes": list(item.get("blocking_classes") or []),
        "pass_blockers": list(pass_readiness.get("blockers") or []),
        "remaining_actions": remaining_actions,
        "required_actions": required_actions,
        "needs_revision_result_cli": needs_revision_result_cli,
        "basis_packet_cli": (
            f"aitp-v5 --base {ws.base} legacy semantic-needs-revision-basis-packet "
            f"--migration-dir {worklist['migration_dir']} --topic {topic}"
        ),
        "repair_plan_cli": (
            f"aitp-v5 --base {ws.base} legacy semantic-repair-plan "
            f"--migration-dir {worklist['migration_dir']} --topic {topic}"
        ),
        "next_action_ref": f"{_next_action_prefix(basis_status)}:{topic}",
        "can_update_claim_trust": False,
    }


def _required_actions(
    item: dict[str, Any],
    remaining_actions: list[str],
    *,
    basis_status: str,
) -> list[str]:
    if basis_status == "human_checkpoint_only":
        return list(_HUMAN_CHECKPOINT_ONLY_ACTIONS)
    actions = list(_DEFAULT_REQUIRED_ACTIONS)
    text = " ".join([*remaining_actions, *[str(value) for value in item.get("blocking_classes", [])]]).lower()
    if "claim_statement" in text or "topic_question" in text:
        actions.insert(1, "supply_or_review_human_topic_question_before_claim_statement_backfill")
    return _unique(actions)


def _basis_status(
    item: dict[str, Any],
    pass_readiness: dict[str, Any],
    remaining_actions: list[str],
) -> str:
    if _is_human_checkpoint_only(item, pass_readiness, remaining_actions):
        return "human_checkpoint_only"
    return "needs_revision_basis_required"


def _is_human_checkpoint_only(
    item: dict[str, Any],
    pass_readiness: dict[str, Any],
    remaining_actions: list[str],
) -> bool:
    if not remaining_actions:
        return False
    if not all(_is_checkpoint_action(action) for action in remaining_actions):
        return False
    if not list(pass_readiness.get("open_human_checkpoint_refs") or item.get("open_human_checkpoint_refs") or []):
        return False
    blockers = {str(blocker) for blocker in pass_readiness.get("blockers", []) if str(blocker)}
    return bool(blockers) and blockers.issubset(_CHECKPOINT_ONLY_BLOCKERS)


def _is_checkpoint_action(action: str) -> bool:
    normalized = " ".join(str(action).lower().replace("_", " ").split())
    return "human checkpoint" in normalized or normalized.startswith("decide human checkpoint")


def _needs_revision_result_cli(
    ws: WorkspacePaths,
    *,
    worklist: dict[str, Any],
    topic: str,
    basis_status: str,
) -> str:
    if basis_status == "human_checkpoint_only":
        return "not_applicable:human_checkpoint_only"
    return (
        f"aitp-v5 --base {ws.base} legacy semantic-review-result "
        f"--migration-dir {worklist['migration_dir']} --topic {topic} "
        "--status needs_revision "
        "--legacy-ref <reviewed-legacy-ref> --typed-ref <reviewed-typed-basis-ref> "
        "--summary <specific repair basis and remaining semantic gaps>"
    )


def _next_action_prefix(basis_status: str) -> str:
    if basis_status == "human_checkpoint_only":
        return "human_checkpoint_only"
    return "needs_revision_basis"


def _required_action_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item["required_actions"])
    return dict(counts)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
