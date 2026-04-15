from __future__ import annotations

import json
import tempfile
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

from run_runtime_parity_audit import build_cross_runtime_parity_audit, load_live_first_turn_evidence


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
            "posture_contracts": {
                "status": {
                    "human_interaction_posture_present": True,
                    "autonomy_posture_present": True,
                }
            },
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
        self.assertGreaterEqual(len(payload["equivalent_surfaces"]), 4)
        self.assertEqual(len(payload["degraded_surfaces"]), 2)
        self.assertEqual(len(payload["open_gaps"]), 2)
        self.assertTrue(any(row["surface"] == "status_posture_contracts" for row in payload["equivalent_surfaces"]))

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

    def test_build_cross_runtime_parity_audit_can_close_live_first_turn_gaps_with_evidence(self) -> None:
        live_evidence = {
            "claude_code": {
                "report_kind": "runtime_live_first_turn_evidence",
                "contract_version": 1,
                "runtime": "claude_code",
                "status": "verified",
                "checks": {
                    "bootstrap_consumed_before_first_substantive_action": True,
                    "human_interaction_posture_visible": True,
                    "autonomy_posture_visible": True,
                    "wait_state_matches_contract": True,
                    "continue_state_matches_contract": True,
                },
            },
            "opencode": {
                "report_kind": "runtime_live_first_turn_evidence",
                "contract_version": 1,
                "runtime": "opencode",
                "status": "verified",
                "checks": {
                    "bootstrap_consumed_before_first_substantive_action": True,
                    "human_interaction_posture_visible": True,
                    "autonomy_posture_visible": True,
                    "wait_state_matches_contract": True,
                    "continue_state_matches_contract": True,
                },
            },
        }
        payload = build_cross_runtime_parity_audit(
            {
                "codex": self._report("codex", status="baseline_ready"),
                "claude_code": self._report("claude_code", status="probe_completed_with_gap", blockers=["live_claude_chat_turn_not_exercised"]),
                "opencode": self._report("opencode", status="probe_completed_with_gap", blockers=["live_opencode_chat_turn_not_exercised"]),
            },
            live_first_turn_evidence=live_evidence,
        )

        self.assertEqual(payload["status"], "parity_verified")
        self.assertEqual(payload["status_by_runtime"]["claude_code"], "parity_verified")
        self.assertEqual(payload["status_by_runtime"]["opencode"], "parity_verified")
        self.assertEqual(payload["degraded_surfaces"], [])
        self.assertEqual(payload["open_gaps"], [])
        self.assertTrue(any(row["surface"] == "live_first_turn_bootstrap_consumption" for row in payload["equivalent_surfaces"]))

    def test_load_live_first_turn_evidence_accepts_schema_valid_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp)
            for runtime in ("claude_code", "opencode"):
                payload = {
                    "report_kind": "runtime_live_first_turn_evidence",
                    "contract_version": 1,
                    "runtime": runtime,
                    "status": "verified",
                    "captured_at": "2026-04-13T00:00:00+08:00",
                    "entry_surface": f"{runtime} live surface",
                    "operator_summary": "Synthetic evidence for loader verification.",
                    "checks": {
                        "bootstrap_consumed_before_first_substantive_action": True,
                        "human_interaction_posture_visible": True,
                        "autonomy_posture_visible": True,
                        "wait_state_matches_contract": True,
                        "continue_state_matches_contract": True,
                    },
                    "artifacts": {
                        "transcript_path": "D:/tmp/transcript.md",
                        "session_start_path": "D:/tmp/session_start.generated.md",
                        "runtime_protocol_path": "D:/tmp/runtime_protocol.generated.md",
                        "status_payload_path": "D:/tmp/status.json",
                        "evidence_refs": ["note:synthetic"],
                    },
                }
                (evidence_root / f"{runtime}.live-first-turn.json").write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )

            evidence = load_live_first_turn_evidence(live_evidence_root=evidence_root)

        self.assertEqual(set(evidence), {"claude_code", "opencode"})
        self.assertTrue(evidence["claude_code"]["_evidence_path"].endswith("claude_code.live-first-turn.json"))


if __name__ == "__main__":
    unittest.main()
