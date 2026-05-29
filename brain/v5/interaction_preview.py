"""Read-only preview of how AITP v5 will record a natural conversation."""

from __future__ import annotations

from typing import Any

from brain.v5.brief import build_execution_brief


def build_interaction_recording_preview(ws, session_id: str) -> dict[str, Any]:
    """Explain recording boundaries for a session without mutating state."""

    brief = build_execution_brief(ws, session_id)
    focus = brief["current_focus"]
    interaction = brief["interaction_profile"]
    risk = brief["risk_assessment"]
    action_budget = brief["action_budget"]
    evidence = brief["evidence_coverage"]
    flow = brief["flow_profile"]

    missing_outputs = evidence.get("missing_outputs", [])
    required_outputs = action_budget.get("required_outputs", [])
    risk_level = risk.get("level", action_budget.get("level", "guided"))
    checkpoint_needed = bool(brief["human_checkpoint"]["needed"])

    return {
        "kind": "interaction_recording_preview",
        "session_id": session_id,
        "topic_id": brief["known_context"]["topic_id"],
        "active_claim": focus["active_claim"],
        "interaction_profile": {
            "requested_role": interaction["requested_role"],
            "effective_role": interaction["profile"]["role"],
            "question_style": interaction["profile"]["question_style"],
            "explanation_style": interaction["profile"]["explanation_style"],
        },
        "risk_level": risk_level,
        "flow_profile": flow["profile"],
        "can_stay_lightweight": risk_level in {"fluid", "guided"} and not checkpoint_needed,
        "max_questions": interaction["effective_max_questions"],
        "mandatory_question_count": len(brief["mandatory_reflection"]),
        "natural_workflow": _natural_workflow(risk_level, bool(focus["active_claim"])),
        "recording_decision": _recording_decision(
            active_claim=bool(focus["active_claim"]),
            risk_level=risk_level,
            missing_outputs=missing_outputs,
            checkpoint_needed=checkpoint_needed,
        ),
        "recommended_records": _recommended_records(
            active_claim=bool(focus["active_claim"]),
            risk_level=risk_level,
            required_outputs=required_outputs,
            missing_outputs=missing_outputs,
        ),
        "deferred_records": _deferred_records(risk_level, checkpoint_needed),
        "heavier_triggers": _heavier_triggers(risk_level, missing_outputs, checkpoint_needed),
        "boundary_notes": interaction.get("boundary_notes", []),
        "forbidden_now": brief["forbidden_now"],
        "source_brief_ref": f"execution_brief:{session_id}",
        "truth_source": "typed_records",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _natural_workflow(risk_level: str, active_claim: bool) -> list[str]:
    if not active_claim:
        return [
            "continue_natural_research_conversation",
            "bind_or_create_a_claim_only_after_a_stable_research_question_emerges",
        ]
    steps = ["continue_natural_research_conversation"]
    if risk_level in {"fluid", "guided"}:
        steps.append("record_only_substantive_new_definitions_claims_evidence_or_failure_modes")
    else:
        steps.append("pause_at_evidence_validation_or_trust_boundaries_before_recording")
    steps.append("treat_summaries_as_orientation_not_evidence")
    return steps


def _recording_decision(
    *,
    active_claim: bool,
    risk_level: str,
    missing_outputs: list[str],
    checkpoint_needed: bool,
) -> dict[str, Any]:
    if not active_claim:
        return _decision(
            mode="lightweight_trace",
            can_continue_without_kernel_write=True,
            next_kernel_entrypoint="",
            required_before_trust_change=["bind_or_create_claim", "aitp_v5_preflight_trust_update"],
            why="no active claim is bound, so natural exploration can stay lightweight until a stable research question emerges",
        )
    if checkpoint_needed or risk_level == "adversarial":
        return _decision(
            mode="trust_boundary_checkpoint",
            can_continue_without_kernel_write=False,
            next_kernel_entrypoint="aitp_v5_request_human_checkpoint",
            required_before_trust_change=[
                "aitp_v5_request_human_checkpoint",
                "aitp_v5_record_evidence_or_tool_run",
                "aitp_v5_preflight_trust_update",
            ],
            why="adversarial risk requires a human checkpoint before recording content that could drive trust changes",
        )
    if missing_outputs:
        return _decision(
            mode="guarded_recording",
            can_continue_without_kernel_write=True,
            next_kernel_entrypoint="aitp_v5_record_sensemaking_report",
            required_before_trust_change=[
                "aitp_v5_record_evidence_or_tool_run",
                "aitp_v5_preflight_trust_update",
            ],
            why="active claim can continue naturally, but missing evidence outputs require typed provenance before trust changes",
        )
    return _decision(
        mode="lightweight_trace",
        can_continue_without_kernel_write=True,
        next_kernel_entrypoint="aitp_v5_record_sensemaking_report",
        required_before_trust_change=["aitp_v5_preflight_trust_update"],
        why="active claim has no missing required outputs, so natural conversation can stay lightweight until trust changes are requested",
    )


def _decision(
    *,
    mode: str,
    can_continue_without_kernel_write: bool,
    next_kernel_entrypoint: str,
    required_before_trust_change: list[str],
    why: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "can_continue_without_kernel_write": can_continue_without_kernel_write,
        "next_kernel_entrypoint": next_kernel_entrypoint,
        "required_before_trust_change": required_before_trust_change,
        "why": why,
        "summary_inputs_trusted": False,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _recommended_records(
    *,
    active_claim: bool,
    risk_level: str,
    required_outputs: list[str],
    missing_outputs: list[str],
) -> list[dict[str, Any]]:
    records = [
        {
            "record_type": "execution_brief",
            "timing": "read_now",
            "required_now": True,
            "reason": "recover typed session state before acting",
        }
    ]
    if not active_claim:
        return records

    records.append(
        {
            "record_type": "sensemaking_report_record",
            "timing": "after_substantive_interpretive_progress",
            "required_now": False,
            "reason": "capture orientation without treating it as validation",
        }
    )
    if "evidence_or_provenance" in missing_outputs:
        records.append(
            {
                "record_type": "evidence_record_or_tool_run_record",
                "timing": "after_real_source_tool_or_code_provenance_exists",
                "required_now": "evidence_or_provenance" in required_outputs,
                "reason": "required outputs are missing for the active claim",
            }
        )
    if risk_level in {"rigorous", "adversarial"}:
        records.append(
            {
                "record_type": "validation_contract_record",
                "timing": "before_claim_validation_or_high_risk_tool_execution",
                "required_now": True,
                "reason": "high-risk work needs explicit checks before trust changes",
            }
        )
    return records


def _deferred_records(risk_level: str, checkpoint_needed: bool) -> list[dict[str, Any]]:
    return [
        {
            "record_type": "promotion_packet_record",
            "until": "evidence_validation_scope_and_failure_modes_are_explicit",
            "reason": "long-term memory promotion is a later trust boundary",
        },
        {
            "record_type": "trust_update_apply",
            "until": "preflight_allows_the_requested_trust_change",
            "reason": "conversation summaries cannot update claim confidence",
        },
        {
            "record_type": "human_checkpoint_record",
            "until": "human_judgment_is_required",
            "reason": "needed now only when risk policy or promotion requires it",
            "required_now": checkpoint_needed or risk_level == "adversarial",
        },
    ]


def _heavier_triggers(risk_level: str, missing_outputs: list[str], checkpoint_needed: bool) -> list[str]:
    triggers = [
        "user_or_agent_requests_a_claim_trust_change",
        "agent_wants_to_promote_content_to_L2_memory",
        "source_is_only_a_summary_task_plan_findings_or_progress_file",
    ]
    if missing_outputs:
        triggers.append("active_claim_has_missing_required_evidence_outputs")
    if risk_level in {"rigorous", "adversarial"}:
        triggers.append("claim_risk_requires_validation_or_adversarial_review")
    if checkpoint_needed:
        triggers.append("risk_budget_requires_human_checkpoint")
    return triggers
