# Receipt: Phase 171 Fresh Formal Positive L2 Closure

## Replay commands

From repo root:

```bash
python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "promote_candidate_writes_tpkn_unit_and_decision or promote_candidate_mirrors_unit_into_repo_canonical_l2_surfaces" -q
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -k "materialize_canonical_index_and_consultation_include_theorem_card_units" -q
python research/knowledge-hub/runtime/scripts/run_formal_positive_l2_acceptance.py --json
```

## Observed results

- `pytest-promotion-mirror.txt`: `2 passed, 151 deselected in 0.71s`
- `pytest-theorem-card-consult.txt`: `1 passed, 6 deselected in 0.23s`
- `formal-positive-l2-acceptance.json`: `status = success`

## Fresh route identifiers

- Topic slug: `fresh-jones-finite-dimensional-factor-closure`
- Bootstrap run id: `2026-04-14-015101-bootstrap`
- Closure run id: `2026-04-14-015101-jones-close`
- Research mode: `formal_derivation`

## Authoritative writeback

- Theorem target unit id: `theorem:jones-ch4-finite-product`
- Theorem canonical mirror path:
  `research/knowledge-hub/canonical/theorem-cards/theorem_card--jones-ch4-finite-product.json`
- Projection target unit id:
  `topic_skill_projection:fresh-jones-finite-dimensional-factor-closure`
- Projection canonical mirror path:
  `research/knowledge-hub/canonical/topic-skill-projections/topic_skill_projection--fresh-jones-finite-dimensional-factor-closure.json`

## Repo-local L2 parity

- Workspace memory map:
  `research/knowledge-hub/canonical/compiled/workspace_memory_map.json`
- Workspace graph report:
  `research/knowledge-hub/canonical/compiled/workspace_graph_report.json`
- Workspace knowledge report:
  `research/knowledge-hub/canonical/compiled/workspace_knowledge_report.json`
- `consult-l2` query:
  `Jones finite product theorem packet`
- Verified consultation ids include:
  - `theorem:jones-ch4-finite-product`
  - `topic_skill_projection:fresh-jones-finite-dimensional-factor-closure`

## Raw artifacts

- `.planning/phases/171-formal-positive-lane-to-authoritative-l2/evidence/formal-positive-l2-acceptance.json`
- `.planning/phases/171-formal-positive-lane-to-authoritative-l2/evidence/pytest-promotion-mirror.txt`
- `.planning/phases/171-formal-positive-lane-to-authoritative-l2/evidence/pytest-theorem-card-consult.txt`
