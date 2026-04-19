"""AITP Stop hook — save progress summary at session end.

Runs when the session ends. Updates state.md with a brief session summary.
"""

from __future__ import annotations

import os
import re
from datetime import datetime


def _parse_frontmatter(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def _find_topics_root() -> str | None:
    cwd = os.getcwd()
    for _ in range(5):
        candidate = os.path.join(cwd, "topics")
        if os.path.isdir(candidate):
            return os.path.dirname(candidate)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return os.environ.get("AITP_TOPICS_ROOT")


def main():
    topics_root = _find_topics_root()
    if not topics_root:
        return

    topics_dir = os.path.join(topics_root, "topics")
    if not os.path.isdir(topics_dir):
        return

    for entry in os.listdir(topics_dir):
        state_path = os.path.join(topics_dir, entry, "state.md")
        if os.path.isfile(state_path):
            # Just update the timestamp
            fm = _parse_frontmatter(state_path)
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            # Append session end marker
            with open(state_path, "a", encoding="utf-8") as f:
                f.write(f"\n## Session ended {now}\n\n")


if __name__ == "__main__":
    main()
