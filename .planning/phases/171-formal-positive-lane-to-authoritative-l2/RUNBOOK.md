# RUNBOOK: Phase 171 Fresh Formal Positive Lane

## Purpose

Replay the current fresh formal positive-lane baseline for Phase `171` using a
fresh public-front-door topic and the reused Jones Chapter 4 closure executor.

## Command

From repo root:

```bash
python research/knowledge-hub/runtime/scripts/run_formal_positive_l2_acceptance.py --json
```

## What the wrapper does

1. Calls `AITPService().new_topic()` with a fresh natural-language formal topic.
2. Verifies entry conformance on the fresh topic shell.
3. Copies the explicit Jones source-topic rows from
   `source-layer/topics/jones-von-neumann-algebras/` onto the fresh topic slug.
4. Delegates the same fresh slug into
   `run_jones_chapter4_finite_product_formal_closure_acceptance.py`.
5. Compiles repo-local L2 workspace memory/graph/knowledge reports.
6. Runs `consult-l2` against the promoted theorem packet and verifies parity.
7. Returns both bootstrap evidence and the reused Jones closure payload.

## Current success boundary

The current wrapper now succeeds through:

- fresh public-front-door bootstrap
- `formal_derivation` mode routing
- explicit L0 source carry-over onto the fresh topic
- formal coverage audit
- formal-theory review
- Lean-bridge materialization
- theorem packet `L2_auto` backend promotion
- topic-skill projection promotion
- repo-local canonical theorem/projection mirrors
- compiled L2 workspace report parity
- natural-language `consult-l2` parity for the promoted theorem packet

## Next bounded gap

Phase `171` is now closed. The next bounded gap is Phase `171.1`: prove the new
positive authoritative rows and the already-proven negative-result
`contradiction_watch` rows coexist honestly on the same compiled and
consultation surfaces.
