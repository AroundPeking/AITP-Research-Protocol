from __future__ import annotations

import json


def _write_legacy_l2(base):
    l2 = base / "research" / "aitp-topics" / "L2"
    (l2 / "entries").mkdir(parents=True)
    (l2 / "graph" / "nodes").mkdir(parents=True)
    (l2 / "graph" / "edges").mkdir(parents=True)
    (l2 / "graph" / "steps").mkdir(parents=True)
    (l2 / "graph" / "towers").mkdir(parents=True)
    (l2 / "index.md").write_text("---\nkind: global_l2_index\n---\n# Global L2\n", encoding="utf-8")
    (l2 / "entries" / "INDEX.md").write_text("# Entries\n", encoding="utf-8")
    (l2 / "entries" / "claim-headwing.md").write_text(
        "---\n"
        "entry_id: claim-headwing\n"
        "role: claim\n"
        "status: verified\n"
        "title: Head-wing formula\n"
        "lane: [formal_theory, code_method]\n"
        "---\n"
        "# Head-wing Formula\n\nThe formula is reusable in the q->0 regime.\n",
        encoding="utf-8",
    )
    (l2 / "entries" / "pitfall-threads.md").write_text(
        "---\n"
        "entry_id: pitfall-threads\n"
        "role: pitfall\n"
        "status: unverified\n"
        "title: Threading pitfall\n"
        "---\n"
        "# Threading Pitfall\n",
        encoding="utf-8",
    )
    (l2 / "graph" / "nodes" / "claim-headwing.md").write_text("# Node\n", encoding="utf-8")
    (l2 / "graph" / "edges" / "e-headwing-pitfall.md").write_text("# Edge\n", encoding="utf-8")
    (l2 / "graph" / "steps" / "step-headwing.md").write_text("# Step\n", encoding="utf-8")
    (l2 / "graph" / "towers" / "tower-screened-interaction.md").write_text("# Tower\n", encoding="utf-8")
    return l2


def test_legacy_l2_obsidian_view_writes_orientation_only_index(tmp_path):
    from brain.v5.legacy_l2_obsidian import write_legacy_l2_obsidian_view
    from brain.v5.markdown import read_md
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.workspace import init_workspace

    ws = init_workspace(tmp_path)
    l2 = _write_legacy_l2(tmp_path)

    payload = write_legacy_l2_obsidian_view(ws, legacy_l2_dir=l2)

    assert require_valid_public_surface("legacy_l2_obsidian_view_bundle", payload) == payload
    assert payload["kind"] == "legacy_l2_obsidian_view_bundle"
    assert payload["memory_entry_count"] == 0
    assert payload["legacy_entry_count"] == 2
    assert payload["graph_counts"]["graph_nodes"] == 1
    assert payload["graph_counts"]["graph_edges"] == 1
    assert payload["graph_counts"]["graph_steps"] == 1
    assert payload["graph_counts"]["graph_towers"] == 1
    assert payload["worklist_file"] == str((tmp_path / ".aitp" / "surfaces" / "legacy_l2_obsidian" / "Legacy L2 Migration Worklist.md"))
    assert payload["migration_work_item_count"] == 6
    assert payload["obsidian_view_maturity"]["status"] == "partial_legacy_views_available"
    assert payload["orientation_only"] is True
    assert payload["can_update_kernel_state"] is False
    overview_fm, overview = read_md(payload["files"]["overview"])
    entries_fm, entries = read_md(payload["files"]["entries_index"])
    graph_fm, graph = read_md(payload["files"]["graph_index"])
    worklist_fm, worklist = read_md(payload["worklist_file"])
    assert overview_fm["truth_source"] is False
    assert entries_fm["view_role"] == "legacy_l2_entries_index"
    assert graph_fm["view_role"] == "legacy_l2_graph_index"
    assert worklist_fm["view_role"] == "legacy_l2_migration_worklist"
    assert "orientation-only" in overview
    assert "claim-headwing" in entries
    assert "pitfall-threads" in entries
    assert "claim-headwing.md" in graph
    assert "e-headwing-pitfall.md" in graph
    assert "step-headwing.md" in graph
    assert "tower-screened-interaction.md" in graph
    assert "legacy_l2_entry:claim-headwing" in worklist
    assert "memory_entry_record" in worklist
    assert "legacy_l2_graph_edge:e-headwing-pitfall" in worklist
    assert "object_relation_record" in worklist
    assert "migrate_legacy_l2_entries_into_memory_records" in overview


def test_legacy_l2_obsidian_view_worklist_uses_full_typed_packet(tmp_path):
    from brain.v5.legacy_l2_obsidian import write_legacy_l2_obsidian_view
    from brain.v5.workspace import init_workspace

    ws = init_workspace(tmp_path)
    l2 = _write_legacy_l2(tmp_path)
    for index in range(2, 121):
        (l2 / "graph" / "steps" / f"s{index:03d}.md").write_text(
            f"# Step {index}\n",
            encoding="utf-8",
        )

    payload = write_legacy_l2_obsidian_view(ws, legacy_l2_dir=l2)
    worklist = (tmp_path / ".aitp" / "surfaces" / "legacy_l2_obsidian" / "Legacy L2 Migration Worklist.md").read_text(
        encoding="utf-8",
    )

    assert payload["migration_work_item_count"] == 125
    assert "legacy_l2_graph_step:s120" in worklist
    assert "legacy_l2_graph_tower:tower-screened-interaction" in worklist
    assert "sensemaking_report_record" in worklist
    assert "review_legacy_l2_steps_for_sensemaking_reports" in payload["next_actions"]


def test_legacy_l2_obsidian_view_cli_mcp_and_runtime_surface(tmp_path, capsys):
    from brain.v5.cli import main
    from brain.v5.mcp_tools import aitp_v5_write_legacy_l2_obsidian_view
    from brain.v5.runtime_entrypoints import runtime_entrypoints

    l2 = _write_legacy_l2(tmp_path)

    assert main([
        "--base",
        str(tmp_path),
        "legacy",
        "l2-obsidian-view",
        "--legacy-l2-dir",
        str(l2),
    ]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    mcp_payload = aitp_v5_write_legacy_l2_obsidian_view(str(tmp_path), legacy_l2_dir=str(l2))

    assert cli_payload["kind"] == "legacy_l2_obsidian_view_bundle"
    assert mcp_payload["kind"] == "legacy_l2_obsidian_view_bundle"
    assert runtime_entrypoints()["legacy_l2_obsidian_view"] == {
        "cli": "aitp-v5 legacy l2-obsidian-view <args>",
        "mcp": "aitp_v5_write_legacy_l2_obsidian_view",
        "surface": "legacy_l2_obsidian_view_bundle",
    }
