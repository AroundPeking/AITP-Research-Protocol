"""Curated heuristic RAG corpus contracts for AITP v5 hosts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from brain.v5.paths import WorkspacePaths


CATALOG_VERSION = "aitp.v5.curated_rag_corpus.v1"

_ALLOWED_USES = [
    "conceptual_scaffolding",
    "literature_orientation",
    "derivation_scaffolding",
    "method_selection",
    "source_backtrace_suggestions",
]
_FORBIDDEN_USES = [
    "evidence_support",
    "validation_result",
    "claim_trust_update",
    "trust_apply",
    "final_gate_satisfaction",
]


def curated_rag_corpus(base: str | Path | WorkspacePaths | None = None) -> dict[str, Any]:
    """Return the canonical lightweight curated RAG corpus catalog.

    Without a workspace corpus file this returns the stable contract fixture.
    When ``.aitp/curated_rag/corpus.json`` exists under ``base``, it is loaded
    as a file-backed corpus manifest and normalized into the same no-trust
    public surface. Retrieved chunks are heuristic context only.
    """

    file_manifest = _load_file_manifest(base)
    if file_manifest is not None:
        documents = _normalize_documents(file_manifest.get("documents"), source="file_backed")
        chunks = _normalize_chunks(file_manifest.get("chunks"), source="file_backed")
        corpus_id = _string(file_manifest.get("corpus_id")) or "aitp.curated.file_backed_background.v1"
        index_extra = _file_index_policy_extra(base, documents=documents, chunks=chunks)
        return _catalog(
            corpus_id=corpus_id,
            documents=documents,
            chunks=chunks,
            index_mode="lexical_file_backed",
            index_extra=index_extra,
        )

    documents = _fixture_documents()
    chunks = _fixture_chunks()
    return _catalog(
        corpus_id="aitp.curated.heuristic_background.v1",
        documents=documents,
        chunks=chunks,
        index_mode="lexical_fixture",
        index_extra={},
    )


def _fixture_documents() -> list[dict[str, Any]]:
    documents = [
        {
            "document_id": "curated_rag_doc:theory_methods_orientation",
            "title": "Theory methods orientation shelf",
            "asset_type": "note",
            "source_uri": "aitp://curated-rag/theory-methods-orientation",
            "version_anchor": {"catalog_version": CATALOG_VERSION, "revision": "v1"},
            "content_hash": "sha256:curated-rag-theory-methods-orientation-v1",
            "tags": ["theoretical-physics", "methods", "orientation"],
            "domain_hints": ["theoretical-physics/general"],
            "topic_hints": ["method-selection", "derivation-scaffolding"],
            "language": "en",
            "priority": "high",
            "intended_use": "background_rag",
            "trust_status": "heuristic_context",
            "orientation_only": True,
            "can_update_claim_trust": False,
        },
        {
            "document_id": "curated_rag_doc:source_backtrace_orientation",
            "title": "Source backtrace orientation shelf",
            "asset_type": "lecture",
            "source_uri": "aitp://curated-rag/source-backtrace-orientation",
            "version_anchor": {"catalog_version": CATALOG_VERSION, "revision": "v1"},
            "content_hash": "sha256:curated-rag-source-backtrace-orientation-v1",
            "tags": ["source-reconstruction", "literature", "orientation"],
            "domain_hints": ["theoretical-physics/general"],
            "topic_hints": ["source-backtrace", "literature-orientation"],
            "language": "en",
            "priority": "medium",
            "intended_use": "background_rag",
            "trust_status": "heuristic_context",
            "orientation_only": True,
            "can_update_claim_trust": False,
        },
    ]
    return documents


def _fixture_chunks() -> list[dict[str, Any]]:
    chunks = [
        {
            "chunk_id": "curated_rag_chunk:theory_methods_orientation:0001",
            "document_id": "curated_rag_doc:theory_methods_orientation",
            "anchor": {"section": "method-selection", "ordinal": 1},
            "text": (
                "When a theory problem feels underdetermined, first separate "
                "definitions, assumptions, calculational handles, and validation "
                "targets before choosing a formal route."
            ),
            "summary": "Use method selection to separate definitions, assumptions, handles, and validation.",
            "tags": ["method-selection", "problem-framing"],
            "token_estimate": 32,
            "content_hash": "sha256:curated-rag-chunk-theory-methods-0001",
            "retrieval_role": "heuristic_context",
            "orientation_only": True,
            "can_update_claim_trust": False,
        },
        {
            "chunk_id": "curated_rag_chunk:source_backtrace_orientation:0001",
            "document_id": "curated_rag_doc:source_backtrace_orientation",
            "anchor": {"section": "source-backtrace", "ordinal": 1},
            "text": (
                "Treat a retrieved lecture or review passage as a pointer to "
                "source reconstruction work. It can suggest where to look next, "
                "but claim support needs explicit reference locations and evidence records."
            ),
            "summary": "Retrieved passages suggest source reconstruction, not claim support.",
            "tags": ["source-backtrace", "trust-boundary"],
            "token_estimate": 38,
            "content_hash": "sha256:curated-rag-chunk-source-backtrace-0001",
            "retrieval_role": "heuristic_context",
            "orientation_only": True,
            "can_update_claim_trust": False,
        },
    ]
    return chunks


def _catalog(
    *,
    corpus_id: str,
    documents: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    index_mode: str,
    index_extra: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kind": "curated_rag_corpus",
        "catalog_version": CATALOG_VERSION,
        "truth_source": "curated_rag_corpus_catalog",
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
        "retrieval_policy": {
            "result_role": "heuristic_context",
            "read_surface_effect": "orientation_only",
            "allowed_uses": _ALLOWED_USES,
            "forbidden_uses": _FORBIDDEN_USES,
            "records_validation_result": False,
            "claim_trust_mutation": "none",
            "summary_inputs_trusted": False,
            "can_update_claim_trust": False,
            "requires_promotion_for_claim_support": True,
        },
        "index_policy": {
            "active_index_mode": index_mode,
            "supported_index_modes": [index_mode],
            "embedding_index_required": False,
            "index_is_derived": True,
            "derived_from": "curated_rag_chunk_manifest",
            "stale_index_behavior": "return_diagnostic_not_trust",
            **index_extra,
        },
        "corpus_id": corpus_id,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "document_index": [document["document_id"] for document in documents],
        "chunk_index": [chunk["chunk_id"] for chunk in chunks],
        "documents": documents,
        "chunks": chunks,
    }


def search_curated_rag_corpus(
    query: str,
    *,
    limit: int = 5,
    base: str | Path | WorkspacePaths | None = None,
) -> dict[str, Any]:
    """Return deterministic lexical retrieval over the curated corpus."""

    catalog = curated_rag_corpus(base)
    terms = [term for term in _tokenize(query) if term]
    scored: list[tuple[int, dict[str, Any]]] = []
    for chunk in catalog["chunks"]:
        haystack = " ".join(
            [
                chunk["text"],
                chunk["summary"],
                " ".join(chunk["tags"]),
                chunk["document_id"],
            ]
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
    results = [
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "score": score,
            "retrieval_role": "heuristic_context",
            "orientation_only": True,
            "can_update_claim_trust": False,
            "summary": chunk["summary"],
            "text": chunk["text"],
            "anchor": chunk["anchor"],
            "tags": chunk["tags"],
            "content_hash": chunk["content_hash"],
        }
        for score, chunk in scored[: max(0, limit)]
    ]
    return {
        "kind": "curated_rag_search_result",
        "catalog_version": CATALOG_VERSION,
        "query": query,
        "index_mode": catalog["index_policy"]["active_index_mode"],
        "result_role": "heuristic_context",
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
        "records_validation_result": False,
        "claim_trust_mutation": "none",
        "requires_promotion_for_claim_support": True,
        "index_status": catalog["index_policy"].get("index_status", "fresh"),
        "stale_index_diagnostics": catalog["index_policy"].get("stale_index_diagnostics", []),
        "result_count": len(results),
        "results": results,
    }


def _tokenize(query: str) -> list[str]:
    return [
        token.strip().lower()
        for token in query.replace("_", " ").replace("-", " ").split()
        if token.strip()
    ]


def _load_file_manifest(base: str | Path | WorkspacePaths | None) -> dict[str, Any] | None:
    if base is None:
        return None
    path = _corpus_manifest_path(base)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("curated RAG corpus manifest must be a JSON object")
    return payload


def _corpus_manifest_path(base: str | Path | WorkspacePaths) -> Path:
    return _aitp_root(base) / "curated_rag" / "corpus.json"


def _lexical_index_path(base: str | Path | WorkspacePaths) -> Path:
    return _aitp_root(base) / "curated_rag" / "indexes" / "lexical_index.json"


def _aitp_root(base: str | Path | WorkspacePaths) -> Path:
    if isinstance(base, WorkspacePaths):
        return base.root
    path = Path(base)
    if path.name == ".aitp":
        return path
    return path / ".aitp"


def _normalize_documents(value: Any, *, source: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("curated RAG documents must be a list")
    documents: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise ValueError("curated RAG document entries must be objects")
        document_id = _required_string(raw, "document_id")
        title = _required_string(raw, "title")
        asset_type = _required_string(raw, "asset_type")
        source_uri = _required_string(raw, "source_uri")
        content_hash = _string(raw.get("content_hash")) or _hash_payload(
            {
                "document_id": document_id,
                "title": title,
                "asset_type": asset_type,
                "source_uri": source_uri,
                "source": source,
            }
        )
        documents.append(
            {
                **raw,
                "document_id": document_id,
                "title": title,
                "asset_type": asset_type,
                "source_uri": source_uri,
                "version_anchor": raw.get("version_anchor")
                if isinstance(raw.get("version_anchor"), dict)
                else {"catalog_version": CATALOG_VERSION, "source": source, "ordinal": index + 1},
                "content_hash": content_hash,
                "tags": _string_list(raw.get("tags")),
                "domain_hints": _string_list(raw.get("domain_hints")),
                "topic_hints": _string_list(raw.get("topic_hints")),
                "language": _string(raw.get("language")) or "en",
                "priority": _string(raw.get("priority")) or "medium",
                "intended_use": _string(raw.get("intended_use")) or "background_rag",
                "trust_status": "heuristic_context",
                "orientation_only": True,
                "can_update_claim_trust": False,
            }
        )
    return documents


def _normalize_chunks(value: Any, *, source: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("curated RAG chunks must be a list")
    chunks: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise ValueError("curated RAG chunk entries must be objects")
        text = _required_string(raw, "text")
        summary = _string(raw.get("summary")) or text[:160]
        token_estimate = raw.get("token_estimate")
        if not isinstance(token_estimate, int) or token_estimate <= 0:
            token_estimate = max(1, len(text.split()))
        chunks.append(
            {
                **raw,
                "chunk_id": _required_string(raw, "chunk_id"),
                "document_id": _required_string(raw, "document_id"),
                "anchor": raw.get("anchor")
                if isinstance(raw.get("anchor"), dict)
                else {"source": source, "ordinal": index + 1},
                "text": text,
                "summary": summary,
                "tags": _string_list(raw.get("tags")),
                "token_estimate": token_estimate,
                "content_hash": _string(raw.get("content_hash")) or _hash_text(text),
                "retrieval_role": "heuristic_context",
                "orientation_only": True,
                "can_update_claim_trust": False,
            }
        )
    return chunks


def _file_index_policy_extra(
    base: str | Path | WorkspacePaths | None,
    *,
    documents: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    if base is None:
        return {}
    manifest_hash = _hash_payload(
        {
            "documents": documents,
            "chunks": chunks,
        }
    )
    index_path = _lexical_index_path(base)
    diagnostics: list[dict[str, Any]] = []
    status = "derived_in_memory"
    if index_path.exists():
        try:
            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            index_payload = {}
            diagnostics.append(
                {
                    "code": "curated_rag_index_unreadable",
                    "message": f"lexical index JSON could not be parsed: {exc.msg}",
                    "path": str(index_path),
                }
            )
        recorded_hash = index_payload.get("manifest_hash") if isinstance(index_payload, dict) else None
        if recorded_hash == manifest_hash:
            status = "fresh"
        else:
            status = "stale"
            diagnostics.append(
                {
                    "code": "curated_rag_index_stale",
                    "message": "lexical index manifest_hash does not match the current chunk manifest",
                    "path": str(index_path),
                }
            )
    return {
        "index_source": "file_backed_corpus_manifest",
        "index_path": str(index_path),
        "manifest_hash": manifest_hash,
        "index_status": status,
        "stale_index_diagnostics": diagnostics,
    }


def _required_string(raw: dict[str, Any], key: str) -> str:
    value = _string(raw.get(key))
    if value:
        return value
    raise ValueError(f"curated RAG {key} must be a non-empty string")


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hash_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return _hash_text(raw)
