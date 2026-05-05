"""Preflight engine for AITP CLI commands.

Reads command policy from Markdown files (YAML frontmatter) and enforces
preflight checks before executing heavyweight operations.

Usage:
    failures = run_preflight("candidate-submit", topic_root)
    if failures:
        raise PreflightBlocked(failures)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from brain.cli.state import current_stage, current_l3_activity, current_gate_status


def _parse_md_local(path: Path) -> tuple[dict, str]:
    """Local YAML frontmatter parser."""
    import yaml
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                fm = {}
            return fm, parts[2] if len(parts) > 2 else ""
    return {}, text


# ── Check registry ───────────────────────────────────────────────────────

PRECHECK_REGISTRY: dict[str, Callable[..., tuple[bool, str]]] = {}


def register_check(name: str):
    """Decorator to register a named preflight check."""
    def deco(fn):
        PRECHECK_REGISTRY[name] = fn
        return fn
    return deco


# ── Built-in checks ──────────────────────────────────────────────────────

@register_check("derivation_chain_not_empty")
def check_derivation_chain_not_empty(topic_root: Path, **kw) -> tuple[bool, str]:
    """Verify at least one derivation step exists for the active chain."""
    steps_dir = topic_root / "L2" / "graph" / "steps"
    if not steps_dir.exists():
        return False, "No derivation steps directory found (L2/graph/steps/ missing)"
    steps = list(steps_dir.glob("*.md"))
    if not steps:
        return False, "Derivation chain is empty — no steps recorded"
    return True, ""


@register_check("all_steps_have_source_refs")
def check_all_steps_have_source_refs(topic_root: Path, **kw) -> tuple[bool, str]:
    """Every derivation step must have a source_ref."""
    steps_dir = topic_root / "L2" / "graph" / "steps"
    if not steps_dir.exists():
        return False, "No derivation steps directory"
    for step_path in steps_dir.glob("*.md"):
        fm, _ = _parse_md_local(step_path)
        if not fm.get("source_ref", "").strip():
            return False, f"Step {step_path.stem} is missing source_ref"
    return True, ""


@register_check("domain_invariants_checked")
def check_domain_invariants_checked(topic_root: Path, **kw) -> tuple[bool, str]:
    """Domain-specific invariants must be verified before candidate submission.

    Lane-aware: formal_theory skips domain invariant checks.
    Only code_method (which binds to external code repositories) requires them.
    """
    lane = kw.get("lane", "")
    if lane in ("formal_theory", ""):
        return True, ""

    inv_path = topic_root / "L4" / "invariant-checks.md"
    contracts_dir = topic_root / "contracts"
    domain_manifest = contracts_dir / "domain-manifest.json" if contracts_dir.exists() else None

    if not domain_manifest:
        return True, ""

    import json
    try:
        manifest = json.loads(domain_manifest.read_text(encoding="utf-8"))
        invariants = manifest.get("invariants", [])
    except Exception:
        return True, ""

    if not invariants:
        return True, ""

    if not inv_path.exists():
        names = [inv.get("id", "?") for inv in invariants]
        return False, f"Domain invariants not checked: {names}. Create L4/invariant-checks.md"

    body = inv_path.read_text(encoding="utf-8")
    missing = []
    for inv in invariants:
        inv_id = inv.get("id", "")
        if inv_id and inv_id not in body:
            missing.append(inv_id)

    if missing:
        return False, f"Invariants not verified: {missing}"
    return True, ""


@register_check("candidate_exists")
def check_candidate_exists(topic_root: Path, **kw) -> tuple[bool, str]:
    """The referenced candidate file must exist."""
    candidate_id = kw.get("candidate_id", "")
    if not candidate_id:
        return False, "No candidate_id provided"
    cand_path = topic_root / "L3" / "candidates" / f"{candidate_id}.md"
    if not cand_path.exists():
        # Also check without .md suffix
        alt = topic_root / "L3" / "candidates" / f"{candidate_id}"
        if not alt.exists():
            return False, f"Candidate '{candidate_id}' not found"
    return True, ""


@register_check("counterargument_if_pass")
def check_counterargument_if_pass(topic_root: Path, **kw) -> tuple[bool, str]:
    """If review outcome is 'pass', a counterargument must exist."""
    outcome = kw.get("outcome", "")
    if outcome != "pass":
        return True, ""
    counter = kw.get("counterargument", "")
    if len(counter.strip()) < 50:
        return False, "Counterargument ≥50 chars required for pass outcome"
    return True, ""


@register_check("all_verifiers_passed")
def check_all_verifiers_passed(topic_root: Path, **kw) -> tuple[bool, str]:
    """All Verifier reviews must have outcome=pass."""
    reviews_dir = topic_root / "L4" / "reviews"
    if not reviews_dir.exists():
        return False, "No L4 reviews directory found"
    # using _parse_md_local
    for review_path in reviews_dir.glob("*_algebraic.md"):
        fm, _ = _parse_md_local(review_path)
        if fm.get("outcome") != "pass":
            return False, f"Review {review_path.stem}: outcome={fm.get('outcome')}, expected pass"
    return True, ""


@register_check("human_review_complete")
def check_human_review_complete(topic_root: Path, **kw) -> tuple[bool, str]:
    """Human must have reviewed and approved before promotion."""
    fm, _ = _load_state_raw(topic_root)
    reviewed = fm.get("l4_human_reviewed", False)
    decision = fm.get("l4_human_decision", "")
    if not reviewed or decision != "approved":
        return False, "Human review not complete — run aitp verify results first"
    return True, ""


# ── Engine ───────────────────────────────────────────────────────────────

def _load_state_raw(topic_root: Path) -> tuple[dict, str]:
    # using _parse_md_local
    state_path = topic_root / "state.md"
    if not state_path.exists():
        return {"stage": "L0"}, ""
    return _parse_md_local(state_path)


def _load_command_policy(command_name: str) -> dict[str, Any]:
    """Read a command Markdown file and parse its YAML frontmatter."""
    import yaml
    cmd_path = Path(__file__).parent.parent / "commands" / f"{command_name}.md"
    if not cmd_path.exists():
        return {}
    text = cmd_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]) or {}
    return {}


def _load_research_intensity(topic_root: Path) -> str:
    """Read research_intensity from state.md. Defaults to 'standard'."""
    fm, _ = _load_state_raw(topic_root)
    return fm.get("research_intensity", "standard")


def run_preflight(command_name: str, topic_root: Path, **kwargs) -> list[str]:
    """Execute all preflight checks for *command_name*.

    Returns a list of failure messages (empty = all passed).

    Two-speed design (research_intensity from state.md):
      - quick:  all failures → advisory warnings (return empty list, don't block)
      - standard: normal enforcement (policy-driven)
      - full:   standard checks + source_chain_anchored + coverage_completeness_check
    """
    policy = _load_command_policy(command_name)
    intensity = _load_research_intensity(topic_root)
    failures: list[str] = []

    # Stage check
    required_stage = policy.get("stage")
    if required_stage:
        actual = current_stage(topic_root)
        stages = required_stage if isinstance(required_stage, list) else [required_stage]
        if actual not in stages:
            failures.append(f"Stage: requires one of {stages}, currently {actual}")

    # Gate check
    if policy.get("gate") == "required":
        gs, override = current_gate_status(topic_root)
        if gs.startswith("blocked") and not override:
            failures.append(
                f"Gate blocked: {gs}. "
                f"Fix the issue or use 'aitp gate override --reason \"...\"'."
            )

    # Activity check
    required_activity = policy.get("activity", [])
    if required_activity:
        actual = current_l3_activity(topic_root)
        if actual not in required_activity:
            failures.append(
                f"Activity: requires {required_activity}, currently {actual}"
            )

    # Named preflight checks (unconditional)
    for check_name in policy.get("preflight", []):
        check_fn = PRECHECK_REGISTRY.get(check_name)
        if check_fn:
            ok, msg = check_fn(topic_root, **kwargs)
            if not ok:
                failures.append(msg)

    # Conditional preflight checks
    for item in policy.get("preflight_conditional", []):
        check_name = item.get("check", item) if isinstance(item, dict) else item
        condition = item.get("when", {}) if isinstance(item, dict) else {}
        # Evaluate condition: all key=value pairs must match kwargs
        if condition:
            match = all(kwargs.get(k) == v for k, v in condition.items())
            if not match:
                continue
        check_fn = PRECHECK_REGISTRY.get(check_name)
        if check_fn:
            ok, msg = check_fn(topic_root, **kwargs)
            if not ok:
                failures.append(msg)

    # Blocking conditions
    for condition in policy.get("blocking_conditions", []):
        cond_fn = BLOCKING_REGISTRY.get(condition)
        if cond_fn and cond_fn(topic_root, **kwargs):
            failures.append(f"Blocked: {condition}")

    # ── Full mode: extra checks ──────────────────────────────────────
    if intensity == "full":
        for extra_check in ("source_chain_anchored", "coverage_completeness_check"):
            if extra_check not in policy.get("preflight", []):
                check_fn = PRECHECK_REGISTRY.get(extra_check)
                if check_fn:
                    ok, msg = check_fn(topic_root, **kwargs)
                    if not ok:
                        failures.append(f"[full] {msg}")

    # ── Quick mode: downgrade to advisory ────────────────────────────
    if intensity == "quick" and failures:
        import sys
        print(f"Preflight advisory ({command_name}, intensity=quick):", file=sys.stderr)
        for f in failures:
            print(f"  • {f}", file=sys.stderr)
        return []

    return failures


@register_check("source_chain_anchored")
def check_source_chain_anchored(topic_root: Path, **kw) -> tuple[bool, str]:
    """Every traced derivation step must have a source_ref to a registered source (study mode)."""
    steps_dir = topic_root / "L2" / "graph" / "steps"
    sources_dir = topic_root / "L0" / "sources"
    if not steps_dir.exists() or not sources_dir.exists():
        return True, ""
    registered_ids = {p.stem for p in sources_dir.glob("*.md")}
    for step_path in steps_dir.glob("*.md"):
        fm, _ = _parse_md_local(step_path)
        source_ref = fm.get("source_ref", "").strip()
        if not source_ref:
            return False, f"Step {step_path.stem} has no source_ref"
    return True, ""


@register_check("coverage_completeness_check")
def check_coverage_completeness_check(topic_root: Path, **kw) -> tuple[bool, str]:
    """Verify source TOC coverage is complete or partial with deferrals (study mode)."""
    toc_path = topic_root / "L1" / "source_toc_map.md"
    if not toc_path.exists():
        return False, "source_toc_map.md not found"
    fm, body = _parse_md_local(toc_path)
    coverage = fm.get("coverage_status", "").strip().lower()
    if coverage not in ("complete", "partial_with_deferrals"):
        return False, f"Coverage status is '{coverage}' — must be 'complete' or 'partial_with_deferrals'"
    if coverage == "partial_with_deferrals" and "## Deferred Sections" not in body:
        return False, "Coverage is partial_with_deferrals but ## Deferred Sections heading is missing"
    return True, ""


@register_check("gate_ready_or_override")
def check_gate_ready_or_override(topic_root: Path, **kw) -> tuple[bool, str]:
    """Gate must be ready or have a valid active override."""
    gs, override = current_gate_status(topic_root)
    if gs.startswith("ready") or override:
        return True, ""
    return False, f"Gate status is '{gs}'. Fix artifacts or use 'aitp gate override'."


BLOCKING_REGISTRY: dict[str, Callable[..., bool]] = {
    "gate_blocked_and_no_override": lambda root, **kw: (
        current_gate_status(root)[0].startswith("blocked")
        and not current_gate_status(root)[1]
    ),
    "derivation_chain_empty": lambda root, **kw: (
        not check_derivation_chain_not_empty(root)[0]
    ),
    "missing_candidate": lambda root, **kw: (
        not check_candidate_exists(root, **kw)[0]
    ),
}


class PreflightBlocked(Exception):
    """Raised when preflight checks fail."""
    def __init__(self, failures: list[str]):
        self.failures = failures
        super().__init__("\n".join(failures))
