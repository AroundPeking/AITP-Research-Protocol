from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _dedupe_strings(values: Iterable[Any]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value or "").strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def research_trajectory_paths(runtime_root: Path) -> dict[str, Path]:
    return {
        "json": runtime_root / "research_trajectory.active.json",
        "note": runtime_root / "research_trajectory.active.md",
    }


def research_trajectory_history_path(runtime_root: Path) -> Path:
    return runtime_root / "research_trajectory.history.jsonl"


def _normalize_decision_row(
    row: dict[str, Any] | Any,
    *,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    payload = row if isinstance(row, dict) else {"summary": str(row or "").strip()}
    recorded_at = str(payload.get("recorded_at") or "").strip() or _now_iso()
    summary = str(payload.get("summary") or "").strip()
    if not summary:
        summary = "Recorded research trajectory decision."
    decision_id = str(payload.get("decision_id") or "").strip()
    if not decision_id:
        decision_id = f"trajectory-{recorded_at}"
    return {
        "decision_id": decision_id,
        "recorded_at": recorded_at,
        "topic_slug": str(payload.get("topic_slug") or topic_slug).strip(),
        "run_id": str(payload.get("run_id") or "").strip(),
        "route": str(payload.get("route") or payload.get("selected_route") or "").strip(),
        "step": str(payload.get("step") or "").strip(),
        "decision": str(payload.get("decision") or "").strip(),
        "summary": summary,
        "rollback_to": str(payload.get("rollback_to") or "").strip(),
        "selected_outcome": str(payload.get("selected_outcome") or "").strip(),
        "success_reason": str(payload.get("success_reason") or "").strip(),
        "failure_reason": str(payload.get("failure_reason") or "").strip(),
        "validation_style": str(payload.get("validation_style") or "").strip(),
        "tags": _dedupe_strings(payload.get("tags") or []),
        "related_topic_slugs": _dedupe_strings(
            payload.get("related_topic_slugs") or []
        ),
        "updated_by": str(payload.get("updated_by") or updated_by).strip(),
    }


def _load_decision_rows(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
) -> list[dict[str, Any]]:
    rows = [
        _normalize_decision_row(
            row,
            topic_slug=str(row.get("topic_slug") or topic_slug or "").strip(),
            updated_by=str(row.get("updated_by") or "aitp-service").strip(),
        )
        for row in _read_jsonl(research_trajectory_history_path(runtime_root))
    ]
    if topic_slug:
        rows = [
            row
            for row in rows
            if str(row.get("topic_slug") or "").strip() == str(topic_slug).strip()
        ]
    rows.sort(
        key=lambda item: (
            str(item.get("recorded_at") or ""),
            str(item.get("decision_id") or ""),
        ),
        reverse=True,
    )
    return rows


def record_decision(
    runtime_root: Path,
    *,
    topic_slug: str,
    decision: str,
    updated_by: str = "aitp-service",
    summary: str | None = None,
    run_id: str | None = None,
    route: str | None = None,
    step: str | None = None,
    rollback_to: str | None = None,
    selected_outcome: str | None = None,
    success_reason: str | None = None,
    failure_reason: str | None = None,
    validation_style: str | None = None,
    tags: list[str] | None = None,
    related_topic_slugs: list[str] | None = None,
) -> tuple[Path, dict[str, Any]]:
    row = _normalize_decision_row(
        {
            "topic_slug": topic_slug,
            "run_id": str(run_id or "").strip(),
            "route": str(route or "").strip(),
            "step": str(step or "").strip(),
            "decision": str(decision or "").strip(),
            "summary": str(summary or decision or "").strip(),
            "rollback_to": str(rollback_to or "").strip(),
            "selected_outcome": str(selected_outcome or "").strip(),
            "success_reason": str(success_reason or "").strip(),
            "failure_reason": str(failure_reason or "").strip(),
            "validation_style": str(validation_style or "").strip(),
            "tags": tags or [],
            "related_topic_slugs": related_topic_slugs or [],
            "updated_by": updated_by,
        },
        topic_slug=topic_slug,
        updated_by=updated_by,
    )
    path = research_trajectory_history_path(runtime_root)
    rows = _read_jsonl(path)
    rows.append(row)
    _write_jsonl(path, rows)
    return path, row


def analyze_decision_patterns(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
) -> dict[str, Any]:
    rows = _load_decision_rows(runtime_root, topic_slug=topic_slug)
    route_counts: dict[str, int] = {}
    rollback_counts: dict[str, int] = {}
    validation_counts: dict[str, int] = {}
    route_sequences: dict[str, int] = {}
    ordered = list(reversed(rows))
    for index, row in enumerate(ordered):
        route = str(row.get("route") or "").strip()
        rollback_to = str(row.get("rollback_to") or "").strip()
        validation_style = str(row.get("validation_style") or "").strip()
        if route:
            route_counts[route] = route_counts.get(route, 0) + 1
        if rollback_to:
            rollback_counts[rollback_to] = rollback_counts.get(rollback_to, 0) + 1
        if validation_style:
            validation_counts[validation_style] = (
                validation_counts.get(validation_style, 0) + 1
            )
        if index + 1 < len(ordered):
            next_route = str(ordered[index + 1].get("route") or "").strip()
            if route and next_route:
                key = f"{route} -> {next_route}"
                route_sequences[key] = route_sequences.get(key, 0) + 1
    preferred_routes = [
        key for key, _ in sorted(route_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    frequent_rollbacks = [
        key
        for key, _ in sorted(rollback_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    preferred_validation_style = ""
    if validation_counts:
        preferred_validation_style = max(
            validation_counts.items(),
            key=lambda item: (item[1], item[0]),
        )[0]
    dominant_sequence = ""
    if route_sequences:
        dominant_sequence = max(
            route_sequences.items(),
            key=lambda item: (item[1], item[0]),
        )[0]
    summary_parts: list[str] = []
    if preferred_routes:
        summary_parts.append(f"Preferred route: {preferred_routes[0]}")
    if dominant_sequence:
        summary_parts.append(f"Common sequence: {dominant_sequence}")
    if frequent_rollbacks:
        summary_parts.append(f"Rollback target: {frequent_rollbacks[0]}")
    if preferred_validation_style:
        summary_parts.append(
            f"Validation preference: {preferred_validation_style}"
        )
    summary = (
        "; ".join(summary_parts)
        if summary_parts
        else "No trajectory pattern is currently strong enough to summarize."
    )
    return {
        "topic_slug": str(topic_slug or "").strip() or None,
        "decision_count": len(rows),
        "preferred_routes": preferred_routes,
        "frequent_rollbacks": frequent_rollbacks,
        "route_sequences": [
            {"sequence": key, "count": count}
            for key, count in sorted(
                route_sequences.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ],
        "preferred_validation_style": preferred_validation_style,
        "summary": summary,
    }


def get_trajectory(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    rows = _load_decision_rows(runtime_root, topic_slug=topic_slug)
    patterns = analyze_decision_patterns(runtime_root, topic_slug=topic_slug)
    latest = rows[0] if rows else {}
    return {
        "topic_slug": str(topic_slug or "").strip() or None,
        "decision_count": len(rows),
        "latest_decision": latest,
        "trajectory": rows[: max(1, limit)],
        "patterns": patterns,
        "history_path": str(research_trajectory_history_path(runtime_root)),
    }


def empty_research_trajectory(*, topic_slug: str, updated_by: str) -> dict[str, Any]:
    return {
        "artifact_kind": "research_trajectory",
        "topic_slug": topic_slug,
        "status": "absent",
        "trajectory_count": 0,
        "latest_run_id": "",
        "latest_summary": "",
        "trajectory_summaries": [],
        "related_topic_slugs": [],
        "recent_related_topic_slugs": [],
        "memory_ids": [],
        "summary": "No research trajectory is currently recorded for this topic.",
        "updated_at": _now_iso(),
        "updated_by": updated_by,
    }


def load_research_trajectory(
    runtime_root: Path,
    *,
    topic_slug: str,
    updated_by: str = "aitp-service",
) -> dict[str, Any] | None:
    json_path = research_trajectory_paths(runtime_root)["json"]
    if not json_path.exists():
        return None
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    payload = {
        **empty_research_trajectory(topic_slug=topic_slug, updated_by=updated_by),
        **payload,
    }
    payload["topic_slug"] = str(payload.get("topic_slug") or topic_slug)
    return payload


def derive_research_trajectory(
    self,
    *,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    rows = [
        row
        for row in self._load_collaborator_memory_rows()
        if self._collaborator_memory_matches_topic(row, topic_slug)
        and str(row.get("memory_kind") or "").strip() == "trajectory"
    ]
    primary_rows = [
        row for row in rows if str(row.get("topic_slug") or "").strip() == topic_slug
    ]
    related_rows = [
        row for row in rows if str(row.get("topic_slug") or "").strip() != topic_slug
    ]
    runtime_root = self._runtime_root(topic_slug)
    decision_rows = _load_decision_rows(runtime_root, topic_slug=topic_slug)
    patterns = analyze_decision_patterns(runtime_root, topic_slug=topic_slug)
    decision_summaries = [
        str(row.get("summary") or "").strip()
        for row in decision_rows
        if str(row.get("summary") or "").strip()
    ]
    ordered_rows = primary_rows + related_rows
    trajectory_summaries = self._dedupe_strings(
        [str(row.get("summary") or "").strip() for row in ordered_rows]
        + decision_summaries
    )
    related_topic_slugs = self._dedupe_strings(
        [
            str(slug).strip()
            for row in rows
            for slug in (row.get("related_topic_slugs") or [])
            if str(slug).strip() and str(slug).strip() != topic_slug
        ]
        + [
            str(slug).strip()
            for row in decision_rows
            for slug in (row.get("related_topic_slugs") or [])
            if str(slug).strip() and str(slug).strip() != topic_slug
        ]
    )
    recent_related_topic_slugs = self._dedupe_strings(
        [
            str(row.get("topic_slug") or "").strip()
            for row in self.recent_topics(limit=25)
            if str(row.get("topic_slug") or "").strip() in related_topic_slugs
        ]
    )
    latest_run_id = next(
        (
            str(row.get("run_id") or "").strip()
            for row in [*decision_rows, *ordered_rows]
            if str(row.get("run_id") or "").strip()
        ),
        "",
    )
    latest_summary = trajectory_summaries[0] if trajectory_summaries else ""
    total_count = len(rows) + len(decision_rows)
    status = "available" if total_count else "absent"
    summary = "No research trajectory is currently recorded for this topic."
    if total_count:
        summary = (
            f"{total_count} trajectory signal(s) connect `{topic_slug}` across "
            f"{len(related_topic_slugs)} related topic(s). Latest trajectory: "
            f"{latest_summary}"
        )
        if patterns.get("decision_count"):
            summary += f" Pattern: {patterns.get('summary') or '(missing)'}"
    updated_at = next(
        (
            str(row.get("recorded_at") or "").strip()
            for row in [*decision_rows, *ordered_rows]
            if str(row.get("recorded_at") or "").strip()
        ),
        _now_iso(),
    )
    return {
        "artifact_kind": "research_trajectory",
        "topic_slug": topic_slug,
        "status": status,
        "trajectory_count": total_count,
        "latest_run_id": latest_run_id,
        "latest_summary": latest_summary,
        "trajectory_summaries": trajectory_summaries,
        "related_topic_slugs": related_topic_slugs,
        "recent_related_topic_slugs": recent_related_topic_slugs,
        "memory_ids": self._dedupe_strings(
            [str(row.get("memory_id") or "").strip() for row in rows]
            + [str(row.get("decision_id") or "").strip() for row in decision_rows]
        ),
        "summary": summary,
        "updated_at": updated_at,
        "updated_by": updated_by,
    }


def render_research_trajectory_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Research trajectory",
        "",
        f"- Topic slug: `{payload.get('topic_slug') or '(missing)'}`",
        f"- Status: `{payload.get('status') or '(missing)'}`",
        f"- Trajectory count: `{payload.get('trajectory_count') or 0}`",
        f"- Latest run id: `{payload.get('latest_run_id') or '(none)'}`",
        (
            f"- Related topics: "
            f"`{', '.join(payload.get('related_topic_slugs') or []) or '(none)'}`"
        ),
        (
            f"- Recent related topics: "
            f"`{', '.join(payload.get('recent_related_topic_slugs') or []) or '(none)'}`"
        ),
        "",
        payload.get("summary") or "(missing)",
        "",
        "## Trajectory summaries",
        "",
    ]
    for row in payload.get("trajectory_summaries") or ["(none)"]:
        lines.append(f"- {row}")
    return "\n".join(lines) + "\n"


def materialize_research_trajectory_surface(
    self,
    *,
    runtime_root: Path,
    topic_slug: str,
    updated_by: str,
) -> tuple[dict[str, Path], dict[str, Any]]:
    paths = research_trajectory_paths(runtime_root)
    payload = derive_research_trajectory(
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
        render_research_trajectory_markdown(payload),
        encoding="utf-8",
    )
    return paths, payload


def normalize_research_trajectory_for_bundle(
    self,
    *,
    shell_surfaces: dict[str, Any],
    runtime_root: Path,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    trajectory = dict(shell_surfaces.get("research_trajectory") or {})
    if not trajectory:
        trajectory = empty_research_trajectory(
            topic_slug=topic_slug,
            updated_by=updated_by,
        )
    paths = research_trajectory_paths(runtime_root)
    if not str(trajectory.get("path") or "").strip():
        trajectory["path"] = self._relativize(paths["json"])
    if not str(trajectory.get("note_path") or "").strip():
        trajectory["note_path"] = self._relativize(paths["note"])
    return trajectory


def research_trajectory_must_read_entry(
    trajectory: dict[str, Any],
) -> dict[str, str] | None:
    if str(trajectory.get("status") or "") != "available":
        return None
    note_path = str(trajectory.get("note_path") or "").strip()
    if not note_path:
        return None
    return {
        "path": note_path,
        "reason": (
            "Recent trajectory context is available for this topic. Read it before "
            "resuming work as if this session had no history."
        ),
    }


def append_research_trajectory_markdown(
    lines: list[str],
    trajectory: dict[str, Any],
) -> None:
    lines.extend(
        [
            "## Research trajectory",
            "",
            f"- Status: `{trajectory.get('status') or '(missing)'}`",
            f"- Trajectory count: `{trajectory.get('trajectory_count') or 0}`",
            f"- Latest run id: `{trajectory.get('latest_run_id') or '(none)'}`",
            f"- Note path: `{trajectory.get('note_path') or '(missing)'}`",
            "",
            f"{trajectory.get('summary') or '(missing)'}",
            "",
        ]
    )
