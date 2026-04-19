"""Research-facing next-action synthesis.

Replaces runtime-jargon summaries like "inspect the runtime resume state"
with research-shaped language drawn from the active contract and source index.
"""

from __future__ import annotations

import re
from typing import Any


def synthesize_research_next_action(
    *,
    topic_slug: str,
    research_contract: dict[str, Any] | None = None,
    source_index: list[dict[str, Any]] | None = None,
    queue_head: dict[str, Any] | None = None,
    topic_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rc = research_contract or {}
    sources = source_index or []
    ts = topic_state or {}

    question = str(rc.get("question") or "").strip()
    has_sources = len(sources) > 0
    has_question = bool(question)
    has_run = bool(ts.get("latest_run_id") or ts.get("resume_stage"))

    is_bootstrap = not has_question and not has_sources and not has_run
    action_type = "inspect_resume_state"

    if is_bootstrap:
        return {
            "summary": f"Initialize the research workspace for topic `{topic_slug}`.",
            "action_type": action_type,
            "is_bootstrap": True,
        }

    key_phrases = _extract_key_phrases(question)
    phrase_str = key_phrases[0] if key_phrases else topic_slug

    if queue_head is None:
        if has_question:
            summary = (
                f"Bootstrap the research workflow for the bounded question on "
                f"{phrase_str} before continuing."
            )
            if has_sources:
                summary = (
                    f"Recover the source basis interpretation for the bounded question on "
                    f"{phrase_str} before continuing execution."
                )
        elif has_sources:
            summary = (
                f"Register the source basis for `{topic_slug}` and formulate "
                f"the bounded research question."
            )
        else:
            summary = f"Resume the research workflow for `{topic_slug}`."
        return {
            "summary": summary,
            "action_type": action_type,
            "is_bootstrap": False,
        }

    existing_summary = str(queue_head.get("summary") or "").strip()
    if _is_generic_runtime_summary(existing_summary) and has_question:
        if "L1 vault" in existing_summary or "L2 staging" in existing_summary:
            summary = (
                f"Review the compiled source basis for the bounded question on "
                f"{phrase_str} before continuing interpretation."
            )
        elif "Layer 2 writeback" in existing_summary:
            summary = (
                f"Confirm the promoted reusable outcome for the bounded question on "
                f"{phrase_str} before opening another bounded route."
            )
        else:
            summary = (
                f"Continue the bounded research on {phrase_str}; "
                f"recover any missing source or derivation evidence."
            )
        return {
            "summary": summary,
            "action_type": action_type,
            "is_bootstrap": False,
        }

    return {
        "summary": existing_summary,
        "action_type": str(queue_head.get("action_type") or action_type),
        "is_bootstrap": False,
    }


_GENERIC_RUNTIME_PHRASES = [
    "inspect the runtime resume state",
    "no explicit pending actions were found",
    "inspect the compiled l1 vault",
    "inspect the current l2 staging",
    "inspect the promoted layer 2",
]


def _is_generic_runtime_summary(summary: str) -> bool:
    lower = summary.lower()
    return any(phrase in lower for phrase in _GENERIC_RUNTIME_PHRASES)


_KEY_PHRASE_PATTERN = re.compile(
    r"(?:[A-Z][a-z]+(?:-[a-z]+)*|[a-z]{3,})(?:\s+(?:of|for|in|on|the|a|an)\s+[a-z]+)*",
)


def _extract_key_phrases(question: str) -> list[str]:
    if not question:
        return []
    question_clean = question.strip().rstrip("?.").strip()
    if not question_clean:
        return []

    words = question_clean.split()
    phrases: list[str] = []
    current: list[str] = []

    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "that", "this", "these", "those", "it", "its",
        "and", "or", "but", "not", "no", "if", "then",
    }

    for w in words:
        wl = w.lower().strip(".,;:!?")
        if wl and wl not in stop_words:
            current.append(w)
        else:
            if len(current) >= 2:
                phrases.append(" ".join(current))
            current = []

    if len(current) >= 2:
        phrases.append(" ".join(current))

    if not phrases and words:
        content_words = [w for w in words if w.lower().strip(".,;:!?") not in stop_words]
        if content_words:
            phrases.append(" ".join(content_words[:5]))

    return phrases[:3]
