from __future__ import annotations

from argparse import Namespace


def test_default_topics_root_discovers_workspace_layout(tmp_path, monkeypatch):
    from brain.cli import paths

    home = tmp_path / "home"
    home.mkdir()
    workspace = tmp_path / "workspace"
    topics_root = workspace / "research" / "aitp-topics"
    topics_root.mkdir(parents=True)

    monkeypatch.delenv("AITP_TOPICS_ROOT", raising=False)
    monkeypatch.setattr(paths.Path, "home", classmethod(lambda cls: home))
    monkeypatch.chdir(workspace)

    assert paths.default_topics_root() == str(topics_root)


def test_source_add_records_l3_supplemental_source(tmp_path, monkeypatch):
    from brain.cli.commands import source

    topics_root = tmp_path / "aitp-topics"
    topic_root = topics_root / "demo"
    monkeypatch.setenv("AITP_TOPICS_ROOT", str(topics_root))
    source._write_md(
        topic_root / "state.md",
        {"stage": "L3", "lane": "code_method"},
        "# State\n",
    )

    result = source.cmd_source_add(
        Namespace(
            topic="demo",
            id="new-paper",
            title="New Paper",
            path="",
            url="",
            repo="",
            branch="",
            commit="",
            type="paper",
            role="direct_dependency",
            notes="",
        )
    )

    assert result == 0
    fm, _ = source._parse_md(topic_root / "L0" / "sources" / "new-paper" / "source.md")
    assert fm["registered_from_stage"] == "L3"
    assert "[L3] Registered source: new-paper" in (topic_root / "research.md").read_text(encoding="utf-8")


def test_v5_native_mcp_exposes_legacy_friendly_discovery_aliases():
    from brain.v5.native_mcp import _TOOLS

    assert "aitp_list_topics" in _TOOLS
    assert "aitp_get_execution_brief" in _TOOLS
    assert "aitp_bootstrap_topic" in _TOOLS
