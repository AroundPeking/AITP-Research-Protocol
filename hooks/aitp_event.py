"""Standalone AITP event recorder — works WITHOUT the MCP server.

Call directly to append events to a topic's runtime/log.md. Used when:
- MCP server is disconnected
- Working via SSH/bash on remote servers
- Recording HPC job submissions, completions, failures

Usage (from any bash/SSH context):
  python3 aitp_event.py <topics_root> <topic_slug> <event_type> <description>

The event is appended to <topics_root>/<topic_slug>/runtime/log.md with timestamp.
If the log doesn't exist, it's created.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_event(topics_root: str, topic_slug: str, event_type: str, description: str = "") -> str:
    """Append an event to the topic's runtime log. Returns the log path."""
    log_path = Path(topics_root) / topic_slug / "runtime" / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        text = log_path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = (
            "---\n"
            f"kind: runtime_log\ntopic_slug: {topic_slug}\n"
            "---\n\n# Runtime Log\n\n## Events\n\n"
        )

    event = f"{event_type}"
    if description:
        event += f": {description}"
    entry = f"\n- {_now()} {event}\n"
    text += entry
    log_path.write_text(text, encoding="utf-8")
    return str(log_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python aitp_event.py <topics_root> <topic_slug> <event_type> [description]")
        print("Example:")
        print("  python aitp_event.py D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics qsgw-headwing-update-librpa L4_job_submit 'Job 1732319 submitted on dongfang'")
        sys.exit(1)

    topics_root = sys.argv[1]
    topic_slug = sys.argv[2]
    event_type = sys.argv[3]
    description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""

    path = record_event(topics_root, topic_slug, event_type, description)
    print(f"Recorded: {event_type} → {path}")
