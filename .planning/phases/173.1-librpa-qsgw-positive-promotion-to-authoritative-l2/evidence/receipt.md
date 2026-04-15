# Receipt: Phase 173.1 LibRPA QSGW Positive Authoritative-L2 Closure

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_positive_l2_acceptance_script_runs_on_isolated_work_root" -q
python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py --json
```

## Observed results

- `pytest-librpa-qsgw-positive-l2.txt`: `1 passed, 76 deselected in 2.77s`
- `librpa-qsgw-positive-l2-acceptance.json`: `status = success`

## Fresh route identifiers

- Topic slug: `librpa-qsgw-deterministic-reduction-consistency-core`
- Run id: `2026-04-14-035044-bootstrap`
- Research mode: `first_principles`

## Authoritative writeback

- Promoted claim id: `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- Canonical mirror path:
  `canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`
- Workspace knowledge report:
  `canonical/compiled/workspace_knowledge_report.json`

## Consultation proof

- Query text: `LibRPA QSGW deterministic reduction thread consistency core`
- Retrieval profile: `l4_adjudication`
- Consultation ids include:
  `claim:librpa-qsgw-deterministic-reduction-consistency-core`

## Raw artifacts

- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/librpa-qsgw-positive-l2-acceptance.json`
- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/pytest-librpa-qsgw-positive-l2.txt`
