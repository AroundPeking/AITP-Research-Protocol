"""CLI dispatch for legacy migration surfaces."""

from __future__ import annotations

from brain.v5.legacy_bridge import migrate_legacy_topic_to_v5
from brain.v5.legacy_migration_audit import audit_legacy_migration_coverage
from brain.v5.public_surfaces import require_valid_public_surface


def add_legacy_parser(subparsers) -> None:
    parser = subparsers.add_parser("legacy")
    legacy_subparsers = parser.add_subparsers(dest="legacy_command", required=True)
    migrate = legacy_subparsers.add_parser("migrate")
    migrate.add_argument("topic_dir")
    migrate.add_argument("--context", required=True, dest="context_id")
    migrate.add_argument("--session", required=True, dest="session_id")
    audit = legacy_subparsers.add_parser("migration-audit")
    audit.add_argument("--migration-dir", default="")


def dispatch_legacy_command(args, ws) -> dict:
    if args.legacy_command == "migrate":
        result = migrate_legacy_topic_to_v5(
            ws,
            args.topic_dir,
            context_id=args.context_id,
            session_id=args.session_id,
        )
        return {"ok": True, **require_valid_public_surface("legacy_migration_result", result)}
    if args.legacy_command == "migration-audit":
        audit = audit_legacy_migration_coverage(ws, migration_dir=args.migration_dir or None)
        return {"ok": True, **require_valid_public_surface("legacy_migration_coverage_audit", audit)}
    raise ValueError(f"unsupported legacy command: {args.legacy_command}")
