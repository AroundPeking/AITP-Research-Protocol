# Candidate

`candidate` is the formal Layer 3 object used for `L3 -> L4` handoff.

Its purpose is to turn exploratory work into an explicit adjudication target.

## Required fields

Every candidate should provide:
- `candidate_id`
- `candidate_type`
- `title`
- `summary`
- `topic_slug`
- `run_id`
- `origin_refs`
- `question`
- `assumptions`
- `proposed_validation_route`
- `intended_l2_targets`
- `status`

## Semantic rules

### 1. Explicit adjudication target

The candidate must name what kind of Layer 2 object is expected if the candidate succeeds.

### 2. Origin trace

The candidate must link back to:
- source-bound intake material,
- the relevant research run,
- and any already-used canonical units.

### 3. Validation is proposed, not assumed

The candidate may suggest the validation route, but it is not yet a decision artifact.

### 4. Candidate is smaller than a run summary

Do not use the entire research log as the candidate.
The candidate should be the smallest adjudicable unit or unit bundle.

If a source-facing candidate is still too wide or mixes settled and unsettled
material, do not force it through promotion. Instead:
- split the reusable child candidates explicitly,
- park the unresolved remainder into the runtime deferred buffer,
- keep the split lineage durable on disk.

Use:
- `feedback/SPLIT_PROTOCOL.md`
- `feedback/schemas/candidate-split-contract.schema.json`

## Typical candidate types

- `concept`
- `definition_card`
- `notation_card`
- `equation_card`
- `assumption_card`
- `regime_card`
- `theorem_card`
- `claim_card`
- `proof_fragment`
- `derivation_step`
- `derivation_object`
- `method`
- `workflow`
- `bridge`
- `example_card`
- `caveat_card`
- `equivalence_map`
- `symbol_binding`
- `validation_pattern`
- `warning_note`

## Storage

Recommended storage:
- `feedback/topics/<topic_slug>/runs/<run_id>/candidate_ledger.jsonl`
- `feedback/topics/<topic_slug>/runs/<run_id>/candidate_split.contract.json`

Machine-readable schema:
- `feedback/schemas/candidate.schema.json`
- `feedback/schemas/candidate-split-contract.schema.json`
