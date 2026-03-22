#!/usr/bin/env python3
"""Dispatch reviewed runtime-controller actions through AITPService."""

from __future__ import annotations

import argparse
import json
import sys

from _aitp_runtime_common import KNOWLEDGE_ROOT, RESEARCH_ROOT, resolve_topic_slug

if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from knowledge_hub.aitp_service import AITPService


SUPPORTED_ACTIONS = {
    "apply_candidate_split_contract",
    "reactivate_deferred_candidate",
    "spawn_followup_subtopics",
    "reintegrate_followup_subtopic",
    "assess_topic_completion",
    "prepare_lean_bridge",
    "auto_promote_candidate",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic-slug")
    parser.add_argument("--action-type", choices=sorted(SUPPORTED_ACTIONS), required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--entry-id")
    parser.add_argument("--query")
    parser.add_argument("--receipt-id")
    parser.add_argument("--child-topic-slug")
    parser.add_argument("--candidate-id")
    parser.add_argument("--backend-id")
    parser.add_argument("--target-backend-root")
    parser.add_argument("--domain")
    parser.add_argument("--subdomain")
    parser.add_argument("--source-id")
    parser.add_argument("--source-section")
    parser.add_argument("--source-section-title")
    parser.add_argument("--notes")
    parser.add_argument("--updated-by", default="openclaw")
    parser.add_argument("--json", action="store_true")
    return parser


def _emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return
    print(json.dumps(payload, ensure_ascii=True))


def _service() -> AITPService:
    return AITPService(kernel_root=KNOWLEDGE_ROOT, repo_root=RESEARCH_ROOT.parent)


def main() -> int:
    args = build_parser().parse_args()
    topic_slug = resolve_topic_slug(args.topic_slug)
    service = _service()

    if args.action_type == "apply_candidate_split_contract":
        payload = service.apply_candidate_split_contract(
            topic_slug=topic_slug,
            run_id=args.run_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "reactivate_deferred_candidate":
        payload = service.reactivate_deferred_candidates(
            topic_slug=topic_slug,
            run_id=args.run_id,
            entry_id=args.entry_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "spawn_followup_subtopics":
        payload = service.spawn_followup_subtopics(
            topic_slug=topic_slug,
            run_id=args.run_id,
            query=args.query,
            receipt_id=args.receipt_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "reintegrate_followup_subtopic":
        if not args.child_topic_slug:
            raise SystemExit("reintegrate_followup_subtopic requires --child-topic-slug")
        payload = service.reintegrate_followup_subtopic(
            topic_slug=topic_slug,
            child_topic_slug=args.child_topic_slug,
            run_id=args.run_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "assess_topic_completion":
        payload = service.assess_topic_completion(
            topic_slug=topic_slug,
            run_id=args.run_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "prepare_lean_bridge":
        payload = service.prepare_lean_bridge(
            topic_slug=topic_slug,
            run_id=args.run_id,
            candidate_id=args.candidate_id,
            updated_by=args.updated_by,
        )
    elif args.action_type == "auto_promote_candidate":
        if not args.candidate_id:
            raise SystemExit("auto_promote_candidate requires --candidate-id")
        payload = service.auto_promote_candidate(
            topic_slug=topic_slug,
            candidate_id=args.candidate_id,
            run_id=args.run_id,
            promoted_by=args.updated_by,
            backend_id=args.backend_id,
            target_backend_root=args.target_backend_root,
            domain=args.domain,
            subdomain=args.subdomain,
            source_id=args.source_id,
            source_section=args.source_section,
            source_section_title=args.source_section_title,
            notes=args.notes,
        )
    else:
        raise SystemExit(f"Unsupported action type: {args.action_type}")

    _emit(payload, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
