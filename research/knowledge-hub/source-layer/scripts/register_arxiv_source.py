#!/usr/bin/env python3
"""Register an arXiv paper into Layer 0 and create a Layer 1 intake projection."""

from __future__ import annotations

import argparse
import json
import re
import tarfile
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "arxiv-paper"


def short_summary(text: str, limit: int = 260) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."


def fetch_url(url: str, timeout: int = 60) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def fetch_metadata(arxiv_id: str) -> dict:
    query = urllib.parse.urlencode(
        {"search_query": f"id:{arxiv_id}", "start": 0, "max_results": 1}
    )
    url = f"https://export.arxiv.org/api/query?{query}"
    payload = fetch_url(url).decode("utf-8")
    root = ET.fromstring(payload)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        raise SystemExit(f"No arXiv entry found for {arxiv_id}")

    title = entry.findtext("atom:title", default="", namespaces=ATOM_NS).strip()
    summary = entry.findtext("atom:summary", default="", namespaces=ATOM_NS).strip()
    published = entry.findtext("atom:published", default="", namespaces=ATOM_NS).strip()
    updated = entry.findtext("atom:updated", default="", namespaces=ATOM_NS).strip()
    identifier = entry.findtext("atom:id", default="", namespaces=ATOM_NS).strip()
    authors = [
        author.findtext("atom:name", default="", namespaces=ATOM_NS).strip()
        for author in entry.findall("atom:author", ATOM_NS)
    ]
    pdf_url = ""
    for link in entry.findall("atom:link", ATOM_NS):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href", "")
            break
    versioned_id = identifier.rsplit("/", 1)[-1] if identifier else arxiv_id
    base_id = re.sub(r"v\d+$", "", versioned_id)
    return {
        "title": title,
        "summary": summary,
        "published": published,
        "updated": updated,
        "identifier": identifier,
        "versioned_id": versioned_id,
        "base_id": base_id,
        "authors": authors,
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{base_id}.pdf",
        "abs_url": identifier or f"https://arxiv.org/abs/{versioned_id}",
        "source_url": f"https://arxiv.org/e-print/{versioned_id}",
    }


def normalize_authors(values: list[Any] | None) -> list[str]:
    authors: list[str] = []
    for value in values or []:
        if isinstance(value, dict):
            candidate = str(
                value.get("name")
                or value.get("full_name")
                or value.get("author")
                or ""
            ).strip()
        else:
            candidate = str(value).strip()
        if candidate:
            authors.append(candidate)
    return authors


def build_metadata_override(arxiv_id: str, metadata_override: dict[str, Any]) -> dict[str, Any]:
    versioned_id = str(
        metadata_override.get("versioned_id")
        or metadata_override.get("arxiv_id")
        or arxiv_id
    ).strip()
    if not versioned_id:
        raise ValueError("Metadata override must include a non-empty arXiv id.")
    base_id = str(metadata_override.get("base_id") or re.sub(r"v\d+$", "", versioned_id)).strip()
    identifier = str(
        metadata_override.get("identifier")
        or metadata_override.get("abs_url")
        or f"https://arxiv.org/abs/{versioned_id}"
    ).strip()
    title = str(metadata_override.get("title") or "").strip()
    if not title:
        raise ValueError("Metadata override must include a non-empty title.")
    summary = str(metadata_override.get("summary") or "").strip()
    published = str(metadata_override.get("published") or "").strip()
    updated = str(metadata_override.get("updated") or published).strip()
    authors = normalize_authors(metadata_override.get("authors"))
    pdf_url = str(
        metadata_override.get("pdf_url")
        or f"https://arxiv.org/pdf/{base_id}.pdf"
    ).strip()
    abs_url = str(metadata_override.get("abs_url") or identifier).strip()
    source_url = str(
        metadata_override.get("source_url")
        or f"https://arxiv.org/e-print/{versioned_id}"
    ).strip()
    return {
        "title": title,
        "summary": summary,
        "published": published,
        "updated": updated,
        "identifier": identifier,
        "versioned_id": versioned_id,
        "base_id": base_id,
        "authors": authors,
        "pdf_url": pdf_url,
        "abs_url": abs_url,
        "source_url": source_url,
    }


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def ensure_topic_manifest(topic_root: Path, topic_slug: str, created_at: str) -> None:
    topic_json = topic_root / "topic.json"
    if not topic_json.exists():
        write_json(
            topic_json,
            {
                "topic_slug": topic_slug,
                "title": topic_slug.replace("-", " ").title(),
                "status": "source_active",
                "created_at": created_at,
            },
        )


def ensure_intake_manifest(topic_root: Path, topic_slug: str, created_at: str) -> None:
    topic_json = topic_root / "topic.json"
    if not topic_json.exists():
        write_json(
            topic_json,
            {
                "topic_slug": topic_slug,
                "title": topic_slug.replace("-", " ").title(),
                "status": "intake_active",
                "created_at": created_at,
            },
        )

    status_json = topic_root / "status.json"
    if not status_json.exists():
        write_json(
            status_json,
            {"stage": "L1_active", "next_stage": "L1", "last_updated": created_at},
        )


def build_source_payload(
    metadata: dict,
    topic_slug: str,
    source_json_rel: str,
    snapshot_rel: str,
    bundle_rel: str,
    extract_rel: str,
    registered_by: str,
    acquired_at: str,
) -> dict:
    return {
        "source_id": f"paper:{slugify(metadata['title'])}-{metadata['base_id'].replace('.', '-')}",
        "source_type": "paper",
        "title": metadata["title"],
        "topic_slug": topic_slug,
        "provenance": {
            "arxiv_id": metadata["versioned_id"],
            "authors": metadata["authors"],
            "published": metadata["published"],
            "updated": metadata["updated"],
            "abs_url": metadata["abs_url"],
            "pdf_url": metadata["pdf_url"],
            "source_url": metadata["source_url"],
        },
        "locator": {
            "local_path": source_json_rel,
            "snapshot_path": snapshot_rel,
            "preferred_open_sequence": [
                "local_extracted_tex",
                "arxiv_source_tex",
                "arxiv_html",
                "arxiv_pdf",
            ],
            "downloaded_source_bundle": bundle_rel,
            "extracted_source_dir": extract_rel,
        },
        "acquired_at": acquired_at,
        "registered_by": registered_by,
        "summary": short_summary(metadata["summary"]),
    }


def append_unique(rows: list[dict], new_row: dict, key_fields: tuple[str, ...]) -> list[dict]:
    filtered = []
    for row in rows:
        if all(row.get(field) == new_row.get(field) for field in key_fields):
            continue
        filtered.append(row)
    filtered.append(new_row)
    return filtered


def build_projection_snapshot(
    topic_slug: str,
    source_id: str,
    layer0_source_json: str,
    layer0_snapshot: str,
    acquired_at: str,
) -> str:
    return textwrap.dedent(
        f"""\
        # Layer 1 source projection

        Topic: `{topic_slug}`
        Source id: `{source_id}`
        Projection created: `{acquired_at}`

        Layer 0 source of truth:
        - `{layer0_source_json}`

        Layer 0 snapshot:
        - `{layer0_snapshot}`

        This intake-side snapshot is a projection only.
        Use the Layer 0 paths above for durable source reopening.
        """
    )


def build_layer0_snapshot(
    metadata: dict,
    topic_slug: str,
    source_id: str,
    download_status: str,
    extraction_status: str,
    bundle_rel: str,
    extract_rel: str,
    download_error: str,
) -> str:
    return textwrap.dedent(
        f"""\
        # {metadata["title"]}

        Source id: `{source_id}`
        arXiv id: `{metadata["versioned_id"]}`
        Topic: `{topic_slug}`

        ## Access priority
        1. local extracted TeX source
        2. arXiv source package
        3. arXiv HTML
        4. arXiv PDF

        ## Metadata
        - Authors: {", ".join(metadata["authors"]) if metadata["authors"] else "(unknown)"}
        - Published: {metadata["published"] or "(unknown)"}
        - Updated: {metadata["updated"] or "(unknown)"}
        - abs: {metadata["abs_url"]}
        - pdf: {metadata["pdf_url"]}
        - source package: {metadata["source_url"]}

        ## Acquisition status
        - Source bundle download: {download_status}
        - Source extraction: {extraction_status}
        - Local bundle: {bundle_rel or "(not present)"}
        - Local extracted dir: {extract_rel or "(not present)"}
        - Error note: {download_error or "(none)"}

        ## Abstract
        {short_summary(metadata["summary"], limit=1200)}
        """
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root")
    parser.add_argument("--topic-slug", required=True)
    parser.add_argument("--arxiv-id", required=True)
    parser.add_argument("--registered-by", default="codex")
    parser.add_argument("--download-source", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-intake-projection", action="store_true")
    parser.add_argument("--metadata-json")
    parser.add_argument("--json", action="store_true")
    return parser


def register_arxiv_source(
    *,
    knowledge_root: Path,
    topic_slug: str,
    arxiv_id: str,
    registered_by: str = "codex",
    download_source: bool = False,
    force: bool = False,
    skip_intake_projection: bool = False,
    metadata_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    del force  # Reserved for future parity with the CLI surface.
    metadata = (
        build_metadata_override(arxiv_id, metadata_override)
        if metadata_override is not None
        else fetch_metadata(arxiv_id)
    )
    source_slug = f"paper-{slugify(metadata['title'])}-{metadata['base_id'].replace('.', '-')}"

    source_layer_topic_root = knowledge_root / "source-layer" / "topics" / topic_slug
    layer0_source_root = source_layer_topic_root / "sources" / source_slug
    layer0_source_root.mkdir(parents=True, exist_ok=True)

    bundle_path = layer0_source_root / "source.tar"
    extract_dir = layer0_source_root / "tex-src"
    download_status = "not_requested"
    extraction_status = "not_requested"
    download_error = ""

    if download_source:
        try:
            payload = fetch_url(metadata["source_url"])
            if payload[:2] == b"\x1f\x8b":
                bundle_path = layer0_source_root / "source.tar.gz"
            bundle_path.write_bytes(payload)
            download_status = "downloaded"
            try:
                extract_dir.mkdir(exist_ok=True)
                with tarfile.open(bundle_path, "r:*") as archive:
                    try:
                        archive.extractall(path=extract_dir, filter="data")
                    except TypeError:
                        archive.extractall(path=extract_dir)
                extraction_status = "extracted"
            except tarfile.TarError as exc:
                extraction_status = "failed"
                download_error = f"downloaded source bundle but extraction failed: {exc}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            download_status = "failed"
            extraction_status = "skipped"
            download_error = str(exc)

    acquired_at = now_iso()
    ensure_topic_manifest(source_layer_topic_root, topic_slug, acquired_at)

    layer0_source_rel = layer0_source_root.relative_to(knowledge_root).as_posix()
    layer0_source_json_rel = f"{layer0_source_rel}/source.json"
    layer0_snapshot_rel = f"{layer0_source_rel}/snapshot.md"
    bundle_rel = bundle_path.relative_to(knowledge_root).as_posix() if bundle_path.exists() else ""
    extract_rel = extract_dir.relative_to(knowledge_root).as_posix() if extract_dir.exists() else ""

    source_payload = build_source_payload(
        metadata=metadata,
        topic_slug=topic_slug,
        source_json_rel=layer0_source_json_rel,
        snapshot_rel=layer0_snapshot_rel,
        bundle_rel=bundle_rel,
        extract_rel=extract_rel,
        registered_by=registered_by,
        acquired_at=acquired_at,
    )
    source_id = source_payload["source_id"]

    write_json(layer0_source_root / "source.json", source_payload)
    (layer0_source_root / "snapshot.md").write_text(
        build_layer0_snapshot(
            metadata=metadata,
            topic_slug=topic_slug,
            source_id=source_id,
            download_status=download_status,
            extraction_status=extraction_status,
            bundle_rel=bundle_rel,
            extract_rel=extract_rel,
            download_error=download_error,
        ),
        encoding="utf-8",
    )

    topic_index_path = source_layer_topic_root / "source_index.jsonl"
    write_jsonl(
        topic_index_path,
        append_unique(load_jsonl(topic_index_path), source_payload, ("source_id",)),
    )

    global_index_path = knowledge_root / "source-layer" / "global_index.jsonl"
    write_jsonl(
        global_index_path,
        append_unique(
            load_jsonl(global_index_path),
            {
                "source_id": source_id,
                "topic_slug": topic_slug,
                "source_type": source_payload["source_type"],
                "title": source_payload["title"],
                "local_path": layer0_source_json_rel,
                "acquired_at": acquired_at,
            },
            ("source_id", "topic_slug"),
        ),
    )

    intake_projection_root: Path | None = None
    if not skip_intake_projection:
        intake_topic_root = knowledge_root / "intake" / "topics" / topic_slug
        intake_projection_root = intake_topic_root / "sources" / source_slug
        intake_projection_root.mkdir(parents=True, exist_ok=True)
        ensure_intake_manifest(intake_topic_root, topic_slug, acquired_at)
        write_json(intake_projection_root / "source.json", source_payload)
        (intake_projection_root / "snapshot.md").write_text(
            build_projection_snapshot(
                topic_slug=topic_slug,
                source_id=source_id,
                layer0_source_json=layer0_source_json_rel,
                layer0_snapshot=layer0_snapshot_rel,
                acquired_at=acquired_at,
            ),
            encoding="utf-8",
        )
        intake_index_path = intake_topic_root / "source_index.jsonl"
        write_jsonl(
            intake_index_path,
            append_unique(load_jsonl(intake_index_path), source_payload, ("source_id",)),
        )
        status_json = intake_topic_root / "status.json"
        status_payload = load_json(status_json)
        if status_payload is not None:
            status_payload["last_updated"] = acquired_at
            write_json(status_json, status_payload)

    return {
        "status": "registered",
        "knowledge_root": knowledge_root,
        "topic_slug": topic_slug,
        "arxiv_id": metadata["versioned_id"],
        "source_id": source_id,
        "source_slug": source_slug,
        "layer0_source_root": layer0_source_root,
        "layer0_source_json": layer0_source_root / "source.json",
        "layer0_snapshot": layer0_source_root / "snapshot.md",
        "intake_projection_root": intake_projection_root,
        "bundle_path": bundle_path if bundle_rel else None,
        "extract_dir": extract_dir if extract_rel else None,
        "metadata": metadata,
        "download_status": download_status,
        "extraction_status": extraction_status,
        "download_error": download_error,
    }


def main() -> int:
    args = build_parser().parse_args()
    knowledge_root = (
        Path(args.knowledge_root).expanduser().resolve()
        if args.knowledge_root
        else Path(__file__).resolve().parents[2]
    )
    metadata_override = None
    if args.metadata_json:
        metadata_path = Path(args.metadata_json).expanduser().resolve()
        metadata_override = load_json(metadata_path)
        if metadata_override is None:
            raise FileNotFoundError(f"Metadata override file does not exist: {metadata_path}")

    result = register_arxiv_source(
        knowledge_root=knowledge_root,
        topic_slug=args.topic_slug,
        arxiv_id=args.arxiv_id,
        registered_by=args.registered_by,
        download_source=args.download_source,
        force=args.force,
        skip_intake_projection=args.skip_intake_projection,
        metadata_override=metadata_override,
    )
    if args.json:
        payload = {
            "status": result["status"],
            "topic_slug": result["topic_slug"],
            "arxiv_id": result["arxiv_id"],
            "source_id": result["source_id"],
            "layer0_source_json": str(result["layer0_source_json"]),
            "layer0_snapshot": str(result["layer0_snapshot"]),
            "intake_projection_root": (
                str(result["intake_projection_root"])
                if result["intake_projection_root"] is not None
                else ""
            ),
            "bundle_path": str(result["bundle_path"]) if result["bundle_path"] is not None else "",
            "extract_dir": str(result["extract_dir"]) if result["extract_dir"] is not None else "",
            "download_status": result["download_status"],
            "extraction_status": result["extraction_status"],
            "download_error": result["download_error"],
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    print(f"Registered arXiv source {result['source_id']}")
    print(f"- layer0 source.json: {result['layer0_source_json']}")
    print(f"- layer0 snapshot.md: {result['layer0_snapshot']}")
    if result["intake_projection_root"] is not None:
        print(f"- intake projection: {result['intake_projection_root']}")
    if result["bundle_path"] is not None:
        print(f"- bundle: {result['bundle_path']}")
    if result["extract_dir"] is not None:
        print(f"- extracted: {result['extract_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
