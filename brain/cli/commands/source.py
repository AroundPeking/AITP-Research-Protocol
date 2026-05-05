"""L0 source management CLI commands."""
from __future__ import annotations
from pathlib import Path


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    import re
    return re.sub(r'[^a-z0-9-]', '-', (text or "untitled").lower().strip())[:60]


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
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", yaml.dump(dict(fm), default_flow_style=False, allow_unicode=True).rstrip(),
             "---", str(body).lstrip("\n")]
    path.write_text("\n".join(lines), encoding="utf-8")


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


def _append_research_md(root: Path, layer: str, entry: str):
    path = root / "research.md"
    line = f"- {_now_iso()} [{layer}] {entry}\n"
    if path.exists():
        _atomic_write(path, path.read_text(encoding="utf-8") + line)
    else:
        _atomic_write(path, f"# Research Trail\n\n{line}")


def cmd_source_add(args):
    if hasattr(args, 'topics_root') and args.topics_root:
        root = Path(args.topics_root)
    else:
        root = _resolve_topic_root(args.topic)
    sources_dir = root / "L0" / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    source_id = args.id or _slugify(args.title or args.path or "untitled")
    path = sources_dir / f"{source_id}.md"
    fm = {
        "source_id": source_id,
        "title": args.title or args.path or "Untitled",
        "type": args.type or "paper",
        "role": args.role or "direct_dependency",
        "created_at": _now_iso(),
    }
    body = f"# {fm['title']}\n\nPath: {args.path or ''}\n\n## Notes\n{args.notes or ''}\n"
    _write_md(path, fm, body)
    _append_research_md(root, "L0", f"Registered source: {source_id}")
    print(f"Source '{source_id}' registered → {path}")


def cmd_source_discover(args):
    """Search arXiv for papers matching a query. Returns results for manual review."""
    query = args.query or ""
    if not query:
        print("Provide --query for arXiv search.")
        return 1

    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET

    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query,
        "max_results": str(args.max or 10),
        "sortBy": "relevance",
    })

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AITP/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"arXiv API error: {e}")
        return 1

    ns = {"atom": "http://www.w3.org/2005/Atom",
          "arxiv": "http://arxiv.org/schemas/atom"}
    root_el = ET.fromstring(data)

    entries = root_el.findall("atom:entry", ns)
    if not entries:
        print(f"No results for '{query}'")
        return 0

    print(f"arXiv results for '{query}': {len(entries)} found\n")
    for i, entry in enumerate(entries, 1):
        title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
        arxiv_id = entry.findtext("atom:id", "", ns).strip()
        # Extract arXiv ID from URL: http://arxiv.org/abs/XXXX.XXXXX
        arxiv_short = arxiv_id.split("/abs/")[-1] if "/abs/" in arxiv_id else arxiv_id
        authors = [
            a.findtext("atom:name", "", ns).strip()
            for a in entry.findall("atom:author", ns)
        ]
        summary = entry.findtext("atom:summary", "", ns).strip()[:200].replace("\n", " ")
        published = entry.findtext("atom:published", "", ns)[:10]
        print(f"{i}. [{arxiv_short}] {title}")
        print(f"   Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        print(f"   Published: {published}  |  {summary[:120]}...")
        print()

    print(f"Register with: aitp source add {args.topic} --id <arxiv_id> --title \"...\" --type paper")
    return 0


def cmd_source_registry(args):
    root = _resolve_topic_root(args.topic)
    sources_dir = root / "L0" / "sources"
    if not sources_dir.exists() or not list(sources_dir.glob("*.md")):
        print("No sources registered yet. Use 'aitp source add' first.")
        return 1
    sources = list(sources_dir.glob("*.md"))
    lines = ["# Source Registry\n", f"\n**Total sources**: {len(sources)}\n"]
    for s in sorted(sources):
        sf, _ = _parse_md(s)
        sid = sf.get("source_id", s.stem)
        title = sf.get("title", "?")
        stype = sf.get("type", "?")
        srole = sf.get("role", "?")
        lines.append(f"- **{sid}**: {title} ({stype}, {srole})\n")
    registry_path = root / "L0" / "source_registry.md"
    fm = {"source_count": len(sources), "search_status": "complete"}
    _write_md(registry_path, fm, "".join(lines))
    _append_research_md(root, "L0", f"Registry synthesized: {len(sources)} sources")
    print(f"Registry written with {len(sources)} sources → {registry_path}")
    return 0


def cmd_source_read(args):
    root = _resolve_topic_root(args.topic)
    path = root / "L0" / "sources" / f"{args.source}.md"
    if not path.exists():
        print(f"Source '{args.source}' not found in L0/sources/")
        return 1
    _, body = _parse_md(path)
    print(body[:2000])
    return 0


def _resolve_topic_root(topic_slug: str) -> Path:
    import os
    base = Path(os.environ.get("AITP_TOPICS_ROOT",
        "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"))
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug
