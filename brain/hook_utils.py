"""Thin shim: re-export hooks/hook_utils symbols for backwards compat.

Historical: brain.cli.decorators and brain.cli.contracts once imported from
brain.hook_utils. The canonical module is hooks/hook_utils.py. This file
exists only to prevent ModuleNotFoundError in stale cached MCP processes.
"""
import sys
from pathlib import Path

_hooks_dir = str(Path(__file__).resolve().parents[1] / "hooks")
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from hook_utils import (  # noqa: F401, E402
    _parse_md,
    _read_aitp_config,
    _parse_frontmatter,
    _atomic_write_text,
    _render_md,
)
