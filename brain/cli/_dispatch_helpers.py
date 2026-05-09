"""Shared helpers for MCP-to-CLI dispatch.

Used by brain/mcp_server.py to invoke CLI commands via direct function call.
Constructs argparse.Namespace from MCP parameters and calls CLI functions.
"""

from __future__ import annotations

import argparse
import inspect
import traceback
from typing import Any


def dispatch(cmd_fn, success_msg: str = "", **kwargs) -> str:
    """Invoke a CLI command function directly.

    Constructs a Namespace from all kwargs, then calls cmd_fn(args).
    CLI commands use a single argparse.Namespace argument.

    Returns:
        success_msg on success (or "OK" if empty).
        "CLI command failed (exit N)" when CLI returns non-zero int.
        "CLI internal error: ExceptionType(message)" when CLI raises.
    """
    sig = inspect.signature(cmd_fn)
    params = list(sig.parameters.keys())

    # CLI commands take a single `args` Namespace — pass all kwargs through.
    # For functions with named params, filter to only accepted kwargs.
    if len(params) == 1 and params[0] == 'args':
        ns = argparse.Namespace(**kwargs)
    else:
        known = set(params)
        filtered = {k: v for k, v in kwargs.items() if k in known}
        ns = argparse.Namespace(**filtered)

    try:
        result = cmd_fn(ns)
    except SystemExit as e:
        if e.code is not None and e.code != 0:
            return f"CLI command failed (exit {e.code})"
        return success_msg or "OK"
    except Exception as e:
        return (
            f"CLI internal error: {type(e).__name__}({e})\n"
            f"{traceback.format_exc()[-500:]}"
        )

    # None (implicit return) and int 0 both mean success.
    # Any non-zero int is a CLI failure code.
    if result is not None and result != 0:
        return f"CLI command failed (exit {result})"
    return success_msg or "OK"
