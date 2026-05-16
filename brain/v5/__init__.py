"""AITP v5 kernel primitives.

This package is intentionally independent from the legacy MCP tool surface.
MCP, CLI, hooks, and skills should call into these modules instead of
duplicating protocol logic.
"""

from brain.v5.paths import WorkspacePaths
from brain.v5.workspace import init_workspace

__all__ = ["WorkspacePaths", "init_workspace"]
