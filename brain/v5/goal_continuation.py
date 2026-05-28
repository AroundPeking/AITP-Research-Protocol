"""Goal continuation and audit packet surfaces.

Write local audit packets so that future agents can read the filesystem
and understand what was done, what passed, what's blocking, and what to
do next — without relying on chat history.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from brain.v5.paths import WorkspacePaths


def write_goal_continuation(
    ws: WorkspacePaths,
    *,
    objective: str,
    changed_files: list[str] | None = None,
    tests_run: list[str] | None = None,
    tests_passed: bool | None = None,
    smoke_commands: list[str] | None = None,
    smoke_passed: bool | None = None,
    readiness_outcome: dict[str, Any] | None = None,
    next_actions: list[str] | None = None,
    trust_boundary: str | None = None,
    blocking_backlog: list[str] | None = None,
    notes: str | None = None,
    session_id: str | None = None,
    commit_ref: str | None = None,
) -> dict[str, Any]:
    surface_dir = ws.root / "surfaces" / "goal_continuation"
    surface_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%f")
    packet_id = f"goal-continuation-{now}"
    packet = _build_packet(
        packet_id=packet_id,
        objective=objective,
        changed_files=changed_files or [],
        tests_run=tests_run or [],
        tests_passed=tests_passed,
        smoke_commands=smoke_commands or [],
        smoke_passed=smoke_passed,
        readiness_outcome=readiness_outcome,
        next_actions=next_actions or [],
        trust_boundary=trust_boundary or "",
        blocking_backlog=blocking_backlog or [],
        notes=notes or "",
        session_id=session_id or "",
        commit_ref=commit_ref or "",
    )
    json_path = surface_dir / f"{packet_id}.json"
    md_path = surface_dir / f"{packet_id}.md"
    json_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_md(packet), encoding="utf-8")
    _update_latest(surface_dir, packet_id, json_path, md_path)
    return {
        "kind": "goal_continuation_packet",
        "packet_id": packet_id,
        "files": {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(surface_dir / "latest.json"),
            "latest_markdown": str(surface_dir / "latest.md"),
        },
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
        "truth_source": False,
    }


def read_latest_goal_continuation(ws: WorkspacePaths) -> dict[str, Any] | None:
    latest_path = ws.root / "surfaces" / "goal_continuation" / "latest.json"
    if not latest_path.exists():
        return None
    return json.loads(latest_path.read_text(encoding="utf-8"))


def list_goal_continuations(ws: WorkspacePaths) -> list[dict[str, Any]]:
    surface_dir = ws.root / "surfaces" / "goal_continuation"
    if not surface_dir.exists():
        return []
    packets = []
    for p in sorted(surface_dir.glob("goal-continuation-*.json")):
        try:
            packets.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return packets


def _build_packet(
    *,
    packet_id: str,
    objective: str,
    changed_files: list[str],
    tests_run: list[str],
    tests_passed: bool | None,
    smoke_commands: list[str],
    smoke_passed: bool | None,
    readiness_outcome: dict[str, Any] | None,
    next_actions: list[str],
    trust_boundary: str,
    blocking_backlog: list[str],
    notes: str,
    session_id: str,
    commit_ref: str,
) -> dict[str, Any]:
    return {
        "kind": "goal_continuation_packet",
        "packet_id": packet_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "commit_ref": commit_ref,
        "objective": objective,
        "changed_files": changed_files,
        "verification": {
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "smoke_commands": smoke_commands,
            "smoke_passed": smoke_passed,
        },
        "readiness_outcome": _compact_readiness(readiness_outcome),
        "next_actions": next_actions,
        "trust_boundary": trust_boundary,
        "blocking_backlog": blocking_backlog,
        "notes": notes,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _compact_readiness(outcome: dict[str, Any] | None) -> dict[str, Any]:
    if not outcome:
        return {}
    return {
        "completion_status": str(outcome.get("completion_status") or ""),
        "blocking_gaps": list(outcome.get("blocking_gaps") or []),
        "can_update_claim_trust": bool(outcome.get("can_update_claim_trust") is True),
        "can_update_kernel_state": bool(outcome.get("can_update_kernel_state") is True),
        "semantic_lossless_proven": bool(outcome.get("semantic_lossless_proven") is True),
    }


def _render_md(packet: dict[str, Any]) -> str:
    lines = [
        f"# Goal Continuation: {packet['packet_id']}\n",
        f"\n**Timestamp:** {packet['timestamp']}",
        f"\n**Session:** {packet['session_id'] or 'unknown'}",
        f"\n**Commit:** {packet['commit_ref'] or 'unknown'}\n",
        f"\n## Objective\n\n{packet['objective']}\n",
    ]
    changed = packet.get("changed_files") or []
    if changed:
        lines.append("\n## Changed Files\n")
        for f in changed:
            lines.append(f"- `{f}`")
        lines.append("")
    v = packet.get("verification") or {}
    lines.append("\n## Verification\n")
    tests = v.get("tests_run") or []
    if tests:
        lines.append(f"\nTests run: {', '.join(tests)}")
    lines.append(f"\nTests passed: {v.get('tests_passed')}")
    smokes = v.get("smoke_commands") or []
    if smokes:
        lines.append(f"\nSmoke commands: {', '.join(smokes)}")
    lines.append(f"\nSmoke passed: {v.get('smoke_passed')}")
    r = packet.get("readiness_outcome") or {}
    if r:
        lines.append("\n## Readiness Outcome\n")
        lines.append(f"\n- completion_status: `{r.get('completion_status', '')}`")
        lines.append(f"\n- blocking_gaps: {r.get('blocking_gaps', [])}")
        lines.append(f"\n- can_update_claim_trust: `{r.get('can_update_claim_trust')}`")
        lines.append(f"\n- semantic_lossless_proven: `{r.get('semantic_lossless_proven')}`")
    next_acts = packet.get("next_actions") or []
    if next_acts:
        lines.append("\n## Next Actions\n")
        for a in next_acts:
            lines.append(f"- {a}")
        lines.append("")
    trust = packet.get("trust_boundary") or ""
    if trust:
        lines.append(f"\n## Trust Boundary\n\n{trust}\n")
    backlog = packet.get("blocking_backlog") or []
    if backlog:
        lines.append("\n## Blocking Backlog\n")
        for b in backlog:
            lines.append(f"- {b}")
        lines.append("")
    notes = packet.get("notes") or ""
    if notes:
        lines.append(f"\n## Notes\n\n{notes}\n")
    lines.append("\n---\n*This is an orientation-only surface. Do not update claim trust or kernel state from it.*\n")
    return "".join(lines)


def _update_latest(
    surface_dir: Path,
    packet_id: str,
    json_path: Path,
    md_path: Path,
) -> None:
    latest_json = surface_dir / "latest.json"
    latest_md = surface_dir / "latest.md"
    if latest_json.exists():
        latest_json.unlink()
    if latest_md.exists():
        latest_md.unlink()
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
