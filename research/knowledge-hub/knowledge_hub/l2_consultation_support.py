from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def consultation_projection_path(
    kernel_root: Path,
    *,
    topic_slug: str,
    stage: str,
    run_id: str | None,
) -> Path | None:
    if not run_id:
        return None
    if stage == "L1":
        return kernel_root / "topics" / topic_slug / "L1" / "l2_consultation_log.jsonl"
    if stage == "L3":
        return kernel_root / "topics" / topic_slug / "L3" / "runs" / run_id / "l2_consultation_log.jsonl"
    return kernel_root / "topics" / topic_slug / "L4" / "runs" / run_id / "l2_consultation_log.jsonl"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _topic_slugs_from_strings(values: list[str]) -> set[str]:
    topic_slugs: set[str] = set()
    for raw_value in values:
        normalized = str(raw_value or "").strip()
        if not normalized:
            continue
        if normalized.startswith("topics/"):
            parts = normalized.split("/")
            if len(parts) >= 2 and parts[1]:
                topic_slugs.add(parts[1])
        segments = normalized.replace("\\", "/").split("/")
        for index, segment in enumerate(segments[:-1]):
            if segment == "topics" and segments[index + 1]:
                topic_slugs.add(segments[index + 1])
    return topic_slugs


def topic_locality_for_hit(row: dict[str, Any], *, topic_slug: str | None) -> dict[str, Any]:
    resolved_topic_slug = str(topic_slug or "").strip()
    if not resolved_topic_slug:
        return {
            "topic_locality": "global",
            "topic_locality_score": 0.0,
            "topic_locality_reasons": [],
        }

    reasons: list[str] = []
    score = 0.0
    applicable_topics = {
        str(item).strip()
        for item in (row.get("applicable_topics") or [])
        if str(item).strip()
    }
    if resolved_topic_slug in applicable_topics:
        reasons.append("applicable_topic")
        score += 3.0

    referenced_slugs = set()
    referenced_slugs.update(_topic_slugs_from_strings(list(row.get("origin_topic_refs") or [])))
    referenced_slugs.update(_topic_slugs_from_strings(list(row.get("origin_run_refs") or [])))
    referenced_slugs.update(_topic_slugs_from_strings(list(row.get("validation_receipts") or [])))
    referenced_slugs.update(_topic_slugs_from_strings(list(row.get("reuse_receipts") or [])))
    referenced_slugs.update(
        {
            str(item).strip()
            for item in (row.get("failed_topics") or [])
            if str(item).strip()
        }
    )
    referenced_slugs.update(_topic_slugs_from_strings(list(row.get("regime_notes") or [])))
    if resolved_topic_slug in referenced_slugs:
        reasons.append("topic_reference")
        score += 2.0

    row_topic_slug = str(row.get("topic_slug") or "").strip()
    if resolved_topic_slug and row_topic_slug == resolved_topic_slug:
        reasons.append("entry_topic_slug")
        score += 4.0

    return {
        "topic_locality": "topic_local" if reasons else "global",
        "topic_locality_score": score,
        "topic_locality_reasons": reasons,
    }


def _summary_card(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row.get("id") or row.get("unit_id") or ""),
        "unit_type": str(row.get("unit_type") or row.get("object_type") or ""),
        "title": str(row.get("title") or ""),
        "summary": str(row.get("summary") or ""),
        "path": str(row.get("path") or ""),
        "trust_surface": str(row.get("trust_surface") or "canonical"),
        "authority_level": str(row.get("authority_level") or ""),
        "score": float(row.get("score") or 0.0),
        "matched_terms": list(row.get("matched_terms") or []),
        "topic_locality": str(row.get("topic_locality") or "global"),
        "topic_locality_reasons": list(row.get("topic_locality_reasons") or []),
        "detail_available": str(row.get("path") or "").endswith(".json"),
    }


def _load_hit_detail(kernel_root: Path, row: dict[str, Any]) -> dict[str, Any] | None:
    relative_path = str(row.get("path") or "").strip()
    if not relative_path:
        return None
    payload = _read_json(kernel_root / relative_path)
    if not isinstance(payload, dict):
        return None
    return {
        **payload,
        "detail_level": "full",
        "detail_path": relative_path,
        "trust_surface": str(row.get("trust_surface") or "canonical"),
        "topic_locality": str(row.get("topic_locality") or "global"),
        "topic_locality_reasons": list(row.get("topic_locality_reasons") or []),
    }


def build_progressive_retrieval_payload(
    kernel_root: Path,
    *,
    primary_hits: list[dict[str, Any]],
    expanded_hits: list[dict[str, Any]],
    detail_unit_ids: list[str] | None = None,
) -> dict[str, Any]:
    requested_detail_ids = [
        str(item).strip()
        for item in (detail_unit_ids or [])
        if str(item).strip()
    ]
    detail_lookup: dict[str, dict[str, Any]] = {}
    for row in [*primary_hits, *expanded_hits]:
        row_id = str(row.get("id") or row.get("unit_id") or "").strip()
        if row_id and row_id not in detail_lookup:
            detail_lookup[row_id] = row

    details_by_id: dict[str, dict[str, Any]] = {}
    for row_id in requested_detail_ids:
        row = detail_lookup.get(row_id)
        if row is None:
            continue
        detail = _load_hit_detail(kernel_root, row)
        if detail is not None:
            details_by_id[row_id] = detail

    return {
        "default_level": "summary",
        "detail_available": any(card["detail_available"] for card in [_summary_card(row) for row in [*primary_hits, *expanded_hits]]),
        "requested_detail_ids": requested_detail_ids,
        "returned_detail_count": len(details_by_id),
        "summary_hits": [_summary_card(row) for row in primary_hits],
        "expanded_summary_hits": [_summary_card(row) for row in expanded_hits],
        "details_by_id": details_by_id,
    }


def build_l2_consultation_record(
    *,
    kernel_root: Path,
    topic_slug: str,
    stage: str,
    run_id: str | None,
    query_text: str,
    retrieval_profile: str,
    dashboard_path: Path,
    context_id: str,
    payload: dict[str, Any],
    relativize: Callable[[Path], str],
) -> dict[str, Any]:
    projection_path = consultation_projection_path(
        kernel_root,
        topic_slug=topic_slug,
        stage=stage,
        run_id=run_id,
    )
    primary_hits = list(payload.get("primary_hits", []))
    expanded_hits = list(payload.get("expanded_hits", []))
    traversal_summary = dict(payload.get("traversal_summary") or {})
    return {
        "record_args": {
            "context_ref": {
                "id": context_id,
                "layer": stage,
                "object_type": "consultation_query",
                "path": relativize(dashboard_path),
                "title": f"L2 consultation query for {topic_slug}",
                "summary": query_text,
            },
            "requested_unit_types": requested_unit_types_for_profile(kernel_root, retrieval_profile),
            "retrieved_refs": [hit_to_object_ref(row) for row in [*primary_hits, *expanded_hits]],
            "result_summary": (
                f"Retrieved {len(primary_hits)} primary hits and "
                f"{len(expanded_hits)} expanded hits "
                f"(max depth reached={int(traversal_summary.get('max_depth_reached') or 0)})."
            ),
            "effect_on_work": (
                f"Recorded canonical L2 consultation context for {stage} work on `{topic_slug}` "
                "so later review can inspect the exact retrieval basis."
            ),
            "outcome": "candidate_narrowed" if primary_hits or expanded_hits else "no_change",
            "projection_paths": [
                relativize(dashboard_path),
                *([relativize(projection_path)] if projection_path is not None else []),
            ],
        },
        "retrieval_summary": traversal_summary,
        "traversal_paths": payload.get("traversal_paths", []),
        "progressive_retrieval": payload.get("progressive_retrieval", {}),
    }


def hit_to_object_ref(row: dict[str, Any]) -> dict[str, str]:
    object_id = str(row.get("id") or row.get("unit_id") or "")
    object_type = str(row.get("unit_type") or row.get("object_type") or "l2_unit")
    return {
        "id": object_id,
        "layer": "L2",
        "object_type": object_type,
        "path": str(row.get("path") or ""),
        "title": str(row.get("title") or object_id),
        "summary": str(row.get("summary") or f"Retrieved {object_type} {object_id} from canonical L2 memory."),
    }


def requested_unit_types_for_profile(kernel_root: Path, retrieval_profile: str) -> list[str]:
    profiles_path = kernel_root / "canonical" / "retrieval_profiles.json"
    if not profiles_path.exists():
        return []
    payload = json.loads(profiles_path.read_text(encoding="utf-8"))
    preferred_types = ((payload.get("profiles") or {}).get(retrieval_profile) or {}).get("preferred_unit_types") or []
    requested_types: list[str] = []
    seen: set[str] = set()
    for unit_type in preferred_types:
        normalized = str(unit_type or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        requested_types.append(normalized)
    return requested_types
