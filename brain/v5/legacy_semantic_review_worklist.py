"""Prioritized worklist for legacy semantic review backlog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.legacy_semantic_review_manifest import build_legacy_semantic_review_manifest
from brain.v5.paths import WorkspacePaths


def build_legacy_semantic_review_worklist(
    ws: WorkspacePaths,
    *,
    migration_dir: str | Path,
) -> dict[str, Any]:
    """Build a read-only prioritized queue for remaining legacy semantic reviews."""

    manifest = build_legacy_semantic_review_manifest(ws, migration_dir=migration_dir)
    candidates = [
        _work_item(item, workspace=manifest["workspace"], migration_dir=manifest["migration_dir"])
        for item in manifest["items"]
        if item["review_status"] in {"pending", "needs_revision", "inconclusive"}
    ]
    items = sorted(candidates, key=lambda item: (-item["priority_score"], item["topic"]))
    return {
        "kind": "legacy_semantic_review_worklist",
        "run_id": manifest["run_id"],
        "migration_dir": manifest["migration_dir"],
        "workspace": manifest["workspace"],
        "work_item_count": len(items),
        "status_counts": _status_counts(items),
        "items": items,
        "next_actions": [f"worklist_item:{item['topic']}" for item in items],
        "semantic_lossless_proven": False,
        "semantic_review_required": True,
        "truth_source": "legacy_semantic_review_manifest",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _work_item(item: dict[str, Any], *, workspace: str, migration_dir: str) -> dict[str, Any]:
    repair_count = int(item.get("repair_candidate_count") or 0)
    missing = list(item.get("missing_source_components") or _missing_source_components_from_reasons(item))
    followup_actions = list(item.get("followup_review_actions", []))
    focus = _review_focus(
        item,
        repair_count=repair_count,
        missing_components=missing,
        followup_review_actions=followup_actions,
    )
    priority_score = _priority_score(item, repair_count=repair_count, missing_components=missing)
    latest = item.get("latest_semantic_review") if isinstance(item.get("latest_semantic_review"), dict) else {}
    satisfied_actions = list(item.get("satisfied_review_actions", []))
    review_action_commands = _review_action_commands(
        item,
        latest_review=latest,
        workspace=workspace,
        migration_dir=migration_dir,
    )
    return {
        "topic": item["topic"],
        "active_claim_id": item["active_claim_id"],
        "review_status": item["review_status"],
        "review_priority": item["review_priority"],
        "priority_score": priority_score,
        "priority_reasons": _priority_reasons(item, repair_count=repair_count, missing_components=missing),
        "latest_review_id": str(latest.get("review_id") or ""),
        "review_focus": focus,
        "missing_source_components": missing,
        "satisfied_review_actions": satisfied_actions,
        "followup_review_actions": followup_actions,
        "review_action_commands": review_action_commands,
        "followup_review_commands": _followup_review_commands(
            item,
            latest_review=latest,
            satisfied_review_actions=satisfied_actions,
            followup_review_actions=followup_actions,
            workspace=workspace,
            migration_dir=migration_dir,
        ),
        "repair_candidate_count": repair_count,
        "repair_candidates": list(item.get("repair_candidates", [])),
        "packet_cli": item["packet_cli"],
        "result_cli_template": item["result_cli_template"],
        "can_update_claim_trust": False,
    }


def _review_action_commands(
    item: dict[str, Any],
    *,
    latest_review: dict[str, Any],
    workspace: str,
    migration_dir: str,
) -> list[dict[str, Any]]:
    if not latest_review:
        return []
    return [
        command
        for action in latest_review.get("remaining_actions", [])
        for command in [
            _review_action_command(
                str(action),
                item,
                latest_review=latest_review,
                workspace=workspace,
                migration_dir=migration_dir,
            )
        ]
        if command is not None
    ]


def _review_action_command(
    action: str,
    item: dict[str, Any],
    *,
    latest_review: dict[str, Any],
    workspace: str,
    migration_dir: str,
) -> dict[str, Any] | None:
    action = action.strip()
    if not action:
        return None
    review_id = str(latest_review.get("review_id") or "")
    if action == "migrate_legacy_l2_graph_entries_into_typed_l2_records":
        return _command(
            action,
            review_id=review_id,
            cli=f"aitp-v5 --base {workspace} legacy l2-graph-manifest",
            mcp="aitp_v5_build_legacy_l2_graph_manifest",
            surface="legacy_l2_graph_manifest",
        )
    if action == "rebuild_l2_obsidian_view_from_typed_graph":
        return _command(
            action,
            review_id=review_id,
            cli=f"aitp-v5 --base {workspace} legacy l2-obsidian-view",
            mcp="aitp_v5_write_legacy_l2_obsidian_view",
            surface="legacy_l2_obsidian_view_bundle",
        )
    if action == "complete_source_reconstruction":
        return _command(
            action,
            review_id=review_id,
            cli=f"aitp-v5 --base {workspace} source reconstruction-review --claim {item['active_claim_id']}",
            mcp="aitp_v5_build_source_reconstruction_review_packet",
            surface="source_reconstruction_review_packet",
        )
    if action == "record_source_reconstruction_review_result":
        return _command(
            action,
            review_id=review_id,
            cli=(
                f"aitp-v5 --base {workspace} source reconstruction-review-result "
                f"--claim {item['active_claim_id']} --status <passed|needs_revision|inconclusive> "
                "--reviewed-component <component> --basis-ref <source-or-typed-ref> "
                "--summary <source reconstruction review basis>"
            ),
            mcp="aitp_v5_record_source_reconstruction_review_result",
            surface="source_reconstruction_review_result_record",
            effect="typed_review_record_write",
            can_update_kernel_state=True,
        )
    if action == "classify_noncanonical_seed_before_promotion":
        return _command(
            action,
            review_id=review_id,
            cli=(
                f"aitp-v5 --base {workspace} legacy semantic-review-result "
                f"--migration-dir {migration_dir} --topic {item['topic']} "
                "--status <passed|inconclusive> --legacy-ref <reviewed-noncanonical-ref> "
                "--summary <classify noncanonical seed and remaining promotion boundary>"
            ),
            mcp="aitp_v5_record_legacy_semantic_review_result",
            surface="legacy_semantic_review_result_record",
            effect="typed_review_record_write",
            can_update_kernel_state=True,
        )
    if action == "decide_human_checkpoint_before_promotion":
        return _command(
            action,
            review_id=review_id,
            cli=(
                f"aitp-v5 --base {workspace} checkpoint request "
                f"--topic {item['topic']} --claim {item['active_claim_id']} "
                "--reason <legacy semantic review promotion decision> --requested-by legacy_semantic_review "
                "--option approve_semantic_review --option keep_backlog_blocking"
            ),
            mcp="aitp_v5_request_human_checkpoint",
            surface="human_checkpoint_record",
        )
    normalized = " ".join(action.lower().replace("_", " ").split())
    if "source reconstruction" in normalized or "reconstruction path" in normalized:
        return _command(
            action,
            review_id=review_id,
            cli=f"aitp-v5 --base {workspace} source reconstruction-review --claim {item['active_claim_id']}",
            mcp="aitp_v5_build_source_reconstruction_review_packet",
            surface="source_reconstruction_review_packet",
        )
    return None


def _command(
    action: str,
    *,
    review_id: str,
    cli: str,
    mcp: str,
    surface: str,
    effect: str = "orientation_only",
    can_update_kernel_state: bool = False,
) -> dict[str, Any]:
    return {
        "action": action,
        "latest_review_id": review_id,
        "cli": cli,
        "mcp": mcp,
        "surface": surface,
        "effect": effect,
        "can_update_kernel_state": can_update_kernel_state,
        "can_update_claim_trust": False,
    }


def _priority_score(
    item: dict[str, Any],
    *,
    repair_count: int,
    missing_components: list[str],
) -> int:
    score = {
        "needs_revision": 300,
        "inconclusive": 200,
        "pending": 100,
    }.get(str(item.get("review_status")), 0)
    score += {"critical": 80, "high": 50, "medium": 20, "low": 0}.get(str(item.get("review_priority")), 0)
    score += repair_count * 40
    score += len(missing_components) * 5
    if "archive_only_records_require_sampling" in set(item.get("review_reasons", [])):
        score += 10
    return score


def _priority_reasons(
    item: dict[str, Any],
    *,
    repair_count: int,
    missing_components: list[str],
) -> list[str]:
    reasons = [f"review_status:{item['review_status']}", f"review_priority:{item['review_priority']}"]
    if repair_count:
        reasons.append(f"repair_candidates:{repair_count}")
    if missing_components:
        reasons.append(f"missing_source_components:{len(missing_components)}")
    reasons.extend(str(reason) for reason in item.get("review_reasons", []))
    return _unique(reasons)


def _review_focus(
    item: dict[str, Any],
    *,
    repair_count: int,
    missing_components: list[str],
    followup_review_actions: list[str],
) -> list[str]:
    focus: list[str] = []
    if repair_count:
        focus.append("apply_or_review_typed_repair_candidates")
    focus.extend(followup_review_actions)
    if missing_components:
        focus.append("complete_source_reconstruction_components")
    if "archive_only_records_require_sampling" in set(item.get("review_reasons", [])):
        focus.append("sample_archive_reference_readback")
    if item["review_status"] == "pending":
        focus.append("perform_initial_semantic_review")
    if item["review_status"] == "inconclusive":
        focus.append("resolve_inconclusive_semantic_review")
    focus.append("record_next_legacy_semantic_review_result")
    return _unique(focus)


def _followup_review_commands(
    item: dict[str, Any],
    *,
    latest_review: dict[str, Any],
    satisfied_review_actions: list[str],
    followup_review_actions: list[str],
    workspace: str,
    migration_dir: str,
) -> list[dict[str, Any]]:
    if not followup_review_actions:
        return []
    legacy_refs = [str(ref) for ref in latest_review.get("reviewed_legacy_refs", []) if str(ref)]
    typed_refs = [str(ref) for ref in latest_review.get("reviewed_typed_refs", []) if str(ref)]
    return [
        {
            "action": action,
            "latest_review_id": str(latest_review.get("review_id") or ""),
            "satisfied_review_actions": list(satisfied_review_actions),
            "result_cli": _followup_result_cli(
                item,
                workspace=workspace,
                migration_dir=migration_dir,
                legacy_refs=legacy_refs,
                typed_refs=typed_refs,
            ),
            "result_mcp": "aitp_v5_record_legacy_semantic_review_result",
            "can_update_claim_trust": False,
        }
        for action in followup_review_actions
    ]


def _followup_result_cli(
    item: dict[str, Any],
    *,
    workspace: str,
    migration_dir: str,
    legacy_refs: list[str],
    typed_refs: list[str],
) -> str:
    refs = " ".join([*(f"--typed-ref {ref}" for ref in typed_refs), *(f"--legacy-ref {ref}" for ref in legacy_refs)])
    if refs:
        refs = f" {refs}"
    return (
        f"aitp-v5 --base {workspace} legacy semantic-review-result "
        f"--migration-dir {migration_dir} --topic {item['topic']} "
        "--status <passed|inconclusive>"
        f"{refs} "
        "--summary <reviewed satisfied actions; explain any remaining semantic gaps>"
    )


def _missing_source_components_from_reasons(item: dict[str, Any]) -> list[str]:
    source = item.get("source_reconstruction")
    if isinstance(source, dict) and isinstance(source.get("missing_components"), list):
        return [str(value) for value in source["missing_components"]]
    return []


def _status_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"needs_revision": 0, "inconclusive": 0, "pending": 0}
    for item in items:
        status = item["review_status"]
        if status in counts:
            counts[status] += 1
    return counts


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
