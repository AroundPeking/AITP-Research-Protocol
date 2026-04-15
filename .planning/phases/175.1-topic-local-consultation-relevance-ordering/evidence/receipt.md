# Receipt: Phase 175.1 Topic-Local Consultation Relevance Ordering

## Replay commands

```bash
python -m pytest research/knowledge-hub/tests/test_l2_graph_activation.py -q
python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "consult_l2" -q
```

## Observed results

- `pytest-l2-graph-activation.txt`: `9 passed in 0.88s`
- `pytest-aitp-service-consult-l2.txt`: `2 passed, 151 deselected in 0.37s`

## Key facts

- `consult_canonical_l2()` now accepts `topic_slug`
- topic-local staged rows can enter `primary_hits` when staging is included
- `aitp_service.consult_l2()` now forwards `topic_slug` into the low-level
  consultation path

## Raw artifacts

- `.planning/phases/175.1-topic-local-consultation-relevance-ordering/evidence/pytest-l2-graph-activation.txt`
- `.planning/phases/175.1-topic-local-consultation-relevance-ordering/evidence/pytest-aitp-service-consult-l2.txt`
