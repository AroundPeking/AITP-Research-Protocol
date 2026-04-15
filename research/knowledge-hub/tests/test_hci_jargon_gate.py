from __future__ import annotations

from pathlib import Path

import unittest


class HCIJargonGateTests(unittest.TestCase):
    def test_operator_facing_support_files_avoid_banned_jargon(self) -> None:
        package_root = Path(__file__).resolve().parents[1]
        banned_phrases = {
            "adjudication route",
            "l0 recovery",
            "promotion approval",
            "bounded route",
        }
        operator_surface_files = [
            package_root / "knowledge_hub" / "topic_shell_support.py",
            package_root / "knowledge_hub" / "mode_envelope_support.py",
            package_root / "knowledge_hub" / "runtime_bundle_support.py",
        ]

        for path in operator_surface_files:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in banned_phrases:
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
