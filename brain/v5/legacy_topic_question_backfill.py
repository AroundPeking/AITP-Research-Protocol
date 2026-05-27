"""Read-only packet for legacy topic-question claim-statement backfill blockers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.legacy_semantic_review_packet import build_legacy_semantic_review_packet
from brain.v5.legacy_semantic_review_worklist import build_legacy_semantic_review_worklist
from brain.v5.paths import WorkspacePaths

_TOPIC_QUESTION_ACTION = "require_human_topic_question_before_claim_backfill"
_REQUIRED_ACTIONS = [
    "request_or_decide_human_topic_question",
    "record_needs_revision_review_after_topic_question_decision",
    "keep_claim_statement_empty_until_human_topic_question_is_provided",
]


def build_legacy_topic_question_backfill_packet(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
) -> dict[str, Any]:
    """Group ambiguous claim-statement backfills that need a human topic question."""

    worklist = build_legacy_semantic_review_worklist(ws, migration_dir=migration_dir)
    items = [
        _backfill_item(ws, worklist, item)
        for item in worklist["items"]
        if _requires_topic_question(item)
    ]
    return {
        "kind": "legacy_topic_question_backfill_packet",
        "run_id": worklist["run_id"],
        "migration_dir": worklist["migration_dir"],
        "workspace": worklist["workspace"],
        "backfill_item_count": len(items),
        "open_decision_count": sum(1 for item in items if item["checkpoint"]["mode"] == "decide_open_checkpoint"),
        "pending_request_count": sum(1 for item in items if item["checkpoint"]["mode"] == "request_checkpoint"),
        "items": items,
        "next_actions": [
            (
                f"topic_question_backfill:{item['topic']}:decide:{item['checkpoint']['checkpoint_id']}"
                if item["checkpoint"]["mode"] == "decide_open_checkpoint"
                else f"topic_question_backfill:{item['topic']}:request_human_topic_question"
            )
            for item in items
        ],
        "auto_backfill_allowed": False,
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "legacy_semantic_review_worklist_topic_question_commands",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _requires_topic_question(item: dict[str, Any]) -> bool:
    if _topic_question_command(item):
        return True
    return False


def _backfill_item(ws: WorkspacePaths, worklist: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    topic = str(item.get("topic") or "")
    semantic_packet = build_legacy_semantic_review_packet(
        ws,
        migration_dir=worklist["migration_dir"],
        topic=topic,
    )
    latest_review = (
        semantic_packet.get("latest_semantic_review")
        if isinstance(semantic_packet.get("latest_semantic_review"), dict)
        else {}
    )
    checkpoint = _checkpoint_payload(item, _topic_question_command(item))
    return {
        "topic": topic,
        "active_claim_id": str(item.get("active_claim_id") or ""),
        "latest_review_id": str(item.get("latest_review_id") or latest_review.get("review_id") or ""),
        "review_status": str(item.get("review_status") or ""),
        "claim_statement_present": bool(item.get("active_claim_statement_present")),
        "auto_backfill_allowed": False,
        "required_actions": list(_REQUIRED_ACTIONS),
        "review_basis": {
            "reviewed_legacy_refs": _clean_refs(latest_review.get("reviewed_legacy_refs", [])),
            "reviewed_typed_refs": _clean_refs(latest_review.get("reviewed_typed_refs", [])),
            "open_checkpoint_refs": _clean_refs(item.get("open_human_checkpoint_refs", [])),
        },
        "checkpoint": checkpoint,
        "needs_revision_result_cli": _needs_revision_result_cli(
            ws,
            migration_dir=worklist["migration_dir"],
            topic=topic,
            active_claim_id=str(item.get("active_claim_id") or ""),
            latest_review=latest_review,
        ),
        "guardrails": [
            "do_not_auto_backfill_ambiguous_aggregate_topic_claim_statement",
            "human_topic_question_required_before_claim_statement_repair",
            "keep_claim_trust_unchanged_until_semantic_review_passes",
        ],
        "can_update_claim_trust": False,
    }


def _topic_question_command(item: dict[str, Any]) -> dict[str, Any]:
    for command in item.get("review_action_commands", []) or []:
        if isinstance(command, dict) and command.get("action") == _TOPIC_QUESTION_ACTION:
            return dict(command)
    return {}


def _checkpoint_payload(item: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    checkpoint_id = str(command.get("checkpoint_id") or "")
    mode = "decide_open_checkpoint" if checkpoint_id else "request_checkpoint"
    open_checkpoint = _open_checkpoint(item, checkpoint_id=checkpoint_id)
    return {
        "mode": mode,
        "checkpoint_id": checkpoint_id,
        "checkpoint_ref": f"human-checkpoint:{checkpoint_id}" if checkpoint_id else "",
        "reason": str(open_checkpoint.get("reason") or "human topic question required before claim backfill"),
        "options": list(open_checkpoint.get("options") or ["provide_topic_question", "keep_backlog_blocking"]),
        "command": command,
        "can_update_claim_trust": False,
    }


def _open_checkpoint(item: dict[str, Any], *, checkpoint_id: str) -> dict[str, Any]:
    for checkpoint in item.get("open_human_checkpoints", []) or []:
        if isinstance(checkpoint, dict) and checkpoint.get("checkpoint_id") == checkpoint_id:
            return checkpoint
    return {}


def _needs_revision_result_cli(
    ws: WorkspacePaths,
    *,
    migration_dir: str,
    topic: str,
    active_claim_id: str,
    latest_review: dict[str, Any],
) -> str:
    parts = [
        f"aitp-v5 --base {ws.base} legacy semantic-review-result",
        f"--migration-dir {migration_dir}",
        f"--topic {topic}",
        "--status needs_revision",
    ]
    if active_claim_id:
        parts.append(f"--active-claim {active_claim_id}")
    parts.extend(f"--legacy-ref {ref}" for ref in _clean_refs(latest_review.get("reviewed_legacy_refs", [])))
    parts.extend(f"--typed-ref {ref}" for ref in _clean_refs(latest_review.get("reviewed_typed_refs", [])))
    parts.append(f"--remaining-action {_TOPIC_QUESTION_ACTION}")
    parts.append("--summary <human-reviewed topic question basis; keep claim backfill blocked if unresolved>")
    return " ".join(parts)


def _clean_refs(values: Any) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]
