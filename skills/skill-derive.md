---
name: skill-derive
description: Derive mode — perform derivations, form candidates, iterate.
trigger: status == "intake_done"
---

# Derive Mode

You are in **derive** mode. Your job: perform structured derivations and form
candidate findings.

## What to Do

1. **Start a derivation** by calling:
   ```
   aitp_record_derivation(
     topics_root, topic_slug,
     derivation_id="d1-reconstruct-hamiltonian",
     kind="source_reconstruction",
     title="Reconstruct H-S Hamiltonian from source",
     source="hs-1988",
     content="Step-by-step reconstruction..."
   )
   ```

2. **Derivation types** (use the appropriate `kind`):
   - `source_reconstruction` — reproduce a result from a source
   - `cross_source_reconstruction` — combine results from multiple sources
   - `candidate_derivation` — derive a new or novel result
   - `failed_attempt` — record a failed approach (do not hide failures)
   - `notation_resolution` — resolve notation conflicts between sources

3. **Record every step**. Each derivation step should include:
   - What you started from (source, previous step)
   - What transformation you applied
   - What you obtained
   - Any assumptions made

4. **When a derivation produces a finding**, form a candidate:
   ```
   aitp_submit_candidate(
     topics_root, topic_slug,
     candidate_id="level-spacing-wigner",
     title="Level spacing follows Wigner-Dyson distribution",
     claim="In the chaotic window, the level spacing distribution...",
     evidence="Numerical data from derivation d3, analytical argument from d2",
     assumptions="Thermalization assumption, finite-size extrapolation",
     validation_criteria="Compare with GOE prediction, check convergence"
   )
   ```

5. **When a candidate is submitted**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="candidate_ready")
   ```

## Rules

- Record **failed attempts**. A negative result is still a result.
- Do not skip steps. If you jump from step 3 to step 7, record why.
- Each candidate must state its claim, evidence, assumptions, and validation criteria.
- Do not claim more than the evidence supports.
- If you need more sources, go back to explore mode (record why in derivations).

## Mode Awareness

- In `learn` mode: focus on `source_reconstruction` and `cross_source_reconstruction`.
  Verify known results before pursuing new ideas.
- In `implement` mode: focus on `candidate_derivation`. Pursue new ideas with
  full L3-I → L3-P → L3-A pipeline.

## When to Transition

Transition to **validate** (skill-validate) when:
- At least one candidate is submitted with clear validation criteria.

Ask the human: "I have a candidate: [title]. Should I proceed to validate it?"
