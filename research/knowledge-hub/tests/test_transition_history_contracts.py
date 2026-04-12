from __future__ import annotations

import unittest
from pathlib import Path


class TransitionHistoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel_root = Path(__file__).resolve().parents[1]
        self.repo_root = self.kernel_root.parents[1]

    def test_transition_history_acceptance_and_runtime_surfaces_are_documented(self) -> None:
        root_readme = (self.repo_root / "README.md").read_text(encoding="utf-8")
        kernel_readme = (self.kernel_root / "README.md").read_text(encoding="utf-8")
        runtime_readme = (self.kernel_root / "runtime" / "README.md").read_text(encoding="utf-8")
        runbook = (self.kernel_root / "runtime" / "AITP_TEST_RUNBOOK.md").read_text(encoding="utf-8")

        self.assertIn("run_transition_history_acceptance.py", root_readme)
        self.assertIn("run_transition_history_acceptance.py", kernel_readme)
        self.assertIn("run_transition_history_acceptance.py", runtime_readme)
        self.assertIn("run_transition_history_acceptance.py", runbook)
        self.assertIn("transition_history", runtime_readme)
        self.assertIn("demotion", runbook)

    def test_acceptance_script_covers_request_reject_status_and_replay(self) -> None:
        script = (
            self.kernel_root / "runtime" / "scripts" / "run_transition_history_acceptance.py"
        ).read_text(encoding="utf-8")

        self.assertIn("request-promotion", script)
        self.assertIn("reject-promotion", script)
        self.assertIn("status", script)
        self.assertIn("replay-topic", script)
        self.assertIn("transition_history.json", script)
        self.assertIn("latest_demotion_reason", script)


if __name__ == "__main__":
    unittest.main()
