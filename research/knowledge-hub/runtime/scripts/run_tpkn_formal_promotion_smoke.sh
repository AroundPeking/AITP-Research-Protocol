#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT="$(cd "${KERNEL_ROOT}/../.." && pwd)"
AITP_PYTHON_BIN="${AITP_PYTHON_BIN:-python3}"
AITP_BIN="${AITP_BIN:-}"
TODAY="${TODAY:-$(date +%F)}"
TOPIC="${TOPIC:-AITP TPKN promotion smoke test ${TODAY}}"
TOPIC_SLUG="${TOPIC_SLUG:-aitp-tpkn-promotion-smoke-${TODAY}}"
RUN_ID="${RUN_ID:-${TODAY}-tpkn-promotion-smoke}"
UPDATED_BY="${UPDATED_BY:-tpkn-promotion-smoke}"
SMOKE_ROOT="${SMOKE_ROOT:-/tmp/aitp-tpkn-promotion-smoke-${TOPIC_SLUG}}"
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
  --statement "Only validate the approval gate and external TPKN writeback path." \
  --human-request "Do one bounded TPKN formal-theory promotion smoke test without scientific conclusions." \
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
            "acquired_at": "2026-03-16T00:00:00+08:00",
            "summary": "Public source row for the bounded TPKN smoke test."
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
            "candidate_id": "candidate:tpkn-smoke-formal-concept",
            "candidate_type": "concept",
            "title": "TPKN Smoke Formal Concept",
            "summary": "A bounded formal-theory concept used only to validate approval-gated TPKN writeback.",
            "topic_slug": topic_slug,
            "run_id": run_id,
            "origin_refs": [
                {
                    "id": "paper:witten-topological-phases-1510-07698v2",
                    "layer": "L0",
                    "object_type": "source",
                    "path": f"source-layer/topics/{topic_slug}/source_index.jsonl",
                    "title": "Three Lectures On Topological Phases Of Matter",
                    "summary": "Public source row for the bounded TPKN smoke test."
                }
            ],
            "question": "Can AITP request approval and then write a bounded concept packet into TPKN?",
            "assumptions": ["This is only a protocol smoke test."],
            "proposed_validation_route": "bounded-smoke",
            "intended_l2_targets": ["concept:tpkn-smoke-formal-concept"],
            "status": "ready_for_validation"
        },
        ensure_ascii=True,
    )
    + "\n",
    encoding="utf-8",
)
PY

run_aitp request-promotion \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --candidate-id "candidate:tpkn-smoke-formal-concept" \
  --backend-id "backend:theoretical-physics-knowledge-network" \
  --target-backend-root "${TPKN_WORK_ROOT}" \
  --notes "Bounded smoke request only." \
  --json >/dev/null

run_aitp approve-promotion \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --candidate-id "candidate:tpkn-smoke-formal-concept" \
  --notes "Approved for bounded protocol smoke test." \
  --json >/dev/null

run_aitp promote \
  --topic-slug "${TOPIC_SLUG}" \
  --run-id "${RUN_ID}" \
  --candidate-id "candidate:tpkn-smoke-formal-concept" \
  --target-backend-root "${TPKN_WORK_ROOT}" \
  --domain "formal-theory-smoke" \
  --subdomain "aitp-bridge" \
  --source-id "paper:witten-topological-phases-1510-07698v2" \
  --source-section "lecture-one/aitp-smoke-concept" \
  --source-section-title "AITP Smoke Concept" \
  --notes "Bounded smoke promotion only." \
  --json >/dev/null

run_aitp audit --topic-slug "${TOPIC_SLUG}" --phase exit >/dev/null

UNIT_PATH="${TPKN_WORK_ROOT}/units/concepts/tpkn-smoke-formal-concept.json"
DECISION_PATH="${KERNEL_ROOT}/validation/topics/${TOPIC_SLUG}/runs/${RUN_ID}/promotion_decisions.jsonl"
GATE_PATH="${KERNEL_ROOT}/runtime/topics/${TOPIC_SLUG}/promotion_gate.json"
CONSULT_PATH="${KERNEL_ROOT}/consultation/topics/${TOPIC_SLUG}/calls/consult-tpkn-promotion-candidate-tpkn-smoke-formal-concept/result.json"

test -f "${UNIT_PATH}"
test -f "${DECISION_PATH}"
test -f "${GATE_PATH}"
test -f "${CONSULT_PATH}"
grep -q '"status": "promoted"' "${GATE_PATH}"
grep -q '"id": "concept:tpkn-smoke-formal-concept"' "${UNIT_PATH}"

echo "status: success"
echo "topic_slug: ${TOPIC_SLUG}"
echo "tpkn_root: ${TPKN_WORK_ROOT}"
echo "unit_path: ${UNIT_PATH}"
echo "promotion_decision_path: ${DECISION_PATH}"
