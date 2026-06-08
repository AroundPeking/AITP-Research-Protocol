"""Curated heuristic RAG corpus contracts for AITP v5 hosts."""

from __future__ import annotations

from typing import Any


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


def curated_rag_corpus() -> dict[str, Any]:
    """Return the canonical lightweight curated RAG corpus catalog.

    This is a deliberately small contract-first catalog. It gives hosts a
    stable schema for background retrieval before a real user-curated corpus and
    richer index backend are added. Retrieved chunks are heuristic context only.
    """

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
            "active_index_mode": "lexical_fixture",
            "supported_index_modes": ["lexical_fixture"],
            "embedding_index_required": False,
            "index_is_derived": True,
            "derived_from": "curated_rag_chunk_manifest",
            "stale_index_behavior": "return_diagnostic_not_trust",
        },
        "corpus_id": "aitp.curated.heuristic_background.v1",
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "document_index": [document["document_id"] for document in documents],
        "chunk_index": [chunk["chunk_id"] for chunk in chunks],
        "documents": documents,
        "chunks": chunks,
    }


def search_curated_rag_corpus(query: str, *, limit: int = 5) -> dict[str, Any]:
    """Return deterministic lexical fixture retrieval over the curated corpus."""

    catalog = curated_rag_corpus()
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
        "result_count": len(results),
        "results": results,
    }


def _tokenize(query: str) -> list[str]:
    return [
        token.strip().lower()
        for token in query.replace("_", " ").replace("-", " ").split()
        if token.strip()
    ]
