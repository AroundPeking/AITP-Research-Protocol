# Receipt Lane B: Toy Model (Haldane-Shastry Model)

**Lane:** B
**Research mode:** `toy_model`
**Topic slug:** `haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum`
**Date:** 2026-04-14

## What was proven

The AITP public front door correctly bootstraps a `toy_model` topic through
`AITPService().new_topic()` when the caller specifies research mode `toy_model`.
The service passes the mode through without remapping.

## Bootstrap evidence

| Check | Result |
|-------|--------|
| Topic created via public front door | Yes |
| No hidden seed state used | Yes |
| Research mode: `toy_model` | Confirmed |
| Conformance audit: 27/27 pass | Confirmed |
| Runtime topic shell materialized | Yes |
| Resume stage: L3 (candidate_shaping) | Confirmed |

## Runtime artifacts

| Artifact | Path |
|----------|------|
| Topic state | `runtime/topics/haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum/topic_state.json` |
| Conformance state | `runtime/topics/haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum/conformance_state.json` |
| Runtime protocol | `runtime/topics/haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum/runtime_protocol.generated.md` |

## Runbook

See `RUNBOOK-B.md` in `.planning/phases/170-positive-promotion-proof-lane/`.

## What was NOT proven

- Actual L4->L2 promotion for a toy model topic
- Chaos indicator computation (OTOC, Lyapunov spectrum)
- Whether the toy_model acceptance surface handles non-integrable model failures

## Additional note

Lane B was also used as the seed for the negative-result proof (Phase 170.1).
The HS model's integrability means it cannot exhibit quantum chaos — this
physics-honest failure was used to prove the negative-result pipeline works.

## Regression replay

```bash
# From repo root:
python -c "
from knowledge_hub.aitp_service import AITPService
svc = AITPService()
result = svc.new_topic(
    topic='Haldane-Shastry model quantum chaos and Lyapunov spectrum',
    statement='Investigate whether the Haldane-Shastry model exhibits quantum chaos through OTOC-based Lyapunov exponent analysis',
    research_mode='toy_model',
    human_request='Bootstrap a toy model topic for HS model quantum chaos analysis'
)
print('Mode:', result.get('research_mode'))
print('Slug:', result.get('topic_slug'))
"
```
