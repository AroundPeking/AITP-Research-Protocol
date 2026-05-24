"""MCP wrappers for interaction-preview surfaces."""

from __future__ import annotations

from pathlib import Path

from brain.v5.interaction_preview import build_interaction_recording_preview
from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.workspace import init_workspace


def aitp_v5_preview_interaction_recording(base: str, *, session_id: str) -> dict:
    return require_valid_public_surface(
        "interaction_recording_preview",
        build_interaction_recording_preview(init_workspace(Path(base)), session_id),
    )
