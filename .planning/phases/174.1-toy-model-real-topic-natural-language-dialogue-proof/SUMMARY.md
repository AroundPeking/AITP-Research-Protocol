# Phase 174.1 Summary: Toy-Model Real-Topic Natural-Language Dialogue Proof

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 2 (inter-layer connection) + Axis 5 (agent-facing steering)

## What was done

Phase `174.1` closed the toy-model leg of the three-lane real-topic
natural-language dialogue milestone.

### Proof route

- started from a fresh natural-language toy-model request in the HS-like
  chaos-window direction
- kept the route tied to the already-proved bounded finite-size positive core
- proved the natural-language request remains visible on runtime-side steering
  artifacts while the final authoritative-L2 claim landing stays unchanged
- re-checked the promotion-gate human actor bindings while the new dialogue
  proof was added

## Acceptance criteria

- [x] One real natural-language dialogue run proves the toy-model baseline can be entered through the public front door
- [x] Runtime steering artifacts preserve the fresh toy-model request
- [x] The route stays aligned with the bounded positive authoritative-L2 toy-model baseline
- [x] Promotion-gate regression acceptances still pass on isolated work roots

## Evidence

| Artifact | Location | Purpose |
|----------|----------|---------|
| `pytest-toy-model-real-topic-dialogue.txt` | `phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/` | Combined isolated regression receipt for the new toy-model dialogue lane plus the two promotion-gate actor-binding checks |
| `toy-model-real-topic-dialogue-acceptance.json` | `phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/` | Raw replay payload with dialogue inputs, steering artifacts, promotion receipts, and repo-local L2 parity |
| `receipt.md` | `phases/174.1-toy-model-real-topic-natural-language-dialogue-proof/evidence/` | Human-readable replay receipt |

## What this phase proved

1. The public AITP front door can steer the bounded HS-like toy-model baseline
   from a real natural-language request without hidden seed state.
2. Runtime steering artifacts preserve the toy-model dialogue request instead
   of erasing it behind internal routing.
3. The bounded toy-model authoritative-L2 landing remains stable under this
   real-dialogue entry path, and the promotion-gate actor bindings still pass
   their isolated regressions.
