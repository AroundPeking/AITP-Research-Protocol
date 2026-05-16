"""Markdown plus YAML frontmatter persistence for AITP v5."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml


def read_md(path: str | Path) -> tuple[dict[str, Any], str]:
    """Read a Markdown file with optional YAML frontmatter."""

    p = Path(path)
    if not p.exists():
        return {}, ""
    text = p.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip("\n")
            return dict(fm), body
    return {}, text


def render_md(frontmatter: dict[str, Any], body: str) -> str:
    """Render frontmatter and body to Markdown text."""

    yaml_text = yaml.safe_dump(
        dict(frontmatter),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    clean_body = body.lstrip("\n")
    return f"---\n{yaml_text}\n---\n{clean_body}"


def write_text_atomic(path: str | Path, text: str) -> None:
    """Atomically write text using os.replace."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(p.parent),
        delete=False,
        newline="\n",
    ) as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, p)


def write_md(path: str | Path, frontmatter: dict[str, Any], body: str) -> None:
    """Write a Markdown file with YAML frontmatter."""

    write_text_atomic(path, render_md(frontmatter, body))
