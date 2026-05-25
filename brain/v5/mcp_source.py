"""MCP wrappers for source reconstruction surfaces."""

from __future__ import annotations

from pathlib import Path

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.source_reconstruction import (
    audit_source_reconstruction,
    build_source_reconstruction_manifest,
    build_source_reconstruction_review_packet,
)
from brain.v5.workspace import init_workspace


def _ws(base: str):
    return init_workspace(Path(base))


def aitp_v5_audit_source_reconstruction(base: str, *, claim_id: str) -> dict:
    result = audit_source_reconstruction(_ws(base), claim_id=claim_id)
    return require_valid_public_surface("source_reconstruction_audit", result)


def aitp_v5_build_source_reconstruction_manifest(base: str) -> dict:
    result = build_source_reconstruction_manifest(_ws(base))
    return {"ok": True, **require_valid_public_surface("source_reconstruction_manifest", result)}


def aitp_v5_build_source_reconstruction_review_packet(base: str, *, claim_id: str) -> dict:
    result = build_source_reconstruction_review_packet(_ws(base), claim_id=claim_id)
    return require_valid_public_surface("source_reconstruction_review_packet", result)
