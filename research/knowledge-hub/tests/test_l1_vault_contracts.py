from __future__ import annotations

import unittest
from pathlib import Path


class L1VaultContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel_root = Path(__file__).resolve().parents[1]
        self.repo_root = self.kernel_root.parents[1]

    def test_l1_vault_docs_and_acceptance_are_documented(self) -> None:
        root_readme = (self.repo_root / "README.md").read_text(encoding="utf-8")
        kernel_readme = (self.kernel_root / "README.md").read_text(encoding="utf-8")
        intake_readme = (self.kernel_root / "intake" / "README.md").read_text(encoding="utf-8")
        runtime_readme = (self.kernel_root / "runtime" / "README.md").read_text(encoding="utf-8")
        runbook = (self.kernel_root / "runtime" / "AITP_TEST_RUNBOOK.md").read_text(encoding="utf-8")
        protocol = (self.kernel_root / "intake" / "L1_VAULT_PROTOCOL.md").read_text(encoding="utf-8")

        self.assertIn("run_l1_vault_acceptance.py", root_readme)
        self.assertIn("run_l1_vault_acceptance.py", kernel_readme)
        self.assertIn("run_l1_vault_acceptance.py", runtime_readme)
        self.assertIn("run_l1_vault_acceptance.py", runbook)
        self.assertIn("raw/wiki/output", intake_readme)
        self.assertIn("flowback", intake_readme)
        self.assertIn("output-to-wiki synchronization", protocol)

    def test_acceptance_script_covers_status_and_vault_receipts(self) -> None:
        script = (
            self.kernel_root / "runtime" / "scripts" / "run_l1_vault_acceptance.py"
        ).read_text(encoding="utf-8")

        self.assertIn("status", script)
        self.assertIn("l1_vault", script)
        self.assertIn("flowback.jsonl", script)
        self.assertIn("research_question.contract.md", script)


if __name__ == "__main__":
    unittest.main()
