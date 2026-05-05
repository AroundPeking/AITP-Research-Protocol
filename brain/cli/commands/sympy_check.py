"""Interactive SymPy verification — lightweight, no preflight."""
from __future__ import annotations
from pathlib import Path
import os


def _resolve_topic_root(topic_slug: str) -> Path:
    base = Path(os.environ.get("AITP_TOPICS_ROOT",
        "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"))
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


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


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def cmd_sympy_check(args):
    from brain.sympy_verify import check_dimensions, check_algebra, check_limit

    sub = getattr(args, 'sympy_subcommand', 'dim')
    expr = " ".join(args.expression) if hasattr(args.expression, '__iter__') else str(args.expression)

    if sub == "dim":
        result = check_dimensions(expr, {})
        ok = isinstance(result, dict) and result.get("pass", False)
        detail = result.get("error", "") or result.get("message", "") or str(result)
    elif sub == "algebra":
        if "=" in expr:
            lhs, rhs = expr.split("=", 1)
        else:
            lhs, rhs = expr, "0"
        result = check_algebra(lhs.strip(), rhs.strip())
        ok = isinstance(result, dict) and result.get("pass", False)
        detail = result.get("error", "") or result.get("message", "") or str(result)
    elif sub == "limit":
        result = check_limit(expr)
        ok = isinstance(result, dict) and result.get("pass", False)
        detail = result.get("error", "") or result.get("message", "") or str(result)
    else:
        print(f"Unknown subcommand: {sub}. Use: dim, algebra, limit")
        return 1

    print(f"{'PASS' if ok else 'FAIL'} {sub}: {detail}")
    return 0 if ok else 1


def cmd_sympy_execute(args):
    """Batch formal verification of a derivation chain. Writes report to L4/reports/."""
    root = _resolve_topic_root(args.topic)
    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"
    if not cand_path.exists():
        print(f"Candidate '{args.candidate_id}' not found")
        return 1

    cand_fm, _ = _parse_md(cand_path)
    chain_id = cand_fm.get("derivation_chain_id", "default")

    # Read derivation steps
    steps_dir = root / "L2" / "graph" / "steps"
    if not steps_dir.exists():
        print("No derivation steps found")
        return 1

    steps = []
    for s in sorted(steps_dir.glob("*.md")):
        fm, body = _parse_md(s)
        if fm.get("chain_id") == chain_id:
            steps.append({"id": fm.get("step_id", s.stem), "input": fm.get("input_expr", ""),
                         "output": fm.get("output_expr", ""), "transform": fm.get("transform", ""),
                         "file": str(s)})

    if not steps:
        print(f"No steps for chain '{chain_id}'")
        return 1

    from brain.sympy_verify import check_dimensions, check_algebra, check_limit

    print(f"Formal verification: {args.candidate_id} (chain={chain_id}, {len(steps)} steps)")
    results = []
    all_pass = True

    for step in steps:
        step_result = {"step": step["id"], "checks": {}}

        # Dimensional check on output expression
        if step["output"]:
            r = check_dimensions(step["output"], {})
            step_result["checks"]["dimensions"] = "pass" if r.get("pass") else f"fail: {r.get('error', r)}"
            if not r.get("pass"):
                all_pass = False

        # Algebraic check: input + transform → output
        if step["input"] and step["output"] and step["transform"]:
            combined = f"{step['input']} → {step['output']} (via {step['transform']})"
            r = check_algebra(step["input"], step["output"])
            step_result["checks"]["algebra"] = "pass" if r.get("pass") else f"fail: {r.get('error', r)}"
            if not r.get("pass"):
                all_pass = False

        # Limit check — only if limit info is in step metadata
        # Requires: limit_var, limit_value, expected (not stored in generic steps)
        # Skipped automatically for steps without limit annotations

        status = "PASS" if all(p == "pass" for p in step_result["checks"].values()) else "FAIL"
        print(f"  {step['id']}: {status} " +
              " | ".join(f"{k}={v}" for k, v in step_result["checks"].items()))
        results.append(step_result)

    # Write formal report
    reports_dir = root / "L4" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{args.candidate_id}_formal.md"

    lines = [
        f"# Formal Verification: {args.candidate_id}",
        f"Generated: {_now_iso()}",
        f"Chain: {chain_id} | Steps: {len(steps)} | Verdict: {'PASS' if all_pass else 'FAIL'}",
        "",
        "## Claim",
        cand_fm.get("claim_statement", "N/A"),
        "",
        "## Per-Step Results",
    ]
    for r in results:
        lines.append(f"\n### {r['step']}")
        for check, result in r["checks"].items():
            icon = "✓" if result == "pass" else "✗"
            lines.append(f"- {icon} **{check}**: {result}")

    lines.extend([
        "",
        "## Summary",
        f"- Total steps: {len(steps)}",
        f"- Passed: {sum(1 for r in results if all(p == 'pass' for p in r['checks'].values()))}",
        f"- Failed: {sum(1 for r in results if not all(p == 'pass' for p in r['checks'].values()))}",
        f"- Verdict: {'**PASS** — all steps verified' if all_pass else '**FAIL** — some steps need attention'}",
    ])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport → {report_path}")
    print(f"Verdict: {'PASS' if all_pass else 'FAIL'}")

    # Append research.md
    rp = root / "research.md"
    line = f"- {_now_iso()} [L4] Formal verification: {args.candidate_id} ({'PASS' if all_pass else 'FAIL'})\n"
    if rp.exists():
        rp.write_text(rp.read_text(encoding="utf-8") + line, encoding="utf-8")

    return 0 if all_pass else 1
