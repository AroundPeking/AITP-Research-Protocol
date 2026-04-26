"""AITP Stop hook — save progress summary at session end.

Only updates the active topic (via .current_topic marker or most-recent),
not every topic in the tree. Records session end in runtime/log.md and
updates state.md updated_at timestamp atomically.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_utils import (
    _atomic_write_text,
    _find_active_topic,
    _find_topics_root,
    _find_workspace_root,
    _hooks_disabled,
    _parse_md,
    _render_md,
)


def stop_for_topic(topics_root: str) -> None:
    from brain.state_model import topics_dir
    td = topics_dir(topics_root)
    slug = _find_active_topic(topics_root)
    if not slug:
        return

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    now_short = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M")
    root = Path(td) / slug

    # Update state.md updated_at atomically
    state_path = root / "state.md"
    if state_path.exists():
        fm, body = _parse_md(state_path)
        fm["updated_at"] = now
        fm["last_session_ended"] = now
        _atomic_write_text(state_path, _render_md(fm, body))

    # Record session end in sessions.md
    marker = root / "runtime" / ".current_session"
    if marker.exists():
        sid = marker.read_text(encoding="utf-8").strip().split("\n")[0]
        sessions_path = root / "runtime" / "sessions.md"
        if sessions_path.exists():
            text = sessions_path.read_text(encoding="utf-8")
            # Replace the open-ended line for this session
            old_line = f"- {sid} | start:"
            for line in text.splitlines():
                if line.startswith(old_line) and "| end: —" in line:
                    text = text.replace(line, line.replace("| end: —", f"| end: {now_short}"))
                    break
            sessions_path.write_text(text, encoding="utf-8")
        marker.unlink(missing_ok=True)

    # Append session-end event to runtime log
    log_path = root / "runtime" / "log.md"
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Topic Log\n\n## Events\n"
    if not log_text.endswith("\n"):
        log_text += "\n"
    _atomic_write_text(log_path, log_text + f"- {now} session ended\n")


def _hooks_disabled(workspace: str) -> bool:
    """Check if hooks are explicitly disabled via env var or config."""
    if os.environ.get("AITP_HOOKS", "").lower() in ("off", "0", "false", "no"):
        return True
    config = _read_aitp_config(workspace)
    return not config.get("hooks_enabled", True)


def main():
    workspace = _find_workspace_root()
    if _hooks_disabled(workspace):
        return
    topics_root = _find_topics_root()
    if not topics_root:
        return
    stop_for_topic(topics_root)


if __name__ == "__main__":
    main()
