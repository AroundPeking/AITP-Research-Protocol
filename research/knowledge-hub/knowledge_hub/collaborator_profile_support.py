from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .bundle_support import default_user_home


PROFILE_MEMORY_KINDS = ("preference", "working_style", "trajectory", "coordination")
DEFAULT_PROFILE_FILENAME = "collaborator_profile.json"
MAX_INTERACTION_HISTORY = 200
_DEFAULT_INTERACTION_STYLE = "collaborative"
_DEFAULT_RESEARCH_STYLE = "mixed"
_DEFAULT_VALIDATION_DEPTH = "standard"
_DEFAULT_RISK_TOLERANCE = "moderate"
_DEFAULT_DERIVATION_STYLE = "formal"
_DEFAULT_READING_DEPTH = "sections"
_VALID_RESEARCH_STYLES = {"analytical", "computational", "experimental", "mixed"}
_VALID_VALIDATION_DEPTHS = {"quick", "standard", "exhaustive"}
_VALID_RISK_TOLERANCE = {"conservative", "moderate", "aggressive"}
_VALID_DERIVATION_STYLES = {"formal", "heuristic", "physical_intuition"}
_VALID_READING_DEPTHS = {"skim", "head", "sections", "full"}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _dedupe_strings(values: Iterable[Any]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value or "").strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def _normalize_choice(value: Any, *, allowed: set[str], fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


def _profile_store_template(*, updated_by: str) -> dict[str, Any]:
    return {
        "profile_version": 1,
        "collaborator_id": "default",
        "expertise_areas": [],
        "preferred_notation": [],
        "interaction_style": _DEFAULT_INTERACTION_STYLE,
        "preferred_research_style": _DEFAULT_RESEARCH_STYLE,
        "preferred_validation_depth": _DEFAULT_VALIDATION_DEPTH,
        "risk_tolerance": _DEFAULT_RISK_TOLERANCE,
        "preferred_derivation_style": _DEFAULT_DERIVATION_STYLE,
        "common_routes_taken": [],
        "failed_routes_pattern": [],
        "source_reading_depth_preference": _DEFAULT_READING_DEPTH,
        "interaction_history": [],
        "updated_at": _now_iso(),
        "updated_by": updated_by,
    }


def collaborator_profile_store_path(profile_path: str | Path | None = None) -> Path:
    if profile_path is not None:
        return Path(profile_path).expanduser().resolve()
    return (default_user_home() / DEFAULT_PROFILE_FILENAME).resolve()


def _normalize_interaction_row(
    row: dict[str, Any] | Any,
    *,
    updated_by: str,
) -> dict[str, Any]:
    payload = row if isinstance(row, dict) else {"summary": str(row or "").strip()}
    recorded_at = str(payload.get("recorded_at") or "").strip() or _now_iso()
    summary = str(payload.get("summary") or "").strip()
    if not summary:
        summary = "Recorded collaborator interaction."
    interaction_id = str(payload.get("interaction_id") or "").strip()
    if not interaction_id:
        interaction_id = f"interaction-{recorded_at}"
    return {
        "interaction_id": interaction_id,
        "recorded_at": recorded_at,
        "topic_slug": str(payload.get("topic_slug") or "").strip(),
        "run_id": str(payload.get("run_id") or "").strip(),
        "summary": summary,
        "tags": _dedupe_strings(payload.get("tags") or []),
        "expertise_areas": _dedupe_strings(payload.get("expertise_areas") or []),
        "notation": _dedupe_strings(
            payload.get("notation")
            or payload.get("preferred_notation")
            or []
        ),
        "interaction_style": str(payload.get("interaction_style") or "").strip(),
        "route": str(payload.get("route") or "").strip(),
        "outcome": str(payload.get("outcome") or "").strip(),
        "notes": str(payload.get("notes") or payload.get("details") or "").strip(),
        "updated_by": str(payload.get("updated_by") or updated_by).strip(),
    }


def _merge_interaction_rows(
    existing_rows: Iterable[dict[str, Any]],
    incoming_rows: Iterable[dict[str, Any] | Any],
    *,
    updated_by: str,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        normalized = _normalize_interaction_row(row, updated_by=updated_by)
        merged[normalized["interaction_id"]] = normalized
    for row in incoming_rows:
        normalized = _normalize_interaction_row(row, updated_by=updated_by)
        merged[normalized["interaction_id"]] = normalized
    ordered = sorted(
        merged.values(),
        key=lambda item: (
            str(item.get("recorded_at") or ""),
            str(item.get("interaction_id") or ""),
        ),
    )
    return ordered[-MAX_INTERACTION_HISTORY:]


def _profile_from_payload(
    payload: dict[str, Any] | None,
    *,
    updated_by: str,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = {
        **_profile_store_template(updated_by=updated_by),
        **(existing or {}),
        **(payload or {}),
    }
    interaction_history = _merge_interaction_rows(
        existing_rows=base.get("interaction_history") or [],
        incoming_rows=[],
        updated_by=updated_by,
    )
    expertise_areas = _dedupe_strings(
        [*list(base.get("expertise_areas") or [])]
        + [
            area
            for row in interaction_history
            for area in (row.get("expertise_areas") or [])
        ]
    )
    preferred_notation = _dedupe_strings(
        [*list(base.get("preferred_notation") or [])]
        + [
            notation
            for row in interaction_history
            for notation in (row.get("notation") or [])
        ]
    )
    common_routes_taken = _dedupe_strings(
        [*list(base.get("common_routes_taken") or [])]
        + [row.get("route") for row in interaction_history if str(row.get("route") or "").strip()]
    )
    failed_routes_pattern = _dedupe_strings(
        [*list(base.get("failed_routes_pattern") or [])]
        + [
            row.get("route")
            for row in interaction_history
            if str(row.get("route") or "").strip()
            and str(row.get("outcome") or "").strip().lower()
            in {"failed", "rollback", "stuck", "abandoned"}
        ]
    )
    interaction_style = str(base.get("interaction_style") or "").strip()
    if not interaction_style:
        interaction_style = next(
            (
                str(row.get("interaction_style") or "").strip()
                for row in reversed(interaction_history)
                if str(row.get("interaction_style") or "").strip()
            ),
            _DEFAULT_INTERACTION_STYLE,
        )
    profile = {
        **_profile_store_template(updated_by=updated_by),
        **base,
        "profile_version": int(base.get("profile_version") or 1),
        "collaborator_id": str(base.get("collaborator_id") or "default").strip()
        or "default",
        "expertise_areas": expertise_areas,
        "preferred_notation": preferred_notation,
        "interaction_style": interaction_style,
        "preferred_research_style": _normalize_choice(
            base.get("preferred_research_style"),
            allowed=_VALID_RESEARCH_STYLES,
            fallback=_DEFAULT_RESEARCH_STYLE,
        ),
        "preferred_validation_depth": _normalize_choice(
            base.get("preferred_validation_depth"),
            allowed=_VALID_VALIDATION_DEPTHS,
            fallback=_DEFAULT_VALIDATION_DEPTH,
        ),
        "risk_tolerance": _normalize_choice(
            base.get("risk_tolerance"),
            allowed=_VALID_RISK_TOLERANCE,
            fallback=_DEFAULT_RISK_TOLERANCE,
        ),
        "preferred_derivation_style": _normalize_choice(
            base.get("preferred_derivation_style"),
            allowed=_VALID_DERIVATION_STYLES,
            fallback=_DEFAULT_DERIVATION_STYLE,
        ),
        "common_routes_taken": common_routes_taken,
        "failed_routes_pattern": failed_routes_pattern,
        "source_reading_depth_preference": _normalize_choice(
            base.get("source_reading_depth_preference"),
            allowed=_VALID_READING_DEPTHS,
            fallback=_DEFAULT_READING_DEPTH,
        ),
        "interaction_history": interaction_history,
        "updated_at": _now_iso(),
        "updated_by": updated_by,
    }
    return profile


def create_profile(
    *,
    profile_path: str | Path | None = None,
    updated_by: str = "aitp-service",
    seed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = collaborator_profile_store_path(profile_path)
    payload = _profile_from_payload(seed or {}, updated_by=updated_by)
    _write_json(path, payload)
    return payload


def get_profile(
    *,
    profile_path: str | Path | None = None,
    updated_by: str = "aitp-service",
) -> dict[str, Any] | None:
    path = collaborator_profile_store_path(profile_path)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return _profile_from_payload(payload, updated_by=updated_by)


def merge_interaction_history(
    profile: dict[str, Any],
    interactions: Iterable[dict[str, Any] | Any],
    *,
    updated_by: str = "aitp-service",
) -> dict[str, Any]:
    merged_rows = _merge_interaction_rows(
        existing_rows=profile.get("interaction_history") or [],
        incoming_rows=interactions,
        updated_by=updated_by,
    )
    return _profile_from_payload(
        {
            **profile,
            "interaction_history": merged_rows,
        },
        updated_by=updated_by,
        existing=profile,
    )


def update_profile(
    *,
    updates: dict[str, Any],
    profile_path: str | Path | None = None,
    updated_by: str = "aitp-service",
) -> dict[str, Any]:
    current = get_profile(profile_path=profile_path, updated_by=updated_by)
    if current is None:
        current = _profile_store_template(updated_by=updated_by)
    interaction_updates = updates.get("interaction_history") or []
    merged_profile = {
        **current,
        **updates,
    }
    if interaction_updates:
        merged_profile = merge_interaction_history(
            merged_profile,
            interaction_updates,
            updated_by=updated_by,
        )
    else:
        merged_profile = _profile_from_payload(
            merged_profile,
            updated_by=updated_by,
            existing=current,
        )
    path = collaborator_profile_store_path(profile_path)
    _write_json(path, merged_profile)
    return merged_profile


def collaborator_profile_paths(runtime_root: Path) -> dict[str, Path]:
    return {
        "json": runtime_root / "collaborator_profile.active.json",
        "note": runtime_root / "collaborator_profile.active.md",
    }


def empty_collaborator_profile(*, topic_slug: str, updated_by: str) -> dict[str, Any]:
    return {
        "artifact_kind": "collaborator_profile",
        "topic_slug": topic_slug,
        "status": "absent",
        "preference_count": 0,
        "working_style_count": 0,
        "trajectory_count": 0,
        "coordination_count": 0,
        "preference_summaries": [],
        "working_style_summaries": [],
        "trajectory_summaries": [],
        "coordination_summaries": [],
        "preferred_tags": [],
        "related_topic_slugs": [],
        "memory_ids": [],
        "summary": "No collaborator profile is currently recorded for this topic.",
        "updated_at": _now_iso(),
        "updated_by": updated_by,
    }


def load_collaborator_profile(
    runtime_root: Path,
    *,
    topic_slug: str,
    updated_by: str = "aitp-service",
) -> dict[str, Any] | None:
    json_path = collaborator_profile_paths(runtime_root)["json"]
    if not json_path.exists():
        return None
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    payload = {
        **empty_collaborator_profile(topic_slug=topic_slug, updated_by=updated_by),
        **payload,
    }
    payload["topic_slug"] = str(payload.get("topic_slug") or topic_slug)
    return payload


def derive_collaborator_profile(
    self,
    *,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    rows = [
        row
        for row in self._load_collaborator_memory_rows()
        if self._collaborator_memory_matches_topic(row, topic_slug)
    ]
    profile_rows = [
        row
        for row in rows
        if str(row.get("memory_kind") or "").strip() in PROFILE_MEMORY_KINDS
    ]
    grouped = {
        kind: [
            row
            for row in profile_rows
            if str(row.get("memory_kind") or "").strip() == kind
        ]
        for kind in PROFILE_MEMORY_KINDS
    }
    preferred_tags = self._dedupe_strings(
        [tag for row in profile_rows for tag in (row.get("tags") or [])]
    )
    related_topics = self._dedupe_strings(
        [slug for row in profile_rows for slug in (row.get("related_topic_slugs") or [])]
    )
    preference_summaries = self._dedupe_strings(
        [str(row.get("summary") or "").strip() for row in grouped["preference"]]
    )
    working_style_summaries = self._dedupe_strings(
        [str(row.get("summary") or "").strip() for row in grouped["working_style"]]
    )
    trajectory_summaries = self._dedupe_strings(
        [str(row.get("summary") or "").strip() for row in grouped["trajectory"]]
    )
    coordination_summaries = self._dedupe_strings(
        [str(row.get("summary") or "").strip() for row in grouped["coordination"]]
    )
    status = "available" if profile_rows else "absent"
    if profile_rows:
        summary = (
            f"{len(grouped['preference'])} preference, "
            f"{len(grouped['working_style'])} working-style, "
            f"{len(grouped['trajectory'])} trajectory, and "
            f"{len(grouped['coordination'])} coordination signal(s) are recorded for "
            f"`{topic_slug}`."
        )
        if preference_summaries:
            summary += f" Latest preference: {preference_summaries[0]}"
    else:
        summary = "No collaborator profile is currently recorded for this topic."
    updated_at = (
        str(profile_rows[0].get("recorded_at") or "").strip()
        if profile_rows
        else _now_iso()
    )
    return {
        "artifact_kind": "collaborator_profile",
        "topic_slug": topic_slug,
        "status": status,
        "preference_count": len(grouped["preference"]),
        "working_style_count": len(grouped["working_style"]),
        "trajectory_count": len(grouped["trajectory"]),
        "coordination_count": len(grouped["coordination"]),
        "preference_summaries": preference_summaries,
        "working_style_summaries": working_style_summaries,
        "trajectory_summaries": trajectory_summaries,
        "coordination_summaries": coordination_summaries,
        "preferred_tags": preferred_tags,
        "related_topic_slugs": related_topics,
        "memory_ids": self._dedupe_strings(
            [str(row.get("memory_id") or "").strip() for row in profile_rows]
        ),
        "summary": summary,
        "updated_at": updated_at,
        "updated_by": updated_by,
    }


def render_collaborator_profile_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Collaborator profile",
        "",
        f"- Topic slug: `{payload.get('topic_slug') or '(missing)'}`",
        f"- Status: `{payload.get('status') or '(missing)'}`",
        f"- Preference count: `{payload.get('preference_count') or 0}`",
        f"- Working-style count: `{payload.get('working_style_count') or 0}`",
        f"- Trajectory count: `{payload.get('trajectory_count') or 0}`",
        f"- Coordination count: `{payload.get('coordination_count') or 0}`",
        (
            f"- Preferred tags: "
            f"`{', '.join(payload.get('preferred_tags') or []) or '(none)'}`"
        ),
        (
            f"- Related topics: "
            f"`{', '.join(payload.get('related_topic_slugs') or []) or '(none)'}`"
        ),
        "",
        payload.get("summary") or "(missing)",
    ]
    for header, key in (
        ("Preference summaries", "preference_summaries"),
        ("Working-style summaries", "working_style_summaries"),
        ("Trajectory summaries", "trajectory_summaries"),
        ("Coordination summaries", "coordination_summaries"),
    ):
        lines.extend(["", f"## {header}", ""])
        for row in payload.get(key) or ["(none)"]:
            lines.append(f"- {row}")
    return "\n".join(lines) + "\n"


def materialize_collaborator_profile_surface(
    self,
    *,
    runtime_root: Path,
    topic_slug: str,
    updated_by: str,
) -> tuple[dict[str, Path], dict[str, Any]]:
    paths = collaborator_profile_paths(runtime_root)
    payload = derive_collaborator_profile(
        self,
        topic_slug=topic_slug,
        updated_by=updated_by,
    )
    payload = {
        **payload,
        "path": self._relativize(paths["json"]),
        "note_path": self._relativize(paths["note"]),
    }
    _write_json(paths["json"], payload)
    paths["note"].write_text(
        render_collaborator_profile_markdown(payload),
        encoding="utf-8",
    )
    return paths, payload


def normalize_collaborator_profile_for_bundle(
    self,
    *,
    shell_surfaces: dict[str, Any],
    runtime_root: Path,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    profile = dict(shell_surfaces.get("collaborator_profile") or {})
    if not profile:
        profile = empty_collaborator_profile(
            topic_slug=topic_slug,
            updated_by=updated_by,
        )
    paths = collaborator_profile_paths(runtime_root)
    if not str(profile.get("path") or "").strip():
        profile["path"] = self._relativize(paths["json"])
    if not str(profile.get("note_path") or "").strip():
        profile["note_path"] = self._relativize(paths["note"])
    return profile


def collaborator_profile_must_read_entry(
    profile: dict[str, Any],
) -> dict[str, str] | None:
    if str(profile.get("status") or "") != "available":
        return None
    note_path = str(profile.get("note_path") or "").strip()
    if not note_path:
        return None
    return {
        "path": note_path,
        "reason": (
            "Topic-scoped collaborator profile is available. Read it before "
            "repeating an old route preference or working-style mismatch."
        ),
    }


def append_collaborator_profile_markdown(
    lines: list[str],
    profile: dict[str, Any],
) -> None:
    lines.extend(
        [
            "## Collaborator profile",
            "",
            f"- Status: `{profile.get('status') or '(missing)'}`",
            f"- Preference count: `{profile.get('preference_count') or 0}`",
            f"- Working-style count: `{profile.get('working_style_count') or 0}`",
            f"- Trajectory count: `{profile.get('trajectory_count') or 0}`",
            f"- Coordination count: `{profile.get('coordination_count') or 0}`",
            f"- Note path: `{profile.get('note_path') or '(missing)'}`",
            "",
            f"{profile.get('summary') or '(missing)'}",
            "",
        ]
    )
