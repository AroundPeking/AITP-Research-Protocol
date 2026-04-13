# Workspace Graph Report

- Generated at: `2026-04-13T23:13:17+08:00`
- Total canonical units: `11`
- Edge count: `15`
- Connected units: `10`
- Isolated units: `1`
- Navigation index: `canonical/compiled/derived_navigation/index.md`

## Graph Hubs

- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow (degree=`6`, outgoing=`4`, incoming=`2`) [[derived_navigation/workflow--tfim-benchmark-workflow|TFIM benchmark workflow]]
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route (degree=`4`, outgoing=`3`, incoming=`1`) [[derived_navigation/topic_skill_projection--tfim-benchmark-first-route|TFIM benchmark-first route]]
- `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper (degree=`4`, outgoing=`0`, incoming=`4`) [[derived_navigation/method--tfim-exact-diagonalization-helper|TFIM exact-diagonalization helper]]
- `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit (degree=`4`, outgoing=`0`, incoming=`4`) [[derived_navigation/warning_note--tfim-dense-ed-finite-size-limit|Dense exact diagonalization finite-size limit]]
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition (degree=`3`, outgoing=`3`, incoming=`0`) [[derived_navigation/physical_picture--tfim-weak-coupling-benchmark-intuition|TFIM weak-coupling benchmark intuition]]
- `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim (degree=`3`, outgoing=`2`, incoming=`1`) [[derived_navigation/claim_card--tfim-benchmark-before-portability-claim|Benchmark before portability claim]]
- `concept:tfim-benchmark-first-validation` Benchmark-first validation (degree=`2`, outgoing=`1`, incoming=`1`) [[derived_navigation/concept--tfim-benchmark-first-validation|Benchmark-first validation]]
- `validation_pattern:tfim-small-system-gap-reproduction` TFIM small-system gap reproduction (degree=`2`, outgoing=`1`, incoming=`1`) [[derived_navigation/validation_pattern--tfim-small-system-gap-reproduction|TFIM small-system gap reproduction]]
- `bridge:tfim-toy-model-code-method-bridge` TFIM toy-model to code-method bridge (degree=`1`, outgoing=`1`, incoming=`0`) [[derived_navigation/bridge--tfim-toy-model-code-method-bridge|TFIM toy-model to code-method bridge]]
- `concept:tfim-transverse-field-ising-model` TFIM benchmark substrate (degree=`1`, outgoing=`0`, incoming=`1`) [[derived_navigation/concept--tfim-transverse-field-ising-model|TFIM benchmark substrate]]

## Relation Clusters

### `depends_on` (`4`)
- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow -> `concept:tfim-benchmark-first-validation` Benchmark-first validation
- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow -> `concept:tfim-transverse-field-ising-model` TFIM benchmark substrate
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route -> `workflow:tfim-benchmark-workflow` TFIM benchmark workflow
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition -> `workflow:tfim-benchmark-workflow` TFIM benchmark workflow

### `uses_method` (`4`)
- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow -> `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route -> `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper
- `validation_pattern:tfim-small-system-gap-reproduction` TFIM small-system gap reproduction -> `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition -> `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper

### `warned_by` (`4`)
- `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim -> `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit
- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow -> `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route -> `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition -> `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit

### `supports` (`2`)
- `concept:tfim-benchmark-first-validation` Benchmark-first validation -> `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim
- `bridge:tfim-toy-model-code-method-bridge` TFIM toy-model to code-method bridge -> `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route

### `validated_by` (`1`)
- `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim -> `validation_pattern:tfim-small-system-gap-reproduction` TFIM small-system gap reproduction

## Consultation Anchors

### `l1_provisional_understanding`
- Available count: `6`
- `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim [[derived_navigation/claim_card--tfim-benchmark-before-portability-claim|Benchmark before portability claim]]
- `concept:tfim-benchmark-first-validation` Benchmark-first validation [[derived_navigation/concept--tfim-benchmark-first-validation|Benchmark-first validation]]
- `concept:tfim-transverse-field-ising-model` TFIM benchmark substrate [[derived_navigation/concept--tfim-transverse-field-ising-model|TFIM benchmark substrate]]
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition [[derived_navigation/physical_picture--tfim-weak-coupling-benchmark-intuition|TFIM weak-coupling benchmark intuition]]
- `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit [[derived_navigation/warning_note--tfim-dense-ed-finite-size-limit|Dense exact diagonalization finite-size limit]]
- `workflow:tfim-benchmark-workflow` TFIM benchmark workflow [[derived_navigation/workflow--tfim-benchmark-workflow|TFIM benchmark workflow]]

### `l3_candidate_formation`
- Available count: `7`
- `bridge:tfim-toy-model-code-method-bridge` TFIM toy-model to code-method bridge [[derived_navigation/bridge--tfim-toy-model-code-method-bridge|TFIM toy-model to code-method bridge]]
- `method:tfim-exact-diagonalization-helper` TFIM exact-diagonalization helper [[derived_navigation/method--tfim-exact-diagonalization-helper|TFIM exact-diagonalization helper]]
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition [[derived_navigation/physical_picture--tfim-weak-coupling-benchmark-intuition|TFIM weak-coupling benchmark intuition]]
- `proof_fragment:jones-codrestrict-comp-subtype-construction-recipe` Jones codRestrict + subtype composition construction recipe [[derived_navigation/proof_fragment--jones-codrestrict-comp-subtype-construction-recipe|Jones codRestrict + subtype composition construction recipe]]
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route [[derived_navigation/topic_skill_projection--tfim-benchmark-first-route|TFIM benchmark-first route]]
- `warning_note:tfim-dense-ed-finite-size-limit` Dense exact diagonalization finite-size limit [[derived_navigation/warning_note--tfim-dense-ed-finite-size-limit|Dense exact diagonalization finite-size limit]]

### `l4_adjudication`
- Available count: `8`
- `claim_card:tfim-benchmark-before-portability-claim` Benchmark before portability claim [[derived_navigation/claim_card--tfim-benchmark-before-portability-claim|Benchmark before portability claim]]
- `concept:tfim-benchmark-first-validation` Benchmark-first validation [[derived_navigation/concept--tfim-benchmark-first-validation|Benchmark-first validation]]
- `concept:tfim-transverse-field-ising-model` TFIM benchmark substrate [[derived_navigation/concept--tfim-transverse-field-ising-model|TFIM benchmark substrate]]
- `physical_picture:tfim-weak-coupling-benchmark-intuition` TFIM weak-coupling benchmark intuition [[derived_navigation/physical_picture--tfim-weak-coupling-benchmark-intuition|TFIM weak-coupling benchmark intuition]]
- `proof_fragment:jones-codrestrict-comp-subtype-construction-recipe` Jones codRestrict + subtype composition construction recipe [[derived_navigation/proof_fragment--jones-codrestrict-comp-subtype-construction-recipe|Jones codRestrict + subtype composition construction recipe]]
- `topic_skill_projection:tfim-benchmark-first-route` TFIM benchmark-first route [[derived_navigation/topic_skill_projection--tfim-benchmark-first-route|TFIM benchmark-first route]]

## Isolated Units

- `proof_fragment:jones-codrestrict-comp-subtype-construction-recipe` Jones codRestrict + subtype composition construction recipe [[derived_navigation/proof_fragment--jones-codrestrict-comp-subtype-construction-recipe|Jones codRestrict + subtype composition construction recipe]]
