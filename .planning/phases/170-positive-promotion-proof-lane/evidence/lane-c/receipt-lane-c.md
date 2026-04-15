# Receipt Lane C: First Principles (LibRPA QSGW)

**Lane:** C
**Research mode:** `first_principles`
**Topic slug:** `librpa-qsgw-convergence-verification-for-h2o-tight-basis`
**Date:** 2026-04-14

## What was proven

The AITP public front door correctly bootstraps a `first_principles` topic
through `AITPService().new_topic()` when the caller specifies research mode
`first_principles`. The service passes the mode through without remapping.

## Bootstrap evidence

| Check | Result |
|-------|--------|
| Topic created via public front door | Yes |
| No hidden seed state used | Yes |
| Research mode: `first_principles` | Confirmed |
| Conformance audit: 27/27 pass | Confirmed |
| Runtime topic shell materialized | Yes |
| Resume stage: L3 (candidate_shaping) | Confirmed |

## Runtime artifacts

| Artifact | Path |
|----------|------|
| Topic state | `runtime/topics/librpa-qsgw-convergence-verification-for-h2o-tight-basis/topic_state.json` |
| Conformance state | `runtime/topics/librpa-qsgw-convergence-verification-for-h2o-tight-basis/conformance_state.json` |
| Runtime protocol | `runtime/topics/librpa-qsgw-convergence-verification-for-h2o-tight-basis/runtime_protocol.generated.md` |

## Runbook

See `RUNBOOK-C.md` in `.planning/phases/170-positive-promotion-proof-lane/`.

## What was NOT proven

- Actual L4->L2 promotion for a first_principles topic
- LibRPA QSGW convergence verification execution
- Whether the first_principles -> code_method mapping works for upstream codebase references

## Regression replay

```bash
# From repo root:
python -c "
from knowledge_hub.aitp_service import AITPService
svc = AITPService()
result = svc.new_topic(
    topic='LibRPA QSGW convergence verification for H2O tight basis',
    statement='Verify QSGW convergence using LibRPA with FHI-aims for H2O in a tight basis set',
    research_mode='first_principles',
    human_request='Bootstrap a first principles topic for LibRPA QSGW convergence verification'
)
print('Mode:', result.get('research_mode'))
print('Slug:', result.get('topic_slug'))
"
```
