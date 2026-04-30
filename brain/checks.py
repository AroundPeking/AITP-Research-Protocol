"""Validation functions for artifact completeness.
"""

from __future__ import annotations

from typing import Any


# -- Frontmatter and heading checks --

def _missing_frontmatter_keys(frontmatter: dict[str, object], required: list[str]) -> list[str]:
    return [key for key in required if not str(frontmatter.get(key, "")).strip()]


def _missing_required_headings(body: str, headings: list[str]) -> list[str]:
    return [h for h in headings if h not in body]



# -- Content checks --

def _check_heading_content(body: str, heading: str, min_chars: int = 80) -> bool:
    """Check that a Markdown heading has substantive body content (not just placeholder text)."""
    idx = body.find(heading)
    if idx == -1:
        return False
    content_start = idx + len(heading)
    remaining = body[content_start:]
    next_heading = remaining.find("\n## ")
    if next_heading == -1:
        section_body = remaining
    else:
        section_body = remaining[:next_heading]
    cleaned = section_body.strip()
    return len(cleaned) >= min_chars


def _check_derivation_steps(topics_root: str) -> tuple[int, list[str]]:
    """Count recorded derivation steps and return (count, [step_ids])."""
    steps_dir = Path(topics_root) / "L2" / "graph" / "steps"
    if not steps_dir.exists():
        return 0, []
    step_files = list(steps_dir.glob("*.md"))
    step_ids = [f.stem for f in step_files]
    return len(step_files), step_ids


# -- Question semantic validity --


_QUESTION_STEMS = [
    "what", "how does", "why", "under what conditions",
    "derive", "compute", "estimate", "prove", "calculate",
    "determine", "predict", "explain", "compare", "evaluate",
    "verify", "test", "examine", "investigate",
    "show", "demonstrate", "characterize",
    "measure", "simulate", "model", "analyze",
    "is it true", "does", "can",
]


def _check_question_semantic_validity(
    fm: dict[str, object], body: str, research_intensity: str = "standard",
) -> list[str]:
    """Check that the bounded question is structurally well-posed.

    Returns a list of missing requirements (empty = valid).
    For quick intensity: only question stem, scope, and targets required.
    For standard/full: also requires competing hypotheses and non-success conditions.
    """
    issues: list[str] = []
    question = str(fm.get("bounded_question", "")).strip().lower()
    scope = str(fm.get("scope_boundaries", "")).strip().lower()
    targets = str(fm.get("target_quantities", "")).strip()

    if question:
        has_stem = False
        for stem in _QUESTION_STEMS:
            if len(stem) < 3:
                if question.startswith(stem + " "):
                    has_stem = True
                    break
            elif stem in question:
                has_stem = True
                break
        if not has_stem:
            issues.append(
                "bounded_question must contain a question stem "
                "(e.g. 'what is', 'derive', 'compute', 'estimate', 'determine'). "
                f"Got: '{str(fm.get('bounded_question', ''))[:100]}'"
            )

    if not scope or "not" not in scope:
        issues.append(
            "scope_boundaries must identify at least one explicit exclusion "
            "(e.g. 'This question does NOT ask about...'). "
            "Without boundaries the question is unbounded."
        )

    if not targets:
        issues.append(
            "target_quantities must name at least one physically measurable "
            "or calculable quantity with units or dimensionless characterization."
        )

    # Competing hypotheses and non-success conditions are only required
    # for standard and full intensity. Quick mode skips them.
    if research_intensity in ("standard", "full"):
        competing = str(fm.get("competing_hypotheses", "")).strip()
        if not competing:
            issues.append(
                "competing_hypotheses must name at least one alternative hypothesis "
                "or prior explanation. State what other answers exist and why they "
                "might be wrong. This prevents tunnel vision."
            )

        if "## Non-Success Conditions" in body:
            nsc_start = body.index("## Non-Success Conditions")
            nsc_end = body.find("##", nsc_start + 1)
            nsc_section = body[nsc_start:nsc_end] if nsc_end > 0 else body[nsc_start:]
            nsc_content = nsc_section.split("\n", 1)[1].strip() if "\n" in nsc_section else ""
            if not nsc_content or len(nsc_content) < 20:
                issues.append(
                    "## Non-Success Conditions must describe at least one specific "
                    "failure mode (not generic text). Describe what would falsify "
                    "or invalidate the expected answer."
                )

    return issues


def _generate_physics_next_action(
    parse_md: Callable[[Path], tuple[dict[str, Any], str]],
    topic_root_path: Path,
    stage: str,
    gate_status: str,
) -> str:
    """Generate a physics-contentful next action prompt.

    When gate is ready, produce a prompt grounded in the topic's question
    contract and domain context. When blocked, describe what needs fixing.
    """
    if gate_status != "ready":
        return ""

    question_path = topic_root_path / "L1" / "question_contract.md"
    if not question_path.exists():
        return ""

    q_fm, _ = parse_md(question_path)
    question = str(q_fm.get("bounded_question", "")).strip()
    scope = str(q_fm.get("scope_boundaries", "")).strip()
    targets = str(q_fm.get("target_quantities", "")).strip()

    if not question:
        return ""

    parts = [f"Your question: {question}"]
    if targets:
        parts.append(f"Key observable: {targets}")
    if scope:
        parts.append(f"Explicitly excluded: {scope}")
    parts.append(
        "Proceed to the next stage, or refine the question first if "
        "the scope or target still feels vague."
    )
    return "\n".join(parts)


# -- Domain rule extraction --

def _extract_domain_rules(skill_path: Path) -> dict[str, list[str]]:
    """Extract '## Hard Domain Rules' section from a domain skill file.

    Returns a dict with keys like 'hard_rules', 'workflow_lanes', 'smoke_test'
    containing lists of rule strings extracted from the skill body.
    """
    if not skill_path.exists():
        return {}
    try:
        _, body = _parse_md(skill_path)
    except Exception:
        return {}

    rules: dict[str, list[str]] = {"hard_rules": [], "workflow_lanes": [], "smoke_test": []}

    # Extract Hard Domain Rules section
    section_start = body.find("## Hard Domain Rules")
    if section_start == -1:
        return rules

    section_body = body[section_start + len("## Hard Domain Rules"):]
    next_section = section_body.find("\n## ")
    if next_section != -1:
        section_body = section_body[:next_section]

    # Parse bullet points and sub-sections
    current_key = "hard_rules"
    for line in section_body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### "):
            # Sub-section: map to appropriate key
            sub = stripped[4:].lower()
            if "smoke" in sub or "test" in sub:
                current_key = "smoke_test"
            elif "workflow" in sub or "lane" in sub:
                current_key = "workflow_lanes"
            else:
                current_key = "hard_rules"
        elif stripped.startswith("- ") or stripped.startswith("* "):
            rules.setdefault(current_key, []).append(stripped[2:].strip())

    return rules
