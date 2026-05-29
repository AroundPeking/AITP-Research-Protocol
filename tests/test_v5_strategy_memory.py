from __future__ import annotations

import json
from pathlib import Path


def _setup_topic(tmp_path: Path):
    from brain.v5.workspace import bind_session, create_topic, init_workspace

    ws = init_workspace(tmp_path / "ws")
    create_topic(ws, "qsgw-headwing-update-librpa", context_id="librpa", title="QSGW head-wing")
    bind_session(
        ws,
        "qsgw-session",
        topic_id="qsgw-headwing-update-librpa",
        context_id="librpa",
    )
    return ws


def test_record_strategy_memory_writes_run_local_jsonl(tmp_path):
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.strategy_memory import record_strategy_memory

    ws = _setup_topic(tmp_path)

    memory = record_strategy_memory(
        ws,
        topic_id="qsgw-headwing-update-librpa",
        run_id="run-20260528-qsgw-dual-lane",
        strategy_type="scope_control",
        outcome="helped",
        lesson="Keep final lane and diagnostic lane separated for group meeting plots.",
        next_time_rule="Use final-only TSVs for paper claims; diagnostic plots must carry diagnostic/human-assumption labels.",
        scope="BN/MgO/Si QSGW head-wing reporting",
        source_refs=["final_output_profile:qsgw-headwing-dual-lane-v1"],
    )

    path = ws.topic_dir("qsgw-headwing-update-librpa") / "L3" / "runs" / "run-20260528-qsgw-dual-lane" / "strategy_memory.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    assert rows[-1]["memory_id"] == memory.memory_id
    assert rows[-1]["strategy_type"] == "scope_control"
    assert memory.can_update_claim_trust is False
    assert require_valid_public_surface("strategy_memory_record", {"ok": True, **memory.__dict__})


def test_execution_brief_exposes_strategy_memory_for_topic(tmp_path):
    from brain.v5.brief import build_execution_brief
    from brain.v5.strategy_memory import record_strategy_memory

    ws = _setup_topic(tmp_path)
    record_strategy_memory(
        ws,
        topic_id="qsgw-headwing-update-librpa",
        run_id="run-20260528-qsgw-dual-lane",
        strategy_type="verification_guardrail",
        outcome="helped",
        lesson="Do not let contaminated MgO roots enter final comparisons.",
        next_time_rule="Reject /data/home/df_iopcas_bhj/ai-runs/mgo-qsgw-k999-headonly-kconv-20260523-1135 for final lane.",
        scope="MgO root provenance",
    )

    brief = build_execution_brief(ws, "qsgw-session")
    strategy = brief["known_context"]["strategy_memory"]

    assert strategy["present"] is True
    assert strategy["items"][0]["strategy_type"] == "verification_guardrail"
    assert "contaminated MgO" in strategy["items"][0]["lesson"]
    assert strategy["can_update_claim_trust"] is False


def test_strategy_memory_cli_mcp_and_runtime_surface(tmp_path, capsys):
    from brain.v5.cli import main
    from brain.v5.mcp_tools import aitp_v5_record_strategy_memory
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.runtime_entrypoints import runtime_entrypoints

    ws = _setup_topic(tmp_path)

    assert main(
        [
            "--base",
            str(ws.base),
            "strategy",
            "memory",
            "record",
            "--topic",
            "qsgw-headwing-update-librpa",
            "--run",
            "run-20260528-qsgw-dual-lane",
            "--type",
            "resource_plan",
            "--outcome",
            "helped",
            "--lesson",
            "Read remote status and summaries only on dongfang login nodes.",
            "--next-time-rule",
            "Do not run numerical workloads on the login node.",
            "--scope",
            "remote QSGW monitoring",
        ]
    ) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    mcp_payload = aitp_v5_record_strategy_memory(
        str(ws.base),
        topic_id="qsgw-headwing-update-librpa",
        run_id="run-20260528-qsgw-dual-lane",
        strategy_type="resource_plan",
        outcome="helped",
        lesson="Read remote status and summaries only on dongfang login nodes.",
        next_time_rule="Do not run numerical workloads on the login node.",
        scope="remote QSGW monitoring",
    )

    assert require_valid_public_surface("strategy_memory_record", cli_payload) == cli_payload
    assert require_valid_public_surface("strategy_memory_record", mcp_payload) == mcp_payload
    assert runtime_entrypoints()["record_strategy_memory"] == {
        "cli": "aitp-v5 strategy memory record <args>",
        "mcp": "aitp_v5_record_strategy_memory",
        "surface": "strategy_memory_record",
    }
