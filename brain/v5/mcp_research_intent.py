"""MCP wrappers for vNext research-intent surfaces."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.research_intent import materialize_steering_redirect, record_research_intent_packet
from brain.v5.workspace import init_workspace


def _ws(base: str):
    return init_workspace(Path(base))


def aitp_v5_record_research_intent_packet(
    base: str, *, topic_id: str, initial_idea: str, novelty_target: str = "",
    non_goals: list[str] | None = None, required_first_validation_route: str = "",
    initial_evidence_bar: str = "", clarification_questions: list[str] | None = None,
    status: str = "needs_clarification",
) -> dict:
    packet = record_research_intent_packet(
        _ws(base),
        topic_id=topic_id,
        initial_idea=initial_idea,
        novelty_target=novelty_target,
        non_goals=non_goals,
        required_first_validation_route=required_first_validation_route,
        initial_evidence_bar=initial_evidence_bar,
        clarification_questions=clarification_questions,
        status=status,
    )
    return require_valid_public_surface("research_intent_packet", {"ok": True, **asdict(packet)})


def aitp_v5_materialize_steering_redirect(
    base: str, *, topic_id: str, steering_text: str, novelty_target: str,
    scope: str, acceptance_posture: str, control_note: str = "",
    session_id: str = "", status: str = "active",
) -> dict:
    decision = materialize_steering_redirect(
        _ws(base),
        topic_id=topic_id,
        steering_text=steering_text,
        novelty_target=novelty_target,
        scope=scope,
        acceptance_posture=acceptance_posture,
        control_note=control_note,
        session_id=session_id,
        status=status,
    )
    return require_valid_public_surface("steering_decision_record", {"ok": True, **asdict(decision)})
