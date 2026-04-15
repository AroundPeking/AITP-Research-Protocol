# RUNBOOK-D: Negative-Result Promotion Reproduction Steps

**Phase:** 170.1
**Date:** 2026-04-13
**Operator:** phase-170.1-runner

## Overview

This runbook reproduces the negative-result promotion proof: one honest
physics-failure bounded route traveling from topic bootstrap through the public
front door into L2 staging as `contradiction_watch`.

## Prerequisites

- AITP kernel installed (`aitp doctor` passes)
- Working directory: repo root `AITP-Research-Protocol`
- Python environment with `knowledge_hub` importable

## Reproduction steps

### Step 1: Bootstrap the failure-bound topic

```bash
cd research/knowledge-hub

python -m knowledge_hub.aitp_cli bootstrap \
  --topic "hs-model-otoc-lyapunov-exponent-failure" \
  --statement "Does the Haldane-Shastry model exhibit a well-defined OTOC-based quantum Lyapunov exponent at finite N? Expected answer: no, because the HS model is integrable and OTOC growth does not follow the exponential chaos-bound pattern." \
  --json
```

**Verify:**
- `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/topic_state.json` exists
- Conformance state shows 27/27 pass

### Step 2: Record the negative result on the topic

```python
from knowledge_hub.scratchpad_support import record_negative_result_payload

result = record_negative_result_payload(
    topic_slug="hs-model-otoc-lyapunov-exponent-failure",
    summary="The Haldane-Shastry model does NOT exhibit a well-defined OTOC-based quantum Lyapunov exponent at finite N. The HS model is integrable (solves the Yang-Baxter equation), and integrable systems do not show exponential OTOC growth.",
    failure_kind="regime_mismatch",
    details="OTOC behavior in the HS model is governed by power-law spreading due to ballistically propagating quasi-particles, not by chaotic dynamics. The MSS chaos bound does not apply.",
    updated_by="phase-170.1-runner"
)
```

**Verify:**
- `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/scratchpad.active.json` shows `negative_result_count: 1`
- An entry ID like `scratch-negative-result-*` appears in `entry_ids`

### Step 3: Stage the negative result into L2

```bash
python -m knowledge_hub.aitp_cli stage-negative-result \
  --title "HS model OTOC Lyapunov exponent: regime mismatch" \
  --summary "The Haldane-Shastry model does NOT exhibit a well-defined OTOC-based quantum Lyapunov exponent at finite N. The HS model is integrable, OTOC growth is power-law not exponential, and the MSS chaos bound does not apply." \
  --failure-kind regime_mismatch \
  --updated-by phase-170.1-runner \
  --json
```

**Verify:**
- Output JSON shows `entry_kind: "negative_result"`, `status: "staged"`, `authoritative: false`
- `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.json` exists

### Step 4: Compile the L2 knowledge report

```bash
python -m knowledge_hub.aitp_cli compile-l2-knowledge-report --json
```

**Verify:**
- Output JSON `summary.contradiction_row_count` >= 1
- The `contradiction_rows` array contains an entry with `knowledge_id` starting with `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`
- That entry has `knowledge_state: "contradiction_watch"` in `knowledge_rows`
- `canonical/compiled/workspace_knowledge_report.json` and `.md` are updated

### Step 5: Confirm end-to-end integrity

1. Check topic conformance: `aitp ci-check --topic-slug hs-model-otoc-lyapunov-exponent-failure`
2. Check scratchpad reflects the negative result count
3. Check the staging manifest includes the new entry
4. Check the compiled report lists it as `contradiction_watch`

## Key code surfaces

| Surface | File | Function/Command |
|---------|------|-----------------|
| Negative result recording | `knowledge_hub/scratchpad_support.py` | `record_negative_result_payload()` |
| Negative result staging | `knowledge_hub/aitp_cli.py` | `stage-negative-result` |
| Knowledge state assignment | `knowledge_hub/l2_compiler.py` | `_staging_knowledge_state()` |
| Report compilation | `knowledge_hub/aitp_cli.py` | `compile-l2-knowledge-report` |
| Acceptance reference | `runtime/scripts/run_l2_knowledge_report_acceptance.py` | Synthetic version of this proof |

## Failure mode notes

- If `stage-negative-result` returns an error, check that the scratchpad entry exists and has a valid `failure_kind`
- If `contradiction_row_count` does not increase, check that `entry_kind == "negative_result"` in the staged entry
- If conformance fails, re-run `aitp audit --topic-slug <slug> --phase entry` to identify which check failed

## Physics context

The Haldane-Shastry model is a long-range interacting spin chain that is exactly
solvable (integrable). For integrable systems, out-of-time-order correlators
(OTOCs) grow as power laws, not exponentials, so there is no well-defined
quantum Lyapunov exponent. The Maldacena-Shenker-Stanford (MSS) chaos bound
$\lambda_L \leq 2\pi T$ does not apply because $\lambda_L$ does not exist in
this system. This is a genuine regime mismatch, not an engineered failure.
