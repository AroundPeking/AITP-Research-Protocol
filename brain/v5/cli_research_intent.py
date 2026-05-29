"""CLI handlers for vNext research-intent surfaces."""

from __future__ import annotations

from dataclasses import asdict

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.research_intent import materialize_steering_redirect, record_research_intent_packet


def add_intent_parser(sp) -> None:
    ip = sp.add_parser("intent"); ips = ip.add_subparsers(dest="intent_command", required=True)
    ipp = ips.add_parser("packet"); ipps = ipp.add_subparsers(dest="intent_packet_command", required=True)
    ipr = ipps.add_parser("record")
    ipr.add_argument("--topic", required=True, dest="topic_id")
    ipr.add_argument("--idea", required=True, dest="initial_idea")
    ipr.add_argument("--novelty-target", default="")
    ipr.add_argument("--non-goal", action="append", default=[], dest="non_goals")
    ipr.add_argument("--required-first-validation-route", default="")
    ipr.add_argument("--initial-evidence-bar", default="")
    ipr.add_argument("--clarification-question", action="append", default=[], dest="clarification_questions")
    ipr.add_argument("--status", default="needs_clarification")

    isr = ips.add_parser("steering"); isrs = isr.add_subparsers(dest="intent_steering_command", required=True)
    ism = isrs.add_parser("materialize")
    ism.add_argument("--topic", required=True, dest="topic_id")
    ism.add_argument("--steering", required=True, dest="steering_text")
    ism.add_argument("--novelty-target", required=True)
    ism.add_argument("--scope", required=True)
    ism.add_argument("--acceptance-posture", required=True)
    ism.add_argument("--control-note", default="")
    ism.add_argument("--session", default="", dest="session_id")
    ism.add_argument("--status", default="active")


def dispatch_intent_command(args, ws) -> dict:
    if args.intent_command == "packet" and args.intent_packet_command == "record":
        packet = record_research_intent_packet(
            ws,
            topic_id=args.topic_id,
            initial_idea=args.initial_idea,
            novelty_target=args.novelty_target,
            non_goals=args.non_goals,
            required_first_validation_route=args.required_first_validation_route,
            initial_evidence_bar=args.initial_evidence_bar,
            clarification_questions=args.clarification_questions,
            status=args.status,
        )
        return require_valid_public_surface("research_intent_packet", {"ok": True, **asdict(packet)})

    if args.intent_command == "steering" and args.intent_steering_command == "materialize":
        decision = materialize_steering_redirect(
            ws,
            topic_id=args.topic_id,
            steering_text=args.steering_text,
            novelty_target=args.novelty_target,
            scope=args.scope,
            acceptance_posture=args.acceptance_posture,
            control_note=args.control_note,
            session_id=args.session_id,
            status=args.status,
        )
        return require_valid_public_surface("steering_decision_record", {"ok": True, **asdict(decision)})

    raise SystemExit(f"unsupported intent command: {args.intent_command}")
