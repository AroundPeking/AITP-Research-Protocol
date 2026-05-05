"""L1 framing CLI commands."""
from __future__ import annotations
from pathlib import Path
from brain.cli.commands.source import (_now_iso, _slugify, _parse_md, _write_md,
                                        _atomic_write, _append_research_md, _resolve_topic_root)


def cmd_question_frame(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L1" / "question_contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    fm = {
        "artifact_kind": "l1_question_contract",
        "bounded_question": args.question or "",
        "scope_boundaries": args.scope or "",
        "target_quantities": args.targets or "",
        "created_at": _now_iso(),
    }
    body = (
        f"# Bounded Question\n{args.question or ''}\n\n"
        f"## Competing Hypotheses\n\n"
        f"## Scope Boundaries\n{args.scope or ''}\n\n"
        f"## Target Quantities Or Claims\n{args.targets or ''}\n\n"
        f"## L2 Cross-Reference\n"
    )
    _write_md(path, fm, body)
    print(f"Question contract → {path}")
    return 0


def cmd_convention_lock(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L1" / "convention_snapshot.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    text = args.add or args.text or ""
    if not text:
        print("Error: provide convention text via --add or --text")
        return 1

    if path.exists():
        _, body = _parse_md(path)
    else:
        body = "# Convention Snapshot\n"

    body += f"\n- {_now_iso()}: {text}\n"
    _write_md(path, {}, body)

    if args.add:
        _append_research_md(root, "L1", f"Convention updated: {args.add}")
    print(f"Convention appended: {text[:80]}...")
    return 0


def cmd_anchor_map(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L1" / "derivation_anchor_map.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    body = path.read_text(encoding="utf-8") if path.exists() else "# Derivation Anchor Map\n"
    body += f"\n- {args.source} → {args.equation or 'see text'}: {args.note or ''}\n"
    _write_md(path, {}, body)
    print("Anchor map updated")
    return 0


def cmd_contradiction_register(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L1" / "contradiction_register.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    body = path.read_text(encoding="utf-8") if path.exists() else "# Contradiction Register\n"
    body += (
        f"\n- {args.source_a} vs {args.source_b}: {args.conflict}\n"
        f"  Status: {args.status or 'unresolved'}\n"
    )
    _write_md(path, {}, body)
    print(f"Contradiction registered: {args.source_a} vs {args.source_b}")
    return 0


def cmd_source_cross_map(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L1" / "source_cross_map.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    sources_dir = root / "L0" / "sources"
    sources = list(sources_dir.glob("*.md")) if sources_dir.exists() else []

    lines = ["# Source Cross-Map\n", f"\n## Registered Sources ({len(sources)})\n"]
    for s in sorted(sources):
        sf, _ = _parse_md(s)
        lines.append(f"- {s.stem}: {sf.get('title', '?')}\n")
    lines.append("\n## Convention Equivalences\n\n## Equation Cross-References\n\n## Unresolved Conflicts\n")

    _write_md(path, {"artifact_kind": "l1_cross_map"}, "".join(lines))
    print(f"Cross-map generated for {len(sources)} sources → {path}")
    return 0
