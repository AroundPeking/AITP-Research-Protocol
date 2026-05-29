"""vNext research-intent and steering surfaces."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from brain.v5.ids import prefixed_id
from brain.v5.markdown import read_md, write_md
from brain.v5.paths import WorkspacePaths


@dataclass
class ResearchIntentPacketRecord:
    intent_id: str
    topic_id: str
    initial_idea: str
    novelty_target: str
    non_goals: list[str] = field(default_factory=list)
    required_first_validation_route: str = ""
    initial_evidence_bar: str = ""
    clarification_questions: list[str] = field(default_factory=list)
    status: str = "needs_clarification"
    execution_ready: bool = False
    summary_inputs_trusted: bool = False
    can_update_claim_trust: bool = False
    kind: str = "research_intent_packet"


@dataclass
class SteeringDecisionRecord:
    decision_id: str
    topic_id: str
    steering_text: str
    novelty_target: str
    scope: str
    acceptance_posture: str
    control_note: str = ""
    session_id: str = ""
    status: str = "active"
    summary_inputs_trusted: bool = False
    can_update_claim_trust: bool = False
    kind: str = "steering_decision"


def record_research_intent_packet(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    initial_idea: str,
    novelty_target: str = "",
    non_goals: list[str] | None = None,
    required_first_validation_route: str = "",
    initial_evidence_bar: str = "",
    clarification_questions: list[str] | None = None,
    status: str = "needs_clarification",
) -> ResearchIntentPacketRecord:
    """Materialize a vNext idea gate before treating a vague idea as executable."""

    if status not in {"needs_clarification", "approved_for_execution", "deferred"}:
        raise ValueError("research intent status must be needs_clarification, approved_for_execution, or deferred")
    packet = ResearchIntentPacketRecord(
        intent_id=prefixed_id("research-intent", f"{topic_id}:{initial_idea}", max_slug=72),
        topic_id=topic_id,
        initial_idea=initial_idea,
        novelty_target=novelty_target,
        non_goals=non_goals or [],
        required_first_validation_route=required_first_validation_route,
        initial_evidence_bar=initial_evidence_bar,
        clarification_questions=clarification_questions or [],
        status=status,
        execution_ready=status == "approved_for_execution",
    )
    runtime_dir = _topic_runtime_dir(ws, topic_id)
    _write_json(runtime_dir / "idea_packet.json", asdict(packet))
    write_md(runtime_dir / "idea_packet.md", asdict(packet), _idea_packet_body(packet))
    return packet


def materialize_steering_redirect(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    steering_text: str,
    novelty_target: str,
    scope: str,
    acceptance_posture: str,
    control_note: str = "",
    session_id: str = "",
    status: str = "active",
) -> SteeringDecisionRecord:
    """Write durable steering state before a redirected topic route continues."""

    if status not in {"active", "superseded", "cancelled"}:
        raise ValueError("steering status must be active, superseded, or cancelled")
    decision = SteeringDecisionRecord(
        decision_id=prefixed_id("steering-decision", f"{topic_id}:{steering_text}", max_slug=72),
        topic_id=topic_id,
        steering_text=steering_text,
        novelty_target=novelty_target,
        scope=scope,
        acceptance_posture=acceptance_posture,
        control_note=control_note,
        session_id=session_id,
        status=status,
    )
    runtime_dir = _topic_runtime_dir(ws, topic_id)
    direction = {
        "kind": "innovation_direction",
        "topic_id": topic_id,
        "current_decision_id": decision.decision_id,
        "novelty_target": novelty_target,
        "scope": scope,
        "acceptance_posture": acceptance_posture,
        "control_note": control_note,
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
    }
    write_md(runtime_dir / "innovation_direction.md", direction, _innovation_direction_body(decision))
    _append_jsonl(runtime_dir / "innovation_decisions.jsonl", asdict(decision))
    return decision


def load_research_intent_gate(ws: WorkspacePaths, topic_id: str) -> dict[str, Any]:
    """Return the brief-facing state of the topic's vNext research-intent gate."""

    runtime_dir = ws.topic_dir(topic_id) / "runtime"
    path = runtime_dir / "idea_packet.json"
    if not path.exists():
        return {
            "present": False,
            "status": "not_recorded",
            "execution_ready": True,
            "required_next_action": "",
            "artifact_paths": {},
            "summary_inputs_trusted": False,
            "can_update_claim_trust": False,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    status = str(data.get("status") or "")
    execution_ready = bool(data.get("execution_ready")) and status == "approved_for_execution"
    return {
        "present": True,
        "intent_id": str(data.get("intent_id") or ""),
        "topic_id": topic_id,
        "status": status,
        "execution_ready": execution_ready,
        "initial_idea": str(data.get("initial_idea") or ""),
        "novelty_target": str(data.get("novelty_target") or ""),
        "required_first_validation_route": str(data.get("required_first_validation_route") or ""),
        "initial_evidence_bar": str(data.get("initial_evidence_bar") or ""),
        "clarification_questions": list(data.get("clarification_questions") or []),
        "required_next_action": "" if execution_ready else "answer_research_intent_clarification",
        "artifact_paths": {
            "markdown": str(runtime_dir / "idea_packet.md"),
            "json": str(path),
        },
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
    }


def load_innovation_direction(ws: WorkspacePaths, topic_id: str) -> dict[str, Any]:
    """Return the current durable steering surface if one exists."""

    path = ws.topic_dir(topic_id) / "runtime" / "innovation_direction.md"
    if not path.exists():
        return {"present": False, "summary_inputs_trusted": False, "can_update_claim_trust": False}
    frontmatter, _ = read_md(path)
    return {
        "present": True,
        "topic_id": topic_id,
        "current_decision_id": str(frontmatter.get("current_decision_id") or ""),
        "novelty_target": str(frontmatter.get("novelty_target") or ""),
        "scope": str(frontmatter.get("scope") or ""),
        "acceptance_posture": str(frontmatter.get("acceptance_posture") or ""),
        "control_note": str(frontmatter.get("control_note") or ""),
        "artifact_path": str(path),
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
    }


def _topic_runtime_dir(ws: WorkspacePaths, topic_id: str) -> Path:
    runtime_dir = ws.topic_dir(topic_id) / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _idea_packet_body(packet: ResearchIntentPacketRecord) -> str:
    questions = "\n".join(f"- {question}" for question in packet.clarification_questions) or "- None"
    non_goals = "\n".join(f"- {item}" for item in packet.non_goals) or "- None"
    return (
        f"# Research Intent Packet\n\n"
        f"Initial idea: {packet.initial_idea}\n\n"
        f"Novelty target: {packet.novelty_target}\n\n"
        f"Required first validation route: {packet.required_first_validation_route}\n\n"
        f"Initial evidence bar: {packet.initial_evidence_bar}\n\n"
        f"Non-goals:\n{non_goals}\n\n"
        f"Clarification questions:\n{questions}\n"
    )


def _innovation_direction_body(decision: SteeringDecisionRecord) -> str:
    return (
        f"# Innovation Direction\n\n"
        f"Steering: {decision.steering_text}\n\n"
        f"Novelty target: {decision.novelty_target}\n\n"
        f"Scope: {decision.scope}\n\n"
        f"Acceptance posture: {decision.acceptance_posture}\n\n"
        f"Control note: {decision.control_note}\n"
    )
