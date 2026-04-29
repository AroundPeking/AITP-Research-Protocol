"""AITP SessionStart hook — inject using-aitp skill content into agent context.

Runs when a new session starts. Reads the active topic's state, then:
1. Reads the full using-aitp gateway skill (with Red Flags table)
2. Builds a context injection with topic state summary
3. Outputs platform-appropriate JSON for Claude Code / Cursor / Copilot CLI

This is the Superpowers pattern: the hook injects skill CONTENT, not just a filename
to read. The agent sees the Red Flags table and protocol rules before its first response.

Diagnostic output goes to stderr so stdout contains only the JSON injection.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_utils import (
    _find_active_topic,
    _find_topics_root,
    _find_workspace_root,
    _hooks_disabled,
    _parse_md,
)

# Path to the gateway skill that all sessions must inject
_GATEWAY_SKILL_REL = "deploy/templates/claude-code/using-aitp.md"


def _read_gateway_skill() -> str:
    """Read the full using-aitp gateway skill content."""
    skill_path = Path(__file__).resolve().parents[1] / _GATEWAY_SKILL_REL
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return ""


def _escape_for_json(s: str) -> str:
    """JSON-escape a string, handling the characters that matter."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def _build_context_injection(
    skill_content: str,
    topic_slug: str,
    stage: str,
    posture: str,
    gate_status: str,
    subplane: str,
    topics_root: str,
    domain_constraints: dict | None = None,
) -> str:
    """Build the context block injected into the agent's session."""
    subplane_info = f", subplane: {subplane}" if subplane else ""
    status_line = (
        f"Active topic: {topic_slug} | "
        f"stage: {stage} | posture: {posture} | "
        f"gate: {gate_status}{subplane_info}"
    )

    domain_block = ""
    if domain_constraints:
        rules = domain_constraints.get("hard_rules", [])
        lanes = domain_constraints.get("workflow_lanes", [])
        smoke = domain_constraints.get("smoke_test", [])
        if rules or lanes or smoke:
            domain_block = "\\n\\n## Domain Constraints (auto-injected)\\n"
            if rules:
                domain_block += "\\n### Hard Rules\\n" + "\\n".join(f"- {r}" for r in rules)
            if lanes:
                domain_block += "\\n\\n### Workflow Lanes\\n" + "\\n".join(f"- {l}" for l in lanes)
            if smoke:
                domain_block += "\\n\\n### Smoke Test\\n" + "\\n".join(f"- {s}" for s in smoke)

    context = (
        "<EXTREMELY_IMPORTANT>\\n"
        "You have AITP superpowers.\\n\\n"
        "**Below is the full content of your 'using-aitp' skill with the AITP protocol.**\\n"
        "For all other skills, use the 'Skill' tool.\\n\\n"
        f"{_escape_for_json(skill_content)}\\n"
        f"{domain_block}\\n"
        "</EXTREMELY_IMPORTANT>\\n\\n"
        f"AITP Runtime: {status_line}\\n"
        f"Topics root: {topics_root}\\n"
    )
    return context


def _record_session_start(
    topic_root: Path, topic_slug: str, stage: str, posture: str, subplane: str = "",
) -> str:
    """Record a new session to runtime/sessions.md. Returns the session ID."""
    sid = uuid.uuid4().hex[:12]
    now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M")
    stage_info = f"{stage}/{posture}" + (f"/{subplane}" if subplane else "")

    marker = topic_root / "runtime" / ".current_session"
    marker.write_text(f"{sid}\n{now}", encoding="utf-8")

    sessions_path = topic_root / "runtime" / "sessions.md"
    if sessions_path.exists():
        text = sessions_path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = (
            "---\n"
            f"kind: session_log\ntopic_slug: {topic_slug}\n"
            "---\n\n"
            "# Session Log\n\n"
            "## Sessions\n\n"
        )
    text += f"- {sid} | start: {now} | end: — | stage: {stage_info}\n"
    sessions_path.write_text(text, encoding="utf-8")
    return sid


def _output_json(context: str) -> None:
    """Output platform-appropriate JSON injection to stdout.

    Claude Code: hookSpecificOutput with hookEventName
    Cursor: additional_context (snake_case)
    Copilot CLI / other: additionalContext (PascalCase)
    """
    if os.environ.get("CURSOR_PLUGIN_ROOT"):
        # Cursor format
        payload = {"additional_context": context}
    elif os.environ.get("CLAUDE_PLUGIN_ROOT") and not os.environ.get("COPILOT_CLI"):
        # Claude Code format
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
    else:
        # Copilot CLI / unknown format
        payload = {"additionalContext": context}

    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()


def main():
    workspace = _find_workspace_root()

    if _hooks_disabled(workspace):
        return

    topics_root = _find_topics_root()

    # Read the gateway skill
    skill_content = _read_gateway_skill()

    if not topics_root:
        config_path = os.path.join(workspace, ".aitp_config.json")
        print("AITP: No topics root configured.", file=sys.stderr)
        print(f"AITP: Workspace root: {workspace}", file=sys.stderr)
        print(f"AITP: Config will be saved to: {config_path}", file=sys.stderr)
        # Inject skill-init guidance even without a topic
        context = (
            "<EXTREMELY_IMPORTANT>\\n"
            f"{_escape_for_json(skill_content)}\\n"
            "</EXTREMELY_IMPORTANT>\\n\\n"
            f"AITP: No topics root configured. Workspace root: {workspace}\\n"
            "AITP: Use AskUserQuestion to ask the user where to store research topics.\\n"
        )
        _output_json(context)
        return

    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        context = (
            "<EXTREMELY_IMPORTANT>\\n"
            f"{_escape_for_json(skill_content)}\\n"
            "</EXTREMELY_IMPORTANT>\\n\\n"
            f"AITP: No active topic found. Topics root: {topics_root}\\n"
            "Use aitp_bootstrap_topic or aitp_list_topics to get started.\\n"
        )
        _output_json(context)
        return

    from brain.state_model import (
        topics_dir, evaluate_l0_stage, evaluate_l1_stage, evaluate_l3_stage,
        evaluate_l4_stage,
        get_tool_catalog, get_pattern_b_instructions,
    )
    td = topics_dir(topics_root)
    root = Path(td) / topic_slug
    fm, _ = _parse_md(root / "state.md")
    stage = str(fm.get("stage", "L1"))

    if stage == "L3":
        snapshot = evaluate_l3_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    elif stage == "L4":
        snapshot = evaluate_l4_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    elif stage == "L0":
        snapshot = evaluate_l0_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    else:
        snapshot = evaluate_l1_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))

    # Build and inject context
    domain_constraints = getattr(snapshot, "domain_constraints", {})
    context = _build_context_injection(
        skill_content,
        topic_slug,
        snapshot.stage,
        snapshot.posture,
        snapshot.gate_status,
        snapshot.l3_subplane,
        str(topics_root),
        domain_constraints,
    )
    _output_json(context)

    # Diagnostic output to stderr
    subplane_info = f", subplane: {snapshot.l3_subplane}" if snapshot.l3_subplane else ""
    print(
        f"AITP: Active topic '{topic_slug}' "
        f"(stage: {snapshot.stage}, posture: {snapshot.posture}, gate: {snapshot.gate_status}{subplane_info}).",
        file=sys.stderr,
    )
    if snapshot.required_artifact_path:
        print(f"AITP: Fill {snapshot.required_artifact_path} before advancing.", file=sys.stderr)
    print(f"AITP: Gateway skill injected via SessionStart hook.", file=sys.stderr)

    # Record session
    sid = _record_session_start(
        root, topic_slug, snapshot.stage, snapshot.posture,
        subplane=snapshot.l3_subplane,
    )
    print(f"AITP: Session {sid} started.", file=sys.stderr)


if __name__ == "__main__":
    main()
