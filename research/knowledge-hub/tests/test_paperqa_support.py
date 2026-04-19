from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.paperqa_support import (
    DEFAULT_PAPERQA_EMBEDDING,
    collect_topic_paperqa_sources,
    run_paperqa_consultation,
    validate_paperqa_model_config,
)


class PaperQASupportTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.kernel_root = Path(self._tmpdir.name) / "kernel"
        self.kernel_root.mkdir(parents=True, exist_ok=True)
        self.topic_slug = "demo-topic"
        self.l0_root = self.kernel_root / "topics" / self.topic_slug / "L0"
        self.l0_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_collect_topic_paperqa_sources_resolves_local_and_pdf_rows(self) -> None:
        local_note = self.kernel_root / "notes" / "seed-note.md"
        local_note.parent.mkdir(parents=True, exist_ok=True)
        local_note.write_text("# Seed note\n", encoding="utf-8")
        source_index_path = self.l0_root / "source_index.jsonl"
        rows = [
            {
                "source_id": "note:seed",
                "source_type": "note",
                "title": "Seed note",
                "summary": "Local seed note",
                "locator": {"local_path": str(local_note)},
            },
            {
                "source_id": "paper:demo-1",
                "source_type": "paper",
                "title": "Dielectric learning for GW",
                "summary": "A screening surrogate paper",
                "provenance": {
                    "pdf_url": "https://arxiv.org/pdf/2305.02990.pdf",
                    "authors": ["A. Researcher", "B. Scientist"],
                },
            },
            {
                "source_id": "paper:demo-duplicate",
                "source_type": "paper",
                "title": "Dielectric learning for GW duplicate",
                "provenance": {
                    "pdf_url": "https://arxiv.org/pdf/2305.02990.pdf",
                },
            },
            {
                "source_id": "misc:skip-me",
                "source_type": "misc",
                "title": "No usable locator",
            },
        ]
        source_index_path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n",
            encoding="utf-8",
        )

        payload = collect_topic_paperqa_sources(
            self.kernel_root,
            self.topic_slug,
            max_sources=4,
        )

        self.assertEqual(payload["source_index_path"], source_index_path)
        self.assertEqual(len(payload["resolved_sources"]), 2)
        self.assertEqual(payload["resolved_sources"][0]["kind"], "file")
        self.assertEqual(payload["resolved_sources"][0]["input"], str(local_note.resolve()))
        self.assertEqual(payload["resolved_sources"][1]["kind"], "url")
        self.assertEqual(
            payload["resolved_sources"][1]["input"],
            "https://arxiv.org/pdf/2305.02990.pdf",
        )
        skipped = [row for row in payload["source_diagnostics"] if row["status"] == "skipped"]
        self.assertEqual(len(skipped), 2)

    def test_validate_paperqa_model_config_requires_provider_prefix(self) -> None:
        payload = validate_paperqa_model_config(
            llm="claude-3-5-sonnet-20240620",
            summary_llm="anthropic/claude-3-5-sonnet-20240620",
            embedding=None,
        )

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["embedding"], DEFAULT_PAPERQA_EMBEDDING)
        self.assertIn("llm", payload["errors"][0]["field"])

    def test_run_paperqa_consultation_returns_preflight_error_for_unqualified_model(self) -> None:
        payload = run_paperqa_consultation(
            query_text="What matters for screening surrogates?",
            resolved_sources=[
                {
                    "source_id": "paper:demo-1",
                    "source_type": "paper",
                    "title": "Dielectric learning for GW",
                    "kind": "url",
                    "input": "https://arxiv.org/pdf/2305.02990.pdf",
                    "citation": "Researcher et al., 2023",
                    "authors": ["A. Researcher"],
                }
            ],
            llm="claude-3-5-sonnet-20240620",
        )

        self.assertEqual(payload["status"], "needs_model_configuration")
        self.assertEqual(payload["mode"], "preflight")
        self.assertIn("provider-prefixed", payload["configuration_errors"][0]["message"])

    def test_run_paperqa_consultation_reports_python_runtime_gate(self) -> None:
        with patch.object(sys, "version_info", (3, 10, 12)):
            payload = run_paperqa_consultation(
                query_text="What matters for screening surrogates?",
                resolved_sources=[
                    {
                        "source_id": "paper:demo-1",
                        "source_type": "paper",
                        "title": "Dielectric learning for GW",
                        "kind": "url",
                        "input": "https://arxiv.org/pdf/2305.02990.pdf",
                        "citation": "Researcher et al., 2023",
                        "authors": ["A. Researcher"],
                    }
                ],
                llm="anthropic/claude-3-5-sonnet-20240620",
            )

        self.assertEqual(payload["status"], "paperqa_runtime_unsupported")
        self.assertEqual(payload["mode"], "preflight")
        self.assertIn("Python 3.11+", payload["install_hint"])

    def test_run_paperqa_consultation_delegates_to_query_runner_when_ready(self) -> None:
        with patch(
            "knowledge_hub.paperqa_support._paperqa_runtime_supported",
            return_value=True,
        ), patch(
            "knowledge_hub.paperqa_support._paperqa_is_available",
            return_value=True,
        ), patch(
            "knowledge_hub.paperqa_support._run_paperqa_query",
            return_value={
                "status": "ok",
                "mode": "query",
                "answer": "Use local dielectric surrogates as bounded priors.",
                "formatted_answer": "Use local dielectric surrogates as bounded priors.\n\nReferences\n\n1. Demo",
                "references": "1. Demo",
                "context_count": 1,
            },
        ) as mock_run:
            payload = run_paperqa_consultation(
                query_text="What matters for screening surrogates?",
                resolved_sources=[
                    {
                        "source_id": "paper:demo-1",
                        "source_type": "paper",
                        "title": "Dielectric learning for GW",
                        "kind": "url",
                        "input": "https://arxiv.org/pdf/2305.02990.pdf",
                        "citation": "Researcher et al., 2023",
                        "authors": ["A. Researcher"],
                    }
                ],
                llm="anthropic/claude-3-5-sonnet-20240620",
            )

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["context_count"], 1)
        mock_run.assert_called_once_with(
            query_text="What matters for screening surrogates?",
            resolved_sources=[
                {
                    "source_id": "paper:demo-1",
                    "source_type": "paper",
                    "title": "Dielectric learning for GW",
                    "kind": "url",
                    "input": "https://arxiv.org/pdf/2305.02990.pdf",
                    "citation": "Researcher et al., 2023",
                    "authors": ["A. Researcher"],
                }
            ],
            llm="anthropic/claude-3-5-sonnet-20240620",
            summary_llm="anthropic/claude-3-5-sonnet-20240620",
            embedding=DEFAULT_PAPERQA_EMBEDDING,
        )


if __name__ == "__main__":
    unittest.main()
