"""Migrate legacy knowledge-hub topics to v2 AITP format.

Usage:
    python scripts/migrate_legacy_topics.py <legacy_topics_dir> <v2_topics_root>

Legacy topics are in the old knowledge-hub JSON format. This script:
1. Reads each topic's metadata (title, slug, status, created_at)
2. Creates v2 directory structure with state.md
3. Copies raw legacy data to legacy/ subdirectory
4. Extracts source references to L0/ v2 format
5. Marks topic as "archived" with reason "migrated_from_legacy"
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


# Skip test/demo topics
SKIP_SLUGS = {
    "demo-topic",
    "test-bootstrap",
    "test-popup",
    "popup-test",
    "fresh-topic",
    "opencode-final-parity-probe-d",
    "opencode-parity-smoke-2026-04-13-fresh-a",
    "aitp-topic",
}


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _read_md(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _guess_lane(slug: str, title: str, topic_data: dict) -> str:
    """Guess research lane from topic metadata."""
    title_lower = title.lower()
    slug_lower = slug.lower()

    if any(kw in title_lower for kw in ["numerical", "benchmark", "code", "script", "convergence"]):
        return "code_method"
    if any(kw in title_lower for kw in ["jones", "algebra", "proof", "theorem", "formal"]):
        return "formal_theory"
    if any(kw in title_lower for kw in ["hs-", "haldane", "otoc", "chaos", "lyapunov"]):
        return "toy_numeric"
    if any(kw in title_lower for kw in ["qsgw", "librpa", "aims", "molecular", "band", "head-wing"]):
        return "code_method"
    if any(kw in title_lower for kw in ["rpa", "scrpa", "variational"]):
        return "formal_theory"
    if any(kw in title_lower for kw in ["von neumann", "mipt", "quantum gravit"]):
        return "formal_theory"
    if any(kw in title_lower for kw in ["witten", "category"]):
        return "formal_theory"

    # Check L3 runs for derivation vs numeric indicators
    l3_dir = Path(str(topic_data.get("_topic_path", ""))) / "L3"
    if l3_dir.exists():
        for run_dir in l3_dir.iterdir():
            derivation_path = run_dir / "derivation_records.jsonl"
            if derivation_path.exists():
                records = _read_jsonl(derivation_path)
                for rec in records:
                    kind = rec.get("derivation_kind", "")
                    if "numerical" in kind or "benchmark" in kind:
                        return "code_method"
                    if "formal" in kind or "proof" in kind:
                        return "formal_theory"

    return "formal_theory"  # default


def _guess_stage(slug: str, topic_path: Path) -> str:
    """Guess current stage from directory contents."""
    has_l3_runs = (topic_path / "L3" / "runs").exists() and any((topic_path / "L3" / "runs").iterdir())
    has_l4 = (topic_path / "L4").exists() and any((topic_path / "L4").iterdir())
    has_candidates = False

    if has_l3_runs:
        for run_dir in (topic_path / "L3" / "runs").iterdir():
            ledger = run_dir / "candidate_ledger.jsonl"
            if ledger.exists():
                rows = _read_jsonl(ledger)
                if rows:
                    has_candidates = True
                    break

    if has_l4 or has_candidates:
        return "L3"
    if has_l3_runs:
        return "L3"
    return "L1"


def _extract_sources(topic_path: Path) -> list[dict]:
    """Extract source information from L0 and L1."""
    sources = []

    # Check L0/topic.json
    l0_data = _read_json(topic_path / "L0" / "topic.json")
    if l0_data:
        source_refs = l0_data.get("source_refs", [])
        for ref in source_refs:
            if isinstance(ref, dict):
                sources.append(ref)
            elif isinstance(ref, str):
                sources.append({"id": ref, "title": ref})

    # Check L1/vault for source data
    vault_dir = topic_path / "L1" / "vault"
    if vault_dir.exists():
        vault_data = _read_json(vault_dir / "vault_manifest.json")
        if vault_data:
            for entry in vault_data.get("entries", []):
                sources.append({
                    "id": entry.get("source_id", ""),
                    "title": entry.get("title", ""),
                    "type": entry.get("source_type", "paper"),
                })

    return sources


def migrate_topic(legacy_path: Path, v2_root: Path) -> dict:
    """Migrate a single legacy topic to v2 format."""
    slug = legacy_path.name

    # Read metadata
    l1_data = _read_json(legacy_path / "L1" / "topic.json")
    l0_data = _read_json(legacy_path / "L0" / "topic.json")
    manifest = _read_md(legacy_path / "topic_manifest.md")

    title = ""
    old_status = ""
    created_at = ""

    if l1_data:
        title = l1_data.get("title", slug)
        old_status = l1_data.get("status", "")
        created_at = l1_data.get("created_at", "")
    elif l0_data:
        title = l0_data.get("title", slug)
        old_status = l0_data.get("status", "")
        created_at = l0_data.get("created_at", "")

    if not title:
        title = slug.replace("-", " ").title()

    topic_data = {"_topic_path": str(legacy_path)}
    lane = _guess_lane(slug, title, topic_data)
    stage = _guess_stage(slug, legacy_path)
    sources = _extract_sources(legacy_path)

    # Create v2 directory structure
    v2_topic = v2_root / slug
    v2_topic.mkdir(parents=True, exist_ok=True)

    now = datetime.now().astimezone().isoformat(timespec="seconds")

    # state.md
    state_fm = {
        "stage": "archived",
        "posture": "read",
        "lane": lane,
        "l3_subplane": None,
        "title": title,
        "created_at": created_at or now,
        "updated_at": now,
        "archived_at": now,
        "archive_reason": "migrated_from_legacy",
        "archive_category": "paused",
        "previous_stage": stage,
    }
    state_body = f"# {title}\n\nMigrated from legacy AITP knowledge-hub.\nPrevious stage: {stage}.\nLane: {lane}.\n"
    state_md = f"---\n"
    for k, v in state_fm.items():
        if v is not None:
            state_md += f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, str) else v}\n"
    state_md += f"---\n{state_body}\n"
    (v2_topic / "state.md").write_text(state_md, encoding="utf-8")

    # L0/sources/ — convert extracted sources to v2 format
    if sources:
        l0_dir = v2_topic / "L0" / "sources"
        l0_dir.mkdir(parents=True, exist_ok=True)
        for i, src in enumerate(sources):
            src_id = src.get("id", f"source-{i}").replace(" ", "-").lower()
            src_fm = {
                "source_id": src_id,
                "source_type": src.get("type", "paper"),
                "title": src.get("title", src_id),
                "registered_at": now,
            }
            src_md = f"---\n"
            for k, v in src_fm.items():
                src_md += f"{k}: {json.dumps(str(v), ensure_ascii=False)}\n"
            src_md += f"---\nMigrated from legacy topic.\n"
            # Clean src_id for filename
            safe_id = re.sub(r'[^\w\-.]', '_', src_id)
            (l0_dir / f"{safe_id}.md").write_text(src_md, encoding="utf-8")

    # legacy/ — copy raw data
    legacy_dest = v2_topic / "legacy"
    if legacy_dest.exists():
        shutil.rmtree(legacy_dest)
    shutil.copytree(legacy_path, legacy_dest)

    # runtime/log.md
    runtime_dir = v2_topic / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    log_content = f"# Topic Log\n\n## Events\n\n- {now} topic migrated from legacy knowledge-hub\n- {now} archived (previous_stage: {stage}, lane: {lane})\n"
    (runtime_dir / "log.md").write_text(log_content, encoding="utf-8")

    # runtime/index.md
    index_content = f"# {title}\n\n- Slug: `{slug}`\n- Lane: {lane}\n- Status: archived (migrated from legacy)\n- Previous stage: {stage}\n- Sources: {len(sources)} registered\n- Legacy data preserved in: `legacy/`\n"
    (runtime_dir / "index.md").write_text(index_content, encoding="utf-8")

    return {
        "slug": slug,
        "title": title,
        "lane": lane,
        "previous_stage": stage,
        "sources_count": len(sources),
    }


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <legacy_topics_dir> <v2_topics_root>")
        sys.exit(1)

    legacy_dir = Path(sys.argv[1])
    v2_root = Path(sys.argv[2])

    if not legacy_dir.exists():
        print(f"Error: {legacy_dir} does not exist")
        sys.exit(1)

    v2_root.mkdir(parents=True, exist_ok=True)

    # Create topics/ subdirectory if v2 layout expects it
    topics_dir = v2_root / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)

    # Collect legacy topics
    topics = sorted([d for d in legacy_dir.iterdir() if d.is_dir() and d.name not in SKIP_SLUGS])

    print(f"Found {len(topics)} legacy topics to migrate (skipping {len(SKIP_SLUGS)} test/demo)")

    migrated = []
    errors = []

    for topic_path in topics:
        try:
            result = migrate_topic(topic_path, topics_dir)
            migrated.append(result)
            print(f"  OK: {result['slug']} ({result['lane']}, prev={result['previous_stage']}, {result['sources_count']} sources)")
        except Exception as e:
            errors.append((topic_path.name, str(e)))
            print(f"  ERR: {topic_path.name}: {e}")

    # Summary
    print(f"\nMigration complete: {len(migrated)} topics migrated, {len(errors)} errors")

    # Write migration manifest
    manifest_path = v2_root / "migration_manifest.json"
    manifest_data = {
        "migrated_at": datetime.now().astimezone().isoformat(),
        "source_dir": str(legacy_dir),
        "total_migrated": len(migrated),
        "errors": len(errors),
        "topics": migrated,
        "skipped": sorted(SKIP_SLUGS),
        "error_details": [(s, e) for s, e in errors],
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
