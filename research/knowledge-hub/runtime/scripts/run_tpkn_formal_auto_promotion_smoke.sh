#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT="$(cd "${KERNEL_ROOT}/../.." && pwd)"
AITP_PYTHON_BIN="${AITP_PYTHON_BIN:-python3}"
AITP_BIN="${AITP_BIN:-}"
TODAY="${TODAY:-$(date +%F)}"
TOPIC="${TOPIC:-AITP TPKN auto-promotion smoke test ${TODAY}}"
TOPIC_SLUG="${TOPIC_SLUG:-aitp-tpkn-auto-promotion-smoke-${TODAY}}"
RUN_ID="${RUN_ID:-${TODAY}-tpkn-auto-promotion-smoke}"
UPDATED_BY="${UPDATED_BY:-tpkn-auto-promotion-smoke}"
SMOKE_ROOT="${SMOKE_ROOT:-/tmp/aitp-tpkn-auto-promotion-smoke-${TOPIC_SLUG}}"
TPKN_TEMPLATE_ROOT="${TPKN_TEMPLATE_ROOT:-}"
TPKN_WORK_ROOT="${TPKN_WORK_ROOT:-${SMOKE_ROOT}/theoretical-physics-knowledge-network}"

if [[ -z "${TPKN_TEMPLATE_ROOT}" ]]; then
  for candidate in \
    "${REPO_ROOT}/../theoretical-physics-knowledge-network" \
    "${REPO_ROOT}/../Theoretical-Physics-Knowledge-Network"
  do
    if [[ -d "${candidate}/scripts" && -f "${candidate}/scripts/kb.py" ]]; then
      TPKN_TEMPLATE_ROOT="${candidate}"
      break
    fi
  done
fi

if [[ -z "${TPKN_TEMPLATE_ROOT}" ]]; then
  echo "Missing TPKN template root. Set TPKN_TEMPLATE_ROOT or clone the standalone repo beside AITP." >&2
  exit 1
fi

run_aitp() {
  if [[ -n "${AITP_BIN}" ]]; then
    "${AITP_BIN}" "$@"
    return
  fi
  "${AITP_PYTHON_BIN}" -m knowledge_hub.aitp_cli \
    --kernel-root "${KERNEL_ROOT}" \
    --repo-root "${REPO_ROOT}" \
    "$@"
}

export AITP_KERNEL_ROOT="${AITP_KERNEL_ROOT:-${KERNEL_ROOT}}"
export AITP_REPO_ROOT="${AITP_REPO_ROOT:-${REPO_ROOT}}"
export PYTHONPATH="${KERNEL_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

rm -rf "${SMOKE_ROOT}"
mkdir -p "${SMOKE_ROOT}"
cp -R "${TPKN_TEMPLATE_ROOT}" "${TPKN_WORK_ROOT}"
rm -rf "${TPKN_WORK_ROOT}/.git" "${TPKN_WORK_ROOT}"/__pycache__ "${TPKN_WORK_ROOT}"/.pytest_cache || true

run_aitp bootstrap \
  --topic "${TOPIC}" \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --statement "Only validate the bounded theory-formal L2_auto route into the standalone TPKN backend." \
  --human-request "Do one bounded TPKN theory-formal auto-promotion smoke test without scientific conclusions." \
  --updated-by "${UPDATED_BY}" \
  --json >/dev/null

python3 - "${KERNEL_ROOT}" "${TOPIC_SLUG}" "${RUN_ID}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

kernel_root = Path(sys.argv[1])
topic_slug = sys.argv[2]
run_id = sys.argv[3]

source_root = kernel_root / "source-layer" / "topics" / topic_slug
source_root.mkdir(parents=True, exist_ok=True)
(source_root / "source_index.jsonl").write_text(
    json.dumps(
        {
            "source_id": "paper:witten-topological-phases-1510-07698v2",
            "source_type": "paper",
            "title": "Three Lectures On Topological Phases Of Matter",
            "topic_slug": topic_slug,
            "provenance": {
                "authors": ["Edward Witten"],
                "published": "2015-10-26T00:00:00+00:00",
                "updated": "2015-11-17T00:00:00+00:00",
                "abs_url": "https://arxiv.org/abs/1510.07698v2",
                "pdf_url": "https://arxiv.org/pdf/1510.07698v2",
                "source_url": "https://arxiv.org/e-print/1510.07698v2"
            },
            "acquired_at": "2026-03-17T00:00:00+08:00",
            "summary": "Public source row for the bounded TPKN auto-promotion smoke test."
        },
        ensure_ascii=True,
    )
    + "\n",
    encoding="utf-8",
)

feedback_root = kernel_root / "feedback" / "topics" / topic_slug / "runs" / run_id
feedback_root.mkdir(parents=True, exist_ok=True)
(feedback_root / "candidate_ledger.jsonl").write_text(
    json.dumps(
        {
            "candidate_id": "candidate:tpkn-auto-smoke-definition",
            "candidate_type": "definition_card",
            "title": "TPKN Auto Smoke Definition",
            "summary": "A bounded definition card used only to validate the theory-formal L2_auto writeback path.",
            "topic_slug": topic_slug,
            "run_id": run_id,
            "origin_refs": [
                {
                    "id": "paper:witten-topological-phases-1510-07698v2",
                    "layer": "L0",
                    "object_type": "source",
                    "path": f"source-layer/topics/{topic_slug}/source_index.jsonl",
                    "title": "Three Lectures On Topological Phases Of Matter",
                    "summary": "Public source row for the bounded TPKN auto-promotion smoke test."
                }
            ],
            "question": "Can AITP auto-promote one bounded definition_card into TPKN after coverage and consensus gates pass?",
            "assumptions": ["This is only a protocol smoke test."],
            "proposed_validation_route": "bounded-auto-smoke",
            "intended_l2_targets": ["definition:tpkn-auto-smoke-definition"],
            "status": "ready_for_validation"
        },
        ensure_ascii=True,
    )
    + "\n",
    encoding="utf-8",
)
PY

run_aitp coverage-audit \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --candidate-id "candidate:tpkn-auto-smoke-definition" \
  --source-section "lecture-one/auto-smoke-definition" \
  --covered-section "lecture-one/auto-smoke-definition" \
  --equation-label "eq:auto-smoke-1" \
  --notation-binding "Z=partition function" \
  --derivation-node "definition:auto-smoke" \
  --derivation-node "equation:auto-smoke-1" \
  --agent-vote "structure=covered" \
  --agent-vote "skeptic=no_major_gap" \
  --agent-vote "adjudicator=unanimous" \
  --consensus-status "unanimous" \
  --critical-unit-recall 1.0 \
  --missing-anchor-count 0 \
  --skeptic-major-gap-count 0 \
  --notes "Bounded auto-promotion smoke only." \
  --json >/dev/null

run_aitp auto-promote \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --candidate-id "candidate:tpkn-auto-smoke-definition" \
  --target-backend-root "${TPKN_WORK_ROOT}" \
  --domain "theory-formal-smoke" \
  --subdomain "aitp-auto-bridge" \
  --source-id "paper:witten-topological-phases-1510-07698v2" \
  --source-section "lecture-one/auto-smoke-definition" \
  --source-section-title "AITP Auto Smoke Definition" \
  --notes "Bounded auto-promotion smoke only." \
  --json >/dev/null

run_aitp audit --topic-slug "${TOPIC_SLUG}" --phase exit >/dev/null

UNIT_PATH="${TPKN_WORK_ROOT}/units/definitions/tpkn-auto-smoke-definition.json"
AUTO_REPORT_PATH="${KERNEL_ROOT}/validation/topics/${TOPIC_SLUG}/runs/${RUN_ID}/theory-packets/candidate-tpkn-auto-smoke-definition/auto_promotion_report.json"
COVERAGE_PATH="${KERNEL_ROOT}/validation/topics/${TOPIC_SLUG}/runs/${RUN_ID}/theory-packets/candidate-tpkn-auto-smoke-definition/coverage_ledger.json"
DECISION_PATH="${KERNEL_ROOT}/validation/topics/${TOPIC_SLUG}/runs/${RUN_ID}/promotion_decisions.jsonl"
GATE_PATH="${KERNEL_ROOT}/runtime/topics/${TOPIC_SLUG}/promotion_gate.json"

test -f "${UNIT_PATH}"
test -f "${AUTO_REPORT_PATH}"
test -f "${COVERAGE_PATH}"
test -f "${DECISION_PATH}"
test -f "${GATE_PATH}"
grep -q '"canonical_layer": "L2_auto"' "${UNIT_PATH}"
grep -q '"review_mode": "ai_auto"' "${UNIT_PATH}"
grep -q '"status": "pass"' "${COVERAGE_PATH}"
grep -q '"status": "promoted"' "${GATE_PATH}"

echo "status: success"
echo "topic_slug: ${TOPIC_SLUG}"
echo "tpkn_root: ${TPKN_WORK_ROOT}"
echo "unit_path: ${UNIT_PATH}"
echo "auto_promotion_report_path: ${AUTO_REPORT_PATH}"
echo "promotion_decision_path: ${DECISION_PATH}"
