"""State management for AITP CLI — authoritative source for all topic state operations.

Provides:
  - current_stage / current_activity  — read topic state from state.md
  - validate_state_transition          — enforce legal stage transitions
  - advance_stage                     — atomically update stage with validation
  - atomic_write                      — crash-safe file writes
  - load_state / save_state            — frontmatter read/write

All state is filesystem-backed. No database, no cache, no in-memory state.
The same logic is used by CLI, MCP tools, and hooks.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Stage transition validation ──────────────────────────────────────────

VALID_TRANSITIONS: dict[str, list[str]] = {
    "L0":  ["L1"],
    "L1":  ["L3"],
    "L3":  ["L4", "L1"],
    "L4":  ["L3", "L1", "promotion"],
    "promotion": ["L2"],
}


def validate_state_transition(
    topic_root: Path, next_stage: str
) -> tuple[bool, str]:
    """Check whether advancing from the current stage to *next_stage* is allowed.

    Returns (ok, reason).
    """
    current = current_stage(topic_root)
    allowed = VALID_TRANSITIONS.get(current, [])
    if next_stage not in allowed:
        return False, (
            f"Cannot advance from {current} to {next_stage}. "
            f"Allowed transitions from {current}: {allowed or 'none'}."
        )
    return True, ""


def current_stage(topic_root: Path) -> str:
    """Read the current stage from the topic's state.md frontmatter."""
    fm, _ = load_state(topic_root)
    return fm.get("stage", "L0")


def current_l3_activity(topic_root: Path) -> str:
    fm, _ = load_state(topic_root)
    return fm.get("l3_activity", "")


def current_gate_status(topic_root: Path) -> tuple[str, bool]:
    """Return (gate_status, has_valid_override)."""
    fm, _ = load_state(topic_root)
    gs = fm.get("gate_status", "blocked_missing_artifact")
    override = fm.get("gate_override", False)
    scope = fm.get("gate_override_scope", "")
    has_override = bool(override and scope in ("current_gate", "this_session"))
    return gs, has_override


def advance_stage(topic_root: Path, next_stage: str) -> None:
    """Atomically advance the topic to *next_stage*, validated."""
    ok, msg = validate_state_transition(topic_root, next_stage)
    if not ok:
        raise InvalidStateTransition(msg)
    fm, body = load_state(topic_root)
    current = fm.get("stage", "L0")
    fm["stage"] = next_stage
    fm["posture"] = _posture_for_stage(next_stage)
    fm["updated_at"] = _now_iso()
    save_state(topic_root, fm, body)
    _append_log(topic_root, f"advanced from {current} to {next_stage}")


def retreat_stage(topic_root: Path, target_stage: str, reason: str = "") -> None:
    """Atomically retreat the topic to *target_stage*, validated.

    Preserves all artifacts; only changes the stage marker and posture.
    Records retreat metadata for audit trail.
    """
    ok, msg = validate_state_transition(topic_root, target_stage)
    if not ok:
        raise InvalidStateTransition(msg)
    fm, body = load_state(topic_root)
    current = fm.get("stage", "L0")
    fm["stage"] = target_stage
    fm["posture"] = _posture_for_stage(target_stage)
    fm["retreated_from"] = current
    fm["retreat_reason"] = reason
    fm["retreated_at"] = _now_iso()
    fm["updated_at"] = _now_iso()
    fm["gate_status"] = "blocked_missing_artifact"
    save_state(topic_root, fm, body)
    _append_log(topic_root,
        f"retreated from {current} to {target_stage}"
        + (f": {reason}" if reason else ""))


def _posture_for_stage(stage: str) -> str:
    _MAP = {"L0": "discover", "L1": "read", "L3": "derive", "L4": "verify",
            "promotion": "promote", "L2": "knowledge"}
    return _MAP.get(stage, "discover")


# ── Path resolution ──────────────────────────────────────────────────────

def resolve_topic_root(topics_root: str, topic_slug: str) -> Path:
    """Find a topic's directory, preferring state.md-bearing paths.

    Checks <topics_root>/<slug> first, then <topics_root>/topics/<slug>.
    This is the canonical path resolver used by both CLI and MCP.
    """
    base = Path(topics_root)
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


# ── State file I/O ───────────────────────────────────────────────────────

def _parse_md_local(path: Path) -> tuple[dict[str, Any], str]:
    """Local YAML frontmatter parser — no external import dependency."""
    import yaml
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                fm = {}
            return fm, parts[2] if len(parts) > 2 else ""
    return {}, text


def _write_md_local(path: Path, fm: dict[str, Any], body: str) -> None:
    """Write YAML frontmatter + body to a Markdown file."""
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    lines.append(yaml.dump(fm, default_flow_style=False, allow_unicode=True).rstrip())
    lines.append("---")
    lines.append(body.lstrip("\n"))
    atomic_write(path, "\n".join(lines))


def load_state(topic_root: Path) -> tuple[dict[str, Any], str]:
    """Read state.md from a topic directory. Returns (frontmatter, body)."""
    state_path = topic_root / "state.md"
    if not state_path.exists():
        return _default_state(), ""
    return _parse_md_local(state_path)


def save_state(topic_root: Path, fm: dict[str, Any], body: str) -> None:
    """Atomically write state.md."""
    state_path = topic_root / "state.md"
    _write_md_local(state_path, fm, body)


def _default_state() -> dict[str, Any]:
    return {
        "stage": "L0",
        "posture": "discover",
        "lane": "unspecified",
        "gate_status": "blocked_missing_artifact",
        "protocol_version": "v1.0",
        "memory_gate_enabled": False,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Atomic write ─────────────────────────────────────────────────────────

def atomic_write(path: Path, content: str) -> None:
    """Write *content* to *path* atomically via tempfile + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    try:
        os.write(fd, content.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)


def atomic_write_md(
    path: Path,
    fm: dict[str, Any],
    body: str,
    write_md_fn,
) -> None:
    """Compatibility wrapper — delegates to the project's _write_md function
    then adds atomicity by writing to a temp file first."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    os.close(fd)
    tmp_path = Path(tmp)
    write_md_fn(tmp_path, fm, body)
    content = tmp_path.read_text(encoding="utf-8")
    tmp_path.unlink()
    atomic_write(path, content)


# ── Logging ──────────────────────────────────────────────────────────────

def _append_log(topic_root: Path, event: str) -> None:
    """Append a timestamped event to runtime/log.md."""
    log_path = topic_root / "runtime" / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {_now_iso()} CLI: {event}\n"
    if log_path.exists():
        atomic_write(log_path, log_path.read_text(encoding="utf-8") + line)
    else:
        atomic_write(log_path, f"# Topic Log\n\n## Events\n\n{line}")


# ── Exceptions ───────────────────────────────────────────────────────────

class InvalidStateTransition(ValueError):
    """Raised when a stage transition is not allowed."""
