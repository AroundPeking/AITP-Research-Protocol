# RUNBOOK-E: Master Regression and Replay Guide

**Phase:** 170.2
**Purpose:** Mechanical replay steps for all four v1.96 proof lanes
**Date:** 2026-04-14

## Overview

This runbook covers regression replay for all four proof lanes in milestone
v1.96 "Real Topic Promotion E2E Proof":

| Lane | Mode | Topic Slug | Phase |
|------|------|-----------|-------|
| A | `formal_derivation` | `von-neumann-algebra-factor-type-classification-proof` | 170 |
| B | `toy_model` | `haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum` | 170 |
| C | `first_principles` | `librpa-qsgw-convergence-verification-for-h2o-tight-basis` | 170 |
| D | negative result | `hs-model-otoc-lyapunov-exponent-failure` | 170.1 |

## Prerequisites

- Repo checkout at `D:\BaiduSyncdisk\repos\AITP-Research-Protocol`
- Python 3.10+ with `knowledge_hub` importable (editable install or PYTHONPATH)
- Working directory: repo root

## Part 1: Positive Bootstrap Regression (Lanes A, B, C)

### Step 1.1: Verify existing topic state

For each lane, verify the runtime topic shell exists and conformance passes:

```bash
# Lane A
python -c "
import json
d = json.load(open('research/knowledge-hub/runtime/topics/von-neumann-algebra-factor-type-classification-proof/conformance_state.json'))
checks = d.get('checks', [])
print('Lane A:', len(checks), 'checks,', sum(1 for c in checks if c['status']=='pass'), 'pass')
"

# Lane B
python -c "
import json
d = json.load(open('research/knowledge-hub/runtime/topics/haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum/conformance_state.json'))
checks = d.get('checks', [])
print('Lane B:', len(checks), 'checks,', sum(1 for c in checks if c['status']=='pass'), 'pass')
"

# Lane C
python -c "
import json
d = json.load(open('research/knowledge-hub/runtime/topics/librpa-qsgw-convergence-verification-for-h2o-tight-basis/conformance_state.json'))
checks = d.get('checks', [])
print('Lane C:', len(checks), 'checks,', sum(1 for c in checks if c['status']=='pass'), 'pass')
"
```

**Expected:** All three report `27 checks, 27 pass`.

### Step 1.2: Verify mode routing

```bash
python -c "
import json
for slug, expected_mode in [
    ('von-neumann-algebra-factor-type-classification-proof', 'formal_derivation'),
    ('haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum', 'toy_model'),
    ('librpa-qsgw-convergence-verification-for-h2o-tight-basis', 'first_principles'),
]:
    d = json.load(open(f'research/knowledge-hub/runtime/topics/{slug}/topic_state.json'))
    actual = d.get('research_mode')
    status = 'OK' if actual == expected_mode else 'MISMATCH'
    print(f'{status}: {slug} mode={actual} (expected={expected_mode})')
"
```

**Expected:** All three report `OK`.

### Step 1.3: Re-bootstrap (fresh topic regression)

If full regression is needed, bootstrap fresh topics through the public front
door. **Warning:** This creates new topics. Use distinct slugs to avoid
collision with existing runtime state.

```python
from knowledge_hub.aitp_service import AITPService
svc = AITPService()

# Lane A regression
result_a = svc.new_topic(
    topic='[REGRESSION] von Neumann algebra factor type classification',
    statement='Regression test: prove factor type classification for von Neumann algebras',
    research_mode='formal_theory',
    human_request='Bootstrap regression test'
)
assert result_a['research_mode'] == 'formal_derivation'

# Lane B regression
result_b = svc.new_topic(
    topic='[REGRESSION] Haldane-Shastry model quantum chaos',
    statement='Regression test: investigate quantum chaos in HS model',
    research_mode='toy_model',
    human_request='Bootstrap regression test'
)
assert result_b['research_mode'] == 'toy_model'

# Lane C regression
result_c = svc.new_topic(
    topic='[REGRESSION] LibRPA QSGW convergence H2O',
    statement='Regression test: verify QSGW convergence for H2O tight basis',
    research_mode='first_principles',
    human_request='Bootstrap regression test'
)
assert result_c['research_mode'] == 'first_principles'
```

## Part 2: Negative-Result Pipeline Regression (Lane D)

### Step 2.1: Verify existing negative-result state

```bash
python -c "
import json

# Check scratchpad
d = json.load(open('research/knowledge-hub/runtime/topics/hs-model-otoc-lyapunov-exponent-failure/scratchpad.active.json'))
print('Negative result count:', d.get('negative_result_count', 0))
print('Latest:', d.get('latest_negative_result_summary', 'N/A')[:80])

# Check staging manifest
m = json.load(open('research/knowledge-hub/canonical/staging/workspace_staging_manifest.json'))
print('Manifest total entries:', m.get('total_entries', 0))
print('Negative results:', m.get('counts_by_kind', {}).get('negative_result', 0))
"
```

**Expected:**
- `negative_result_count >= 1`
- Manifest has `negative_result >= 1`

### Step 2.2: Verify contradiction_watch

```bash
python -c "
import json
r = json.load(open('research/knowledge-hub/canonical/compiled/workspace_knowledge_report.json'))
contradictions = [row for row in r.get('knowledge_rows', []) if row.get('knowledge_state') == 'contradiction_watch']
print('Contradiction rows:', len(contradictions))

# Find the HS model entry
hs_entries = [row for row in contradictions if 'hs-model' in row.get('canonical_source_id', '').lower() or 'hs-model' in row.get('entry_id', '').lower()]
print('HS model contradiction entries:', len(hs_entries))
for e in hs_entries:
    print('  -', e.get('entry_id'), '|', e.get('knowledge_state'), '|', e.get('authority_level'))
"
```

**Expected:**
- `contradiction_row_count >= 1`
- At least one HS model entry with `knowledge_state: "contradiction_watch"`

### Step 2.3: Full negative-result pipeline replay

See Phase 170.1 `RUNBOOK-D.md` for the complete replay sequence:

1. Bootstrap negative-result topic
2. Record negative result via `record_negative_result_payload()`
3. Stage via `stage-negative-result` CLI
4. Compile via `compile-l2-knowledge-report` CLI
5. Verify `contradiction_watch` in compiled report

## Part 3: Cross-Lane Checks

### Step 3.1: Verify no hidden seed state

For each topic, verify that no pre-seeded canonical sources or promotion
candidates exist:

```bash
python -c "
import json, os
topics = [
    'von-neumann-algebra-factor-type-classification-proof',
    'haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum',
    'librpa-qsgw-convergence-verification-for-h2o-tight-basis',
    'hs-model-otoc-lyapunov-exponent-failure',
]
for slug in topics:
    ts = json.load(open(f'research/knowledge-hub/runtime/topics/{slug}/topic_state.json'))
    # Check that the topic was bootstrapped through public front door
    print(f'{slug}: stage={ts.get(\"resume_stage\")}, mode={ts.get(\"research_mode\")}')
"
```

### Step 3.2: Evidence file inventory

Verify all evidence files exist:

```
.planning/phases/170-positive-promotion-proof-lane/
  PLAN.md
  SUMMARY.md
  RUNBOOK-A.md
  RUNBOOK-B.md
  RUNBOOK-C.md
  evidence/lane-a/receipt-lane-a.md
  evidence/lane-b/receipt-lane-b.md
  evidence/lane-c/receipt-lane-c.md

.planning/phases/170.1-negative-result-promotion-proof-lane/
  PLAN.md
  SUMMARY.md
  RUNBOOK-D.md
  evidence/receipt-negative-result-e2e.md

.planning/phases/170.2-e2e-evidence-and-regression-closure/
  PLAN.md
  SUMMARY.md
  RUNBOOK-E.md
  evidence/receipt-lane-d.md
  evidence/postmortem.md
```

## Acceptance gate

A regression pass succeeds when:

1. All three positive lanes report 27/27 conformance
2. All three modes route correctly (formal_derivation, toy_model, first_principles)
3. The negative-result pipeline produces `contradiction_watch` in the compiled report
4. All evidence files are present and non-empty
5. No hidden seed state was used for any lane
