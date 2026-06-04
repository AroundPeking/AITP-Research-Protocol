"""Shared path resolution for legacy AITP CLI commands."""

from __future__ import annotations

import json
import os
from pathlib import Path


FALLBACK_TOPICS_ROOT = str(Path.home() / "aitp-topics")


def default_topics_root() -> str:
    """Return the best available topics root without requiring an env var."""
    env = os.environ.get("AITP_TOPICS_ROOT", "").strip()
    if env:
        return env

    record_path = Path.home() / ".aitp" / "install-record.json"
    if record_path.exists():
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            record = {}
        for inst in record.get("installs", {}).values():
            topics_root = inst.get("variables", {}).get("TOPICS_ROOT", "")
            if topics_root and Path(topics_root).exists():
                return topics_root

    cwd = Path.cwd()
    for base in (cwd, *cwd.parents):
        candidate = base / "research" / "aitp-topics"
        if candidate.exists():
            return str(candidate)

    return FALLBACK_TOPICS_ROOT


def resolve_topic_root(topic_slug: str, topics_root: str | None = None) -> Path:
    """Find a topic, supporting both <root>/<slug> and <root>/topics/<slug>."""
    base = Path(topics_root or default_topics_root())
    for candidate in (base / topic_slug, base / "topics" / topic_slug):
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


def topics_root_path(topics_root: str | None = None) -> Path:
    return Path(topics_root or default_topics_root())
