from __future__ import annotations

import argparse
from typing import Any


PAPERQA_COMMANDS = {
    "consult-paperqa",
}


def register_paperqa_commands(subparsers: argparse._SubParsersAction[Any]) -> None:
    consult_paperqa = subparsers.add_parser(
        "consult-paperqa",
        help="Consult topic-scoped sources through an optional PaperQA retrieval path",
    )
    consult_paperqa.add_argument("--topic-slug", required=True)
    consult_paperqa.add_argument("--query-text", required=True)
    consult_paperqa.add_argument("--llm")
    consult_paperqa.add_argument("--summary-llm")
    consult_paperqa.add_argument("--embedding")
    consult_paperqa.add_argument("--max-sources", type=int, default=8)
    consult_paperqa.add_argument("--updated-by", default="aitp-cli")
    consult_paperqa.add_argument("--json", action="store_true")


def dispatch_paperqa_command(args: argparse.Namespace, service: Any) -> dict[str, Any] | None:
    if args.command != "consult-paperqa":
        return None
    return service.consult_paperqa(
        topic_slug=args.topic_slug,
        query_text=args.query_text,
        llm=args.llm,
        summary_llm=args.summary_llm,
        embedding=args.embedding,
        max_sources=args.max_sources,
        updated_by=args.updated_by,
    )
