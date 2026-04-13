# RUNBOOK-B: Toy Model Lane — Haldane-Shastry Quantum Chaos

## Topic
- **Slug:** `haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum`
- **Mode:** `toy_model`
- **Front door command:**
  ```
  python -c "from knowledge_hub.aitp_service import AITPService; AITPService().new_topic(
    topic='Haldane-Shastry Model Quantum Chaos and Lyapunov Spectrum',
    question='Investigate the onset of quantum chaos in the Haldane-Shastry spin chain.',
    mode='toy_model',
    human_request='Produce one bounded numeric result characterizing chaos in the HS model.'
  )"
  ```

## Bootstrap Result
- **Conformance audit:** pass (all checks)
- **Resume stage:** L3 (candidate_shaping)
- **Research mode:** toy_model
- **Next action:** L0 source expansion
- **Runtime root:** `research/knowledge-hub/runtime/topics/haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum/`

## Acceptance Infrastructure Gap
The `toy_model` mode currently has only smoke/profile acceptance. This lane
may surface gaps in the promotion infrastructure for toy-model numerics.
If the bounded loop cannot reach promotion readiness, the honest gap will be
recorded as evidence.

## Promotion Path
1. Register sources (Haldane 1988, Shastry 1988, chaos literature)
2. Advance L1 → L3 numerics (spectral form factor / OTOC computation)
3. Create candidate with bounded numeric result
4. Attempt promotion through standard pipeline
5. Document any mode-specific gaps

## Evidence Location
- `.planning/phases/170-positive-promotion-proof-lane/evidence/lane-b/`
