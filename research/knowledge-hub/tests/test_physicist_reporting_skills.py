from __future__ import annotations

from pathlib import Path
import unittest


class PhysicistReportingSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[3]

    def test_repo_contains_physicist_reporting_skill_bundle(self) -> None:
        expected = {
            "aitp-problem-framing": "Problem",
            "aitp-derivation-discipline": "Derivation",
            "aitp-l3-l4-round": "L3-L4",
            "aitp-current-claims-auditor": "Current Claims",
            "aitp-topic-report-author": "Topic Report",
        }
        for skill_name, keyword in expected.items():
            skill_path = self.repo_root / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"Missing skill file: {skill_path}")
            text = skill_path.read_text(encoding="utf-8")
            self.assertIn(f"name: {skill_name}", text)
            self.assertIn(keyword, text)

    def test_existing_aitp_entry_skills_reference_physicist_reporting_subskills(self) -> None:
        using_skill = (self.repo_root / "skills" / "using-aitp" / "SKILL.md").read_text(encoding="utf-8")
        runtime_skill = (self.repo_root / "skills" / "aitp-runtime" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("aitp-problem-framing", using_skill)
        self.assertIn("aitp-topic-report-author", runtime_skill)
        self.assertIn("aitp-derivation-discipline", runtime_skill)
        self.assertIn("aitp-l3-l4-round", runtime_skill)


if __name__ == "__main__":
    unittest.main()

