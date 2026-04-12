from __future__ import annotations

import unittest
from pathlib import Path

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    script_root = package_root / "runtime" / "scripts"
    if str(script_root) not in sys.path:
        sys.path.insert(0, str(script_root))


_bootstrap_path()

from run_runtime_parity_audit import build_cross_runtime_parity_audit


class RuntimeParityAuditTests(unittest.TestCase):
    def _report(self, runtime: str, *, status: str, blockers: list[str] | None = None) -> dict[str, object]:
        bootstrap_receipt = {"contains_using_aitp": True}
        if runtime == "opencode":
            bootstrap_receipt["contains_tool_mapping"] = True
        return {
            "runtime": runtime,
            "status": status,
            "load_profile": "light",
            "checked_artifacts": [
                {"label": "topic_state"},
                {"label": "loop_state"},
                {"label": "session_runtime_protocol"},
                {"label": "status_runtime_protocol"},
            ],
            "status_payload": {"selected_action_id": f"action:{runtime}:01"},
            "bootstrap_receipt": bootstrap_receipt,
            "blockers": blockers or [],
            "falls_short_of_codex_baseline": [f"{runtime}:live-app-gap"] if blockers else [],
        }

    def test_build_cross_runtime_parity_audit_reports_open_gaps_honestly(self) -> None:
        payload = build_cross_runtime_parity_audit(
            {
                "codex": self._report("codex", status="baseline_ready"),
                "claude_code": self._report("claude_code", status="probe_completed_with_gap", blockers=["live_claude_chat_turn_not_exercised"]),
                "opencode": self._report("opencode", status="probe_completed_with_gap", blockers=["live_opencode_chat_turn_not_exercised"]),
            }
        )

        self.assertEqual(payload["status"], "audited_with_open_gaps")
        self.assertEqual(payload["baseline_runtime"], "codex")
        self.assertEqual(payload["status_by_runtime"]["claude_code"], "probe_completed_with_gap")
        self.assertEqual(payload["status_by_runtime"]["opencode"], "probe_completed_with_gap")
        self.assertGreaterEqual(len(payload["equivalent_surfaces"]), 3)
        self.assertEqual(len(payload["degraded_surfaces"]), 2)
        self.assertEqual(len(payload["open_gaps"]), 2)

    def test_build_cross_runtime_parity_audit_can_report_verified_state(self) -> None:
        payload = build_cross_runtime_parity_audit(
            {
                "codex": self._report("codex", status="baseline_ready"),
                "claude_code": self._report("claude_code", status="parity_verified"),
                "opencode": self._report("opencode", status="parity_verified"),
            }
        )

        self.assertEqual(payload["status"], "parity_verified")
        self.assertEqual(payload["open_gaps"], [])


if __name__ == "__main__":
    unittest.main()
