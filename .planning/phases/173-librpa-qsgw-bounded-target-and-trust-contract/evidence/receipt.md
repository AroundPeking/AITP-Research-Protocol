# Receipt: Phase 173 LibRPA QSGW Bounded Target Contract

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_target_contract_acceptance_script_runs_on_isolated_work_root" -q
python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -k "first_principles" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_target_contract_acceptance.py --json
```

## Observed results

- `pytest-librpa-qsgw-target-contract.txt`: `1 passed, 75 deselected in 2.34s`
- `pytest-first-principles-routing.txt`: `2 passed, 4 deselected in 0.09s`
- `librpa-qsgw-target-contract-acceptance.json`: `status = success`

## Key facts

- Fresh topic slug: `librpa-qsgw-deterministic-reduction-consistency-core`
- Research mode: `first_principles`
- Topic synopsis lane observed by the runtime: `toy_numeric`
- Chosen candidate:
  `candidate:librpa-qsgw-deterministic-reduction-consistency-core`
- Trust status: `pass`
- Bounded reference case: `H2O/really_tight iter=10`

## Source-of-truth anchors

- Code root: `D:\BaiduSyncdisk\Theoretical-Physics\LibRPA-develop`
- Workflow wrapper root: `D:\BaiduSyncdisk\repos\oh-my-LibRPA`
- Validator:
  `D:\BaiduSyncdisk\Theoretical-Physics\automation\validators\qsgw_validator.py`

## Raw artifacts

- `.planning/phases/173-librpa-qsgw-bounded-target-and-trust-contract/evidence/pytest-librpa-qsgw-target-contract.txt`
- `.planning/phases/173-librpa-qsgw-bounded-target-and-trust-contract/evidence/pytest-first-principles-routing.txt`
- `.planning/phases/173-librpa-qsgw-bounded-target-and-trust-contract/evidence/librpa-qsgw-target-contract-acceptance.json`
