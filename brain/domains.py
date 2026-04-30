"""Domain detection and skill mapping.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Any, Callable

# Domain-skill mapping: maps domain_id (from domain-manifest files) to the
# AITP skill that encodes its conventions. New domains just add an entry here.
DOMAIN_ID_TO_SKILL: dict[str, str] = {
    "abacus-librpa": "skill-librpa",
    "oh-my-librpa": "skill-librpa",
}

# Legacy slug-based fallback: used when no domain manifest is present.
# Only needed for topics created before the contract-based mechanism.
_SLUG_FALLBACK_PATTERNS: dict[str, str] = {
    "librpa": "skill-librpa",
    "crpa": "skill-librpa",
    "scrpa": "skill-librpa",
    "qsgw": "skill-librpa",
    "gw-topology": "skill-librpa",
}


def _detect_domains_from_contracts(topic_root_path: Path) -> list[str]:
    """Scan topic's contracts/ for domain manifests, return domain_ids.

    Supports two formats:
    1. contracts/domain-manifest.md — AITP native (YAML frontmatter with domain_id)
    2. contracts/domain-manifest.<domain_id>.json — multi-domain convention
    """
    contracts_dir = topic_root_path / "contracts"
    if not contracts_dir.is_dir():
        return []
    domain_ids = []

    # Format 1: domain-manifest.md (AITP native, used by aitp_bind_repo etc.)
    md_path = contracts_dir / "domain-manifest.md"
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if m:
            import yaml
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except Exception:
                fm = {}
            did = fm.get("domain_id")
            if did:
                domain_ids.append(str(did))

    # Format 2: domain-manifest.<domain_id>.json (oh-my-LibRPA multi-domain)
    for manifest_path in contracts_dir.glob("domain-manifest.*.json"):
        stem = manifest_path.stem
        parts = stem.split(".", 1)
        if len(parts) == 2 and parts[0] == "domain-manifest":
            domain_ids.append(parts[1])

    # Deduplicate while preserving order
    seen = set()
    return [d for d in domain_ids if not (d in seen or seen.add(d))]


def _detect_domains_from_state(topic_root_path: Path) -> list[str]:
    """Read the 'domains' field from state.md frontmatter if present."""
    state_path = topic_root_path / "state.md"
    if not state_path.exists():
        return []
    text = state_path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return []
    import yaml
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        return []
    domains = fm.get("domains", [])
    if isinstance(domains, list):
        return [str(d) for d in domains]
    if isinstance(domains, str):
        return [domains]
    return []


def resolve_domain_prerequisites(topic_root_path: Path, topic_slug: str = "") -> list[str]:
    """Return domain skills that must be loaded for the given topic.

    Detection order (first match wins, all sources are merged):
    1. domain-manifest.*.json files in topic's contracts/ directory
    2. 'domains' field in state.md frontmatter
    3. Legacy slug-pattern fallback
    """
    skills = []

    # 1. Contract-based detection (robust, content-driven)
    domain_ids = _detect_domains_from_contracts(topic_root_path)
    for did in domain_ids:
        skill = DOMAIN_ID_TO_SKILL.get(did)
        if skill and skill not in skills:
            skills.append(skill)

    # 2. State frontmatter detection
    state_domains = _detect_domains_from_state(topic_root_path)
    for did in state_domains:
        skill = DOMAIN_ID_TO_SKILL.get(did)
        if skill and skill not in skills:
            skills.append(skill)

    # 3. Legacy slug fallback
    if not skills and topic_slug:
        slug_lower = topic_slug.lower()
        for pattern, skill in _SLUG_FALLBACK_PATTERNS.items():
            if re.search(rf'(?<![a-z]){re.escape(pattern)}(?![a-z])', slug_lower) and skill not in skills:
                skills.append(skill)

    return skills


def topics_dir(topics_root: str | Path) -> Path:
    """Resolve the actual topics directory.

    If topics_root contains a ``topics/`` subdirectory, use it.
    Otherwise treat topics_root itself as the topics directory.
    """
    root = Path(topics_root)
    nested = root / "topics"
    return nested if nested.is_dir() else root


def validate_topic_slug(topic_slug: str) -> str:
    """Reject path-traversal, absolute, multi-component, or empty slugs."""
    slug = topic_slug.strip()
    if not slug:
        raise ValueError("topic_slug must be non-empty")
    pure = PurePath(slug)
    if pure.is_absolute():
        raise ValueError("topic_slug must be relative, got absolute path")
    if any(part in {"..", "."} for part in pure.parts):
        raise ValueError("topic_slug contains unsafe path traversal")
    if len(pure.parts) != 1:
        raise ValueError("topic_slug must be a single path component")
    return slug


def topic_root(topics_root: str | Path, topic_slug: str) -> Path:
    """Resolve the canonical directory for a single topic."""
    safe_slug = validate_topic_slug(topic_slug)
    root = topics_dir(topics_root) / safe_slug
    if not root.is_dir():
        raise FileNotFoundError(f"Topic not found: {safe_slug}")
    return root

