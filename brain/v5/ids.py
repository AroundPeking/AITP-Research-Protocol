"""Stable identifier helpers for AITP v5 records."""

from __future__ import annotations

import hashlib
import re


def slugify(value: str, *, fallback: str = "untitled", max_length: int = 80) -> str:
    """Return a conservative ASCII slug."""

    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not text:
        text = fallback
    return text[:max_length].strip("-") or fallback


def short_hash(value: str, length: int = 10) -> str:
    """Return a deterministic short hash for IDs tied to external state."""

    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def prefixed_id(prefix: str, value: str, *, max_slug: int = 48) -> str:
    """Create a readable stable ID from a prefix and value."""

    slug = slugify(value, fallback=prefix, max_length=max_slug)
    digest = short_hash(f"{prefix}:{value}", 8)
    return f"{prefix}-{slug}-{digest}"
