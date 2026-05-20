"""Focused record writers for legacy-topic migration."""

from __future__ import annotations

from pathlib import Path

from brain.v5.evidence import record_evidence
from brain.v5.ids import prefixed_id
from brain.v5.markdown import read_md
from brain.v5.paths import WorkspacePaths
from brain.v5.sensemaking import record_sensemaking_report
from brain.v5.trace import TraceEvent, append_trace_event


def migrate_legacy_l1_understanding(
    ws: WorkspacePaths,
    root: Path,
    *,
    topic_id: str,
    claim_id: str,
) -> tuple[list[str], list[str]]:
    specs = [
        ("source_basis.md", "legacy_l1_source_basis", "Legacy L1 source basis"),
        (
            "convention_snapshot.md",
            "legacy_l1_convention_snapshot",
            "Legacy L1 convention snapshot",
        ),
        (
            "derivation_anchor_map.md",
            "legacy_l1_derivation_anchor_map",
            "Legacy L1 derivation anchor map",
        ),
        (
            "contradiction_register.md",
            "legacy_l1_contradiction_register",
            "Legacy L1 contradiction register",
        ),
    ]
    evidence_ids: list[str] = []
    report_ids: list[str] = []
    for filename, evidence_type, title in specs:
        path = root / "L1" / filename
        if not path.exists():
            continue
        fm, body = read_md(path)
        summary = str(fm.get("summary") or _first_paragraph(body) or title)
        evidence = record_evidence(
            ws,
            topic_id=topic_id,
            claim_id=claim_id,
            evidence_type=evidence_type,
            status="legacy_seed",
            summary=summary,
            supports_outputs=["evidence_or_provenance"],
            source_refs=[f"legacy_l1:{path.as_posix()}"],
        )
        report = record_sensemaking_report(
            ws,
            topic_id=topic_id,
            claim_id=claim_id,
            title=title,
            summary=summary,
            evidence_refs=[evidence.evidence_id],
            next_actions=["review_legacy_l1_understanding"],
        )
        evidence_ids.append(evidence.evidence_id)
        report_ids.append(report.report_id)
    return evidence_ids, report_ids


def migrate_legacy_runtime_log(
    ws: WorkspacePaths,
    root: Path,
    *,
    session_id: str,
    topic_id: str,
    claim_id: str,
) -> list[str]:
    log_path = root / "runtime" / "log.md"
    summaries = _legacy_runtime_log_summaries(log_path)
    if not summaries:
        return []

    trace_path = ws.root / "runtime" / "legacy_migration_trace.jsonl"
    event_ids: list[str] = []
    for index, summary in enumerate(summaries, start=1):
        event_id = prefixed_id(
            "event",
            f"legacy-runtime-log:{topic_id}:{index}:{summary}",
            max_slug=64,
        )
        event = TraceEvent(
            event_id=event_id,
            session_id=session_id,
            topic_id=topic_id,
            event_type="legacy_runtime_log",
            risk_level="legacy",
            claim_id=claim_id,
            payload={
                "source_ref": f"legacy_runtime_log:{log_path.as_posix()}#{index}",
                "summary": summary,
                "orientation_only": True,
            },
        )
        append_trace_event(trace_path, event)
        event_ids.append(event_id)
    return event_ids


def _legacy_runtime_log_summaries(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    summaries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        if stripped.startswith("-"):
            stripped = stripped[1:].strip()
        if stripped:
            summaries.append(stripped)
    return summaries


def _first_paragraph(body: str) -> str:
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if lines:
                break
            continue
        if stripped.startswith("#"):
            continue
        lines.append(stripped)
    return " ".join(lines)
