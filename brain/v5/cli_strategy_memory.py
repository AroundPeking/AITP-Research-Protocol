"""CLI handlers for topic-local strategy memory."""

from __future__ import annotations

from dataclasses import asdict

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.strategy_memory import record_strategy_memory


def add_strategy_parser(sp) -> None:
    st = sp.add_parser("strategy"); sts = st.add_subparsers(dest="strategy_command", required=True)
    mem = sts.add_parser("memory"); ms = mem.add_subparsers(dest="strategy_memory_command", required=True)
    rec = ms.add_parser("record")
    rec.add_argument("--topic", required=True, dest="topic_id")
    rec.add_argument("--run", required=True, dest="run_id")
    rec.add_argument("--type", required=True, dest="strategy_type")
    rec.add_argument("--outcome", required=True)
    rec.add_argument("--lesson", required=True)
    rec.add_argument("--next-time-rule", required=True)
    rec.add_argument("--scope", default="")
    rec.add_argument("--source-ref", action="append", default=[], dest="source_refs")
    rec.add_argument("--status", default="active")


def dispatch_strategy_command(args, ws) -> dict:
    if args.strategy_command == "memory" and args.strategy_memory_command == "record":
        memory = record_strategy_memory(
            ws,
            topic_id=args.topic_id,
            run_id=args.run_id,
            strategy_type=args.strategy_type,
            outcome=args.outcome,
            lesson=args.lesson,
            next_time_rule=args.next_time_rule,
            scope=args.scope,
            source_refs=args.source_refs,
            status=args.status,
        )
        return require_valid_public_surface("strategy_memory_record", {"ok": True, **asdict(memory)})
    raise SystemExit(f"unsupported strategy command: {args.strategy_command}")
