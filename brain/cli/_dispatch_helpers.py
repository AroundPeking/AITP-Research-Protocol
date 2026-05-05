"""Shared helpers for MCP-to-CLI dispatch.

Used by brain/mcp_server.py to invoke CLI commands via direct function call.
Constructs argparse.Namespace from MCP parameters and calls CLI functions.
"""

from __future__ import annotations

import argparse
from typing import Any


def dispatch(cmd_fn, success_msg: str = "", **kwargs) -> str:
    """Invoke a CLI command function directly.

    Filters out kwargs that the CLI function doesn't expect,
    constructs a Namespace, calls the function, and converts
    the return value to an MCP-compatible string.
    """
    args = argparse.Namespace(**kwargs)
    result = cmd_fn(args)
    if result != 0:
        return f"CLI command failed (exit {result})"
    return success_msg or "OK"
