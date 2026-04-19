"""AITP SessionStart hook — inject skill based on topic status.

Runs when a new session starts. Reads the active topic's state and prints
a skill injection instruction for the agent to follow.
"""

from __future__ import annotations

import json
import os
import re
import sys


def _find_topics_root() -> str | None:
    """Find the topics root directory by walking up from cwd."""
    cwd = os.getcwd()
    for _ in range(5):
        candidate = os.path.join(cwd, "topics")
        if os.path.isdir(candidate):
            return os.path.dirname(candidate)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    # Check environment variable
    return os.environ.get("AITP_TOPICS_ROOT")


def _parse_frontmatter(path: str) -> dict:
    """Parse YAML frontmatter from a Markdown file (minimal parser)."""
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


def _find_active_topic(topics_root: str) -> str | None:
    """Find the most recently updated topic."""
    topics_dir = os.path.join(topics_root, "topics")
    if not os.path.isdir(topics_dir):
        return None
    best_slug = None
    best_time = ""
    for entry in os.listdir(topics_dir):
        state_path = os.path.join(topics_dir, entry, "state.md")
        if os.path.isfile(state_path):
            fm = _parse_frontmatter(state_path)
            updated = fm.get("updated_at", "")
            if updated > best_time:
                best_time = updated
                best_slug = entry
    return best_slug


_SKILL_MAP = {
    "new": "skill-explore",
    "sources_registered": "skill-intake",
    "intake_done": "skill-derive",
    "candidate_ready": "skill-validate",
    "validated": "skill-promote",
}


def main():
    topics_root = _find_topics_root()
    if not topics_root:
        print("AITP: No topics root found. Skipping skill injection.")
        return

    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        print("AITP: No active topic found. Start one with aitp_bootstrap_topic.")
        return

    state_path = os.path.join(topics_root, "topics", topic_slug, "state.md")
    fm = _parse_frontmatter(state_path)
    status = fm.get("status", "new")
    skill = _SKILL_MAP.get(status, "skill-continuous")

    print(f"AITP: Active topic '{topic_slug}' (status: {status}).")
    print(f"AITP: Read and follow skills/{skill}.md before continuing.")


if __name__ == "__main__":
    main()
