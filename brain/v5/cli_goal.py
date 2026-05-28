"""CLI handlers for goal continuation audit packets."""

from __future__ import annotations

import json

from brain.v5.goal_continuation import (
    list_goal_continuations,
    read_latest_goal_continuation,
    write_goal_continuation,
)
from brain.v5.public_surfaces import require_valid_public_surface


def add_goal_parser(sp) -> None:
    goal = sp.add_parser("goal")
    gs = goal.add_subparsers(dest="goal_command", required=True)

    write_p = gs.add_parser("write")
    write_p.add_argument("--objective", required=True)
    write_p.add_argument("--changed-files", default="")
    write_p.add_argument("--tests-run", default="")
    write_p.add_argument("--tests-passed", default=None, dest="tests_passed_raw")
    write_p.add_argument("--smoke-commands", default="")
    write_p.add_argument("--smoke-passed", default=None, dest="smoke_passed_raw")
    write_p.add_argument("--readiness-json", default="{}")
    write_p.add_argument("--next-actions", default="")
    write_p.add_argument("--trust-boundary", default="")
    write_p.add_argument("--blocking-backlog", default="")
    write_p.add_argument("--notes", default="")
    write_p.add_argument("--session-id", default="")
    write_p.add_argument("--commit-ref", default="")

    gs.add_parser("latest")
    gs.add_parser("list")


def _csv(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def _bool_or_none(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() in ("true", "1", "yes")


def dispatch_goal_command(args, ws) -> dict:
    if args.goal_command == "write":
        readiness = {}
        if args.readiness_json and args.readiness_json != "{}":
            readiness = json.loads(args.readiness_json)
        packet = write_goal_continuation(
            ws,
            objective=args.objective,
            changed_files=_csv(args.changed_files),
            tests_run=_csv(args.tests_run),
            tests_passed=_bool_or_none(args.tests_passed_raw),
            smoke_commands=_csv(args.smoke_commands),
            smoke_passed=_bool_or_none(args.smoke_passed_raw),
            readiness_outcome=readiness or None,
            next_actions=_csv(args.next_actions),
            trust_boundary=args.trust_boundary,
            blocking_backlog=_csv(args.blocking_backlog),
            notes=args.notes,
            session_id=args.session_id,
            commit_ref=args.commit_ref,
        )
        return require_valid_public_surface("goal_continuation_packet", packet)
    if args.goal_command == "latest":
        result = read_latest_goal_continuation(ws)
        if result is None:
            return {"kind": "goal_continuation_packet", "found": False}
        return result
    if args.goal_command == "list":
        packets = list_goal_continuations(ws)
        return {
            "kind": "goal_continuation_list",
            "count": len(packets),
            "packet_ids": [p.get("packet_id", "") for p in packets],
            "latest_objectives": [
                {"packet_id": p.get("packet_id", ""), "objective": (p.get("objective") or "")[:120]}
                for p in packets[-5:]
            ],
        }
    raise SystemExit(f"unsupported goal command: {args.goal_command}")
