from __future__ import annotations

import asyncio
import importlib.util
import json
import re
import sys
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Any

from .topic_truth_root_support import layer_root

DEFAULT_PAPERQA_EMBEDDING = "st-multi-qa-MiniLM-L6-cos-v1"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower())
    return normalized.strip("-") or "source"


def _resolve_existing_path(raw_path: str, *, kernel_root: Path, source_index_path: Path) -> Path | None:
    target = str(raw_path or "").strip()
    if not target:
        return None
    candidate = Path(target).expanduser()
    candidates = [candidate]
    if not candidate.is_absolute():
        candidates.extend([kernel_root / candidate, source_index_path.parent / candidate])
    seen: set[Path] = set()
    for item in candidates:
        resolved = item.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.exists() and resolved.is_file():
            return resolved
    return None


def _extract_year(row: dict[str, Any]) -> str | None:
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    candidates = [
        provenance.get("published"),
        provenance.get("updated"),
        row.get("acquired_at"),
    ]
    for value in candidates:
        text = str(value or "").strip()
        match = re.search(r"\b(19|20)\d{2}\b", text)
        if match:
            return match.group(0)
    return None


def _resolve_authors(row: dict[str, Any]) -> list[str]:
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    authors = provenance.get("authors")
    if not isinstance(authors, list):
        return []
    return [str(author).strip() for author in authors if str(author).strip()]


def _build_citation(row: dict[str, Any], *, authors: list[str]) -> str:
    title = str(row.get("title") or row.get("source_id") or "Untitled source").strip()
    year = _extract_year(row)
    if authors:
        lead = authors[0]
        author_label = lead if len(authors) == 1 else f"{lead} et al."
        if year:
            return f"{author_label}, {year}. {title}"
        return f"{author_label}. {title}"
    if year:
        return f"{title} ({year})"
    return title


def _resolve_row_to_source(
    row: dict[str, Any],
    *,
    kernel_root: Path,
    source_index_path: Path,
) -> tuple[dict[str, Any] | None, str]:
    locator = row.get("locator") if isinstance(row.get("locator"), dict) else {}
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    raw_local_path = str(locator.get("local_path") or "").strip()
    local_path = _resolve_existing_path(
        raw_local_path,
        kernel_root=kernel_root,
        source_index_path=source_index_path,
    )
    if local_path is not None and local_path.suffix.lower() != ".json":
        authors = _resolve_authors(row)
        return (
            {
                "source_id": str(row.get("source_id") or row.get("id") or _slugify(row.get("title") or "source")),
                "source_type": str(row.get("source_type") or "unknown"),
                "title": str(row.get("title") or local_path.name),
                "kind": "file",
                "input": str(local_path),
                "citation": _build_citation(row, authors=authors),
                "docname": _slugify(row.get("source_id") or row.get("title") or local_path.stem),
                "authors": authors,
            },
            "local_path",
        )

    pdf_url = str(provenance.get("pdf_url") or "").strip()
    if pdf_url:
        authors = _resolve_authors(row)
        return (
            {
                "source_id": str(row.get("source_id") or row.get("id") or _slugify(row.get("title") or pdf_url)),
                "source_type": str(row.get("source_type") or "paper"),
                "title": str(row.get("title") or pdf_url),
                "kind": "url",
                "input": pdf_url,
                "citation": _build_citation(row, authors=authors),
                "docname": _slugify(row.get("source_id") or row.get("title") or pdf_url),
                "authors": authors,
            },
            "pdf_url",
        )
    if raw_local_path:
        return None, "missing_local_path"
    return None, "missing_supported_locator"


def collect_topic_paperqa_sources(
    kernel_root: Path,
    topic_slug: str,
    *,
    max_sources: int = 8,
) -> dict[str, Any]:
    source_index_path = layer_root(kernel_root, topic_slug, "L0") / "source_index.jsonl"
    rows = _read_jsonl(source_index_path)
    limit = int(max_sources) if max_sources is not None else 8
    resolved_sources: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    seen_inputs: set[tuple[str, str]] = set()
    for row in rows:
        resolved_source, reason = _resolve_row_to_source(
            row,
            kernel_root=kernel_root,
            source_index_path=source_index_path,
        )
        diagnostic = {
            "source_id": str(row.get("source_id") or row.get("id") or ""),
            "title": str(row.get("title") or ""),
            "source_type": str(row.get("source_type") or ""),
        }
        if resolved_source is None:
            diagnostics.append({**diagnostic, "status": "skipped", "reason": reason})
            continue
        dedupe_key = (resolved_source["kind"], resolved_source["input"])
        if dedupe_key in seen_inputs:
            diagnostics.append({**diagnostic, "status": "skipped", "reason": "duplicate_input"})
            continue
        if limit > 0 and len(resolved_sources) >= limit:
            diagnostics.append({**diagnostic, "status": "skipped", "reason": "max_sources_reached"})
            continue
        seen_inputs.add(dedupe_key)
        resolved_sources.append(resolved_source)
        diagnostics.append(
            {
                **diagnostic,
                "status": "resolved",
                "kind": resolved_source["kind"],
                "reason": reason,
            }
        )
    return {
        "topic_slug": topic_slug,
        "source_index_path": source_index_path,
        "resolved_sources": resolved_sources,
        "source_diagnostics": diagnostics,
    }


def validate_paperqa_model_config(
    *,
    llm: str | None,
    summary_llm: str | None = None,
    embedding: str | None = None,
) -> dict[str, Any]:
    resolved_llm = str(llm or "").strip() or None
    resolved_summary_llm = str(summary_llm or "").strip() or resolved_llm
    resolved_embedding = str(embedding or "").strip() or DEFAULT_PAPERQA_EMBEDDING
    errors: list[dict[str, str]] = []
    if resolved_llm is None:
        errors.append(
            {
                "field": "llm",
                "message": "PaperQA requires an explicit LLM model name.",
            }
        )
    for field, value in (("llm", resolved_llm), ("summary_llm", resolved_summary_llm)):
        if value and "/" not in value:
            errors.append(
                {
                    "field": field,
                    "message": (
                        "PaperQA uses LiteLLM model routing; use a provider-prefixed model "
                        "name such as 'anthropic/claude-3-5-sonnet-20240620'."
                    ),
                }
            )
    return {
        "ok": not errors,
        "llm": resolved_llm,
        "summary_llm": resolved_summary_llm,
        "embedding": resolved_embedding,
        "errors": errors,
    }


def _paperqa_is_available() -> bool:
    return importlib.util.find_spec("paperqa") is not None


def _paperqa_runtime_supported() -> bool:
    return tuple(sys.version_info[:2]) >= (3, 11)


def _load_paperqa_api() -> tuple[Any, Any]:
    from paperqa import Docs, Settings

    return Docs, Settings


async def _run_paperqa_query_async(
    *,
    query_text: str,
    resolved_sources: list[dict[str, Any]],
    llm: str,
    summary_llm: str,
    embedding: str,
) -> dict[str, Any]:
    Docs, Settings = _load_paperqa_api()
    docs = Docs()
    ingest_settings = Settings(embedding=embedding)
    query_settings = Settings(
        llm=llm,
        summary_llm=summary_llm,
        embedding=embedding,
    )
    ingested_ids: list[str] = []
    for source in resolved_sources:
        citation = str(source.get("citation") or source.get("title") or source.get("source_id") or "")
        title = str(source.get("title") or "") or None
        docname = str(source.get("docname") or source.get("source_id") or "") or None
        authors = source.get("authors") if isinstance(source.get("authors"), list) else None
        if source.get("kind") == "file":
            ingested = await docs.aadd(
                source["input"],
                citation=citation,
                docname=docname,
                title=title,
                authors=authors,
                settings=ingest_settings,
            )
        elif source.get("kind") == "url":
            with urllib.request.urlopen(source["input"], timeout=60) as handle:  # noqa: S310
                payload = BytesIO(handle.read())
            ingested = await docs.aadd_file(
                payload,
                citation=citation,
                docname=docname,
                title=title,
                authors=authors,
                settings=ingest_settings,
            )
        else:
            continue
        if ingested:
            ingested_ids.append(str(ingested))
    session = await docs.aquery(query_text, settings=query_settings)
    return {
        "status": "ok",
        "mode": "query",
        "answer": str(getattr(session, "answer", "") or getattr(session, "raw_answer", "")),
        "formatted_answer": str(getattr(session, "formatted_answer", "") or getattr(session, "answer", "")),
        "references": str(getattr(session, "references", "") or ""),
        "context_count": len(getattr(session, "contexts", []) or []),
        "ingested_docnames": ingested_ids,
    }


def _run_paperqa_query(
    *,
    query_text: str,
    resolved_sources: list[dict[str, Any]],
    llm: str,
    summary_llm: str,
    embedding: str,
) -> dict[str, Any]:
    return asyncio.run(
        _run_paperqa_query_async(
            query_text=query_text,
            resolved_sources=resolved_sources,
            llm=llm,
            summary_llm=summary_llm,
            embedding=embedding,
        )
    )


def run_paperqa_consultation(
    *,
    query_text: str,
    resolved_sources: list[dict[str, Any]],
    llm: str | None,
    summary_llm: str | None = None,
    embedding: str | None = None,
) -> dict[str, Any]:
    config = validate_paperqa_model_config(
        llm=llm,
        summary_llm=summary_llm,
        embedding=embedding,
    )
    if not config["ok"]:
        return {
            "status": "needs_model_configuration",
            "mode": "preflight",
            "configuration_errors": config["errors"],
            "embedding": config["embedding"],
        }
    if not resolved_sources:
        return {
            "status": "no_sources",
            "mode": "preflight",
            "configuration_errors": [],
            "embedding": config["embedding"],
        }
    if not _paperqa_runtime_supported():
        return {
            "status": "paperqa_runtime_unsupported",
            "mode": "preflight",
            "configuration_errors": [],
            "embedding": config["embedding"],
            "install_hint": (
                "PaperQA integration requires Python 3.11+ even though the core AITP kernel "
                "still supports Python 3.10+. Install the optional PaperQA extra in a Python 3.11+ environment."
            ),
            "python_version": ".".join(str(part) for part in sys.version_info[:3]),
        }
    if not _paperqa_is_available():
        return {
            "status": "paperqa_unavailable",
            "mode": "preflight",
            "configuration_errors": [],
            "embedding": config["embedding"],
            "install_hint": (
                "Install the optional PaperQA extra into the active Python 3.11+ environment, "
                "for example: pip install 'aitp-kernel[paperqa]'."
            ),
        }
    try:
        return _run_paperqa_query(
            query_text=query_text,
            resolved_sources=resolved_sources,
            llm=config["llm"],
            summary_llm=config["summary_llm"],
            embedding=config["embedding"],
        )
    except Exception as exc:  # pragma: no cover - exercised through integration, not unit shape tests.
        return {
            "status": "query_failed",
            "mode": "query",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "embedding": config["embedding"],
        }
