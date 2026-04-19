"""AITP Brain MCP Server v2 — Minimal skill-driven research protocol.

Provides ~10 tools for the agent to read/write topic state.
All storage is Markdown with YAML frontmatter. No JSON, no JSONL.

Dependencies: fastmcp, pyyaml
Install: pip install fastmcp pyyaml
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("aitp-brain")


# ---------------------------------------------------------------------------
# Helpers — Markdown + YAML frontmatter I/O
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _topic_root(topics_root: str, topic_slug: str) -> Path:
    root = Path(topics_root) / topic_slug
    if not root.is_dir():
        raise FileNotFoundError(f"Topic not found: {topic_slug}")
    return root


def _parse_md(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    import yaml
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def _write_md(path: Path, fm: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    frontmatter = yaml.dump(fm, default_flow_style=False, allow_unicode=True).strip()
    path.write_text(f"---\n{frontmatter}\n---\n{body}\n", encoding="utf-8")


def _append_section(path: Path, section: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + section + "\n", encoding="utf-8")


def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "untitled"


# ---------------------------------------------------------------------------
# Skill injection logic
# ---------------------------------------------------------------------------

_SKILL_MAP = {
    "new": "skill-explore",
    "sources_registered": "skill-intake",
    "intake_done": "skill-derive",
    "candidate_ready": "skill-validate",
    "validated": "skill-promote",
}

_VALID_STATUSES = set(_SKILL_MAP.keys()) | {"promoted", "complete", "blocked"}


def _infer_status(fm: dict[str, Any], topic_root: Path) -> str:
    explicit = str(fm.get("status") or "").strip()
    if explicit and explicit in _VALID_STATUSES:
        return explicit
    # Infer from filesystem state
    src_dir = topic_root / "L0" / "sources"
    intake_dir = topic_root / "L1" / "intake"
    cand_dir = topic_root / "L3" / "candidates"
    l2_dir = topic_root / "L2" / "canonical"
    if src_dir.is_dir() and list(src_dir.glob("*.md")):
        if intake_dir.is_dir() and list(intake_dir.glob("*.md")):
            if cand_dir.is_dir() and list(cand_dir.glob("*.md")):
                return "candidate_ready"
            return "intake_done"
        return "sources_registered"
    return "new"


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def aitp_get_status(topics_root: str, topic_slug: str) -> dict[str, Any]:
    """Read topic state and return current status, mode, layer, and counts."""
    root = _topic_root(topics_root, topic_slug)
    fm, body = _parse_md(root / "state.md")
    status = _infer_status(fm, root)
    src_dir = root / "L0" / "sources"
    intake_dir = root / "L1" / "intake"
    cand_dir = root / "L3" / "candidates"
    l2_dir = root / "L2" / "canonical"
    return {
        "topic_slug": topic_slug,
        "status": status,
        "mode": fm.get("mode", "explore"),
        "layer": fm.get("layer", "L0"),
        "title": fm.get("title", topic_slug),
        "sources_count": len(list(src_dir.glob("*.md"))) if src_dir.is_dir() else 0,
        "intake_count": len(list(intake_dir.glob("*.md"))) if intake_dir.is_dir() else 0,
        "candidates_count": len(list(cand_dir.glob("*.md"))) if cand_dir.is_dir() else 0,
        "l2_count": len(list(l2_dir.glob("*.md"))) if l2_dir.is_dir() else 0,
        "updated_at": fm.get("updated_at", ""),
    }


@mcp.tool()
def aitp_update_status(
    topics_root: str,
    topic_slug: str,
    status: str | None = None,
    mode: str | None = None,
    layer: str | None = None,
) -> str:
    """Update topic state.md frontmatter fields."""
    root = _topic_root(topics_root, topic_slug)
    state_path = root / "state.md"
    fm, body = _parse_md(state_path)
    if status:
        fm["status"] = status
    if mode:
        fm["mode"] = mode
    if layer:
        fm["layer"] = layer
    fm["updated_at"] = _now()
    _write_md(state_path, fm, body)
    return f"Updated {topic_slug}: status={fm.get('status')}, mode={fm.get('mode')}, layer={fm.get('layer')}"


@mcp.tool()
def aitp_bootstrap_topic(
    topics_root: str,
    topic_slug: str,
    title: str,
    question: str,
) -> str:
    """Create a new topic directory structure with state.md."""
    root = Path(topics_root) / topic_slug
    if root.exists():
        return f"Topic {topic_slug} already exists."
    root.mkdir(parents=True)
    for sub in ["L0/sources", "L1/intake", "L2/canonical", "L3/candidates", "L4/reviews", "runtime"]:
        (root / sub).mkdir(parents=True)
    fm = {
        "topic_slug": topic_slug,
        "title": title,
        "status": "new",
        "mode": "explore",
        "layer": "L0",
        "created_at": _now(),
        "updated_at": _now(),
        "sources_count": 0,
        "candidates_count": 0,
    }
    body = f"# {title}\n\n## Research Question\n{question}\n"
    _write_md(root / "state.md", fm, body)
    return f"Bootstrapped topic {topic_slug} at {root}"


@mcp.tool()
def aitp_register_source(
    topics_root: str,
    topic_slug: str,
    source_id: str,
    source_type: str = "paper",
    title: str = "",
    arxiv_id: str = "",
    fidelity: str = "arxiv_preprint",
    notes: str = "",
) -> str:
    """Register a source in L0. Creates a Markdown file with frontmatter."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(source_id)
    path = root / "L0" / "sources" / f"{slug}.md"
    if path.exists():
        return f"Source {slug} already registered."
    fm = {
        "source_id": slug,
        "type": source_type,
        "title": title or source_id,
        "arxiv_id": arxiv_id,
        "fidelity": fidelity,
        "registered": _now(),
    }
    body = f"# {title or source_id}\n\n{notes}\n" if notes else f"# {title or source_id}\n"
    _write_md(path, fm, body)
    # Update state
    return f"Registered source {slug}"


@mcp.tool()
def aitp_list_sources(topics_root: str, topic_slug: str) -> list[dict[str, Any]]:
    """List all registered sources for a topic."""
    root = _topic_root(topics_root, topic_slug)
    src_dir = root / "L0" / "sources"
    if not src_dir.is_dir():
        return []
    results = []
    for path in sorted(src_dir.glob("*.md")):
        fm, _ = _parse_md(path)
        results.append({"source_id": fm.get("source_id", path.stem), "title": fm.get("title", ""), "type": fm.get("type", ""), "arxiv_id": fm.get("arxiv_id", "")})
    return results


@mcp.tool()
def aitp_record_derivation(
    topics_root: str,
    topic_slug: str,
    derivation_id: str,
    kind: str,
    title: str,
    status: str = "in_progress",
    source: str = "",
    content: str = "",
) -> str:
    """Append a derivation record to L3/derivations.md."""
    root = _topic_root(topics_root, topic_slug)
    deriv_path = root / "L3" / "derivations.md"
    section = (
        f"\n## {title}\n\n"
        f"- id: {derivation_id}\n"
        f"- kind: {kind}\n"
        f"- status: {status}\n"
        f"- source: {source}\n"
        f"- recorded: {_now()}\n\n"
        f"{content}\n"
    )
    _append_section(deriv_path, section)
    return f"Recorded derivation {derivation_id}"


@mcp.tool()
def aitp_submit_candidate(
    topics_root: str,
    topic_slug: str,
    candidate_id: str,
    title: str,
    claim: str,
    evidence: str = "",
    assumptions: str = "",
    validation_criteria: str = "",
) -> str:
    """Submit a candidate finding. Creates L3/candidates/<id>.md."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(candidate_id)
    path = root / "L3" / "candidates" / f"{slug}.md"
    fm = {
        "candidate_id": slug,
        "title": title,
        "status": "submitted",
        "mode": "candidate",
        "created_at": _now(),
        "updated_at": _now(),
    }
    body = (
        f"# {title}\n\n"
        f"## Claim\n{claim}\n\n"
        f"## Evidence\n{evidence}\n\n"
        f"## Assumptions\n{assumptions}\n\n"
        f"## Validation Criteria\n{validation_criteria}\n"
    )
    _write_md(path, fm, body)
    return f"Submitted candidate {slug}"


@mcp.tool()
def aitp_request_promotion(
    topics_root: str,
    topic_slug: str,
    candidate_id: str,
) -> str:
    """Request promotion of a validated candidate to L2."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(candidate_id)
    cand_path = root / "L3" / "candidates" / f"{slug}.md"
    if not cand_path.exists():
        return f"Candidate {slug} not found."
    fm, body = _parse_md(cand_path)
    if fm.get("status") != "validated":
        return f"Candidate {slug} status is '{fm.get('status')}', not 'validated'. Run validation first."
    fm["status"] = "pending_approval"
    fm["promotion_requested"] = _now()
    _write_md(cand_path, fm, body)
    return f"Candidate {slug} pending human approval for L2 promotion."


@mcp.tool()
def aitp_list_candidates(topics_root: str, topic_slug: str) -> list[dict[str, Any]]:
    """List all candidates for a topic."""
    root = _topic_root(topics_root, topic_slug)
    cand_dir = root / "L3" / "candidates"
    if not cand_dir.is_dir():
        return []
    results = []
    for path in sorted(cand_dir.glob("*.md")):
        fm, _ = _parse_md(path)
        results.append({"candidate_id": fm.get("candidate_id", path.stem), "title": fm.get("title", ""), "status": fm.get("status", "")})
    return results


@mcp.tool()
def aitp_get_popup(topics_root: str, topic_slug: str) -> dict[str, Any]:
    """Check if there is a blocker requiring human input."""
    root = _topic_root(topics_root, topic_slug)
    cand_dir = root / "L3" / "candidates"
    if not cand_dir.is_dir():
        return {"kind": "none"}
    for path in cand_dir.glob("*.md"):
        fm, _ = _parse_md(path)
        if fm.get("status") == "pending_approval":
            return {
                "kind": "promotion_gate",
                "candidate_id": fm.get("candidate_id", path.stem),
                "title": fm.get("title", ""),
                "summary": f"Candidate '{fm.get('title')}' is ready for L2 promotion. Approve?",
                "options": ["Approve promotion", "Request revision", "Reject"],
            }
    ctrl_path = root / "runtime" / "control_note.md"
    if ctrl_path.exists():
        fm, body = _parse_md(ctrl_path)
        if fm.get("active"):
            return {"kind": "control_note", "summary": body.strip()[:200], "options": ["Acknowledge"]}
    return {"kind": "none"}


@mcp.tool()
def aitp_resolve_popup(
    topics_root: str,
    topic_slug: str,
    choice_index: int,
    comment: str = "",
) -> str:
    """Resolve a popup by recording the human's choice."""
    root = _topic_root(topics_root, topic_slug)
    popup = aitp_get_popup(topics_root, topic_slug)
    if popup["kind"] == "none":
        return "No active popup."
    if popup["kind"] == "promotion_gate":
        cand_slug = popup["candidate_id"]
        cand_path = root / "L3" / "candidates" / f"{cand_slug}.md"
        fm, body = _parse_md(cand_path)
        if choice_index == 0:  # Approve
            fm["status"] = "promoted"
            fm["promoted_at"] = _now()
            fm["promotion_comment"] = comment
            _write_md(cand_path, fm, body)
            # Write to L2
            l2_path = root / "L2" / "canonical" / f"{cand_slug}.md"
            _write_md(l2_path, fm, body)
            return f"Promoted {cand_slug} to L2."
        elif choice_index == 1:  # Revise
            fm["status"] = "revision_requested"
            fm["revision_comment"] = comment
            _write_md(cand_path, fm, body)
            return f"Revision requested for {cand_slug}."
        else:  # Reject
            fm["status"] = "rejected"
            fm["rejection_comment"] = comment
            _write_md(cand_path, fm, body)
            return f"Rejected {cand_slug}."
    if popup["kind"] == "control_note":
        ctrl_path = root / "runtime" / "control_note.md"
        fm, body = _parse_md(ctrl_path)
        fm["active"] = False
        fm["resolved_at"] = _now()
        _write_md(ctrl_path, fm, body)
        return "Control note acknowledged."
    return f"Resolved popup of kind {popup['kind']}."


@mcp.tool()
def aitp_get_skill_context(topics_root: str, topic_slug: str) -> dict[str, Any]:
    """Determine which skill to inject based on current topic status."""
    root = _topic_root(topics_root, topic_slug)
    fm, _ = _parse_md(root / "state.md")
    status = _infer_status(fm, root)
    skill_name = _SKILL_MAP.get(status, "skill-continuous")
    return {
        "topic_slug": topic_slug,
        "status": status,
        "mode": fm.get("mode", "explore"),
        "skill": skill_name,
        "message": f"Topic is in '{status}' state. Inject '{skill_name}'.",
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
