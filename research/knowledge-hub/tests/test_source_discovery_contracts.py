from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def _load_module(module_name: str, relative_path: str):
    kernel_root = Path(__file__).resolve().parents[1]
    target_path = kernel_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, target_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {target_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceDiscoveryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel_root = Path(__file__).resolve().parents[1]
        self.repo_root = self.kernel_root.parents[1]
        self.module = _load_module(
            "discover_and_register_module",
            "source-layer/scripts/discover_and_register.py",
        )

    def test_discovery_bridge_selects_and_registers_offline_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            work_root = Path(tmpdir)
            kernel_root = work_root / "kernel"
            search_results_path = work_root / "search-results.json"
            search_results_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "arxiv_id": "2401.00002v1",
                                "title": "Irrelevant benchmark note",
                                "summary": "Numerical benchmark only.",
                                "published": "2024-01-02T00:00:00Z",
                                "updated": "2024-01-02T00:00:00Z",
                                "authors": ["Auxiliary Author"],
                                "identifier": "https://arxiv.org/abs/2401.00002v1",
                                "abs_url": "https://arxiv.org/abs/2401.00002v1",
                                "pdf_url": "https://arxiv.org/pdf/2401.00002.pdf",
                                "source_url": "https://arxiv.org/e-print/2401.00002v1",
                                "score": 0.25,
                            },
                            {
                                "arxiv_id": "2401.00001v2",
                                "title": "Topological Order and Anyon Condensation",
                                "summary": "A direct match for topological order and anyon condensation discovery.",
                                "published": "2024-01-03T00:00:00Z",
                                "updated": "2024-01-04T00:00:00Z",
                                "authors": ["Primary Author", "Secondary Author"],
                                "identifier": "https://arxiv.org/abs/2401.00001v2",
                                "abs_url": "https://arxiv.org/abs/2401.00001v2",
                                "pdf_url": "https://arxiv.org/pdf/2401.00001.pdf",
                                "source_url": "https://arxiv.org/e-print/2401.00001v2",
                                "score": 0.91,
                            },
                        ]
                    },
                    ensure_ascii=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            payload = self.module.discover_and_register(
                knowledge_root=kernel_root,
                topic_slug="demo-topic",
                query="topological order anyon condensation",
                provider_chain=["search_results_json"],
                search_results_json=search_results_path,
                max_results=5,
                deepxiv_bin="deepxiv",
                preferred_arxiv_id="",
                select_index=0,
                registered_by="unit-test",
                download_source=False,
                force=False,
                skip_intake_projection=False,
            )

            self.assertEqual(payload["status"], "registered")
            self.assertEqual(payload["selected_provider"], "search_results_json")
            self.assertEqual(payload["selected_candidate"]["arxiv_id"], "2401.00001v2")
            self.assertTrue(payload["query_path"].exists())
            self.assertTrue(payload["candidate_evaluation_path"].exists())
            self.assertTrue(payload["registration_receipt_path"].exists())
            self.assertTrue(payload["layer0_source_json"].exists())
            self.assertIsNotNone(payload["intake_projection_root"])

            layer0_payload = json.loads(payload["layer0_source_json"].read_text(encoding="utf-8"))
            self.assertEqual(layer0_payload["provenance"]["arxiv_id"], "2401.00001v2")
            self.assertEqual(layer0_payload["title"], "Topological Order and Anyon Condensation")

    def test_source_discovery_docs_and_acceptance_are_documented(self) -> None:
        kernel_readme = (self.kernel_root / "README.md").read_text(encoding="utf-8")
        runtime_readme = (self.kernel_root / "runtime" / "README.md").read_text(encoding="utf-8")
        runbook = (self.kernel_root / "runtime" / "AITP_TEST_RUNBOOK.md").read_text(encoding="utf-8")
        l0_doc = (self.kernel_root / "L0_SOURCE_LAYER.md").read_text(encoding="utf-8")
        source_layer_readme = (self.kernel_root / "source-layer" / "README.md").read_text(encoding="utf-8")

        self.assertIn("discover_and_register.py", kernel_readme)
        self.assertIn("run_l0_source_discovery_acceptance.py", kernel_readme)
        self.assertIn("run_l0_source_discovery_acceptance.py", runtime_readme)
        self.assertIn("run_l0_source_discovery_acceptance.py", runbook)
        self.assertIn("discoveries/", l0_doc)
        self.assertIn("discover_and_register.py", l0_doc)
        self.assertIn("discover_and_register.py", source_layer_readme)
        self.assertIn("search_results_json", source_layer_readme)

    def test_acceptance_script_mentions_discovery_evaluation_and_registration(self) -> None:
        script = (
            self.kernel_root / "runtime" / "scripts" / "run_l0_source_discovery_acceptance.py"
        ).read_text(encoding="utf-8")

        self.assertIn("discover_and_register.py", script)
        self.assertIn("candidate_evaluation_path", script)
        self.assertIn("layer0_source_json", script)
        self.assertIn("search_results_json", script)


if __name__ == "__main__":
    unittest.main()
