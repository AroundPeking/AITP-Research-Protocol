"""AITP Dashboard — lightweight HTTP server for the web preview panel.

Zero external dependencies (stdlib + PyYAML which ships with the project).
Serves a single-page app and two JSON API endpoints.

Usage:
    python tools/aitp_dashboard.py [--port PORT] [--topics-root PATH]
"""

import json
import os
import re
import sys
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# --- Path resolution ---

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR  # where dashboard.html lives

def _default_topics_root():
    env = os.environ.get("AITP_TOPICS_ROOT", "")
    if env and Path(env).is_dir():
        return Path(env)
    # Fallback: sibling research/aitp-topics relative to repo root
    repo_root = SCRIPT_DIR.parent
    candidate = repo_root / "research" / "aitp-topics"
    if candidate.is_dir():
        return candidate
    configured = Path("{{TOPICS_ROOT}}")
    if configured.is_dir():
        return configured
    return candidate

DEFAULT_TOPICS_ROOT = _default_topics_root()


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from markdown text. Returns {} on failure."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        import yaml
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def read_topic_state(topics_root: Path, slug: str) -> dict:
    """Read state.md frontmatter for a topic."""
    sf = topics_root / slug / "state.md"
    if not sf.exists():
        return {"slug": slug, "title": slug, "_error": "no state.md"}
    try:
        fm = parse_frontmatter(sf.read_text(encoding="utf-8"))
    except Exception:
        return {"slug": slug, "title": slug, "_error": "unreadable state.md"}
    return fm


def count_candidates(topics_root: Path, slug: str) -> int:
    """Count candidate files in L3/candidates/."""
    d = topics_root / slug / "L3" / "candidates"
    if not d.is_dir():
        return 0
    return sum(1 for f in d.iterdir() if f.suffix == ".md")


def list_candidates(topics_root: Path, slug: str) -> list[dict]:
    """List all candidates for a topic with their metadata."""
    d = topics_root / slug / "L3" / "candidates"
    if not d.is_dir():
        return []
    results = []
    for f in sorted(d.iterdir()):
        if f.suffix != ".md":
            continue
        try:
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            fm = {}
        results.append({
            "id": fm.get("candidate_id", f.stem),
            "title": fm.get("claim", f.stem)[:120],
            "type": fm.get("candidate_type", ""),
            "status": fm.get("status", "draft"),
            "depends_on": fm.get("depends_on", []),
        })
    return results


def _iter_sources(topics_root: Path, slug: str):
    """Yield (source_id, source_path) for both source formats.

    Format A (subdirectory): L0/sources/<id>/source.md
    Format B (flat file):   L0/sources/<id>.md
    """
    d = topics_root / slug / "L0" / "sources"
    if not d.is_dir():
        return

    seen: set[str] = set()
    for entry in sorted(d.iterdir()):
        if entry.name in seen:
            continue
        if entry.is_dir():
            sm = entry / "source.md"
            if sm.exists():
                seen.add(entry.name)
                yield entry.name, sm
        elif entry.suffix == ".md" and entry.stem not in seen:
            seen.add(entry.stem)
            yield entry.stem, entry


def count_sources(topics_root: Path, slug: str) -> int:
    """Count sources (both subdirectory and flat-file formats)."""
    return sum(1 for _ in _iter_sources(topics_root, slug))


def list_sources(topics_root: Path, slug: str) -> list[dict]:
    """List all registered sources for a topic (both formats)."""
    results = []
    for source_id, filepath in _iter_sources(topics_root, slug):
        fm = {}
        try:
            fm = parse_frontmatter(filepath.read_text(encoding="utf-8"))
        except Exception:
            pass
        results.append({
            "id": source_id,
            "title": fm.get("title", source_id),
            "type": fm.get("type", "unknown"),
            "role": fm.get("role", ""),
            "arxiv_id": fm.get("arxiv_id", ""),
        })
    return results


def evaluate_gate(fm: dict) -> dict:
    """Simple heuristic gate status from frontmatter fields."""
    gs = fm.get("gate_status", "")
    return {
        "status": gs,
        "missing": [] if gs == "ready" or gs == "clean" else [gs],
    }


def get_l4_jobs(fm: dict) -> list[dict]:
    """Extract L4 job info from state frontmatter."""
    bg = fm.get("l4_background_status", "")
    if not bg or bg == "idle":
        return []
    return [{
        "job_id": fm.get("l4_job_id", ""),
        "status": bg,
        "host": fm.get("l4_job_host", fm.get("compute", "")),
        "estimated_time": fm.get("l4_job_estimated_time", ""),
    }]


def build_topic_list(topics_root: Path) -> list[dict]:
    """Build the full topic overview list."""
    topics = []
    for d in sorted(topics_root.iterdir()):
        if not d.is_dir():
            continue
        if d.name in ("L2", "aitp-protocol-v3"):
            continue
        slug = d.name
        fm = read_topic_state(topics_root, slug)
        if fm.get("_error"):
            topics.append({
                "slug": slug, "title": slug,
                "stage": "?", "posture": "", "lane": "unspecified",
                "gate_status": "not_evaluated",
                "sources_count": 0, "candidates_count": 0,
            })
            continue
        topics.append({
            "slug": slug,
            "title": fm.get("title", slug),
            "stage": fm.get("stage", "?"),
            "posture": fm.get("posture", fm.get("l3_activity", "")),
            "lane": fm.get("lane", "unspecified"),
            "gate_status": fm.get("gate_status", "not_evaluated"),
            "sources_count": count_sources(topics_root, slug),
            "candidates_count": count_candidates(topics_root, slug),
        })
    return topics


def build_topic_detail(topics_root: Path, slug: str) -> dict:
    """Build the full detail for a single topic."""
    fm = read_topic_state(topics_root, slug)
    title = fm.pop("title", slug) if isinstance(fm, dict) else slug
    _error = fm.pop("_error", None) if isinstance(fm, dict) else None

    return {
        "slug": slug,
        "title": title,
        "_error": _error,
        "state": {
            "stage": fm.get("stage", "?"),
            "posture": fm.get("posture", fm.get("l3_activity", "")),
            "lane": fm.get("lane", "unspecified"),
            "status": fm.get("status", ""),
            "compute": fm.get("compute", None),
            "protocol_version": fm.get("protocol_version", ""),
            "l3_subplane": fm.get("l3_subplane", ""),
            "created_at": fm.get("created_at", ""),
            "domains": fm.get("domains", []),
        },
        "gate": evaluate_gate(fm),
        "candidates": list_candidates(topics_root, slug),
        "sources": list_sources(topics_root, slug),
        "l4_jobs": get_l4_jobs(fm),
    }


# --- HTTP Server ---

class DashboardHandler(SimpleHTTPRequestHandler):
    """HTTP handler for AITP Dashboard."""

    topics_root: Path = DEFAULT_TOPICS_ROOT
    html_path: Path = TOOLS_DIR / "aitp_dashboard.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(TOOLS_DIR), **kwargs)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Suppress default stderr logging."""
        _ = (format, args)
        return

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_html(self):
        try:
            html = self.html_path.read_bytes()
        except Exception:
            self.send_error(500, "Cannot read dashboard.html")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/" or path == "/index.html":
            return self._serve_html()

        if path == "/api/health":
            topics = build_topic_list(self.topics_root)
            by_stage = {}
            for t in topics:
                s = t["stage"]
                by_stage[s] = by_stage.get(s, 0) + 1
            return self._json({
                "total_topics": len(topics),
                "by_stage": by_stage,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "topics": topics,
            })

        if path.startswith("/api/topics/"):
            slug = path[len("/api/topics/"):].strip("/")
            if not slug:
                return self._json({"error": "missing topic slug"}, 400)
            topic_dir = self.topics_root / slug
            if not topic_dir.is_dir():
                return self._json({"error": f"topic not found: {slug}"}, 404)
            return self._json(build_topic_detail(self.topics_root, slug))

        # Let SimpleHTTPRequestHandler serve static files from TOOLS_DIR
        return super().do_GET()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AITP Dashboard Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--topics-root", type=str, default=str(DEFAULT_TOPICS_ROOT))
    args = parser.parse_args()

    DashboardHandler.topics_root = Path(args.topics_root)
    if not DashboardHandler.topics_root.is_dir():
        print(f"ERROR: topics root not found: {DashboardHandler.topics_root}", file=sys.stderr)
        sys.exit(1)

    server = HTTPServer(("127.0.0.1", args.port), DashboardHandler)
    print(f"AITP Dashboard → http://127.0.0.1:{args.port}")
    print(f"Topics root   : {DashboardHandler.topics_root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
