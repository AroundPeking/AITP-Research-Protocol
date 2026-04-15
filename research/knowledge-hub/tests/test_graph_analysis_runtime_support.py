from __future__ import annotations

import unittest
from pathlib import Path

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.graph_analysis_tools import build_graph_analysis_surface


class GraphAnalysisRuntimeSupportTests(unittest.TestCase):
    def test_build_graph_analysis_surface_tracks_cross_iteration_diff(self) -> None:
        previous_payload = {
            "graph_snapshot": {
                "nodes": [
                    {
                        "source_id": "paper:anyon-condensation",
                        "source_title": "Anyon condensation paper",
                        "source_type": "paper",
                        "node_id": "concept:topological-order",
                        "label": "Topological order",
                        "node_type": "concept",
                    }
                ],
                "edges": [],
                "hyperedges": [],
                "communities": [],
                "god_nodes": [
                    {
                        "source_id": "paper:anyon-condensation",
                        "node_id": "concept:topological-order",
                        "label": "Topological order",
                    }
                ],
            }
        }
        l1_source_intake = {
            "concept_graph": {
                "nodes": [
                    {
                        "source_id": "paper:anyon-condensation",
                        "source_title": "Anyon condensation paper",
                        "source_type": "paper",
                        "node_id": "concept:anyon-condensation",
                        "label": "Anyon condensation",
                        "node_type": "concept",
                        "confidence_tier": "EXTRACTED",
                        "confidence_score": 0.94,
                    },
                    {
                        "source_id": "note:operator-algebra",
                        "source_title": "Operator algebra note",
                        "source_type": "local_note",
                        "node_id": "concept:anyon-condensation-operator",
                        "label": "Anyon condensation",
                        "node_type": "concept",
                        "confidence_tier": "EXTRACTED",
                        "confidence_score": 0.9,
                    },
                ],
                "edges": [],
                "hyperedges": [],
                "communities": [
                    {
                        "source_id": "paper:anyon-condensation",
                        "community_id": "community-anyon-condensation",
                        "label": "Anyon condensation cluster",
                        "node_ids": ["concept:anyon-condensation"],
                    },
                    {
                        "source_id": "note:operator-algebra",
                        "community_id": "community-anyon-condensation-operator",
                        "label": "Anyon condensation cluster",
                        "node_ids": ["concept:anyon-condensation-operator"],
                    },
                ],
                "god_nodes": [
                    {
                        "source_id": "paper:anyon-condensation",
                        "node_id": "concept:anyon-condensation",
                        "label": "Anyon condensation",
                    },
                    {
                        "source_id": "note:operator-algebra",
                        "node_id": "concept:anyon-condensation-operator",
                        "label": "Anyon condensation",
                    },
                ],
            }
        }

        payload = build_graph_analysis_surface(
            topic_slug="demo-topic",
            l1_source_intake=l1_source_intake,
            previous_payload=previous_payload,
            updated_by="test-suite",
        )

        self.assertEqual(payload["topic_slug"], "demo-topic")
        self.assertEqual(payload["summary"]["connection_count"], 1)
        self.assertEqual(payload["summary"]["question_count"], 1)
        self.assertEqual(payload["summary"]["history_length"], 2)
        self.assertEqual(payload["diff"]["added"]["node_count"], 2)
        self.assertEqual(payload["diff"]["removed"]["node_count"], 1)
        self.assertIn("Anyon condensation", payload["diff"]["added"]["node_labels"])


if __name__ == "__main__":
    unittest.main()
