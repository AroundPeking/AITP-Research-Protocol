from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


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


def research_judgment_history_path(runtime_root: Path) -> Path:
    return runtime_root / "research_judgment.history.jsonl"


def _normalize_accuracy_status(predicted_outcome: str, actual_outcome: str) -> str:
    predicted = str(predicted_outcome or "").strip().lower()
    actual = str(actual_outcome or "").strip().lower()
    if not predicted or not actual:
        return "pending"
    return "correct" if predicted == actual else "incorrect"


def _normalize_judgment_row(
    row: dict[str, Any] | Any,
    *,
    topic_slug: str,
    updated_by: str,
) -> dict[str, Any]:
    payload = row if isinstance(row, dict) else {"summary": str(row or "").strip()}
    recorded_at = str(payload.get("recorded_at") or "").strip() or _now_iso()
    summary = str(payload.get("summary") or "").strip()
    if not summary:
        summary = "Recorded research judgment."
    judgment_id = str(payload.get("judgment_id") or "").strip()
    if not judgment_id:
        judgment_id = f"judgment-{recorded_at}"
    predicted_outcome = str(payload.get("predicted_outcome") or "").strip()
    actual_outcome = str(payload.get("actual_outcome") or "").strip()
    surprise_flag = bool(payload.get("surprise_flag"))
    if not surprise_flag:
        surprise_flag = actual_outcome.lower() in {"surprise", "unexpected"}
    stuckness_flag = bool(payload.get("stuckness_flag"))
    if not stuckness_flag:
        stuckness_flag = actual_outcome.lower() in {"stuck", "rollback", "repeat"}
    return {
        "judgment_id": judgment_id,
        "recorded_at": recorded_at,
        "topic_slug": str(payload.get("topic_slug") or topic_slug).strip(),
        "run_id": str(payload.get("run_id") or "").strip(),
        "judgment_kind": str(payload.get("judgment_kind") or "general").strip(),
        "summary": summary,
        "predicted_outcome": predicted_outcome,
        "actual_outcome": actual_outcome,
        "accuracy_status": str(payload.get("accuracy_status") or "").strip()
        or _normalize_accuracy_status(predicted_outcome, actual_outcome),
        "selected_action_id": str(payload.get("selected_action_id") or "").strip(),
        "selected_action_summary": str(
            payload.get("selected_action_summary") or ""
        ).strip(),
        "momentum_signal": str(payload.get("momentum_signal") or "").strip(),
        "stuckness_flag": stuckness_flag,
        "surprise_flag": surprise_flag,
        "evidence_refs": _dedupe_strings(payload.get("evidence_refs") or []),
        "tags": _dedupe_strings(payload.get("tags") or []),
        "updated_by": str(payload.get("updated_by") or updated_by).strip(),
    }


def _load_judgment_rows(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
) -> list[dict[str, Any]]:
    rows = [
        _normalize_judgment_row(
            row,
            topic_slug=str(row.get("topic_slug") or topic_slug or "").strip(),
            updated_by=str(row.get("updated_by") or "aitp-service").strip(),
        )
        for row in _read_jsonl(research_judgment_history_path(runtime_root))
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
            str(item.get("judgment_id") or ""),
        ),
        reverse=True,
    )
    return rows


def record_judgment(
    runtime_root: Path,
    *,
    topic_slug: str,
    judgment_kind: str,
    summary: str,
    updated_by: str = "aitp-service",
    run_id: str | None = None,
    predicted_outcome: str | None = None,
    actual_outcome: str | None = None,
    selected_action_id: str | None = None,
    selected_action_summary: str | None = None,
    momentum_signal: str | None = None,
    stuckness_flag: bool = False,
    surprise_flag: bool = False,
    evidence_refs: list[str] | None = None,
    tags: list[str] | None = None,
) -> tuple[Path, dict[str, Any]]:
    normalized_summary = str(summary or "").strip()
    if not normalized_summary:
        raise ValueError("summary must not be empty")
    row = _normalize_judgment_row(
        {
            "topic_slug": topic_slug,
            "run_id": str(run_id or "").strip(),
            "judgment_kind": str(judgment_kind or "general").strip(),
            "summary": normalized_summary,
            "predicted_outcome": str(predicted_outcome or "").strip(),
            "actual_outcome": str(actual_outcome or "").strip(),
            "selected_action_id": str(selected_action_id or "").strip(),
            "selected_action_summary": str(selected_action_summary or "").strip(),
            "momentum_signal": str(momentum_signal or "").strip(),
            "stuckness_flag": bool(stuckness_flag),
            "surprise_flag": bool(surprise_flag),
            "evidence_refs": evidence_refs or [],
            "tags": tags or [],
            "updated_by": updated_by,
        },
        topic_slug=topic_slug,
        updated_by=updated_by,
    )
    path = research_judgment_history_path(runtime_root)
    rows = _read_jsonl(path)
    rows.append(row)
    _write_jsonl(path, rows)
    return path, row


def get_judgment_history(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    rows = _load_judgment_rows(runtime_root, topic_slug=topic_slug)
    return {
        "topic_slug": str(topic_slug or "").strip() or None,
        "judgment_count": len(rows),
        "latest_judgment": rows[0] if rows else {},
        "judgments": rows[: max(1, limit)],
        "history_path": str(research_judgment_history_path(runtime_root)),
    }


def evaluate_judgment_accuracy(
    runtime_root: Path,
    *,
    topic_slug: str | None = None,
) -> dict[str, Any]:
    rows = _load_judgment_rows(runtime_root, topic_slug=topic_slug)
    resolved_rows = [
        row
        for row in rows
        if str(row.get("accuracy_status") or "").strip() in {"correct", "incorrect"}
    ]
    correct_count = sum(
        1
        for row in resolved_rows
        if str(row.get("accuracy_status") or "").strip() == "correct"
    )
    by_kind: dict[str, dict[str, int]] = {}
    for row in resolved_rows:
        kind = str(row.get("judgment_kind") or "general").strip()
        kind_bucket = by_kind.setdefault(kind, {"total": 0, "correct": 0})
        kind_bucket["total"] += 1
        if str(row.get("accuracy_status") or "").strip() == "correct":
            kind_bucket["correct"] += 1
    accuracy_ratio = (
        round(correct_count / len(resolved_rows), 4) if resolved_rows else 0.0
    )
    return {
        "topic_slug": str(topic_slug or "").strip() or None,
        "judgment_count": len(rows),
        "resolved_count": len(resolved_rows),
        "correct_count": correct_count,
        "accuracy_ratio": accuracy_ratio,
        "latest_accuracy_status": str(
            (resolved_rows[0] if resolved_rows else {}).get("accuracy_status") or ""
        ),
        "by_kind": {
            kind: {
                **bucket,
                "accuracy_ratio": round(
                    bucket["correct"] / bucket["total"],
                    4,
                )
                if bucket["total"]
                else 0.0,
            }
            for kind, bucket in sorted(by_kind.items())
        },
        "summary": (
            f"Judgment accuracy is {accuracy_ratio:.0%} across {len(resolved_rows)} "
            f"resolved judgment(s)."
            if resolved_rows
            else "No resolved judgment accuracy data is currently available."
        ),
    }


def _history_ref(runtime_root: Path) -> str:
    path = research_judgment_history_path(runtime_root)
    return str(path) if path.exists() else ""


def _topic_memory_rows(
    self,
    *,
    topic_slug: str,
    memory_kind: str,
) -> list[dict[str, Any]]:
    return [
        row
        for row in self._load_collaborator_memory_rows()
        if str(row.get("memory_kind") or "").strip() == memory_kind
        and self._collaborator_memory_matches_topic(row, topic_slug)
    ]


def _dedup_refs(self, refs: list[str]) -> list[str]:
    return self._dedupe_strings(
        [str(ref).strip() for ref in refs if str(ref).strip()]
    )


def _consecutive_success_count(rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        accuracy_status = str(row.get("accuracy_status") or "").strip()
        momentum_signal = str(row.get("momentum_signal") or "").strip().lower()
        actual_outcome = str(row.get("actual_outcome") or "").strip().lower()
        if (
            accuracy_status == "correct"
            or momentum_signal in {"advance", "advancing", "success"}
            or actual_outcome in {"success", "advanced", "resolved"}
        ):
            count += 1
            continue
        break
    return count


def _consecutive_stuck_count(rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        actual_outcome = str(row.get("actual_outcome") or "").strip().lower()
        if bool(row.get("stuckness_flag")) or actual_outcome in {"stuck", "rollback", "repeat"}:
            count += 1
            continue
        break
    return count


def empty_research_judgment(
    *,
    topic_slug: str,
    run_id: str,
    updated_by: str,
) -> dict[str, Any]:
    return {
        "artifact_kind": "research_judgment",
        "topic_slug": topic_slug,
        "run_id": run_id,
        "status": "steady",
        "selected_action_id": None,
        "selected_action_summary": "No bounded action is currently selected.",
        "momentum": {
            "status": "unknown",
            "summary": "No bounded momentum signal is currently recorded.",
            "evidence_refs": [],
        },
        "stuckness": {
            "status": "none",
            "signal_count": 0,
            "latest_summary": "No durable stuckness signal is currently recorded.",
            "memory_ids": [],
            "evidence_refs": [],
        },
        "surprise": {
            "status": "none",
            "signal_count": 0,
            "latest_summary": "No durable surprise signal is currently recorded.",
            "memory_ids": [],
            "evidence_refs": [],
        },
        "guidance": [],
        "summary": "Momentum `unknown`; stuckness `none`; surprise `none`.",
        "updated_at": "",
        "updated_by": updated_by,
    }


def derive_research_judgment(
    self,
    *,
    topic_slug: str,
    latest_run_id: str,
    updated_by: str,
    topic_status_explainability: dict[str, Any],
    selected_pending_action: dict[str, Any] | None,
    open_gap_summary: dict[str, Any],
    strategy_memory: dict[str, Any],
    dependency_state: dict[str, Any],
    gap_map_path: str,
) -> dict[str, Any]:
    payload = empty_research_judgment(
        topic_slug=topic_slug,
        run_id=latest_run_id,
        updated_by=updated_by,
    )
    current_route_choice = topic_status_explainability.get("current_route_choice") or {}
    active_human_need = topic_status_explainability.get("active_human_need") or {}
    last_evidence_return = topic_status_explainability.get("last_evidence_return") or {}
    selected_action_id = (
        str((selected_pending_action or {}).get("action_id") or "").strip() or None
    )
    selected_action_summary = (
        str((selected_pending_action or {}).get("summary") or "").strip()
        or "No bounded action is currently selected."
    )

    stuckness_rows = _topic_memory_rows(
        self,
        topic_slug=topic_slug,
        memory_kind="stuckness",
    )
    surprise_rows = _topic_memory_rows(
        self,
        topic_slug=topic_slug,
        memory_kind="surprise",
    )
    trajectory_rows = _topic_memory_rows(
        self,
        topic_slug=topic_slug,
        memory_kind="trajectory",
    )
    runtime_root = self._runtime_root(topic_slug)
    judgment_rows = _load_judgment_rows(runtime_root, topic_slug=topic_slug)
    accuracy_summary = evaluate_judgment_accuracy(
        runtime_root,
        topic_slug=topic_slug,
    )
    recent_successes = _consecutive_success_count(judgment_rows)
    recent_stuck = _consecutive_stuck_count(judgment_rows)
    history_surprises = [row for row in judgment_rows if bool(row.get("surprise_flag"))]
    collaborator_note_ref = self._relativize(self._collaborator_memory_paths()["note"])
    collaborator_json_ref = self._relativize(self._collaborator_memory_paths()["jsonl"])
    strategy_latest_ref = str(strategy_memory.get("latest_path") or "").strip()
    last_evidence_ref = str(last_evidence_return.get("path") or "").strip()
    judgment_history_ref = _history_ref(runtime_root)

    if str(active_human_need.get("status") or "").strip() == "requested":
        momentum_status = "held"
        momentum_summary = (
            str(active_human_need.get("summary") or "").strip()
            or "Momentum is held at an active human checkpoint."
        )
        momentum_refs = _dedup_refs(
            self,
            [
                str(active_human_need.get("path") or ""),
                str(current_route_choice.get("next_action_decision_note_path") or ""),
                judgment_history_ref,
            ],
        )
    elif str(dependency_state.get("status") or "").strip() == "dependency_blocked":
        momentum_status = "stalled"
        momentum_summary = (
            str(dependency_state.get("summary") or "").strip()
            or "Momentum is stalled by an active topic dependency."
        )
        momentum_refs = _dedup_refs(
            self,
            [
                self._relativize(self._active_topics_registry_paths()["json"]),
                judgment_history_ref,
            ],
        )
    elif bool(open_gap_summary.get("requires_l0_return")) or str(
        open_gap_summary.get("status") or ""
    ).strip() == "capability_gap":
        momentum_status = "stalled"
        momentum_summary = (
            str(open_gap_summary.get("summary") or "").strip()
            or "Momentum is stalled until the current gap surface is discharged."
        )
        momentum_refs = _dedup_refs(self, [gap_map_path, judgment_history_ref])
    elif recent_successes >= 2:
        momentum_status = "advancing"
        momentum_summary = (
            f"Momentum is high after {recent_successes} consecutive successful "
            f"judgment(s). {accuracy_summary.get('summary') or ''}".strip()
        )
        momentum_refs = _dedup_refs(self, [judgment_history_ref, strategy_latest_ref])
    elif str(last_evidence_return.get("status") or "").strip() == "available":
        momentum_status = "advancing"
        momentum_summary = (
            str(last_evidence_return.get("summary") or "").strip()
            or "Momentum is advancing from a recent durable evidence return."
        )
        momentum_refs = _dedup_refs(self, [last_evidence_ref, strategy_latest_ref])
    elif selected_action_id:
        momentum_status = "queued"
        momentum_summary = (
            f"The current bounded route is queued on `{selected_action_summary}`."
        )
        momentum_refs = _dedup_refs(
            self,
            [
                str(current_route_choice.get("next_action_decision_note_path") or ""),
                strategy_latest_ref,
                judgment_history_ref,
            ],
        )
    else:
        momentum_status = "unknown"
        momentum_summary = "No bounded momentum signal is currently recorded."
        momentum_refs = _dedup_refs(self, [judgment_history_ref])

    stuckness_refs = _dedup_refs(
        self,
        [
            collaborator_note_ref,
            collaborator_json_ref,
            gap_map_path,
            strategy_latest_ref,
            judgment_history_ref,
        ],
    )
    if stuckness_rows:
        stuckness_status = "active"
        stuckness_summary = (
            str(stuckness_rows[0].get("summary") or "").strip()
            or "A stuckness signal is active."
        )
        stuckness_count = len(stuckness_rows)
        stuckness_ids = [
            str(row.get("memory_id") or "")
            for row in stuckness_rows
            if str(row.get("memory_id") or "").strip()
        ]
    elif recent_stuck >= 2:
        stuckness_status = "active"
        stuckness_summary = (
            f"Recent judgment history shows {recent_stuck} consecutive rollback or "
            f"repeat signal(s)."
        )
        stuckness_count = recent_stuck
        stuckness_ids = [
            str(row.get("judgment_id") or "")
            for row in judgment_rows[:recent_stuck]
            if str(row.get("judgment_id") or "").strip()
        ]
    elif str(open_gap_summary.get("status") or "").strip() in {
        "open",
        "return_to_L0",
        "capability_gap",
    }:
        stuckness_status = "active"
        stuckness_summary = (
            str(open_gap_summary.get("summary") or "").strip()
            or "The current gap surface indicates bounded stuckness."
        )
        stuckness_count = 1
        stuckness_ids = []
    elif int(strategy_memory.get("harmful_count") or 0) > 0 and int(
        strategy_memory.get("relevant_count") or 0
    ) > 0:
        stuckness_status = "active"
        stuckness_summary = (
            "Relevant harmful strategy memory overlaps with the current bounded route."
        )
        stuckness_count = 1
        stuckness_ids = []
    else:
        stuckness_status = "none"
        stuckness_summary = "No durable stuckness signal is currently recorded."
        stuckness_count = 0
        stuckness_ids = []
        stuckness_refs = []

    surprise_refs = _dedup_refs(
        self,
        [collaborator_note_ref, collaborator_json_ref, judgment_history_ref],
    )
    if surprise_rows:
        surprise_status = "active"
        surprise_summary = (
            str(surprise_rows[0].get("summary") or "").strip()
            or "A surprise signal is active."
        )
        surprise_count = len(surprise_rows)
        surprise_ids = [
            str(row.get("memory_id") or "")
            for row in surprise_rows
            if str(row.get("memory_id") or "").strip()
        ]
    elif history_surprises:
        surprise_status = "active"
        surprise_summary = (
            str(history_surprises[0].get("summary") or "").strip()
            or "Recent judgment history recorded an unexpected result."
        )
        surprise_count = len(history_surprises)
        surprise_ids = [
            str(row.get("judgment_id") or "")
            for row in history_surprises
            if str(row.get("judgment_id") or "").strip()
        ]
    else:
        surprise_status = "none"
        surprise_summary = "No durable surprise signal is currently recorded."
        surprise_count = 0
        surprise_ids = []
        surprise_refs = []

    guidance = []
    if momentum_status == "held":
        guidance.append(
            "Resolve the active human checkpoint before trusting heuristic queue selection."
        )
    elif momentum_status == "stalled":
        guidance.append(
            "Do not keep the current route on autopilot; discharge the blocker or reroute explicitly."
        )
    if stuckness_status == "active":
        guidance.append(
            "Read the stuckness signal before repeating the same bounded route."
        )
    if surprise_status == "active":
        guidance.append(
            "Read the surprise signal before smoothing the anomaly into routine prose."
        )
    guidance.extend(list(strategy_memory.get("guidance") or []))
    if trajectory_rows:
        guidance.append(
            f"Latest trajectory signal: "
            f"{str(trajectory_rows[0].get('summary') or '').strip() or 'review the current trajectory note.'}"
        )
    if accuracy_summary.get("resolved_count"):
        guidance.append(accuracy_summary.get("summary") or "")
    guidance = self._dedupe_strings(guidance)

    payload["selected_action_id"] = selected_action_id
    payload["selected_action_summary"] = selected_action_summary
    payload["momentum"] = {
        "status": momentum_status,
        "summary": momentum_summary,
        "evidence_refs": momentum_refs,
    }
    payload["stuckness"] = {
        "status": stuckness_status,
        "signal_count": stuckness_count,
        "latest_summary": stuckness_summary,
        "memory_ids": stuckness_ids,
        "evidence_refs": stuckness_refs,
    }
    payload["surprise"] = {
        "status": surprise_status,
        "signal_count": surprise_count,
        "latest_summary": surprise_summary,
        "memory_ids": surprise_ids,
        "evidence_refs": surprise_refs,
    }
    payload["guidance"] = guidance
    payload["status"] = (
        "signals_active"
        if (
            stuckness_status == "active"
            or surprise_status == "active"
            or momentum_status in {"held", "stalled"}
        )
        else "steady"
    )
    payload["summary"] = (
        f"Momentum `{momentum_status}`; stuckness `{stuckness_status}`; "
        f"surprise `{surprise_status}`."
        + (f" {guidance[0]}" if guidance else "")
    )
    payload["updated_at"] = self._coalesce_string(
        str(topic_status_explainability.get("updated_at") or "").strip(),
        str((judgment_rows[0] if judgment_rows else {}).get("recorded_at") or "").strip(),
        str((stuckness_rows[0] if stuckness_rows else {}).get("recorded_at") or "").strip(),
        str((surprise_rows[0] if surprise_rows else {}).get("recorded_at") or "").strip(),
        str((trajectory_rows[0] if trajectory_rows else {}).get("recorded_at") or "").strip(),
    )
    payload["updated_by"] = updated_by
    return payload


def render_research_judgment_markdown(payload: dict[str, Any]) -> str:
    momentum = payload.get("momentum") or {}
    stuckness = payload.get("stuckness") or {}
    surprise = payload.get("surprise") or {}
    lines = [
        "# Research judgment",
        "",
        f"- Topic slug: `{payload.get('topic_slug') or '(missing)'}`",
        f"- Run id: `{payload.get('run_id') or '(missing)'}`",
        f"- Status: `{payload.get('status') or '(missing)'}`",
        f"- Selected action id: `{payload.get('selected_action_id') or '(none)'}`",
        (
            f"- Selected action summary: "
            f"{payload.get('selected_action_summary') or '(missing)'}"
        ),
        "",
        payload.get("summary") or "(missing)",
        "",
        "## Momentum",
        "",
        f"- Status: `{momentum.get('status') or '(missing)'}`",
        (
            f"- Evidence refs: "
            f"`{', '.join(momentum.get('evidence_refs') or []) or '(none)'}`"
        ),
        "",
        momentum.get("summary") or "(missing)",
        "",
        "## Stuckness",
        "",
        f"- Status: `{stuckness.get('status') or '(missing)'}`",
        f"- Signal count: `{stuckness.get('signal_count') or 0}`",
        (
            f"- Memory ids: "
            f"`{', '.join(stuckness.get('memory_ids') or []) or '(none)'}`"
        ),
        (
            f"- Evidence refs: "
            f"`{', '.join(stuckness.get('evidence_refs') or []) or '(none)'}`"
        ),
        "",
        stuckness.get("latest_summary") or "(missing)",
        "",
        "## Surprise",
        "",
        f"- Status: `{surprise.get('status') or '(missing)'}`",
        f"- Signal count: `{surprise.get('signal_count') or 0}`",
        (
            f"- Memory ids: "
            f"`{', '.join(surprise.get('memory_ids') or []) or '(none)'}`"
        ),
        (
            f"- Evidence refs: "
            f"`{', '.join(surprise.get('evidence_refs') or []) or '(none)'}`"
        ),
        "",
        surprise.get("latest_summary") or "(missing)",
        "",
        "## Guidance",
        "",
    ]
    for row in payload.get("guidance") or ["(none)"]:
        lines.append(f"- {row}")
    return "\n".join(lines) + "\n"
