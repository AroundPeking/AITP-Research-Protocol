"""Read-only manifest for legacy global L2 graph migration planning."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from brain.v5.markdown import read_md
from brain.v5.paths import WorkspacePaths


def build_legacy_l2_graph_manifest(
    ws: WorkspacePaths,
    *,
    legacy_l2_dir: str | Path = "",
) -> dict[str, Any]:
    """Scan legacy L2 files without promoting them into typed memory."""

    l2_dir = Path(legacy_l2_dir) if legacy_l2_dir else ws.base / "research" / "aitp-topics" / "L2"
    if not l2_dir.exists():
        return _empty_manifest(l2_dir, status="missing_legacy_l2_dir")
    entries = _scan_entries(l2_dir / "entries")
    graph_files = _scan_graph_files(l2_dir / "graph")
    graph_counts = _graph_counts(graph_files)
    has_graph = any(graph_counts.values())
    migration_work_items = _migration_work_items(entries, graph_files)
    counts = {
        "entries": len(entries),
        **graph_counts,
        "index_files": len(_obsidian_view_targets(l2_dir)),
    }
    return {
        "kind": "legacy_l2_graph_manifest",
        "legacy_l2_dir": str(l2_dir),
        "legacy_shape": "global_l2_graph",
        "typed_migration_status": (
            "needs_typed_l2_migration" if entries or has_graph else "no_legacy_l2_records_found"
        ),
        "counts": counts,
        "entries_by_role": _counts_by(entries, "role"),
        "entries_by_status": _counts_by(entries, "status"),
        "entry_samples": entries[:10],
        "obsidian_view_targets": _obsidian_view_targets(l2_dir),
        "obsidian_view_maturity": _obsidian_view_maturity(l2_dir),
        "migration_worklist_status": (
            "pending_typed_migration" if migration_work_items else "no_legacy_l2_work_items"
        ),
        "work_item_count": len(migration_work_items),
        "work_item_counts_by_kind": _work_item_counts_by_kind(migration_work_items),
        "migration_work_items": migration_work_items[:100],
        "next_actions": _next_actions(entries=entries, has_graph=has_graph),
        "truth_source": "legacy_l2_filesystem",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _empty_manifest(l2_dir: Path, *, status: str) -> dict[str, Any]:
    return {
        "kind": "legacy_l2_graph_manifest",
        "legacy_l2_dir": str(l2_dir),
        "legacy_shape": "missing",
        "typed_migration_status": status,
        "counts": {
            "entries": 0,
            "graph_nodes": 0,
            "graph_edges": 0,
            "graph_steps": 0,
            "graph_towers": 0,
            "index_files": 0,
        },
        "entries_by_role": {},
        "entries_by_status": {},
        "entry_samples": [],
        "obsidian_view_targets": [],
        "obsidian_view_maturity": {
            "status": "missing_core_legacy_views",
            "core_views_available": False,
            "available_targets": [],
            "missing_core_targets": ["index.md", "entries/INDEX.md", "graph/index.html"],
        },
        "migration_worklist_status": "missing_legacy_l2_dir",
        "work_item_count": 0,
        "work_item_counts_by_kind": {
            "entry": 0,
            "graph_edge": 0,
            "graph_node": 0,
            "graph_step": 0,
            "graph_tower": 0,
        },
        "migration_work_items": [],
        "next_actions": ["locate_legacy_l2_directory"],
        "truth_source": "legacy_l2_filesystem",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _scan_entries(entries_dir: Path) -> list[dict[str, str]]:
    if not entries_dir.exists():
        return []
    entries: list[dict[str, str]] = []
    for path in sorted(entries_dir.glob("*.md")):
        if path.stem.upper().startswith("INDEX"):
            continue
        frontmatter, _body = read_md(path)
        entry_id = _text(frontmatter.get("entry_id")) or path.stem
        entries.append({
            "entry_id": entry_id,
            "role": _text(frontmatter.get("role")) or "unknown",
            "status": _text(frontmatter.get("status")) or "unknown",
            "lane": _lane_text(frontmatter.get("lane")),
            "path": str(path),
        })
    return entries


def _scan_graph_files(graph_dir: Path) -> list[dict[str, str]]:
    graph_files: list[dict[str, str]] = []
    for work_item_kind, dirname in (
        ("graph_node", "nodes"),
        ("graph_edge", "edges"),
        ("graph_step", "steps"),
        ("graph_tower", "towers"),
    ):
        path = graph_dir / dirname
        if not path.exists():
            continue
        for item in sorted(path.glob("*.md")):
            frontmatter, _body = read_md(item)
            legacy_id = (
                _text(frontmatter.get("node_id"))
                or _text(frontmatter.get("edge_id"))
                or _text(frontmatter.get("step_id"))
                or _text(frontmatter.get("tower_id"))
                or item.stem
            )
            graph_files.append({
                "work_item_kind": work_item_kind,
                "legacy_id": legacy_id,
                "role": _text(frontmatter.get("type")) or work_item_kind.removeprefix("graph_"),
                "status": _text(frontmatter.get("status")) or "legacy_graph",
                "path": str(item),
            })
    return graph_files


def _graph_counts(graph_files: list[dict[str, str]]) -> dict[str, int]:
    by_kind = _work_item_counts_by_kind(graph_files)
    return {
        "graph_nodes": by_kind["graph_node"],
        "graph_edges": by_kind["graph_edge"],
        "graph_steps": by_kind["graph_step"],
        "graph_towers": by_kind["graph_tower"],
    }


def _obsidian_view_targets(l2_dir: Path) -> list[str]:
    candidates = [
        "index.md",
        "entries/INDEX.md",
        "entries/INDEX_status.md",
        "entries/INDEX_pitfalls.md",
        "entries/INDEX_reverse.md",
        "graph/index.html",
    ]
    return [rel for rel in candidates if (l2_dir / rel).exists()]


def _obsidian_view_maturity(l2_dir: Path) -> dict[str, Any]:
    core_targets = ["index.md", "entries/INDEX.md", "graph/index.html"]
    available = _obsidian_view_targets(l2_dir)
    missing = [target for target in core_targets if target not in set(available)]
    if not missing:
        status = "core_legacy_views_available"
    elif available:
        status = "partial_legacy_views_available"
    else:
        status = "missing_core_legacy_views"
    return {
        "status": status,
        "core_views_available": not missing,
        "available_targets": available,
        "missing_core_targets": missing,
    }


def _migration_work_items(
    entries: list[dict[str, str]],
    graph_files: list[dict[str, str]],
) -> list[dict[str, Any]]:
    items = [
        _work_item(
            work_item_kind="entry",
            legacy_id=entry["entry_id"],
            role=entry["role"],
            status=entry["status"],
            source_path=entry["path"],
            recommended_target_surface="memory_entry_record",
            migration_action="review_and_promote_into_typed_l2_memory",
        )
        for entry in entries
    ]
    items.extend(
        _work_item(
            work_item_kind=item["work_item_kind"],
            legacy_id=item["legacy_id"],
            role=item["role"],
            status=item["status"],
            source_path=item["path"],
            recommended_target_surface=_target_surface_for_graph_kind(item["work_item_kind"]),
            migration_action=_migration_action_for_graph_kind(item["work_item_kind"]),
        )
        for item in graph_files
    )
    return items


def _work_item(
    *,
    work_item_kind: str,
    legacy_id: str,
    role: str,
    status: str,
    source_path: str,
    recommended_target_surface: str,
    migration_action: str,
) -> dict[str, Any]:
    return {
        "work_item_id": f"legacy_l2_{work_item_kind}:{legacy_id}",
        "work_item_kind": work_item_kind,
        "legacy_id": legacy_id,
        "role": role,
        "status": status,
        "source_path": source_path,
        "recommended_target_surface": recommended_target_surface,
        "migration_action": migration_action,
        "can_update_claim_trust": False,
    }


def _target_surface_for_graph_kind(work_item_kind: str) -> str:
    return {
        "graph_node": "physics_object_record",
        "graph_edge": "object_relation_record",
        "graph_step": "sensemaking_report_record",
        "graph_tower": "memory_entry_record",
    }.get(work_item_kind, "memory_entry_record")


def _migration_action_for_graph_kind(work_item_kind: str) -> str:
    return {
        "graph_node": "review_and_convert_legacy_l2_node_to_typed_physics_object",
        "graph_edge": "review_and_convert_legacy_l2_edge_to_typed_object_relation",
        "graph_step": "review_and_convert_legacy_l2_step_to_sensemaking_or_trace",
        "graph_tower": "review_and_convert_legacy_l2_tower_to_memory_entry",
    }.get(work_item_kind, "review_and_convert_legacy_l2_graph_file")


def _work_item_counts_by_kind(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "entry": 0,
        "graph_edge": 0,
        "graph_node": 0,
        "graph_step": 0,
        "graph_tower": 0,
    }
    for item in items:
        kind = item.get("work_item_kind")
        if kind in counts:
            counts[kind] += 1
    return counts


def _next_actions(*, entries: list[dict[str, str]], has_graph: bool) -> list[str]:
    actions: list[str] = []
    if entries:
        actions.append("migrate_legacy_l2_entries_into_memory_records")
    if has_graph:
        actions.append("migrate_legacy_l2_graph_edges_into_object_relations")
    if entries or has_graph:
        actions.extend([
            "rebuild_l2_obsidian_view_from_typed_graph",
            "keep_legacy_l2_orientation_only_until_typed_migration",
        ])
    if not actions:
        actions.append("locate_legacy_l2_directory")
    return actions


def _counts_by(entries: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        value = entry.get(field) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _lane_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(item) for item in value if _text(item))
    return _text(value)
