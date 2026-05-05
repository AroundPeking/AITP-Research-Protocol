"""Memory recording commands — lightweight, no preflight."""
from __future__ import annotations
from pathlib import Path


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


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


def _ensure_memory_template(root: Path):
    mem_path = root / "MEMORY.md"
    if not mem_path.exists():
        template = (
            "# Topic Memory\n\n"
            "## Steering\n<!-- What the user said. Direct quotes preferred. -->\n\n"
            "## Decisions\n<!-- What approach we chose and why. -->\n\n"
            "## Dead Ends\n<!-- Approaches that failed. -->\n\n"
            "## Pitfalls\n<!-- Known bugs, config traps. -->\n"
        )
        mem_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(mem_path, template)
    return mem_path


def _resolve_topic_root(topic_slug: str) -> Path:
    import os
    base = Path(os.environ.get("AITP_TOPICS_ROOT",
        "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"))
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


def cmd_memory_steer(args):
    root = _resolve_topic_root(args.topic)
    mem_path = _ensure_memory_template(root)
    body = mem_path.read_text(encoding="utf-8")
    entry = f"\n- {_now_iso()}: \"{args.text}\"\n"
    body = body.replace("## Steering\n", f"## Steering\n{entry}")
    _atomic_write(mem_path, body)
    print(f"Steering recorded: {args.text}")
    return 0


def cmd_memory_decide(args):
    root = _resolve_topic_root(args.topic)
    mem_path = _ensure_memory_template(root)
    body = mem_path.read_text(encoding="utf-8")
    entry = f"\n- {_now_iso()}: {args.text}\n"
    if args.rejected:
        entry = f"\n- {_now_iso()}: Chose {args.text}. Rejected: {args.rejected}.\n"
    body = body.replace("## Decisions\n", f"## Decisions\n{entry}")
    _atomic_write(mem_path, body)
    print(f"Decision recorded: {args.text}")
    return 0


def cmd_memory_pitfall(args):
    root = _resolve_topic_root(args.topic)
    mem_path = _ensure_memory_template(root)
    body = mem_path.read_text(encoding="utf-8")
    entry = f"\n- {args.text}\n"
    body = body.replace("## Pitfalls\n", f"## Pitfalls\n{entry}")
    _atomic_write(mem_path, body)
    print(f"Pitfall recorded: {args.text}")
    return 0
