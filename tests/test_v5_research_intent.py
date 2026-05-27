from __future__ import annotations

import json
from pathlib import Path


def _setup_topic(tmp_path: Path):
    from brain.v5.workspace import bind_session, create_topic, init_workspace

    ws = init_workspace(tmp_path / "ws")
    create_topic(ws, "new-qg-idea", context_id="formal-theory", title="New QG Idea")
    bind_session(
        ws,
        "idea-session",
        topic_id="new-qg-idea",
        context_id="formal-theory",
    )
    return ws


def test_record_research_intent_packet_writes_markdown_and_json_gate(tmp_path):
    from brain.v5.markdown import read_md
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.research_intent import record_research_intent_packet

    ws = _setup_topic(tmp_path)

    packet = record_research_intent_packet(
        ws,
        topic_id="new-qg-idea",
        initial_idea="Explore whether modular inclusions can organize a toy bulk reconstruction question.",
        novelty_target="bounded toy criterion before any broad quantum-gravity claim",
        non_goals=["no claim of AdS/CFT proof"],
        required_first_validation_route="source-grounded literature and toy algebra check",
        initial_evidence_bar="one source anchor plus one falsifiable toy check",
        clarification_questions=["Which algebraic setting is the first target?"],
    )

    md_path = ws.topic_dir("new-qg-idea") / "runtime" / "idea_packet.md"
    json_path = ws.topic_dir("new-qg-idea") / "runtime" / "idea_packet.json"
    fm, body = read_md(md_path)
    raw_json = json.loads(json_path.read_text(encoding="utf-8"))

    assert packet.status == "needs_clarification"
    assert fm["kind"] == "research_intent_packet"
    assert fm["execution_ready"] is False
    assert raw_json["topic_id"] == "new-qg-idea"
    assert "Which algebraic setting" in body
    assert require_valid_public_surface("research_intent_packet", {"ok": True, **packet.__dict__})


def test_execution_brief_blocks_deeper_execution_for_unapproved_idea_packet(tmp_path):
    from brain.v5.brief import build_execution_brief
    from brain.v5.research_intent import record_research_intent_packet

    ws = _setup_topic(tmp_path)
    record_research_intent_packet(
        ws,
        topic_id="new-qg-idea",
        initial_idea="A vague but possibly meaningful new direction.",
        novelty_target="unknown",
        required_first_validation_route="not selected",
        initial_evidence_bar="not selected",
        clarification_questions=["What is the scoped output?"],
    )

    brief = build_execution_brief(ws, "idea-session")
    gate = brief["known_context"]["research_intent_gate"]

    assert gate["status"] == "needs_clarification"
    assert gate["execution_ready"] is False
    assert "vnext:execute_without_research_intent_approval" in brief["forbidden_now"]
    assert brief["next_action_candidates"][0]["action"] == "answer_research_intent_clarification"


def test_materialize_steering_redirect_writes_direction_and_ledger(tmp_path):
    from brain.v5.markdown import read_md
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.research_intent import materialize_steering_redirect

    ws = _setup_topic(tmp_path)

    decision = materialize_steering_redirect(
        ws,
        topic_id="new-qg-idea",
        steering_text="继续这个 topic，但方向改成先做 toy algebra obstruction。",
        novelty_target="toy algebra obstruction before broad interpretation",
        scope="first bounded algebraic obstruction check",
        acceptance_posture="diagnostic until source grounded and validated",
        control_note="Do not promote broad quantum-gravity claims from this redirect.",
        session_id="idea-session",
    )

    direction_path = ws.topic_dir("new-qg-idea") / "runtime" / "innovation_direction.md"
    ledger_path = ws.topic_dir("new-qg-idea") / "runtime" / "innovation_decisions.jsonl"
    fm, body = read_md(direction_path)
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]

    assert fm["kind"] == "innovation_direction"
    assert fm["current_decision_id"] == decision.decision_id
    assert "toy algebra obstruction" in body
    assert ledger[-1]["decision_id"] == decision.decision_id
    assert require_valid_public_surface("steering_decision_record", {"ok": True, **decision.__dict__})


def test_research_intent_cli_and_mcp_surfaces(tmp_path, capsys):
    from brain.v5.cli import main
    from brain.v5.mcp_tools import aitp_v5_record_research_intent_packet
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.runtime_entrypoints import runtime_entrypoints

    ws = _setup_topic(tmp_path)

    assert main(
        [
            "--base",
            str(ws.base),
            "intent",
            "packet",
            "record",
            "--topic",
            "new-qg-idea",
            "--idea",
            "Start from a vague modular-inclusion idea.",
            "--novelty-target",
            "bounded toy criterion",
            "--required-first-validation-route",
            "literature plus toy check",
            "--initial-evidence-bar",
            "one source and one falsifier",
            "--clarification-question",
            "Which setting is first?",
        ]
    ) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    mcp_payload = aitp_v5_record_research_intent_packet(
        str(ws.base),
        topic_id="new-qg-idea",
        initial_idea="Start from a vague modular-inclusion idea.",
        novelty_target="bounded toy criterion",
        required_first_validation_route="literature plus toy check",
        initial_evidence_bar="one source and one falsifier",
        clarification_questions=["Which setting is first?"],
    )

    assert require_valid_public_surface("research_intent_packet", cli_payload) == cli_payload
    assert require_valid_public_surface("research_intent_packet", mcp_payload) == mcp_payload
    assert runtime_entrypoints()["record_research_intent_packet"] == {
        "cli": "aitp-v5 intent packet record <args>",
        "mcp": "aitp_v5_record_research_intent_packet",
        "surface": "research_intent_packet",
    }
