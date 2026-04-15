from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        s = str(item).strip()
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return result


def detect_popup_trigger(
    *,
    topic_slug: str,
    promotion_gate: dict[str, Any] | None,
    operator_checkpoint: dict[str, Any] | None,
    pending_decision_points: list[dict[str, Any]],
    h_plane_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Detect whether the topic needs a human-interaction popup and what kind."""
    promotion_gate = promotion_gate or {}
    operator_checkpoint = operator_checkpoint or {}
    h_plane_payload = h_plane_payload or {}

    # Priority 1: promotion gate pending human approval
    promotion_status = str(promotion_gate.get("status") or "not_requested").strip()
    if promotion_status in {"requested", "pending_human_approval"}:
        return {
            "needs_popup": True,
            "popup_kind": "promotion_gate",
            "priority": 1,
            "topic_slug": topic_slug,
            "summary": f"Promotion gate waiting for approval: `{promotion_gate.get('candidate_id') or '(missing)'}`",
        }

    # Priority 2: operator checkpoint requested
    checkpoint_status = str(operator_checkpoint.get("status") or "").strip()
    if checkpoint_status == "requested":
        return {
            "needs_popup": True,
            "popup_kind": "operator_checkpoint",
            "priority": 2,
            "topic_slug": topic_slug,
            "summary": f"Checkpoint requires response: {operator_checkpoint.get('question') or '(missing)'}",
        }

    # Priority 3: pending decision points
    if pending_decision_points:
        first = dict(pending_decision_points[0])
        return {
            "needs_popup": True,
            "popup_kind": "decision_point",
            "priority": 3,
            "topic_slug": topic_slug,
            "summary": f"Decision point pending: {first.get('question') or '(missing)'}",
        }

    # Priority 4: H-plane blocking steering
    steering = h_plane_payload.get("steering") or {}
    steering_status = str(steering.get("status") or "").strip()
    blocking_steering = {
        "active_redirect",
        "paused_by_control_note",
        "active_pause",
        "active_stop",
    }
    if steering_status in blocking_steering:
        return {
            "needs_popup": True,
            "popup_kind": "h_plane_steering",
            "priority": 4,
            "topic_slug": topic_slug,
            "summary": f"H-plane steering is active: `{steering_status}`",
        }

    # Priority 5: H-plane checkpoint requested
    h_checkpoint = h_plane_payload.get("checkpoint") or {}
    if str(h_checkpoint.get("status") or "").strip() == "requested":
        return {
            "needs_popup": True,
            "popup_kind": "h_plane_checkpoint",
            "priority": 5,
            "topic_slug": topic_slug,
            "summary": "H-plane checkpoint is requested.",
        }

    return {
        "needs_popup": False,
        "popup_kind": "none",
        "priority": 99,
        "topic_slug": topic_slug,
        "summary": "No active human gate requires a popup.",
    }


def build_popup_payload(
    *,
    trigger: dict[str, Any],
    promotion_gate: dict[str, Any] | None,
    operator_checkpoint: dict[str, Any] | None,
    pending_decision_points: list[dict[str, Any]],
    h_plane_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a structured popup payload for the detected trigger."""
    popup_kind = str(trigger.get("popup_kind") or "none").strip()
    promotion_gate = promotion_gate or {}
    operator_checkpoint = operator_checkpoint or {}
    h_plane_payload = h_plane_payload or {}

    popup: dict[str, Any] = {
        "popup_kind": popup_kind,
        "topic_slug": trigger["topic_slug"],
        "updated_at": _now_iso(),
        "title": "AITP Human Gate",
        "choices": [],
        "resolve_command": None,
        "context": {},
    }

    if popup_kind == "promotion_gate":
        candidate_id = str(promotion_gate.get("candidate_id") or "").strip() or "(missing)"
        candidate_type = str(promotion_gate.get("candidate_type") or "").strip() or "(missing)"
        title = str(promotion_gate.get("title") or "").strip() or candidate_id
        popup["title"] = "🔷 Promotion Review Gate"
        popup["message"] = f"Candidate `{candidate_id}` ({candidate_type}) is requesting promotion to L2."
        popup["subtitle"] = title
        popup["choices"] = [
            {
                "index": 1,
                "key": "approve",
                "label": "Approve promotion to L2",
                "description": "Promote this candidate to canonical reusable knowledge.",
                "resolve_command": "approve-promotion",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "candidate_id": candidate_id,
                },
            },
            {
                "index": 2,
                "key": "reject",
                "label": "Reject and return to L3",
                "description": "Reject this promotion and keep the candidate in exploratory state.",
                "resolve_command": "reject-promotion",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "candidate_id": candidate_id,
                },
            },
            {
                "index": 3,
                "key": "inspect",
                "label": "View gate details",
                "description": "Read the full promotion gate note before deciding.",
                "resolve_command": "inspect",
                "resolve_args": {
                    "path": str(promotion_gate.get("gate_note_path") or ""),
                },
            },
        ]
        blockers = _dedupe_strings(list(promotion_gate.get("promotion_blockers") or []))
        if blockers:
            popup["context"]["blockers"] = blockers

    elif popup_kind == "operator_checkpoint":
        question = str(operator_checkpoint.get("question") or "").strip() or "AITP needs your input."
        checkpoint_kind = str(operator_checkpoint.get("checkpoint_kind") or "").strip() or "operator_input"
        popup["title"] = f"🔶 Operator Checkpoint — {checkpoint_kind.replace('_', ' ').title()}"
        popup["message"] = question
        popup["subtitle"] = str(operator_checkpoint.get("required_response") or "").strip() or "Please choose an option."
        options = list(operator_checkpoint.get("options") or [])
        choices: list[dict[str, Any]] = []
        for idx, opt in enumerate(options, start=1):
            opt = dict(opt or {})
            choices.append({
                "index": idx,
                "key": str(opt.get("key") or f"option-{idx-1}"),
                "label": str(opt.get("label") or f"Option {idx}"),
                "description": str(opt.get("description") or "").strip(),
                "resolve_command": "resolve-checkpoint",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "option": idx - 1,
                },
            })
        if not choices:
            choices.append({
                "index": 1,
                "key": "acknowledge",
                "label": "Acknowledge and continue",
                "description": "Mark this checkpoint as addressed.",
                "resolve_command": "resolve-checkpoint",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "option": 0,
                },
            })
        choices.append({
            "index": len(choices) + 1,
            "key": "inspect",
            "label": "View checkpoint details",
            "description": "Read the full checkpoint note before deciding.",
            "resolve_command": "inspect",
            "resolve_args": {
                "path": str(operator_checkpoint.get("note_path") or ""),
            },
        })
        popup["choices"] = choices

    elif popup_kind == "decision_point":
        first = dict(pending_decision_points[0]) if pending_decision_points else {}
        question = str(first.get("question") or "").strip() or "A research decision is pending."
        decision_id = str(first.get("decision_id") or "").strip() or "(missing)"
        phase = str(first.get("phase") or "").strip() or "routing"
        popup["title"] = f"🔷 Decision Point — {phase.title()}"
        popup["message"] = question
        popup["subtitle"] = f"Decision ID: {decision_id}"
        opts = list(first.get("options") or [])
        choices = []
        for idx, opt in enumerate(opts, start=1):
            opt = dict(opt or {})
            choices.append({
                "index": idx,
                "key": str(opt.get("key") or f"option-{idx-1}"),
                "label": str(opt.get("label") or f"Option {idx}"),
                "description": str(opt.get("description") or "").strip(),
                "resolve_command": "resolve-decision",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "decision_id": decision_id,
                    "option": idx - 1,
                },
            })
        if not choices:
            choices.append({
                "index": 1,
                "key": "acknowledge",
                "label": "Acknowledge",
                "description": "Record a neutral resolution for this decision.",
                "resolve_command": "resolve-decision",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "decision_id": decision_id,
                    "option": 0,
                },
            })
        popup["choices"] = choices

    elif popup_kind in {"h_plane_steering", "h_plane_checkpoint"}:
        steering = h_plane_payload.get("steering") or {}
        directive = str(steering.get("directive") or "").strip()
        summary = str(steering.get("summary") or "").strip()
        popup["title"] = "🔶 H-Plane Steering Active"
        popup["message"] = summary or "Human steering is blocking the bounded loop."
        popup["subtitle"] = f"Directive: {directive or '(none)'}"
        popup["choices"] = [
            {
                "index": 1,
                "key": "steer_continue",
                "label": "Continue",
                "description": "Release the block and allow the topic to continue.",
                "resolve_command": "steer-topic",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "decision": "continue",
                },
            },
            {
                "index": 2,
                "key": "steer_pause",
                "label": "Pause topic",
                "description": "Keep the topic paused in the registry.",
                "resolve_command": "steer-topic",
                "resolve_args": {
                    "topic_slug": trigger["topic_slug"],
                    "decision": "pause",
                },
            },
            {
                "index": 3,
                "key": "inspect",
                "label": "View H-plane audit",
                "description": "Read the full H-plane audit note.",
                "resolve_command": "inspect",
                "resolve_args": {
                    "path": str(steering.get("control_note_path") or ""),
                },
            },
        ]

    else:
        popup["title"] = "AITP"
        popup["message"] = "No active human gate requires interaction."
        popup["choices"] = []

    return popup


def render_popup_markdown(popup: dict[str, Any]) -> str:
    """Render a popup payload into a Superpowers-style terminal popup."""
    title = str(popup.get("title") or "AITP Human Gate")
    message = str(popup.get("message") or "").strip()
    subtitle = str(popup.get("subtitle") or "").strip()
    choices = list(popup.get("choices") or [])
    popup_kind = str(popup.get("popup_kind") or "none")

    if popup_kind == "none":
        return f"{title}\n{message}"

    width = 72
    lines: list[str] = []

    def _box_line(text: str, align: str = "left") -> str:
        pad = width - 4 - len(text)
        if align == "center":
            left = pad // 2
            right = pad - left
            return f"║ {' ' * left}{text}{' ' * right} ║"
        return f"║ {text}{' ' * (width - 4 - len(text))} ║"

    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append(_box_line(title, "center"))
    lines.append("╠" + "═" * (width - 2) + "╣")

    if message:
        for chunk in _wrap_text(message, width - 4):
            lines.append(_box_line(chunk))
        lines.append(_box_line(""))

    if subtitle:
        for chunk in _wrap_text(subtitle, width - 4):
            lines.append(_box_line(chunk))
        lines.append(_box_line(""))

    if choices:
        lines.append(_box_line("Options:", "left"))
        lines.append(_box_line(""))
        for choice in choices:
            idx = choice.get("index")
            label = str(choice.get("label") or "")
            desc = str(choice.get("description") or "").strip()
            header = f"[{idx}] {label}"
            lines.append(_box_line(f"  {header}"))
            if desc:
                for chunk in _wrap_text(f"      {desc}", width - 4):
                    lines.append(_box_line(chunk))
            lines.append(_box_line(""))

    context = dict(popup.get("context") or {})
    blockers = context.get("blockers")
    if blockers:
        lines.append(_box_line("Blockers:", "left"))
        lines.append(_box_line(""))
        for blocker in blockers:
            for chunk in _wrap_text(f"  • {blocker}", width - 4):
                lines.append(_box_line(chunk))
        lines.append(_box_line(""))

    lines.append("╚" + "═" * (width - 2) + "╝")
    return "\n".join(lines)


def _wrap_text(text: str, width: int) -> list[str]:
    """Simple word-wrap for box content."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip() if current else word
    if current:
        lines.append(current)
    return lines or [""]


def resolve_popup_choice(
    service: Any,
    *,
    popup: dict[str, Any],
    choice_index: int,
    comment: str | None = None,
    resolved_by: str = "human",
) -> dict[str, Any]:
    """Resolve a popup choice by delegating to the appropriate service method."""
    choices = list(popup.get("choices") or [])
    choice = next((c for c in choices if int(c.get("index") or -1) == choice_index), None)
    if choice is None:
        raise ValueError(f"Invalid popup choice index: {choice_index}")

    cmd = str(choice.get("resolve_command") or "").strip()
    args = dict(choice.get("resolve_args") or {})
    topic_slug = str(args.get("topic_slug") or popup.get("topic_slug") or "").strip()

    if cmd == "inspect":
        path = str(args.get("path") or "").strip()
        return {
            "resolved": False,
            "action": "inspect",
            "path": path,
            "message": f"Please inspect: {path}",
        }

    if cmd == "approve-promotion":
        return service.approve_promotion(
            topic_slug=topic_slug,
            candidate_id=str(args["candidate_id"]),
            approved_by=resolved_by,
            notes=comment,
        )

    if cmd == "reject-promotion":
        return service.reject_promotion(
            topic_slug=topic_slug,
            candidate_id=str(args["candidate_id"]),
            rejected_by=resolved_by,
            notes=comment,
        )

    if cmd == "resolve-checkpoint":
        return service.resolve_operator_checkpoint(
            topic_slug=topic_slug,
            option_index=int(args["option"]),
            comment=comment,
            resolved_by=resolved_by,
        )

    if cmd == "resolve-decision":
        from .decision_point_handler import resolve_decision_point
        return resolve_decision_point(
            topic_slug=topic_slug,
            decision_id=str(args["decision_id"]),
            option_index=int(args["option"]),
            comment=comment,
            resolved_by=resolved_by,
            kernel_root=service.kernel_root,
        )

    if cmd == "steer-topic":
        return service.steer_topic(
            topic_slug=topic_slug,
            decision=str(args["decision"]),
            updated_by=resolved_by,
            summary=comment or "",
        )

    raise ValueError(f"Unsupported popup resolve command: {cmd}")
