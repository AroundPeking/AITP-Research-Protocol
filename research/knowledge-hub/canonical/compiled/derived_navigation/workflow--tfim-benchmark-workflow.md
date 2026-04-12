# TFIM benchmark workflow

- Unit id: `workflow:tfim-benchmark-workflow`
- Unit type: `workflow`
- Canonical path: `canonical/workflows/workflow--tfim-benchmark-workflow.json`
- Degree: `6`
- Consultation profiles: `l1_provisional_understanding, l3_candidate_formation`

## Summary

Benchmark-first workflow that runs the tiny TFIM exact result before reuse.

## Outgoing Relations

- `depends_on` -> [[concept--tfim-benchmark-first-validation|Benchmark-first validation]]
- `depends_on` -> [[concept--tfim-transverse-field-ising-model|TFIM benchmark substrate]]
- `uses_method` -> [[method--tfim-exact-diagonalization-helper|TFIM exact-diagonalization helper]]
- `warned_by` -> [[warning_note--tfim-dense-ed-finite-size-limit|Dense exact diagonalization finite-size limit]]

## Incoming Relations

- `depends_on` <- [[topic_skill_projection--tfim-benchmark-first-route|TFIM benchmark-first route]]
- `depends_on` <- [[physical_picture--tfim-weak-coupling-benchmark-intuition|TFIM weak-coupling benchmark intuition]]

## Navigation

- [[index|L2 Graph Navigation Index]]
