"""L4 verification commands: verify run, verify results, promote."""
from __future__ import annotations
from pathlib import Path


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _parse_md(path: Path):
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


def _write_md(path: Path, fm: dict, body: str):
    import yaml
    from brain.cli.state import atomic_write
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", yaml.dump(dict(fm), default_flow_style=False, allow_unicode=True).rstrip(),
             "---", str(body).lstrip("\n")]
    atomic_write(path, "\n".join(lines))


def _atomic_write(path: Path, content: str):
    import os, tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    try:
        os.write(fd, content.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)


def _resolve_topic_root(topic_slug: str) -> Path:
    import os
    base = Path(os.environ.get("AITP_TOPICS_ROOT",
        "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"))
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


def cmd_verify_run(args):
    """Spawn verification agents for a candidate.

    Generates spawn instructions for the orchestrator agent to execute.
    The orchestrator must use Claude Code's Agent tool with isolation=worktree
    to spawn the 3 Verifier agents (Algebraic, Physical, Numerical).
    """
    root = _resolve_topic_root(args.topic)
    from brain.cli.preflight import run_preflight

    failures = run_preflight("verify-run", root, candidate_id=args.candidate_id)
    if failures:
        print("Preflight blocked:")
        for f in failures:
            print(f"  • {f}")
        return 1

    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"
    if not cand_path.exists():
        print(f"Candidate '{args.candidate_id}' not found")
        return 1

    cand_fm, cand_body = _parse_md(cand_path)
    claim = cand_fm.get("claim_statement", "")
    chain_id = cand_fm.get("derivation_chain_id", "default")
    ctype = cand_fm.get("candidate_type", "research_claim")

    # Study mode: 1 adversarial reader + source anchoring + coverage
    # Research mode: 3 Verifiers + Skeptic
    if ctype in ("atomic_concept", "derivation_chain"):
        verifiers = [
            {"type": "adversarial", "prompt": "brain/agents/skeptic.md",
             "input": f"L3/candidates/{args.candidate_id}.md (study mode: source anchoring + coverage check)",
             "output": f"L4/reviews/{args.candidate_id}_adversarial.md"},
        ]
        preflight_checks = ["source_chain_anchored", "coverage_completeness_check"]
    else:
        verifiers = [
            {"type": "algebraic", "prompt": "brain/agents/algebraic_verifier.md",
             "input": f"L3/candidates/{args.candidate_id}.md + L2/graph/steps/ (chain={chain_id})",
             "output": f"L4/reviews/{args.candidate_id}_algebraic.md"},
            {"type": "physical", "prompt": "brain/agents/physical_verifier.md",
             "input": "claim statement + L2 access",
             "output": f"L4/reviews/{args.candidate_id}_physical.md"},
            {"type": "numerical", "prompt": "brain/agents/numerical_verifier.md",
             "input": "candidate + L4/outputs/ + compute/targets.yaml",
             "output": f"L4/reviews/{args.candidate_id}_numerical.md"},
        ]
        preflight_checks = []

    topic = args.topic
    spawn_json = {
        "candidate": args.candidate_id, "topic": topic,
        "claim": claim[:200], "chain": chain_id, "type": ctype,
        "verifiers": verifiers,
        "preflight_checks": preflight_checks,
        "isolation": "worktree", "parallel": True,
        "next_command": f"aitp verify results {topic} --candidate {args.candidate_id}",
    }
    import json
    print(json.dumps(spawn_json, indent=2, ensure_ascii=False))
    return 0


def cmd_verify_results(args):
    """Collect Verifier outputs and generate disagreement matrix."""
    root = _resolve_topic_root(args.topic)
    from brain.cli.preflight import run_preflight

    failures = run_preflight("verify-results", root, candidate_id=args.candidate_id)
    if failures:
        print("Preflight blocked:")
        for f in failures:
            print(f"  • {f}")
        return 1

    reviews_dir = root / "L4" / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    review_types = ["algebraic", "physical", "numerical", "skeptic"]
    results = {}
    for rtype in review_types:
        path = reviews_dir / f"{args.candidate_id}_{rtype}.md"
        if path.exists():
            fm, _ = _parse_md(path)
            results[rtype] = fm.get("outcome", "unknown")
        else:
            results[rtype] = "missing"

    # Build disagreement matrix
    outcomes = list(results.values())
    if "missing" in outcomes:
        verdict = "incomplete"
    elif all(o == "pass" for o in outcomes):
        verdict = "unanimous_pass"
    elif all(o in ("pass", "fail") for o in outcomes) and "fail" in outcomes:
        verdict = "divergent"
    else:
        verdict = "mixed"

    # Write matrix
    state_fm, state_body = _parse_md(root / "state.md")
    state_fm["l4_verdict"] = verdict
    _write_md(root / "state.md", state_fm, state_body)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  VERIFICATION RESULTS — {args.candidate_id}
╚══════════════════════════════════════════════════════════════╝

| Verifier     | Outcome    |
|-------------|-----------|""")
    for rtype, outcome in results.items():
        print(f"| {rtype:<11} | {outcome:<10} |")
    print(f"\nVerdict: {verdict}")

    if verdict == "unanimous_pass":
        print("""
All Verifiers passed. Next step:
  Spawn Skeptic agent (brain/agents/skeptic.md) with claim-only input.
  If Skeptic also passes → aitp promote {topic} --candidate {candidate_id}
""".format(topic=args.topic, candidate_id=args.candidate_id))
    elif verdict == "divergent":
        print("\nDisagreement detected. Human review recommended.")

    return 0


def cmd_promote(args):
    """Promote a validated candidate to L2."""
    root = _resolve_topic_root(args.topic)
    from brain.cli.preflight import run_preflight

    failures = run_preflight("promote", root, candidate_id=args.candidate_id)
    if failures:
        print("Preflight blocked:")
        for f in failures:
            print(f"  • {f}")
        return 1

    state_fm, state_body = _parse_md(root / "state.md")
    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"

    if not cand_path.exists():
        print(f"Candidate '{args.candidate_id}' not found")
        return 1

    verdict = state_fm.get("l4_verdict", "")
    if verdict not in ("unanimous_pass",):
        print(f"Verification not complete. Current verdict: {verdict or 'none'}")
        print("Run 'aitp verify results' first.")
        return 1

    # Skeptic gate: must pass blind adversarial review before promotion
    skeptic_path = root / "L4" / "reviews" / f"{args.candidate_id}_skeptic.md"
    if not skeptic_path.exists():
        print(f"Skeptic review not found: {skeptic_path}")
        print("Run the Skeptic agent (brain/agents/skeptic.md) before promoting.")
        print("Skeptic reviews the claim without seeing the derivation, checking for L2 contradictions.")
        return 1
    sfm, _ = _parse_md(skeptic_path)
    skeptic_outcome = sfm.get("outcome", "unknown")
    if skeptic_outcome != "pass":
        print(f"Skeptic review outcome: {skeptic_outcome} (requires 'pass')")
        print("Address the Skeptic's concerns before re-submitting for promotion.")
        return 1
    print(f"Skeptic gate: {skeptic_outcome}")

    # Update candidate status
    cand_fm, cand_body = _parse_md(cand_path)
    cand_fm["status"] = "validated"
    _write_md(cand_path, cand_fm, cand_body)

    # Clear research loop and advance to promotion with validation
    from brain.cli.state import validate_state_transition, save_state
    ok, msg = validate_state_transition(root, "promotion")
    if not ok:
        print(f"Stage transition blocked: {msg}")
        return 1
    state_fm["research_loop_active"] = False
    state_fm["stage"] = "promotion"
    state_fm["updated_at"] = _now_iso()
    save_state(root, state_fm, state_body)

    print(f"Candidate '{args.candidate_id}' promoted to validation. Ready for human review → L2.")
    print("Use aitp l2 node create + aitp l2 merge to complete promotion to global L2.")
    return 0
