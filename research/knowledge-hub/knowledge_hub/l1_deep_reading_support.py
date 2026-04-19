from __future__ import annotations

"""Helpers for source-backed L1 deep-reading enrichment and comparison."""

import re
from datetime import datetime
from typing import Any

from .source_intelligence import detect_assumptions, detect_notation_candidates

READING_DEPTH_STATE_ORDER = {
    "skim": 0,
    "head": 1,
    "sections": 2,
    "full": 3,
}

SECTION_PRIORITY_NEEDLES = (
    "setup",
    "method",
    "derivation",
    "result",
    "discussion",
    "conclusion",
)

REGIME_DESCRIPTOR_PATTERNS = (
    (re.compile(r"\b(?P<value>weak|strong|intermediate)\s+coupling\b", re.IGNORECASE), "coupling"),
    (re.compile(r"\b(?P<value>zero|finite|high|low)\s+temperature\b", re.IGNORECASE), "temperature"),
    (
        re.compile(
            r"\b(?P<value>1d|2d|3d|one-dimensional|two-dimensional|three-dimensional)\b",
            re.IGNORECASE,
        ),
        "dimension",
    ),
    (re.compile(r"\b(?P<value>non-relativistic|relativistic)\b", re.IGNORECASE), "kinematics"),
    (re.compile(r"\b(?P<value>continuum limit|thermodynamic limit)\b", re.IGNORECASE), "limit"),
    (
        re.compile(r"\b(?P<value>open|periodic|closed)\s+boundary conditions?\b", re.IGNORECASE),
        "boundary_condition",
    ),
)

EXTRA_ASSUMPTION_PATTERNS = (
    re.compile(r"\bsuppos(?:e|es|ed|ing)\s+(?P<clause>[^.;,\n]+)", re.IGNORECASE),
    re.compile(r"\btake\s+(?P<clause>[^.;,\n]+?)\s+to\s+be\b", re.IGNORECASE),
    re.compile(r"\bvalid\s+only\s+when\s+(?P<clause>[^.;,\n]+)", re.IGNORECASE),
)

OPPOSING_REGIME_VALUES: dict[str, dict[str, str]] = {
    "coupling": {
        "weak": "strong",
        "strong": "weak",
    },
    "temperature": {
        "zero": "finite",
        "finite": "zero",
    },
    "kinematics": {
        "non-relativistic": "relativistic",
        "relativistic": "non-relativistic",
    },
}


def now_iso() -> str:
    """Return the current local timestamp in ISO-8601 form."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def dedupe_strings(values: list[str]) -> list[str]:
    """Keep the first occurrence of each non-empty normalized string."""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def normalize_phrase(text: str) -> str:
    """Collapse whitespace so extracted phrases compare and render consistently."""
    return re.sub(r"\s+", " ", str(text or "").strip())


def slugify_token(text: str) -> str:
    """Generate a stable lowercase token for synthetic ids."""
    lowered = normalize_phrase(text).lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "item"


def depth_rank(state: str) -> int:
    """Map a reading-depth state to its monotonic ordering."""
    return READING_DEPTH_STATE_ORDER.get(str(state or "").strip().lower(), 0)


def reading_depth_state_from_row(row: dict[str, Any] | None) -> str:
    """Infer the normalized reading-depth state from a stored row."""
    if not isinstance(row, dict):
        return "skim"
    explicit_state = str(row.get("reading_depth_state") or "").strip().lower()
    if explicit_state in READING_DEPTH_STATE_ORDER:
        return explicit_state
    basis = str(row.get("basis") or "").strip().lower()
    if basis in {"deepxiv_head", "section_headings", "title_and_headings"}:
        return "head"
    if basis in {"deepxiv_sections", "selected_sections", "section_extract"}:
        return "sections"
    if basis in {
        "deepxiv_full",
        "snapshot_preview",
        "local_source_text",
        "extracted_source_bundle",
        "full_text",
        "manual_full_read",
    }:
        return "full"
    reading_depth = str(row.get("reading_depth") or "").strip().lower()
    if reading_depth in {"full", "full_read"}:
        return "full"
    return "skim"


def legacy_reading_depth_for_state(state: str, preferred: str = "") -> str:
    """Project the richer state model back onto the legacy depth labels."""
    normalized_preferred = str(preferred or "").strip()
    if normalized_preferred in {"full_read", "abstract_only", "skim"}:
        if state != "full" or normalized_preferred == "full_read":
            return normalized_preferred
    return "full_read" if state == "full" else "skim"


def deepxiv_sections_for_row(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize DeepXiv section metadata into a stable local structure."""
    provenance = row.get("provenance") or {}
    if not isinstance(provenance, dict):
        return []
    sections = provenance.get("deepxiv_sections") or []
    if not isinstance(sections, list):
        return []
    normalized: list[dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        name = normalize_phrase(section.get("name") or "")
        tldr = normalize_phrase(section.get("tldr") or "")
        if not name and not tldr:
            continue
        normalized.append(
            {
                "name": name or "section",
                "idx": int(section.get("idx") or 0),
                "tldr": tldr,
            }
        )
    return normalized


def key_section_titles_for_row(row: dict[str, Any], *, max_count: int = 4) -> list[str]:
    """Select the most informative section titles for head-level reading."""
    sections = deepxiv_sections_for_row(row)
    if not sections:
        return []

    def _priority(section: dict[str, Any]) -> tuple[int, int, str]:
        lower_name = str(section.get("name") or "").lower()
        for index, needle in enumerate(SECTION_PRIORITY_NEEDLES):
            if needle in lower_name:
                return (0, index, lower_name)
        return (1, int(section.get("idx") or 0), lower_name)

    ordered = sorted(sections, key=_priority)
    return dedupe_strings([str(section.get("name") or "").strip() for section in ordered[:max_count]])


def selected_section_titles_for_row(row: dict[str, Any], *, max_count: int = 3) -> list[str]:
    """Pick the section titles that represent sections-level reading coverage."""
    sections = deepxiv_sections_for_row(row)
    if not sections:
        return []
    selected = key_section_titles_for_row(row, max_count=max_count)
    if selected:
        return selected
    ordered = sorted(sections, key=lambda section: (int(section.get("idx") or 0), str(section.get("name") or "").lower()))
    return dedupe_strings([str(section.get("name") or "").strip() for section in ordered[:max_count]])


def covered_sections_for_state(row: dict[str, Any], state: str) -> list[str]:
    """Return the section titles that should count as covered for a depth state."""
    if state == "full":
        return dedupe_strings([str(section.get("name") or "").strip() for section in deepxiv_sections_for_row(row)])
    if state == "sections":
        return selected_section_titles_for_row(row)
    if state == "head":
        return key_section_titles_for_row(row)
    return []


def reading_depth_transition(
    *,
    from_state: str,
    to_state: str,
    basis: str,
    covered_sections: list[str],
    reason: str,
    transition_at: str,
) -> dict[str, Any]:
    """Build a durable transition record for reading-depth upgrades."""
    return {
        "from_state": from_state,
        "to_state": to_state,
        "basis": str(basis or "").strip() or "summary_only",
        "covered_sections": dedupe_strings([str(item) for item in covered_sections]),
        "reason": str(reason or "").strip() or "reading-depth transition",
        "transition_at": str(transition_at or "").strip() or now_iso(),
    }


def merge_reading_depth_row(
    *,
    source_row: dict[str, Any],
    existing_row: dict[str, Any] | None,
    incoming_row: dict[str, Any] | None,
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Merge a previous depth snapshot with the latest observation for one source."""
    timestamp = str(observed_at or "").strip() or now_iso()
    existing = dict(existing_row or {})
    incoming = dict(incoming_row or {})

    existing_state = reading_depth_state_from_row(existing)
    incoming_state = reading_depth_state_from_row(incoming or existing)
    existing_rank = depth_rank(existing_state)
    incoming_rank = depth_rank(incoming_state)
    deepest_state = incoming_state if incoming_rank >= existing_rank else existing_state

    deepest_basis = str(incoming.get("basis") or "").strip() or str(existing.get("basis") or "").strip() or "summary_only"
    if existing_rank > incoming_rank:
        deepest_basis = str(existing.get("basis") or "").strip() or deepest_basis

    deepest_sections = covered_sections_for_state(source_row, deepest_state)
    observed_sections = covered_sections_for_state(source_row, incoming_state)
    history: list[dict[str, Any]] = []
    for item in existing.get("transition_history") or []:
        if isinstance(item, dict):
            history.append(
                {
                    "from_state": str(item.get("from_state") or "").strip(),
                    "to_state": str(item.get("to_state") or "").strip(),
                    "basis": str(item.get("basis") or "").strip(),
                    "covered_sections": dedupe_strings([str(value) for value in item.get("covered_sections") or []]),
                    "reason": str(item.get("reason") or "").strip(),
                    "transition_at": str(item.get("transition_at") or "").strip(),
                }
            )

    if incoming_rank > existing_rank:
        next_transition = reading_depth_transition(
            from_state=existing_state if existing_row else "",
            to_state=incoming_state,
            basis=str(incoming.get("basis") or "").strip(),
            covered_sections=observed_sections,
            reason=f"Reading depth advanced to {incoming_state}.",
            transition_at=timestamp,
        )
        if not history or history[-1] != next_transition:
            history.append(next_transition)

    state_entered_at = str(existing.get("state_entered_at") or "").strip()
    if not state_entered_at or incoming_rank > existing_rank:
        state_entered_at = timestamp

    return {
        "source_id": str(incoming.get("source_id") or existing.get("source_id") or "").strip(),
        "source_title": str(incoming.get("source_title") or existing.get("source_title") or "").strip(),
        "source_type": str(incoming.get("source_type") or existing.get("source_type") or "").strip(),
        "reading_depth": legacy_reading_depth_for_state(
            deepest_state,
            preferred=str(incoming.get("reading_depth") or existing.get("reading_depth") or "").strip(),
        ),
        "reading_depth_state": deepest_state,
        "latest_reading_depth_state": incoming_state,
        "basis": deepest_basis,
        "latest_basis": str(incoming.get("basis") or deepest_basis).strip() or deepest_basis,
        "covered_sections": deepest_sections,
        "latest_covered_sections": observed_sections,
        "key_section_titles": key_section_titles_for_row(source_row),
        "state_entered_at": state_entered_at,
        "latest_observed_at": timestamp,
        "transition_count": len(history),
        "transition_history": history,
    }


def source_fragments_for_row(
    source_row: dict[str, Any],
    *,
    reading_depth_row: dict[str, Any],
) -> list[dict[str, str]]:
    """Select the source fragments that the current reading depth is allowed to use."""
    state = reading_depth_state_from_row(reading_depth_row)
    fragments: list[dict[str, str]] = []
    title = normalize_phrase(source_row.get("title") or "")
    summary = normalize_phrase(source_row.get("summary") or "")
    provenance = source_row.get("provenance") or {}
    if not isinstance(provenance, dict):
        provenance = {}

    if title:
        fragments.append(
            {
                "fragment_kind": "title",
                "source_section": "title",
                "source_locator": "title",
                "text": title,
            }
        )
    basis = str(reading_depth_row.get("latest_basis") or reading_depth_row.get("basis") or "").strip().lower()
    deepxiv_driven = basis in {"deepxiv_head", "deepxiv_sections", "deepxiv_full"}
    if summary and not deepxiv_driven:
        fragments.append(
            {
                "fragment_kind": "summary",
                "source_section": "summary",
                "source_locator": "summary",
                "text": summary,
            }
        )

    deepxiv_tldr = normalize_phrase(provenance.get("deepxiv_tldr") or "")
    if deepxiv_tldr:
        fragments.append(
            {
                "fragment_kind": "deepxiv_tldr",
                "source_section": "deepxiv_tldr",
                "source_locator": "deepxiv_tldr",
                "text": deepxiv_tldr,
            }
        )

    sections = deepxiv_sections_for_row(source_row)
    if state in {"sections", "full"} and sections:
        covered = set(reading_depth_row.get("covered_sections") or [])
        for section in sections:
            name = str(section.get("name") or "").strip()
            if state == "sections" and covered and name not in covered:
                continue
            tldr = str(section.get("tldr") or "").strip()
            if not tldr:
                continue
            fragments.append(
                {
                    "fragment_kind": "deepxiv_section_tldr",
                    "source_section": name or "section",
                    "source_locator": f"section:{name or 'section'}",
                    "text": tldr,
                }
            )

    return fragments


def explicit_assumption_candidates(text: str) -> list[str]:
    """Extract explicit assumption clauses from a text fragment."""
    candidates = list(detect_assumptions(text=text))
    for pattern in EXTRA_ASSUMPTION_PATTERNS:
        for match in pattern.finditer(text):
            clause = normalize_phrase(match.group("clause") or "")
            if clause:
                candidates.append(clause)
    return dedupe_strings(candidates)


def regime_descriptors(text: str) -> list[dict[str, Any]]:
    """Extract structured regime descriptors from a text fragment."""
    descriptors: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    normalized_text = normalize_phrase(text)
    for pattern, axis in REGIME_DESCRIPTOR_PATTERNS:
        for match in pattern.finditer(normalized_text):
            phrase = normalize_phrase(match.group(0))
            value = normalize_phrase(match.group("value"))
            key = (axis, value.lower())
            if not phrase or not value or key in seen:
                continue
            seen.add(key)
            boundary_conditions = [phrase] if axis == "boundary_condition" else []
            descriptors.append(
                {
                    "regime": phrase,
                    "regime_axis": axis,
                    "regime_value": value.lower(),
                    "boundary_conditions": boundary_conditions,
                    "boundary_summary": phrase if boundary_conditions else "",
                    "compatibility_key": f"{axis}:{value.lower()}",
                }
            )
    return descriptors


def assumption_rows_for_source(
    *,
    source_row: dict[str, Any],
    reading_depth_row: dict[str, Any],
    fragments: list[dict[str, str]],
    regime_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate assumption rows for one source from selected deep-reading fragments."""
    rows: list[dict[str, Any]] = []
    source_id = str(source_row.get("source_id") or "").strip()
    source_title = str(source_row.get("title") or "").strip()
    source_type = str(source_row.get("source_type") or "").strip()
    reading_depth = str(reading_depth_row.get("reading_depth") or "").strip() or "skim"
    reading_depth_state = reading_depth_state_from_row(reading_depth_row)
    seen: set[tuple[str, str]] = set()

    regimes_by_locator: dict[str, list[str]] = {}
    for regime_row in regime_rows:
        locator = str(regime_row.get("source_locator") or "").strip()
        regime = str(regime_row.get("regime") or "").strip()
        if locator and regime:
            regimes_by_locator.setdefault(locator, []).append(regime)

    for fragment in fragments:
        text = str(fragment.get("text") or "").strip()
        if not text:
            continue
        applicable_regime = ", ".join(dedupe_strings(regimes_by_locator.get(str(fragment.get("source_locator") or "").strip(), [])))
        for assumption in explicit_assumption_candidates(text):
            key = (assumption.lower(), str(fragment.get("source_locator") or "").lower())
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "assumption_id": f"assumption:{source_id}:{slugify_token(assumption)}",
                    "source_id": source_id,
                    "source_title": source_title,
                    "source_type": source_type,
                    "assumption": assumption,
                    "description": assumption,
                    "reading_depth": reading_depth,
                    "reading_depth_state": reading_depth_state,
                    "source_section": str(fragment.get("source_section") or "").strip(),
                    "source_locator": str(fragment.get("source_locator") or "").strip(),
                    "source_fragment_kind": str(fragment.get("fragment_kind") or "").strip(),
                    "confidence_tier": "explicit",
                    "confidence_score": 0.95,
                    "applicable_regime": applicable_regime,
                    "evidence_excerpt": text[:220],
                }
            )

    for regime_row in regime_rows:
        regime = str(regime_row.get("regime") or "").strip()
        if not regime:
            continue
        axis = str(regime_row.get("regime_axis") or "").strip()
        if axis == "boundary_condition":
            assumption = f"The derivation assumes {regime}."
        else:
            assumption = f"The analysis is bounded to the {regime} regime."
        key = (assumption.lower(), str(regime_row.get("source_locator") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "assumption_id": f"assumption:{source_id}:{slugify_token(assumption)}",
                "source_id": source_id,
                "source_title": source_title,
                "source_type": source_type,
                "assumption": assumption,
                "description": assumption,
                "reading_depth": reading_depth,
                "reading_depth_state": reading_depth_state,
                "source_section": str(regime_row.get("source_section") or "").strip(),
                "source_locator": str(regime_row.get("source_locator") or "").strip(),
                "source_fragment_kind": str(regime_row.get("source_fragment_kind") or "").strip(),
                "confidence_tier": "inferred",
                "confidence_score": 0.6,
                "applicable_regime": regime,
                "evidence_excerpt": str(regime_row.get("evidence_excerpt") or "").strip(),
            }
        )

    return rows


def regime_rows_for_source(
    *,
    source_row: dict[str, Any],
    reading_depth_row: dict[str, Any],
    fragments: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Generate regime rows for one source from selected deep-reading fragments."""
    rows: list[dict[str, Any]] = []
    source_id = str(source_row.get("source_id") or "").strip()
    source_title = str(source_row.get("title") or "").strip()
    source_type = str(source_row.get("source_type") or "").strip()
    reading_depth = str(reading_depth_row.get("reading_depth") or "").strip() or "skim"
    reading_depth_state = reading_depth_state_from_row(reading_depth_row)
    seen: set[tuple[str, str, str]] = set()

    for fragment in fragments:
        text = str(fragment.get("text") or "").strip()
        if not text:
            continue
        for descriptor in regime_descriptors(text):
            axis = str(descriptor.get("regime_axis") or "").strip()
            value = str(descriptor.get("regime_value") or "").strip()
            regime = str(descriptor.get("regime") or "").strip()
            key = (
                str(fragment.get("source_locator") or "").strip().lower(),
                axis.lower(),
                value.lower(),
            )
            if not axis or not value or not regime or key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "regime_id": f"regime:{source_id}:{axis}:{slugify_token(value)}",
                    "source_id": source_id,
                    "source_title": source_title,
                    "source_type": source_type,
                    "regime": regime,
                    "reading_depth": reading_depth,
                    "reading_depth_state": reading_depth_state,
                    "regime_axis": axis,
                    "regime_value": value,
                    "boundary_conditions": list(descriptor.get("boundary_conditions") or []),
                    "boundary_summary": str(descriptor.get("boundary_summary") or "").strip(),
                    "compatibility_key": str(descriptor.get("compatibility_key") or "").strip(),
                    "source_section": str(fragment.get("source_section") or "").strip(),
                    "source_locator": str(fragment.get("source_locator") or "").strip(),
                    "source_fragment_kind": str(fragment.get("fragment_kind") or "").strip(),
                    "evidence_excerpt": text[:220],
                }
            )

    return rows


def notation_rows_for_source(
    *,
    source_row: dict[str, Any],
    reading_depth_row: dict[str, Any],
    fragments: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Generate notation-definition rows for one source from selected fragments."""
    rows: list[dict[str, Any]] = []
    source_id = str(source_row.get("source_id") or "").strip()
    source_title = str(source_row.get("title") or "").strip()
    source_type = str(source_row.get("source_type") or "").strip()
    reading_depth = str(reading_depth_row.get("reading_depth") or "").strip() or "skim"
    reading_depth_state = reading_depth_state_from_row(reading_depth_row)
    seen: set[tuple[str, str]] = set()

    for fragment in fragments:
        text = str(fragment.get("text") or "").strip()
        if not text:
            continue
        for candidate in detect_notation_candidates(text=text):
            symbol = normalize_phrase(candidate.get("symbol") or "")
            meaning = normalize_phrase(candidate.get("meaning") or "")
            key = (symbol.lower(), meaning.lower())
            if not symbol or not meaning or key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "source_id": source_id,
                    "source_title": source_title,
                    "source_type": source_type,
                    "symbol": symbol,
                    "meaning": meaning,
                    "concept_key": slugify_token(meaning),
                    "reading_depth": reading_depth,
                    "reading_depth_state": reading_depth_state,
                    "source_section": str(fragment.get("source_section") or "").strip(),
                    "source_locator": str(fragment.get("source_locator") or "").strip(),
                    "source_fragment_kind": str(fragment.get("fragment_kind") or "").strip(),
                    "evidence_excerpt": text[:220],
                }
            )
    return rows


def pairwise_regime_overlap_rows(
    *,
    source_rows_by_id: dict[str, dict[str, Any]],
    reading_depth_by_source: dict[str, dict[str, Any]],
    regime_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compare source regimes pairwise and mark compatible or disjoint overlaps."""
    regimes_by_source: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in regime_rows:
        source_id = str(row.get("source_id") or "").strip()
        axis = str(row.get("regime_axis") or "").strip()
        if not source_id or not axis:
            continue
        regimes_by_source.setdefault(source_id, {}).setdefault(axis, []).append(row)

    ordered_source_ids = sorted(regimes_by_source)
    rows: list[dict[str, Any]] = []
    for index, source_id in enumerate(ordered_source_ids):
        for against_source_id in ordered_source_ids[index + 1 :]:
            source_axes = regimes_by_source.get(source_id) or {}
            against_axes = regimes_by_source.get(against_source_id) or {}
            compared_axes = sorted(set(source_axes).intersection(against_axes))
            compatible_axes: list[str] = []
            conflicting_axes: list[str] = []
            detail_parts: list[str] = []
            for axis in compared_axes:
                source_values = {str(item.get("regime_value") or "").strip() for item in source_axes.get(axis) or []}
                against_values = {str(item.get("regime_value") or "").strip() for item in against_axes.get(axis) or []}
                if source_values.intersection(against_values):
                    compatible_axes.append(axis)
                    continue
                opposing = False
                for source_value in source_values:
                    opposite = OPPOSING_REGIME_VALUES.get(axis, {}).get(source_value)
                    if opposite and opposite in against_values:
                        opposing = True
                        break
                if opposing or source_values != against_values:
                    conflicting_axes.append(axis)
                    detail_parts.append(
                        f"{axis}: {', '.join(sorted(source_values))} vs {', '.join(sorted(against_values))}"
                    )

            overlap_status = "compatible"
            if conflicting_axes:
                overlap_status = "disjoint"
            elif compared_axes and len(compatible_axes) != len(compared_axes):
                overlap_status = "partial"
            elif not compared_axes:
                overlap_status = "partial"

            source_row = source_rows_by_id.get(source_id) or {}
            against_row = source_rows_by_id.get(against_source_id) or {}
            source_depth = reading_depth_by_source.get(source_id) or {}
            against_depth = reading_depth_by_source.get(against_source_id) or {}
            rows.append(
                {
                    "source_id": source_id,
                    "source_title": str(source_row.get("title") or "").strip(),
                    "source_type": str(source_row.get("source_type") or "").strip(),
                    "reading_depth": str(source_depth.get("reading_depth") or "").strip() or "skim",
                    "reading_depth_state": reading_depth_state_from_row(source_depth),
                    "against_source_id": against_source_id,
                    "against_source_title": str(against_row.get("title") or "").strip(),
                    "against_source_type": str(against_row.get("source_type") or "").strip(),
                    "against_reading_depth": str(against_depth.get("reading_depth") or "").strip() or "skim",
                    "against_reading_depth_state": reading_depth_state_from_row(against_depth),
                    "overlap_status": overlap_status,
                    "compared_axes": compared_axes,
                    "compatible_axes": compatible_axes,
                    "conflicting_axes": conflicting_axes,
                    "detail": "; ".join(detail_parts) or "No directly comparable regime axes were detected.",
                    "source_regimes": dedupe_strings(
                        [str(item.get("regime") or "").strip() for axis_rows in source_axes.values() for item in axis_rows]
                    ),
                    "against_regimes": dedupe_strings(
                        [
                            str(item.get("regime") or "").strip()
                            for axis_rows in against_axes.values()
                            for item in axis_rows
                        ]
                    ),
                }
            )
    return rows


def notation_alignment_rows(
    *,
    source_rows_by_id: dict[str, dict[str, Any]],
    reading_depth_by_source: dict[str, dict[str, Any]],
    notation_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Record cross-source cases where different symbols refer to the same concept."""
    rows_by_source: dict[str, list[dict[str, Any]]] = {}
    for row in notation_rows:
        source_id = str(row.get("source_id") or "").strip()
        if source_id:
            rows_by_source.setdefault(source_id, []).append(row)

    ordered_source_ids = sorted(rows_by_source)
    alignments: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for index, source_id in enumerate(ordered_source_ids):
        for against_source_id in ordered_source_ids[index + 1 :]:
            for source_binding in rows_by_source.get(source_id) or []:
                for against_binding in rows_by_source.get(against_source_id) or []:
                    source_symbol = str(source_binding.get("symbol") or "").strip()
                    against_symbol = str(against_binding.get("symbol") or "").strip()
                    source_meaning = str(source_binding.get("meaning") or "").strip()
                    against_meaning = str(against_binding.get("meaning") or "").strip()
                    if not source_symbol or not against_symbol or not source_meaning or not against_meaning:
                        continue
                    if source_meaning.lower() != against_meaning.lower():
                        continue
                    if source_symbol.lower() == against_symbol.lower():
                        continue
                    key = (
                        source_id.lower(),
                        against_source_id.lower(),
                        source_meaning.lower(),
                        source_symbol.lower(),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    source_row = source_rows_by_id.get(source_id) or {}
                    against_row = source_rows_by_id.get(against_source_id) or {}
                    source_depth = reading_depth_by_source.get(source_id) or {}
                    against_depth = reading_depth_by_source.get(against_source_id) or {}
                    alignments.append(
                        {
                            "source_id": source_id,
                            "source_title": str(source_row.get("title") or "").strip(),
                            "source_type": str(source_row.get("source_type") or "").strip(),
                            "reading_depth": str(source_depth.get("reading_depth") or "").strip() or "skim",
                            "reading_depth_state": reading_depth_state_from_row(source_depth),
                            "against_source_id": against_source_id,
                            "against_source_title": str(against_row.get("title") or "").strip(),
                            "against_source_type": str(against_row.get("source_type") or "").strip(),
                            "against_reading_depth": str(against_depth.get("reading_depth") or "").strip() or "skim",
                            "against_reading_depth_state": reading_depth_state_from_row(against_depth),
                            "meaning": source_meaning,
                            "source_symbol": source_symbol,
                            "against_symbol": against_symbol,
                            "alignment_kind": "different_symbols_same_concept",
                            "detail": f"{source_symbol} vs {against_symbol} for {source_meaning}",
                        }
                    )
    return alignments


def notation_tension_rows(
    *,
    source_rows_by_id: dict[str, dict[str, Any]],
    reading_depth_by_source: dict[str, dict[str, Any]],
    notation_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Record cross-source cases where the same symbol shifts meaning."""
    rows_by_source: dict[str, list[dict[str, Any]]] = {}
    for row in notation_rows:
        source_id = str(row.get("source_id") or "").strip()
        if source_id:
            rows_by_source.setdefault(source_id, []).append(row)

    ordered_source_ids = sorted(rows_by_source)
    tensions: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for index, source_id in enumerate(ordered_source_ids):
        for against_source_id in ordered_source_ids[index + 1 :]:
            for source_binding in rows_by_source.get(source_id) or []:
                for against_binding in rows_by_source.get(against_source_id) or []:
                    source_symbol = str(source_binding.get("symbol") or "").strip()
                    against_symbol = str(against_binding.get("symbol") or "").strip()
                    source_meaning = str(source_binding.get("meaning") or "").strip()
                    against_meaning = str(against_binding.get("meaning") or "").strip()
                    if not source_symbol or not against_symbol or not source_meaning or not against_meaning:
                        continue
                    if source_symbol.lower() != against_symbol.lower():
                        continue
                    if source_meaning.lower() == against_meaning.lower():
                        continue
                    key = (source_id.lower(), against_source_id.lower(), source_symbol.lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    source_row = source_rows_by_id.get(source_id) or {}
                    against_row = source_rows_by_id.get(against_source_id) or {}
                    source_depth = reading_depth_by_source.get(source_id) or {}
                    against_depth = reading_depth_by_source.get(against_source_id) or {}
                    tensions.append(
                        {
                            "source_id": source_id,
                            "source_title": str(source_row.get("title") or "").strip(),
                            "source_type": str(source_row.get("source_type") or "").strip(),
                            "reading_depth": str(source_depth.get("reading_depth") or "").strip() or "skim",
                            "reading_depth_state": reading_depth_state_from_row(source_depth),
                            "against_source_id": against_source_id,
                            "against_source_title": str(against_row.get("title") or "").strip(),
                            "against_source_type": str(against_row.get("source_type") or "").strip(),
                            "against_reading_depth": str(against_depth.get("reading_depth") or "").strip() or "skim",
                            "against_reading_depth_state": reading_depth_state_from_row(against_depth),
                            "symbol": source_symbol,
                            "source_meaning": source_meaning,
                            "against_meaning": against_meaning,
                            "detail": f"{source_symbol} maps to {source_meaning} vs {against_meaning}",
                        }
                    )
    return tensions
