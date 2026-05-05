"""Observability: JSONL event logging for AITP sessions."""
from __future__ import annotations
from pathlib import Path
import json


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def log_event(topic_root: Path, category: str, action: str, status: str = "completed",
              phase: str = "", plan: str = "", detail: str = ""):
    """Append a structured JSONL event to the topic's observability log."""
    obs_dir = topic_root / "runtime" / "observability"
    obs_dir.mkdir(parents=True, exist_ok=True)

    # Per-session event log
    import os
    session_id = os.environ.get("AITP_SESSION_ID", _now_iso().replace(":", "-")[:19])
    session_path = obs_dir / f"{session_id}.jsonl"

    event = {
        "timestamp": _now_iso(),
        "session_id": session_id,
        "category": category,
        "action": action,
        "status": status,
        "phase": phase,
        "plan": plan,
        "detail": detail,
    }
    with open(session_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    # Update current-session pointer
    current = {
        "session_id": session_id,
        "last_event": _now_iso(),
        "event_count": _count_events(session_path),
    }
    current_path = obs_dir / "current-session.json"
    current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _count_events(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").strip().split("\n"))


def recent_events(topic_root: Path, limit: int = 10) -> list[dict]:
    """Return the most recent events from the current session."""
    obs_dir = topic_root / "runtime" / "observability"
    current_path = obs_dir / "current-session.json"
    if not current_path.exists():
        return []
    current = json.loads(current_path.read_text(encoding="utf-8"))
    session_path = obs_dir / f"{current['session_id']}.jsonl"
    if not session_path.exists():
        return []
    lines = session_path.read_text(encoding="utf-8").strip().split("\n")
    return [json.loads(line) for line in lines[-limit:]]
