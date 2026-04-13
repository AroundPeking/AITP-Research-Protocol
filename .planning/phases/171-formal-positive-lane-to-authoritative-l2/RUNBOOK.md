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
5. Returns both bootstrap evidence and the reused Jones closure payload.

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

## Current known open gap

This wrapper does **not** yet prove repo-local compiled L2 and `consult-l2`
parity for the positive authoritative landing. That remains the next Phase 171
execution slice.
