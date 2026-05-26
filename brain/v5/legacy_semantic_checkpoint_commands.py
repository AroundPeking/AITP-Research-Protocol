"""Human checkpoint command hints for legacy semantic review worklists."""

from __future__ import annotations

from typing import Any


def human_checkpoint_command(
    action: str,
    item: dict[str, Any],
    *,
    review_id: str,
    workspace: str,
    reason: str,
    options: list[str],
) -> dict[str, Any]:
    checkpoint = _matching_open_checkpoint(item, reason=reason, options=options)
    if checkpoint:
        command = _command(
            action,
            review_id=review_id,
            cli=(
                f"aitp-v5 --base {workspace} checkpoint decide {checkpoint['checkpoint_id']} "
                f"--decision <{'|'.join(options)}> --rationale <human rationale> --decided-by <reviewer>"
            ),
            mcp="aitp_v5_decide_human_checkpoint",
            surface="human_checkpoint_record",
            effect="typed_record_write",
            can_update_kernel_state=True,
        )
        command["checkpoint_id"] = str(checkpoint["checkpoint_id"])
        return command
    option_args = " ".join(f"--option {option}" for option in options)
    return _command(
        action,
        review_id=review_id,
        cli=(
            f"aitp-v5 --base {workspace} checkpoint request "
            f"--topic {item['topic']} --claim {item['active_claim_id']} "
            f"--reason <{reason}> --requested-by legacy_semantic_review {option_args}"
        ),
        mcp="aitp_v5_request_human_checkpoint",
        surface="human_checkpoint_record",
        effect="typed_record_write",
        can_update_kernel_state=True,
    )


def _matching_open_checkpoint(
    item: dict[str, Any],
    *,
    reason: str,
    options: list[str],
) -> dict[str, Any] | None:
    for checkpoint in item.get("open_human_checkpoints", []) or []:
        if not isinstance(checkpoint, dict):
            continue
        if checkpoint.get("status") != "open":
            continue
        if checkpoint.get("requested_by") != "legacy_semantic_review":
            continue
        if str(checkpoint.get("reason") or "") != reason:
            continue
        if list(checkpoint.get("options") or []) != list(options):
            continue
        return checkpoint
    return None


def _command(
    action: str,
    *,
    review_id: str,
    cli: str,
    mcp: str,
    surface: str,
    effect: str,
    can_update_kernel_state: bool,
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
