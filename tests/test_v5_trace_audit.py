from __future__ import annotations

import json


def _hook_trace_payload():
    from brain.v5.hook_adapters import hook_trace_event_payload
    from brain.v5.hooks import post_tool_use_trace_event

    event = post_tool_use_trace_event(
        session_id="s1",
        topic_id="fqhe",
        claim_id="claim-fqhe",
        risk_level="guided",
        tool_name="exact-diagonalization",
        evidence_status="supports",
    )
    return hook_trace_event_payload(event, hook_name="post_tool")


def _invoke(args, capsys):
    from brain.v5.cli import main

    assert main(args) == 0
    output = capsys.readouterr().out
    return json.loads(output)


def test_trace_logger_appends_jsonl_events(tmp_path):
    from brain.v5.trace import TraceEvent, append_trace_event, read_trace_events

    trace_path = tmp_path / "trace.jsonl"
    append_trace_event(
        trace_path,
        TraceEvent(
            event_id="event-1",
            session_id="s1",
            topic_id="fqhe",
            event_type="brief_built",
            risk_level="fluid",
            payload={"max_questions": 1},
        ),
    )
    append_trace_event(
        trace_path,
        TraceEvent(
            event_id="event-2",
            session_id="s1",
            topic_id="fqhe",
            event_type="question_asked",
            risk_level="fluid",
            payload={"question_id": "q1"},
        ),
    )

    events = read_trace_events(trace_path)

    assert [event.event_id for event in events] == ["event-1", "event-2"]
    assert events[0].payload == {"max_questions": 1}


def test_persist_hook_trace_event_records_stdout_payload_in_workspace(tmp_path):
    from brain.v5.trace import persist_hook_trace_event, read_trace_events
    from brain.v5.workspace import init_workspace

    ws = init_workspace(tmp_path)
    record = persist_hook_trace_event(ws, _hook_trace_payload())

    assert record["ok"] is True
    assert record["kind"] == "hook_trace_event_record"
    assert record["source_kind"] == "hook_trace_event"
    assert record["source_hook"] == "post_tool"
    assert record["summary_inputs_trusted"] is False
    assert record["can_update_claim_trust"] is False
    assert record["writes_trace_event"] is True
    assert record["trace_path"].replace("\\", "/").endswith(".aitp/runtime/hook_trace_events.jsonl")

    events = read_trace_events(ws.root / "runtime" / "hook_trace_events.jsonl")
    assert [event.event_id for event in events] == [record["event_id"]]
    assert events[0].event_type == "tool_run_recorded"
    assert events[0].payload["tool_name"] == "exact-diagonalization"


def test_cli_trace_hook_event_persist_records_payload(tmp_path, capsys):
    payload = _invoke(
        [
            "--base",
            str(tmp_path),
            "trace",
            "hook-event",
            "persist",
            "--payload-json",
            json.dumps(_hook_trace_payload()),
        ],
        capsys,
    )

    assert payload["ok"] is True
    assert payload["kind"] == "hook_trace_event_record"
    assert payload["source_hook"] == "post_tool"
    assert payload["summary_inputs_trusted"] is False


def test_mcp_persist_hook_trace_event_returns_contract_payload(tmp_path):
    from brain.v5.mcp_tools import aitp_v5_persist_hook_trace_event
    from brain.v5.trace import read_trace_events
    from brain.v5.workspace import init_workspace

    ws = init_workspace(tmp_path)
    payload = aitp_v5_persist_hook_trace_event(str(tmp_path), hook_payload=_hook_trace_payload())

    assert payload["ok"] is True
    assert payload["kind"] == "hook_trace_event_record"
    assert read_trace_events(ws.root / "runtime" / "hook_trace_events.jsonl")


def test_audit_detects_underthinking_when_rigorous_action_lacks_evidence():
    from brain.v5.audit import audit_trace_events
    from brain.v5.trace import TraceEvent

    incidents = audit_trace_events(
        [
            TraceEvent(
                event_id="event-1",
                session_id="s1",
                topic_id="librpa-gw",
                claim_id="claim-1",
                event_type="brief_built",
                risk_level="rigorous",
                payload={"required_outputs": ["evidence_or_provenance"]},
            ),
            TraceEvent(
                event_id="event-2",
                session_id="s1",
                topic_id="librpa-gw",
                claim_id="claim-1",
                event_type="action_completed",
                risk_level="rigorous",
                payload={"action": "accept_code_method_result", "outputs": []},
            ),
        ]
    )

    assert len(incidents) == 1
    assert incidents[0].violation_kind == "under_thinking"
    assert incidents[0].change_direction == "tighten"
    assert incidents[0].severity == "high"
    assert "evidence_or_provenance" in incidents[0].suggested_harness_fix


def test_audit_detects_overharnessing_when_fluid_mode_asks_too_many_questions():
    from brain.v5.audit import audit_trace_events
    from brain.v5.trace import TraceEvent

    events = [
        TraceEvent(
            event_id="event-1",
            session_id="s1",
            topic_id="fqhe",
            event_type="brief_built",
            risk_level="fluid",
            payload={"max_questions": 1},
        )
    ]
    for index in range(3):
        events.append(
            TraceEvent(
                event_id=f"event-q{index}",
                session_id="s1",
                topic_id="fqhe",
                event_type="question_asked",
                risk_level="fluid",
                payload={"question_id": f"q{index}"},
            )
        )

    incidents = audit_trace_events(events)

    assert len(incidents) == 1
    assert incidents[0].violation_kind == "over_harnessing"
    assert incidents[0].change_direction == "loosen"
    assert "fluid" in incidents[0].observed_behavior
