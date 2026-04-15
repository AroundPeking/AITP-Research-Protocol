from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_CONSULTATION_RETRIEVAL_PROFILE = "l1_provisional_understanding"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def consultation_followup_selection_paths(runtime_root: Path) -> dict[str, Path]:
    return {
        "json": runtime_root / "consultation_followup_selection.active.json",
        "note": runtime_root / "consultation_followup_selection.active.md",
    }


def derive_consultation_followup_query(
    *,
    topic_slug: str,
    topic_state: dict[str, Any],
    research_question_contract: dict[str, Any] | None,
) -> str:
    for candidate in (
        str((research_question_contract or {}).get("question") or "").strip(),
        str((research_question_contract or {}).get("title") or "").strip(),
        str(topic_state.get("title") or "").strip(),
        topic_slug.replace("-", " ").strip(),
    ):
        if candidate:
            return candidate
    return topic_slug.replace("-", " ").strip() or topic_slug


def select_bounded_consultation_candidate(
    *,
    topic_slug: str,
    consult_payload: dict[str, Any],
) -> dict[str, Any]:
    staged_hits = [
        row for row in (consult_payload.get("staged_hits") or []) if isinstance(row, dict)
    ]
    topic_local_hits = [
        row
        for row in staged_hits
        if str(row.get("topic_slug") or "").strip() == topic_slug
    ]
    if not topic_local_hits:
        return {
            "status": "no_selection",
            "selected_candidate_id": "",
            "selected_candidate_title": "",
            "selected_candidate_path": "",
            "selected_candidate_trust_surface": "",
            "selected_candidate_topic_slug": "",
            "selection_reason": "No topic-local staged hit was available for bounded automatic selection.",
        }

    winner = topic_local_hits[0]
    return {
        "status": "selected",
        "selected_candidate_id": str(
            winner.get("entry_id") or winner.get("id") or ""
        ).strip(),
        "selected_candidate_title": str(winner.get("title") or "").strip(),
        "selected_candidate_path": str(winner.get("path") or "").strip(),
        "selected_candidate_trust_surface": str(
            winner.get("trust_surface") or ""
        ).strip(),
        "selected_candidate_topic_slug": str(
            winner.get("topic_slug") or ""
        ).strip(),
        "selection_reason": "Selected the first topic-local staged hit from the bounded consultation result.",
    }


def build_consultation_followup_selection_payload(
    *,
    topic_slug: str,
    run_id: str | None,
    query_text: str,
    retrieval_profile: str,
    consultation_paths: dict[str, str],
    consult_payload: dict[str, Any],
    selected: dict[str, Any],
    updated_by: str,
) -> dict[str, Any]:
    return {
        "topic_slug": topic_slug,
        "run_id": run_id,
        "status": str(selected.get("status") or "no_selection"),
        "query_text": query_text,
        "retrieval_profile": retrieval_profile,
        "consultation_index_path": str(
            consultation_paths.get("consultation_index_path") or ""
        ),
        "consultation_result_path": str(
            consultation_paths.get("consultation_result_path") or ""
        ),
        "selected_candidate_id": str(selected.get("selected_candidate_id") or ""),
        "selected_candidate_title": str(
            selected.get("selected_candidate_title") or ""
        ),
        "selected_candidate_path": str(selected.get("selected_candidate_path") or ""),
        "selected_candidate_trust_surface": str(
            selected.get("selected_candidate_trust_surface") or ""
        ),
        "selected_candidate_topic_slug": str(
            selected.get("selected_candidate_topic_slug") or ""
        ),
        "selection_reason": str(selected.get("selection_reason") or ""),
        "primary_hit_count": len(consult_payload.get("primary_hits") or []),
        "staged_hit_count": len(consult_payload.get("staged_hits") or []),
        "updated_at": now_iso(),
        "updated_by": updated_by,
    }


def render_consultation_followup_selection_markdown(payload: dict[str, Any]) -> str:
    return (
        "# Consultation Followup Selection\n\n"
        f"- Status: `{payload.get('status') or 'no_selection'}`\n"
        f"- Query: `{payload.get('query_text') or ''}`\n"
        f"- Retrieval profile: `{payload.get('retrieval_profile') or ''}`\n"
        f"- Selected candidate: `{payload.get('selected_candidate_id') or '(none)'}`\n"
        f"- Selection reason: {payload.get('selection_reason') or '(missing)'}\n"
    )
