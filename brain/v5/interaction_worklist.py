"""Actionable read-only worklist for natural interaction recording."""

from __future__ import annotations

from collections import Counter
from typing import Any

from brain.v5.workspace_interaction_preview import build_workspace_interaction_preview


def build_interaction_recording_worklist(ws) -> dict[str, Any]:
    """Translate workspace interaction previews into conservative kernel actions."""

    preview = build_workspace_interaction_preview(ws)
    items = [_work_item(item) for item in preview.get("items", [])]
    mode_counts = Counter(item["recording_mode"] for item in items)
    return {
        "kind": "interaction_recording_worklist",
        "session_count": int(preview.get("session_count") or 0),
        "work_item_count": len(items),
        "required_now_count": sum(1 for item in items if item["required_now"]),
        "decision_mode_counts": dict(mode_counts),
        "items": items,
        "source_preview_refs": list(preview.get("preview_refs") or []),
        "source_records": dict(preview.get("source_records") or {}),
        "derived_from": "workspace_interaction_preview_bundle",
        "truth_source": "typed_records",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "adapter_rule": "read_for_orientation_then_call_kernel_before_trust_updates",
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _work_item(preview_item: dict[str, Any]) -> dict[str, Any]:
    session_id = str(preview_item.get("session_id") or "")
    topic_id = str(preview_item.get("topic_id") or "")
    claim_id = str(preview_item.get("active_claim") or "")
    mode = str(preview_item.get("recording_mode") or "")
    action = _action_plan(
        session_id=session_id,
        topic_id=topic_id,
        claim_id=claim_id,
        mode=mode,
    )
    return {
        "session_id": session_id,
        "topic_id": topic_id,
        "active_claim": claim_id,
        "recording_mode": mode,
        "action_kind": action["action_kind"],
        "required_now": action["required_now"],
        "next_kernel_entrypoint": str(preview_item.get("next_kernel_entrypoint") or ""),
        "mcp_entrypoints": action["mcp_entrypoints"],
        "cli_templates": action["cli_templates"],
        "before_trust_change": action["before_trust_change"],
        "source_preview_ref": str(preview_item.get("source_preview_ref") or ""),
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _action_plan(*, session_id: str, topic_id: str, claim_id: str, mode: str) -> dict[str, Any]:
    if not claim_id:
        return {
            "action_kind": "keep_lightweight_until_claim_binding",
            "required_now": False,
            "mcp_entrypoints": ["aitp_v5_create_claim", "aitp_v5_bind_session"],
            "cli_templates": [
                (
                    "aitp-v5 --base <workspace> claim create "
                    f"--topic {topic_id} --statement <stable research question or claim> "
                    "--evidence-profile <profile> --confidence-state hypothesis "
                    "--uncertainty <active uncertainty>"
                ),
                (
                    "aitp-v5 --base <workspace> session bind "
                    f"{session_id} --topic {topic_id} --context <context-id> --claim <claim-id>"
                ),
            ],
            "before_trust_change": [
                "bind or create a claim only after a stable research question emerges",
                "run trust preflight before any claim confidence change",
            ],
        }
    if mode == "trust_boundary_checkpoint":
        return {
            "action_kind": "request_checkpoint_before_natural_recording",
            "required_now": True,
            "mcp_entrypoints": [
                "aitp_v5_request_human_checkpoint",
                "aitp_v5_record_evidence",
                "aitp_v5_preflight_trust_update",
            ],
            "cli_templates": [
                (
                    "aitp-v5 --base <workspace> checkpoint request "
                    f"--topic {topic_id} --claim {claim_id} --reason <reason> "
                    "--requested-by interaction_recording_worklist "
                    "--option approve_recording --option keep_lightweight"
                ),
                _evidence_cli(topic_id, claim_id),
                _trust_preflight_cli(session_id, topic_id, claim_id),
            ],
            "before_trust_change": [
                "record a human checkpoint decision before high-risk recording",
                "record typed evidence or tool-run provenance",
                "run trust preflight before any claim confidence change",
            ],
        }
    if mode == "guarded_recording":
        return {
            "action_kind": "record_sensemaking_then_evidence_before_trust",
            "required_now": False,
            "mcp_entrypoints": [
                "aitp_v5_record_sensemaking_report",
                "aitp_v5_record_evidence",
                "aitp_v5_preflight_trust_update",
            ],
            "cli_templates": [
                _sensemaking_cli(topic_id, claim_id),
                _evidence_cli(topic_id, claim_id),
                _trust_preflight_cli(session_id, topic_id, claim_id),
            ],
            "before_trust_change": [
                "record typed evidence or tool-run provenance",
                "run trust preflight before any claim confidence change",
            ],
        }
    return {
        "action_kind": "optional_sensemaking_trace_before_trust",
        "required_now": False,
        "mcp_entrypoints": [
            "aitp_v5_record_sensemaking_report",
            "aitp_v5_preflight_trust_update",
        ],
        "cli_templates": [
            _sensemaking_cli(topic_id, claim_id),
            _trust_preflight_cli(session_id, topic_id, claim_id),
        ],
        "before_trust_change": [
            "run trust preflight before any claim confidence change",
        ],
    }


def _sensemaking_cli(topic_id: str, claim_id: str) -> str:
    return (
        "aitp-v5 --base <workspace> sensemaking report "
        f"--topic {topic_id} --claim {claim_id} "
        "--title <title> --summary <orientation-only summary>"
    )


def _evidence_cli(topic_id: str, claim_id: str) -> str:
    return (
        "aitp-v5 --base <workspace> evidence record "
        f"--topic {topic_id} --claim {claim_id} "
        "--type <evidence-type> --status <supports|contradicts|mixed|inconclusive> "
        "--summary <source-grounded summary> --supports-output <output> "
        "--source-ref <typed-source-ref>"
    )


def _trust_preflight_cli(session_id: str, topic_id: str, claim_id: str) -> str:
    return (
        "aitp-v5 --base <workspace> trust preflight <action> "
        f"--session {session_id} --topic {topic_id} --claim {claim_id} "
        "--source-kind typed_records --source-ref <record-ref> --rationale <rationale>"
    )
