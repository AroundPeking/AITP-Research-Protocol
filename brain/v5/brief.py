"""Execution brief construction for AITP v5."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from brain.v5.flow import resolve_flow_profile
from brain.v5.models import ClaimRecord
from brain.v5.question_engine import generate_questions
from brain.v5.workspace import get_claim, get_session_binding


def build_execution_brief(ws, session_id: str) -> dict[str, Any]:
    """Build the state packet an agent should see before acting."""

    session = get_session_binding(ws, session_id)
    claim: ClaimRecord | None = None
    flow = None
    questions = []

    if session.active_claim:
        claim = get_claim(ws, session.active_claim)
        flow = resolve_flow_profile(claim)
        questions = generate_questions(claim, flow)

    mandatory_reflection = [
        asdict(q) for q in questions[:3]
    ]

    next_action_candidates = []
    if claim and flow:
        if flow.profile == "autopilot":
            next_action_candidates.append(
                {
                    "action": "run_trusted_recipe",
                    "rank": 1,
                    "why": flow.reason,
                    "expected_evidence_gain": "confirm recipe output remains inside trusted tolerance",
                }
            )
        elif flow.profile == "research":
            next_action_candidates.append(
                {
                    "action": "answer_dynamic_physics_questions",
                    "rank": 1,
                    "why": "new or weakly trusted claim needs object-relation sense-making",
                    "expected_evidence_gain": "clarify claim scope, mechanism, and failure mode",
                }
            )
        else:
            next_action_candidates.append(
                {
                    "action": "select_high_information_check",
                    "rank": 1,
                    "why": flow.reason,
                    "expected_evidence_gain": "reduce active uncertainty",
                }
            )

    return {
        "session": asdict(session),
        "current_focus": {
            "active_claim": session.active_claim,
            "active_route": session.active_route,
            "active_cycle": session.active_cycle,
            "claim_statement": claim.statement if claim else "",
            "confidence_state": claim.confidence_state if claim else "",
            "evidence_profile": claim.evidence_profile if claim else "",
            "main_uncertainty": claim.active_uncertainty if claim else "",
        },
        "flow_profile": asdict(flow) if flow else {"profile": "guided", "reason": "no active claim", "escalation_triggers": []},
        "known_context": {
            "topic_id": session.topic_id,
            "context_id": session.context_id,
            "previous_failed_attempts": [],
        },
        "mandatory_reflection": mandatory_reflection,
        "next_action_candidates": next_action_candidates,
        "forbidden_now": _forbidden_actions(flow.profile if flow else "guided"),
        "human_checkpoint": {"needed": False, "reason": None},
    }


def _forbidden_actions(profile: str) -> list[str]:
    if profile == "autopilot":
        return ["promote_new_claim_without_review"]
    if profile == "research":
        return ["treat_claim_as_validated", "skip_failure_mode_analysis"]
    if profile == "adversarial":
        return ["ignore_counterargument", "promote_without_human_checkpoint"]
    return ["change_claim_confidence_without_evidence"]
