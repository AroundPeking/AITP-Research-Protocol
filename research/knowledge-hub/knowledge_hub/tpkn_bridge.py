from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


AITP_TO_TPKN_TYPE = {
    "concept": "concept",
    "claim_card": "claim",
    "derivation_object": "derivation",
    "method": "method",
    "workflow": "method",
    "bridge": "bridge",
    "validation_pattern": "method",
    "warning_note": "warning",
}

AITP_ID_PREFIX_TO_TPKN_TYPE = {
    "concept": "concept",
    "claim_card": "claim",
    "derivation_object": "derivation",
    "method": "method",
    "workflow": "method",
    "bridge": "bridge",
    "validation_pattern": "method",
    "warning_note": "warning",
}

TPKN_UNIT_DIRS = {
    "concept": "units/concepts",
    "claim": "units/claims",
    "derivation": "units/derivations",
    "method": "units/methods",
    "bridge": "units/bridges",
    "warning": "units/warnings",
}

SOURCE_MANIFEST_REQUIRED_URL_KEYS = ("abs", "pdf", "doi")


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "aitp"


def today_iso() -> str:
    return datetime.now().date().isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_or_replace_jsonl(path: Path, row: dict[str, Any], *, key: str) -> None:
    rows = [existing for existing in read_jsonl(path) if existing.get(key) != row.get(key)]
    rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in rows),
        encoding="utf-8",
    )


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def load_unit_index_rows(tpkn_root: Path) -> list[dict[str, Any]]:
    unit_index_path = tpkn_root / "indexes" / "unit_index.jsonl"
    if unit_index_path.exists():
        return read_jsonl(unit_index_path)

    rows: list[dict[str, Any]] = []
    for unit_type, relative_dir in TPKN_UNIT_DIRS.items():
        unit_dir = tpkn_root / relative_dir
        if not unit_dir.exists():
            continue
        for unit_path in sorted(unit_dir.glob("*.json")):
            payload = read_json(unit_path)
            if payload is None:
                continue
            rows.append(
                {
                    "id": payload["id"],
                    "type": payload["type"],
                    "title": payload["title"],
                    "summary": payload["summary"],
                    "path": str(unit_path.relative_to(tpkn_root)),
                    "domain": payload.get("domain"),
                    "subdomain": payload.get("subdomain"),
                    "tags": payload.get("tags") or [],
                    "aliases": payload.get("aliases") or [],
                    "dependencies": payload.get("dependencies") or [],
                    "related_units": payload.get("related_units") or [],
                    "formalization_status": payload.get("formalization_status"),
                    "validation_status": payload.get("validation_status"),
                    "maturity": payload.get("maturity"),
                    "source_anchor_count": len(payload.get("source_anchors") or []),
                }
            )
    return rows


def find_collision_rows(
    *,
    tpkn_root: Path,
    candidate_title: str,
    candidate_summary: str,
    candidate_tags: list[str],
    candidate_aliases: list[str],
    domain: str | None,
    target_type: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    title_norm = normalize_text(candidate_title)
    alias_norms = {normalize_text(value) for value in candidate_aliases if value.strip()}
    tag_set = {tag.strip().lower() for tag in candidate_tags if tag.strip()}

    scored: list[tuple[int, dict[str, Any]]] = []
    for row in load_unit_index_rows(tpkn_root):
        score = 0
        row_title = normalize_text(str(row.get("title") or ""))
        row_aliases = {normalize_text(value) for value in row.get("aliases") or [] if str(value).strip()}
        row_tags = {str(value).strip().lower() for value in row.get("tags") or [] if str(value).strip()}
        row_type = str(row.get("type") or "")
        row_domain = str(row.get("domain") or "")

        if row_type == target_type:
            score += 2
        if row_title == title_norm:
            score += 10
        if title_norm in row_aliases or row_title in alias_norms:
            score += 6
        if alias_norms & row_aliases:
            score += 4
        if tag_set and row_tags:
            score += min(3, len(tag_set & row_tags))
        if domain and row_domain and domain == row_domain:
            score += 1
        if candidate_summary and row.get("summary") and normalize_text(candidate_summary) == normalize_text(str(row["summary"])):
            score += 5
        if score <= 0:
            continue
        scored.append((score, row))

    scored.sort(
        key=lambda item: (
            -item[0],
            str(item[1].get("type") or ""),
            str(item[1].get("title") or ""),
        )
    )
    return [row for _, row in scored[:limit]]


def map_aitp_candidate_type(candidate_type: str) -> str:
    mapped = AITP_TO_TPKN_TYPE.get(candidate_type)
    if mapped is None:
        raise ValueError(f"Unsupported AITP candidate_type for TPKN promotion: {candidate_type}")
    return mapped


def _map_aitp_id_to_tpkn_id(identifier: str) -> str | None:
    if ":" not in identifier:
        return None
    prefix, slug = identifier.split(":", 1)
    mapped_prefix = AITP_ID_PREFIX_TO_TPKN_TYPE.get(prefix)
    if mapped_prefix is None:
        return None
    return f"{mapped_prefix}:{slug}"


def derive_tpkn_unit_id(candidate: dict[str, Any], target_type: str) -> str:
    for identifier in candidate.get("intended_l2_targets") or []:
        mapped = _map_aitp_id_to_tpkn_id(str(identifier))
        if mapped and mapped.startswith(f"{target_type}:"):
            return mapped
    slug = str(candidate.get("candidate_id") or "").split(":", 1)[-1]
    return f"{target_type}:{slugify(slug)}"


def choose_source_row(
    *,
    source_rows: list[dict[str, Any]],
    candidate: dict[str, Any],
) -> dict[str, Any] | None:
    origin_ids = {str(ref.get("id") or "").strip() for ref in candidate.get("origin_refs") or [] if str(ref.get("id") or "").strip()}
    for row in source_rows:
        source_id = str(row.get("source_id") or "").strip()
        if source_id and source_id in origin_ids:
            return row
    for row in source_rows:
        if str(row.get("source_type") or "").strip() == "paper":
            return row
    return source_rows[0] if source_rows else None


def ensure_source_manifest(
    *,
    tpkn_root: Path,
    source_row: dict[str, Any] | None,
    source_id: str,
    source_section: str,
    source_section_title: str,
    source_section_summary: str,
) -> tuple[Path, bool]:
    source_slug = source_id.split(":", 1)[-1]
    manifest_path = tpkn_root / "sources" / source_slug / "manifest.json"
    existing = read_json(manifest_path)
    created = existing is None
    provenance = (source_row or {}).get("provenance") or {}
    acquired_at = str((source_row or {}).get("acquired_at") or today_iso())
    published = str(provenance.get("published") or "")[:10] or acquired_at[:10]
    updated = str(provenance.get("updated") or "")[:10] or published
    title = str((source_row or {}).get("title") or source_id)
    authors = [str(value) for value in provenance.get("authors") or [] if str(value).strip()]
    urls = {
        "abs": str(provenance.get("abs_url") or ""),
        "pdf": str(provenance.get("pdf_url") or ""),
        "doi": str(provenance.get("doi") or ""),
    }
    optional_urls = {
        "source_archive": str(provenance.get("source_url") or ""),
        "journal": str(provenance.get("journal_url") or ""),
    }

    if existing is None:
        manifest = {
            "source_id": source_id,
            "title": title,
            "authors": authors,
            "version": str(provenance.get("arxiv_id") or provenance.get("versioned_id") or "unknown"),
            "submitted_date": published,
            "updated_date": updated,
            "canonical_scope": f"AITP source-onboarding bridge for {source_id}.",
            "urls": urls,
            "section_map": [],
            "equation_map": [],
            "figure_map": [],
        }
        for key, value in optional_urls.items():
            if value:
                manifest["urls"][key] = value
    else:
        manifest = existing
        manifest.setdefault("section_map", [])
        manifest.setdefault("equation_map", [])
        manifest.setdefault("figure_map", [])

    section_ids = {str(entry.get("id") or "") for entry in manifest.get("section_map") or []}
    if source_section not in section_ids:
        manifest["section_map"].append(
            {
                "id": source_section,
                "title": source_section_title,
                "summary": source_section_summary,
            }
        )

    for key in SOURCE_MANIFEST_REQUIRED_URL_KEYS:
        manifest.setdefault("urls", {})
        manifest["urls"].setdefault(key, "")

    write_json(manifest_path, manifest)
    return manifest_path, created


def build_tpkn_unit(
    *,
    candidate: dict[str, Any],
    unit_id: str,
    target_type: str,
    domain: str,
    subdomain: str,
    source_id: str,
    source_section: str,
    source_anchor_notes: str,
    existing_tpkn_ids: set[str],
) -> dict[str, Any]:
    assumptions = [str(value) for value in candidate.get("assumptions") or [] if str(value).strip()]
    if not assumptions:
        assumptions = ["Promoted from an AITP candidate; refine assumptions in later review."]

    dependencies: list[str] = []
    related_units: list[str] = []
    for identifier in candidate.get("intended_l2_targets") or []:
        mapped = _map_aitp_id_to_tpkn_id(str(identifier))
        if not mapped or mapped == unit_id or mapped not in existing_tpkn_ids:
            continue
        if mapped not in dependencies:
            dependencies.append(mapped)
    for ref in candidate.get("origin_refs") or []:
        mapped = _map_aitp_id_to_tpkn_id(str(ref.get("id") or ""))
        if not mapped or mapped == unit_id or mapped not in existing_tpkn_ids:
            continue
        if mapped not in related_units and mapped not in dependencies:
            related_units.append(mapped)

    return {
        "id": unit_id,
        "type": target_type,
        "title": str(candidate["title"]),
        "summary": str(candidate["summary"]),
        "domain": domain,
        "subdomain": subdomain,
        "tags": sorted(
            {
                str(candidate.get("candidate_type") or "").strip(),
                str(candidate.get("topic_slug") or "").strip(),
                target_type,
            }
            - {""}
        ),
        "aliases": [],
        "assumptions": assumptions,
        "regime": (
            f"Promoted from AITP topic {candidate['topic_slug']} via candidate {candidate['candidate_id']} "
            "after explicit human approval."
        ),
        "scope": str(candidate.get("question") or candidate["summary"]),
        "dependencies": dependencies,
        "related_units": related_units,
        "source_anchors": [
            {
                "source_id": source_id,
                "section": source_section,
                "notes": source_anchor_notes,
            }
        ],
        "formalization_status": "candidate",
        "validation_status": "validated",
        "maturity": "seed",
        "failure_modes": [
            "Review the regime and assumptions before treating this promoted unit as stable."
        ],
        "formal_targets": ["aitp-l2"],
        "retrieval_hints": [
            f"Promoted from AITP candidate {candidate['candidate_id']}.",
        ],
        "created_at": today_iso(),
        "updated_at": today_iso(),
    }


def unit_path_for(tpkn_root: Path, unit_type: str, unit_id: str) -> Path:
    relative_dir = TPKN_UNIT_DIRS.get(unit_type)
    if relative_dir is None:
        raise ValueError(f"Unsupported TPKN unit type: {unit_type}")
    slug = unit_id.split(":", 1)[-1]
    return tpkn_root / relative_dir / f"{slug}.json"


def run_tpkn_checks(tpkn_root: Path) -> dict[str, Any]:
    commands = {
        "check": ["python3", "scripts/kb.py", "check"],
        "build": ["python3", "scripts/kb.py", "build"],
    }
    results: dict[str, Any] = {}
    for key, command in commands.items():
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            cwd=tpkn_root,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
            raise RuntimeError(f"TPKN {key} failed: {message}")
        results[key] = {
            "command": command,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    return results
