# RUNBOOK: Phase 173 LibRPA QSGW Bounded Target Contract

## Purpose

Replay the bounded `LibRPA QSGW` target-contract baseline for the remaining
first-principles / code-method lane.

## Commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_target_contract_acceptance_script_runs_on_isolated_work_root" -q
python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -k "first_principles" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_target_contract_acceptance.py --json
```

## What the wrapper does

1. Opens a fresh `first_principles` topic through the public front door.
2. Registers local-note source anchors for the LibRPA codebase root, workflow
   trust note, and the existing QSGW engineering reports.
3. Writes one bounded target contract and one candidate-ledger row for the
   deterministic-reduction consistency core.
4. Scaffolds baseline, atomic-understanding, operation, trust-audit, and
   strategy-memory artifacts for that bounded route.

## Expected success markers

- topic slug: `librpa-qsgw-deterministic-reduction-consistency-core`
- candidate id: `candidate:librpa-qsgw-deterministic-reduction-consistency-core`
- target contract:
  `runtime/topics/<slug>/librpa_qsgw_target_contract.json`
- candidate ledger:
  `feedback/topics/<slug>/runs/<run>/candidate_ledger.jsonl`
- trust audit status: `pass`

## Current success boundary

This phase succeeds only for the bounded deterministic-reduction consistency
core. Broader QSGW convergence and broader workflow portability remain deferred
to later phases.
