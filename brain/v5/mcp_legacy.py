"""MCP wrappers for legacy migration surfaces."""

from __future__ import annotations

from pathlib import Path

from brain.v5.legacy_bridge import migrate_legacy_topic_to_v5
from brain.v5.legacy_migration_audit import audit_legacy_migration_coverage
from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.workspace import init_workspace


def _ws(base: str):
    return init_workspace(Path(base))


def aitp_v5_migrate_legacy_topic_to_v5(
    base: str,
    *,
    topic_dir: str,
    context_id: str,
    session_id: str,
) -> dict:
    result = migrate_legacy_topic_to_v5(
        _ws(base),
        topic_dir,
        context_id=context_id,
        session_id=session_id,
    )
    return {"ok": True, **require_valid_public_surface("legacy_migration_result", result)}


def aitp_v5_audit_legacy_migration_coverage(base: str, *, migration_dir: str = "") -> dict:
    result = audit_legacy_migration_coverage(_ws(base), migration_dir=migration_dir or None)
    return {"ok": True, **require_valid_public_surface("legacy_migration_coverage_audit", result)}
