from __future__ import annotations

import unittest
from pathlib import Path

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.graph_analysis_tools import graph_diff, suggest_questions, surprising_connections


class GraphAnalysisToolsTests(unittest.TestCase):
    def test_surprising_connections_and_question_suggestions_bridge_shared_foundations(self) -> None:
        concept_graph = {
            "nodes": [
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "concept:topological-order",
                    "label": "Topological order",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.95,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "concept:topological-order-operator",
                    "label": "Topological order",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.91,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "concept:von-neumann-algebra",
                    "label": "von Neumann algebra",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.88,
                },
            ],
            "edges": [],
            "hyperedges": [],
            "communities": [
                {
                    "source_id": "paper:anyon-condensation",
                    "community_id": "community-topological-order",
                    "label": "Topological order cluster",
                    "node_ids": ["concept:topological-order"],
                },
                {
                    "source_id": "note:operator-algebra",
                    "community_id": "community-topological-order-operator",
                    "label": "Topological order cluster",
                    "node_ids": ["concept:topological-order-operator", "concept:von-neumann-algebra"],
                },
            ],
            "god_nodes": [
                {
                    "source_id": "paper:anyon-condensation",
                    "node_id": "concept:topological-order",
                    "label": "Topological order",
                },
                {
                    "source_id": "note:operator-algebra",
                    "node_id": "concept:topological-order-operator",
                    "label": "Topological order",
                },
            ],
        }

        connections = surprising_connections(concept_graph)

        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["kind"], "shared_foundation_bridge")
        self.assertEqual(connections[0]["bridge_label"], "Topological order")
        self.assertEqual(set(connections[0]["source_ids"]), {"paper:anyon-condensation", "note:operator-algebra"})
        self.assertIn("Topological order cluster", connections[0]["community_labels"])

        questions = suggest_questions(concept_graph)

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["question_type"], "bridge_question")
        self.assertEqual(questions[0]["bridge_label"], "Topological order")
        self.assertIn("How does Topological order connect", questions[0]["question"])

    def test_surprising_connections_detect_shared_community_bridge_without_shared_node_labels(self) -> None:
        concept_graph = {
            "nodes": [
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "concept:anyon-condensation",
                    "label": "Anyon condensation",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.95,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "concept:operator-sector",
                    "label": "Operator algebra sector",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.91,
                },
            ],
            "edges": [],
            "hyperedges": [],
            "communities": [
                {
                    "source_id": "paper:anyon-condensation",
                    "community_id": "community-topological-order-paper",
                    "label": "Topological order cluster",
                    "node_ids": ["concept:anyon-condensation"],
                },
                {
                    "source_id": "note:operator-algebra",
                    "community_id": "community-topological-order-note",
                    "label": "Topological order cluster",
                    "node_ids": ["concept:operator-sector"],
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
                    "node_id": "concept:operator-sector",
                    "label": "Operator algebra sector",
                },
            ],
        }

        connections = surprising_connections(concept_graph)

        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["kind"], "shared_community_bridge")
        self.assertEqual(connections[0]["bridge_label"], "Topological order cluster")
        self.assertEqual(set(connections[0]["source_ids"]), {"paper:anyon-condensation", "note:operator-algebra"})

        questions = suggest_questions(concept_graph)

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["graph_analysis_kind"], "shared_community_bridge")
        self.assertEqual(questions[0]["bridge_label"], "Topological order cluster")
        self.assertIn("How does Topological order cluster connect", questions[0]["question"])

    def test_surprising_connections_detect_shared_hyperedge_pattern_bridge_without_shared_labels(self) -> None:
        concept_graph = {
            "nodes": [
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "theorem:condensation-criterion",
                    "label": "Condensation criterion",
                    "node_type": "theorem",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.95,
                },
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "approximation:weak-coupling",
                    "label": "Weak coupling",
                    "node_type": "approximation",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.91,
                },
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "concept:anyon-condensation",
                    "label": "Anyon condensation",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.92,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "theorem:sector-criterion",
                    "label": "Sector decomposition criterion",
                    "node_type": "theorem",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.94,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "approximation:finite-index",
                    "label": "Finite-index assumption",
                    "node_type": "approximation",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.9,
                },
                {
                    "source_id": "note:operator-algebra",
                    "source_title": "Operator algebra note",
                    "source_type": "local_note",
                    "node_id": "concept:operator-sector",
                    "label": "Operator algebra sector",
                    "node_type": "concept",
                    "confidence_tier": "EXTRACTED",
                    "confidence_score": 0.89,
                },
            ],
            "edges": [],
            "hyperedges": [
                {
                    "source_id": "paper:anyon-condensation",
                    "hyperedge_id": "hyperedge:paper-supports",
                    "relation": "supports",
                    "node_ids": [
                        "theorem:condensation-criterion",
                        "approximation:weak-coupling",
                        "concept:anyon-condensation",
                    ],
                },
                {
                    "source_id": "note:operator-algebra",
                    "hyperedge_id": "hyperedge:note-supports",
                    "relation": "supports",
                    "node_ids": [
                        "theorem:sector-criterion",
                        "approximation:finite-index",
                        "concept:operator-sector",
                    ],
                },
            ],
            "communities": [],
            "god_nodes": [],
        }

        connections = surprising_connections(concept_graph)

        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["kind"], "shared_hyperedge_pattern_bridge")
        self.assertEqual(connections[0]["bridge_label"], "supports pattern (approximation + concept + theorem)")
        self.assertEqual(set(connections[0]["source_ids"]), {"paper:anyon-condensation", "note:operator-algebra"})

        questions = suggest_questions(concept_graph)

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["graph_analysis_kind"], "shared_hyperedge_pattern_bridge")
        self.assertEqual(questions[0]["bridge_label"], "supports pattern (approximation + concept + theorem)")
        self.assertIn("realize the `supports pattern (approximation + concept + theorem)` structural pattern", questions[0]["question"])

    def test_graph_diff_tracks_added_and_removed_labels_and_edges(self) -> None:
        previous_graph = {
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
        current_graph = {
            "nodes": [
                {
                    "source_id": "paper:anyon-condensation",
                    "source_title": "Anyon condensation paper",
                    "source_type": "paper",
                    "node_id": "concept:anyon-condensation",
                    "label": "Anyon condensation",
                    "node_type": "concept",
                }
            ],
            "edges": [
                {
                    "source_id": "paper:anyon-condensation",
                    "edge_id": "edge:1",
                    "from_id": "concept:anyon-condensation",
                    "relation": "special_case_of",
                    "to_id": "concept:topological-order",
                }
            ],
            "hyperedges": [],
            "communities": [],
            "god_nodes": [],
        }

        diff = graph_diff(previous_graph=previous_graph, current_graph=current_graph)

        self.assertEqual(diff["added"]["node_count"], 1)
        self.assertEqual(diff["removed"]["node_count"], 1)
        self.assertIn("Anyon condensation", diff["added"]["node_labels"])
        self.assertIn("Topological order", diff["removed"]["node_labels"])
        self.assertEqual(diff["added"]["edge_count"], 1)
        self.assertIn("special_case_of", diff["added"]["edge_relations"])
        self.assertEqual(diff["removed"]["god_node_count"], 1)


if __name__ == "__main__":
    unittest.main()
