# Receipt Lane A: Formal Derivation (von Neumann Algebras)

**Lane:** A
**Research mode:** `formal_derivation`
**Topic slug:** `von-neumann-algebra-factor-type-classification-proof`
**Date:** 2026-04-14

## What was proven

The AITP public front door correctly bootstraps a `formal_derivation` topic
through `AITPService().new_topic()` when the caller specifies research mode
`formal_theory`. The service correctly routes `formal_theory` to the internal
mode `formal_derivation`.

## Bootstrap evidence

| Check | Result |
|-------|--------|
| Topic created via public front door | Yes |
| No hidden seed state used | Yes |
| Research mode: `formal_derivation` | Confirmed |
| Conformance audit: 27/27 pass | Confirmed |
| Runtime topic shell materialized | Yes |
| Resume stage: L3 (candidate_shaping) | Confirmed |

## Runtime artifacts

| Artifact | Path |
|----------|------|
| Topic state | `runtime/topics/von-neumann-algebra-factor-type-classification-proof/topic_state.json` |
| Conformance state | `runtime/topics/von-neumann-algebra-factor-type-classification-proof/conformance_state.json` |
| Runtime protocol | `runtime/topics/von-neumann-algebra-factor-type-classification-proof/runtime_protocol.generated.md` |

## Runbook

See `RUNBOOK-A.md` in `.planning/phases/170-positive-promotion-proof-lane/`.

## What was NOT proven

- Actual L4->L2 promotion for a formal derivation topic
- Source registration (L0) for Jones (1983) or related von Neumann algebra references
- Derivation execution through L1->L3->L4->L2

## Regression replay

```bash
# From repo root:
python -c "
from knowledge_hub.aitp_service import AITPService
svc = AITPService()
result = svc.new_topic(
    topic='von Neumann algebra factor type classification proof',
    statement='Prove the factor type classification theorem for von Neumann algebras on separable Hilbert spaces',
    research_mode='formal_theory',
    human_request='Bootstrap a formal derivation topic for von Neumann algebra factor classification'
)
print('Mode:', result.get('research_mode'))
print('Slug:', result.get('topic_slug'))
"

# Verify conformance:
python -c "
import json
d = json.load(open('research/knowledge-hub/runtime/topics/von-neumann-algebra-factor-type-classification-proof/conformance_state.json'))
checks = d.get('checks', [])
print(f'{len(checks)}/{len(checks)} pass:', all(c['status']=='pass' for c in checks))
"
```
