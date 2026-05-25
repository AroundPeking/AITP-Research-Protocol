"""CLI helpers for source reconstruction audit surfaces."""

from __future__ import annotations

import argparse

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.source_reconstruction import (
    audit_source_reconstruction,
    build_source_reconstruction_manifest,
    build_source_reconstruction_review_packet,
)


def add_source_parser(sp: argparse._SubParsersAction) -> None:
    source = sp.add_parser("source")
    commands = source.add_subparsers(dest="source_command", required=True)
    audit = commands.add_parser("reconstruction-audit")
    audit.add_argument("--claim", required=True, dest="claim_id")
    commands.add_parser("reconstruction-manifest")
    review = commands.add_parser("reconstruction-review")
    review.add_argument("--claim", required=True, dest="claim_id")


def dispatch_source_command(args: argparse.Namespace, ws) -> dict:
    if args.source_command == "reconstruction-audit":
        return require_valid_public_surface(
            "source_reconstruction_audit",
            audit_source_reconstruction(ws, claim_id=args.claim_id),
        )
    if args.source_command == "reconstruction-manifest":
        return require_valid_public_surface(
            "source_reconstruction_manifest",
            build_source_reconstruction_manifest(ws),
        )
    if args.source_command == "reconstruction-review":
        return require_valid_public_surface(
            "source_reconstruction_review_packet",
            build_source_reconstruction_review_packet(ws, claim_id=args.claim_id),
        )
    raise SystemExit(f"unsupported source command: {args.source_command}")
