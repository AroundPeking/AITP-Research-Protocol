"""CLI dispatch for interaction-preview surfaces."""

from __future__ import annotations

import argparse

from brain.v5.interaction_preview import build_interaction_recording_preview
from brain.v5.public_surfaces import require_valid_public_surface


def add_interaction_parser(sp: argparse._SubParsersAction) -> None:
    parser = sp.add_parser("interaction")
    sub = parser.add_subparsers(dest="interaction_command", required=True)
    preview = sub.add_parser("preview")
    preview.add_argument("session_id")


def dispatch_interaction_command(args: argparse.Namespace, ws) -> dict:
    if args.interaction_command == "preview":
        return require_valid_public_surface(
            "interaction_recording_preview",
            build_interaction_recording_preview(ws, args.session_id),
        )
    raise SystemExit(f"unsupported interaction command: {args.interaction_command}")
