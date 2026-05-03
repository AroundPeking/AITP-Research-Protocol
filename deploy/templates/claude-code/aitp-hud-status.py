"""Output a compact AITP dashboard panel for the Claude HUD statusline.

Runs every ~300ms. Uses file timestamp caching to avoid re-reading state.md.
Depends on aitp-panel.py for rendering.
"""
import os
import sys
from pathlib import Path

# Add hooks dir to path so we can import aitp_panel
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aitp_panel import get_active_topic, read_topic_state, render_hud_panel

CACHE_FILE = Path(os.environ.get("TEMP", "/tmp")) / ".aitp_hud_cache_v2"


def main():
    slug = get_active_topic()
    if not slug:
        return

    # Check mtime for cache invalidation
    from aitp_panel import _resolve_topics_root
    root = _resolve_topics_root()
    state_file = root / slug / "state.md"
    try:
        mtime = state_file.stat().st_mtime
    except OSError:
        return

    # Return cached result if unchanged
    if CACHE_FILE.exists():
        try:
            cached = CACHE_FILE.read_text(encoding="utf-8").strip().split("\n", 2)
            if len(cached) >= 3 and cached[0] == f"{slug}:{mtime}":
                print("\n".join(cached[1:]))
                return
        except Exception:
            pass

    fm = read_topic_state(slug)
    if not fm:
        return

    panel = render_hud_panel(fm, slug)

    # Cache
    try:
        CACHE_FILE.write_text(f"{slug}:{mtime}\n{panel}", encoding="utf-8")
    except Exception:
        pass

    print(panel)


if __name__ == "__main__":
    main()
