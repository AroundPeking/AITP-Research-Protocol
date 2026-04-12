from __future__ import annotations

import unittest
from pathlib import Path


class StatementCompilationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel_root = Path(__file__).resolve().parents[1]
        self.repo_root = self.kernel_root.parents[1]

    def test_statement_compilation_docs_and_acceptance_are_documented(self) -> None:
        root_readme = (self.repo_root / "README.md").read_text(encoding="utf-8")
        kernel_readme = (self.kernel_root / "README.md").read_text(encoding="utf-8")
        runtime_readme = (self.kernel_root / "runtime" / "README.md").read_text(encoding="utf-8")
        runbook = (self.kernel_root / "runtime" / "AITP_TEST_RUNBOOK.md").read_text(encoding="utf-8")

        self.assertIn("aitp statement-compilation", kernel_readme)
        self.assertIn("run_statement_compilation_acceptance.py", root_readme)
        self.assertIn("run_statement_compilation_acceptance.py", runtime_readme)
        self.assertIn("run_statement_compilation_acceptance.py", runbook)
        self.assertIn("proof-repair", runtime_readme)
        self.assertIn("statement-compilation", runbook)

    def test_acceptance_script_covers_statement_compilation_and_lean_bridge_consumption(self) -> None:
        script = (
            self.kernel_root / "runtime" / "scripts" / "run_statement_compilation_acceptance.py"
        ).read_text(encoding="utf-8")

        self.assertIn("statement-compilation", script)
        self.assertIn("proof_repair_plan.json", script)
        self.assertIn("lean-bridge", script)
        self.assertIn("statement_compilation_path", script)


if __name__ == "__main__":
    unittest.main()
