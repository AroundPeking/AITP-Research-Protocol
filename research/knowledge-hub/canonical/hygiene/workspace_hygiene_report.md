# Workspace Hygiene Report

- Generated at: `2026-04-11T17:08:29+08:00`
- Source contract: `canonical/L2_COMPILER_PROTOCOL.md`
- Audit mode: `report_only`
- Status: `needs_review`
- Total canonical units: `10`
- Edge count: `15`
- Total findings: `23`

## Finding Counts

- Stale summary candidates: `0`
- Missing bridge candidates: `22`
- Contradiction findings: `0`
- Orphaned units: `0`
- Weakly connected units: `1`

## Stale Summary Candidates

- `(none)`

## Missing Bridge Candidates

- `bridge:tfim-toy-model-code-method-bridge` <-> `claim_card:tfim-benchmark-before-portability-claim` shared_tags=`tfim`
- `bridge:tfim-toy-model-code-method-bridge` <-> `concept:tfim-benchmark-first-validation` shared_tags=`code-method, tfim`
- `bridge:tfim-toy-model-code-method-bridge` <-> `method:tfim-exact-diagonalization-helper` shared_tags=`tfim`
- `bridge:tfim-toy-model-code-method-bridge` <-> `physical_picture:tfim-weak-coupling-benchmark-intuition` shared_tags=`tfim`
- `bridge:tfim-toy-model-code-method-bridge` <-> `validation_pattern:tfim-small-system-gap-reproduction` shared_tags=`tfim`
- `bridge:tfim-toy-model-code-method-bridge` <-> `warning_note:tfim-dense-ed-finite-size-limit` shared_tags=`tfim`
- `claim_card:tfim-benchmark-before-portability-claim` <-> `concept:tfim-transverse-field-ising-model` shared_tags=`tfim`
- `claim_card:tfim-benchmark-before-portability-claim` <-> `method:tfim-exact-diagonalization-helper` shared_tags=`tfim`
- `claim_card:tfim-benchmark-before-portability-claim` <-> `workflow:tfim-benchmark-workflow` shared_tags=`benchmark-first, tfim`
- `concept:tfim-benchmark-first-validation` <-> `concept:tfim-transverse-field-ising-model` shared_tags=`tfim`
- `concept:tfim-benchmark-first-validation` <-> `method:tfim-exact-diagonalization-helper` shared_tags=`tfim`
- `concept:tfim-benchmark-first-validation` <-> `physical_picture:tfim-weak-coupling-benchmark-intuition` shared_tags=`benchmark-first, tfim`
- `concept:tfim-benchmark-first-validation` <-> `topic_skill_projection:tfim-benchmark-first-route` shared_tags=`benchmark-first, tfim`
- `concept:tfim-benchmark-first-validation` <-> `validation_pattern:tfim-small-system-gap-reproduction` shared_tags=`tfim`
- `concept:tfim-benchmark-first-validation` <-> `warning_note:tfim-dense-ed-finite-size-limit` shared_tags=`tfim`
- `concept:tfim-transverse-field-ising-model` <-> `topic_skill_projection:tfim-benchmark-first-route` shared_tags=`tfim`
- `concept:tfim-transverse-field-ising-model` <-> `validation_pattern:tfim-small-system-gap-reproduction` shared_tags=`tfim`
- `concept:tfim-transverse-field-ising-model` <-> `warning_note:tfim-dense-ed-finite-size-limit` shared_tags=`tfim`
- `physical_picture:tfim-weak-coupling-benchmark-intuition` <-> `topic_skill_projection:tfim-benchmark-first-route` shared_tags=`benchmark-first, tfim`
- `physical_picture:tfim-weak-coupling-benchmark-intuition` <-> `validation_pattern:tfim-small-system-gap-reproduction` shared_tags=`tfim`
- `topic_skill_projection:tfim-benchmark-first-route` <-> `validation_pattern:tfim-small-system-gap-reproduction` shared_tags=`tfim`
- `validation_pattern:tfim-small-system-gap-reproduction` <-> `warning_note:tfim-dense-ed-finite-size-limit` shared_tags=`tfim`

## Contradiction Findings

- `(none)`

## Orphaned Units

- `(none)`

## Weakly Connected Units

- `concept:tfim-benchmark-first-validation` Benchmark-first validation (`canonical/concepts/concept--tfim-benchmark-first-validation.json`)
  - link_count: 1

## Hygiene Rule

This report is audit-only. Findings are candidates for review unless the underlying canonical artifacts already state the issue explicitly.
