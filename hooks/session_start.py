"""AITP SessionStart hook — inject skill based on topic stage/posture.

Runs when a new session starts. Reads the active topic's state and prints
a stage/posture-aware skill injection instruction for the agent to follow.
"""

from __future__ import annotations

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


def _record_session_start(topic_root: Path, topic_slug: str, stage: str, posture: str, subplane: str = "") -> str:
    """Record a new session to runtime/sessions.md. Returns the session ID."""
    sid = uuid.uuid4().hex[:12]
    now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M")
    stage_info = f"{stage}/{posture}" + (f"/{subplane}" if subplane else "")

    # Write session marker
    marker = topic_root / "runtime" / ".current_session"
    marker.write_text(f"{sid}\n{now}", encoding="utf-8")

    # Append to sessions log
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


def main():
    workspace = _find_workspace_root()

    if _hooks_disabled(workspace):
        return

    topics_root = _find_topics_root()

    if not topics_root:
        config_path = os.path.join(workspace, ".aitp_config.json")
        print("AITP: No topics root configured. This is a first run in this workspace.")
        print("AITP: MANDATORY — read and follow skills/skill-init.md before continuing.")
        print(f"AITP: Workspace root detected: {workspace}")
        print(f"AITP: Config will be saved to: {config_path}")
        print("AITP: Use AskUserQuestion to ask the user where to store research topics.")
        return

    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        print("AITP: No active topic found. Start one with aitp_bootstrap_topic.")
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

    subplane_info = f", subplane: {snapshot.l3_subplane}" if snapshot.l3_subplane else ""
    print(
        f"AITP: Active topic '{topic_slug}' "
        f"(stage: {snapshot.stage}, posture: {snapshot.posture}, gate: {snapshot.gate_status}{subplane_info})."
    )
    if snapshot.required_artifact_path:
        print(f"AITP: Fill {snapshot.required_artifact_path} before advancing.")
    print(f"AITP: MANDATORY — read and follow skills/{snapshot.skill}.md before continuing.")

    # Record session
    sid = _record_session_start(
        root, topic_slug, snapshot.stage, snapshot.posture,
        subplane=snapshot.l3_subplane,
    )
    print(f"AITP: Session {sid} started. Recorded to runtime/sessions.md.")

    # Progressive-disclosure tool catalog with integration patterns.
    # Pattern A: load on demand  |  Pattern B: invoke at checkpoint  |  Pattern C: already in skill
    posture_key = snapshot.l3_subplane or snapshot.posture
    catalog = get_tool_catalog(snapshot.stage, posture_key)
    if catalog:
        pattern_a = [(n, d) for n, d, p in catalog if p == "A"]
        pattern_b = [(n, d) for n, d, p in catalog if p == "B"]
        pattern_c = [(n, d) for n, d, p in catalog if p == "C"]
        if pattern_b:
            print("AITP: INVOKE at checkpoint (Pattern B — load before discussion rounds):")
            for name, desc in pattern_b:
                print(f"  - {name} — {desc}")
        if pattern_a:
            print("AITP: Available on demand (Pattern A — load with Skill or ToolSearch when needed):")
            for name, desc in pattern_a:
                print(f"  - {name} — {desc}")
        if pattern_c:
            print("AITP: Already embedded in current skill (Pattern C):")
            for name, desc in pattern_c:
                print(f"  - {name} — {desc}")

    # Pattern B explicit invoke instructions
    b_instructions = get_pattern_b_instructions(snapshot.stage, posture_key)
    for tool_name, instruction in b_instructions:
        print(f"AITP: PATTERN-B [{tool_name}]: {instruction}")


if __name__ == "__main__":
    main()
