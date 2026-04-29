"""AITP Compact hook — re-inject gateway skill after context compaction.

Runs when context is compacted. Re-injects the full using-aitp skill content
(with Red Flags table) since the agent loses all context during compaction.

This is critical: without re-injection, the agent loses the protocol discipline
after compaction and may start bypassing AITP tools.
"""

from __future__ import annotations

import json
import os
import sys
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

_GATEWAY_SKILL_REL = "deploy/templates/claude-code/using-aitp.md"


def _read_gateway_skill() -> str:
    skill_path = Path(__file__).resolve().parents[1] / _GATEWAY_SKILL_REL
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return ""


def _escape_for_json(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def _output_json(context: str) -> None:
    if os.environ.get("CURSOR_PLUGIN_ROOT"):
        payload = {"additional_context": context}
    elif os.environ.get("CLAUDE_PLUGIN_ROOT") and not os.environ.get("COPILOT_CLI"):
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
    else:
        payload = {"additionalContext": context}

    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()


def main():
    workspace = _find_workspace_root()

    if _hooks_disabled(workspace):
        return

    topics_root = _find_topics_root()
    skill_content = _read_gateway_skill()

    if not topics_root:
        return

    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        return

    from brain.state_model import (
        topics_dir, evaluate_l0_stage, evaluate_l1_stage,
        evaluate_l3_stage, evaluate_l4_stage,
    )
    td = topics_dir(topics_root)
    root = Path(td) / topic_slug
    fm, _ = _parse_md(root / "state.md")
    stage = str(fm.get("stage", "L0"))

    if stage == "L3":
        snapshot = evaluate_l3_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    elif stage == "L4":
        snapshot = evaluate_l4_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    elif stage == "L0":
        snapshot = evaluate_l0_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))
    else:
        snapshot = evaluate_l1_stage(_parse_md, root, lane=fm.get("lane", "unspecified"))

    subplane_info = f", subplane: {snapshot.l3_subplane}" if snapshot.l3_subplane else ""

    # Build re-injection context
    domain_constraints = getattr(snapshot, "domain_constraints", {})
    domain_block = ""
    if domain_constraints:
        rules = domain_constraints.get("hard_rules", [])
        if rules:
            domain_block = "\\n\\n## Domain Constraints (re-injected after compaction)\\n" + "\\n".join(f"- {r}" for r in rules)

    context = (
        "<EXTREMELY_IMPORTANT>\\n"
        "Context was compacted. The AITP protocol is re-injected below.\\n"
        "Re-read the Red Flags table — all entries still apply.\\n\\n"
        f"{_escape_for_json(skill_content)}\\n"
        f"{domain_block}\\n"
        "</EXTREMELY_IMPORTANT>\\n\\n"
        f"AITP: Compaction resume. Topic: {topic_slug} | "
        f"stage: {snapshot.stage} | posture: {snapshot.posture} | "
        f"gate: {snapshot.gate_status}{subplane_info}\\n"
        f"Required skill: skills/{snapshot.skill}.md\\n"
    )
    _output_json(context)

    # Diagnostic
    print(
        f"AITP: Context compacted. Gateway skill re-injected for topic '{topic_slug}' "
        f"(stage: {snapshot.stage}, posture: {snapshot.posture}, gate: {snapshot.gate_status}{subplane_info}).",
        file=sys.stderr,
    )

    # Record compact event
    marker = root / "runtime" / ".current_session"
    if marker.exists():
        now_short = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M")
        sessions_path = root / "runtime" / "sessions.md"
        if sessions_path.exists():
            text = sessions_path.read_text(encoding="utf-8")
            if not text.endswith("\n"):
                text += "\n"
            text += f"  - compacted at {now_short} (stage: {snapshot.stage}/{snapshot.posture})\n"
            sessions_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
