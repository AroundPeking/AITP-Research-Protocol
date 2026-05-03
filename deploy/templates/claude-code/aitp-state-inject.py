"""UserPromptSubmit hook: inject AITP topic dashboard into agent context.

Runs on every user message when an active AITP topic exists.
Must be fast (<50ms).
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aitp_panel import get_active_topic, read_topic_state, render_dashboard


def safe_json_loads(raw_text):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        if "Invalid \\escape" in str(e):
            fixed = raw_text
            fixed = re.sub(r'\\([^"\\/bfnrtu])', r"\\\\\1", fixed)
            fixed = re.sub(r"\\u(?![0-9a-fA-F]{4})", r"\\\\u", fixed)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                return {}
        return {}


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    data = safe_json_loads(raw)
    if not data:
        return 0

    topic_slug = get_active_topic()
    if not topic_slug:
        return 0

    try:
        fm = read_topic_state(topic_slug)
        if not fm:
            return 0

        dashboard = render_dashboard(fm, topic_slug)

        payload = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": dashboard,
            }
        }

        json.dump(payload, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
