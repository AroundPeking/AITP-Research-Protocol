# RUNBOOK-C: Code Method Lane — LibRPA QSGW Convergence Verification

## Topic
- **Slug:** `librpa-qsgw-convergence-verification-for-h2o-tight-basis`
- **Mode:** `first_principles` (grouped with `toy_model` in `semantic_routing.py`)
- **Front door command:**
  ```
  python -c "from knowledge_hub.aitp_service import AITPService; AITPService().new_topic(
    topic='LibRPA QSGW Convergence Verification for H2O Tight Basis',
    question='Verify the numerical convergence of LibRPA QSGW self-energy iterations for H2O.',
    mode='first_principles',
    human_request='Produce one bounded convergence verification result.'
  )"
  ```

## Bootstrap Result
- **Conformance audit:** pass (all checks)
- **Resume stage:** L3 (candidate_shaping)
- **Research mode:** first_principles
- **Next action:** L0 source expansion
- **Runtime root:** `research/knowledge-hub/runtime/topics/librpa-qsgw-convergence-verification-for-h2o-tight-basis/`

## Mode Mapping Note
LibRPA QSGW was user-specified as "大型代码库" (large codebase). The semantic
router maps `first_principles` together with `toy_model` for validation mode
selection. The existing `run_tfim_benchmark_code_method_acceptance.py` and
`run_scrpa_control_plane_acceptance.py` provide code-method acceptance coverage.
The runtime_projection_handler returns `code_method` for relevant projections.

This topic tests whether the `first_principles` front-door path can reach L2
promotion through the existing code-method acceptance infrastructure.

## Promotion Path
1. Register sources (LibRPA documentation, QSGW methodology papers)
2. Advance L1 → L3 (convergence verification workflow)
3. Create candidate with bounded convergence result
4. Attempt promotion through standard pipeline
5. Document mode mapping and any gaps

## Evidence Location
- `.planning/phases/170-positive-promotion-proof-lane/evidence/lane-c/`
