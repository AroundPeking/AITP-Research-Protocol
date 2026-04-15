from __future__ import annotations

import argparse
from typing import Any


L1_GRAPH_COMMANDS = {
    "sync-l1-graph-export-to-theoretical-physics-brain",
}


def register_l1_graph_commands(subparsers: argparse._SubParsersAction[Any]) -> None:
    sync_graph_export = subparsers.add_parser(
        "sync-l1-graph-export-to-theoretical-physics-brain",
        help="Mirror the repo-local L1 concept-graph export into the configured theoretical-physics brain",
    )
    sync_graph_export.add_argument("--topic-slug", required=True)
    sync_graph_export.add_argument("--target-root")
    sync_graph_export.add_argument("--updated-by", default="aitp-cli")
    sync_graph_export.add_argument("--json", action="store_true")


def dispatch_l1_graph_command(args: argparse.Namespace, service: Any) -> dict[str, Any] | None:
    if args.command == "sync-l1-graph-export-to-theoretical-physics-brain":
        return service.sync_l1_graph_export_to_theoretical_physics_brain(
            topic_slug=args.topic_slug,
            updated_by=args.updated_by,
            target_root=args.target_root,
        )
    return None
