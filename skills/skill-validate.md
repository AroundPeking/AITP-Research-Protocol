---
name: skill-validate
description: Validate mode — check candidates against evidence and known results.
trigger: status == "candidate_ready"
---

# Validate Mode

You are in **validate** mode. Your job: verify candidates against their declared
validation criteria.

## What to Do

1. **Read the candidate** from `L3/candidates/<id>.md`. Note its:
   - Claim
   - Evidence provided
   - Assumptions
   - Validation criteria

2. **Run validation checks** appropriate to the candidate:

   ### Numerical Validation
   - Run benchmark comparisons if applicable
   - Check convergence (parameter sweeps, finite-size scaling)
   - Verify error budgets are within tolerance
   - Record results in a Python script or notebook

   ### Analytical Validation
   - Check limiting cases: do formulas reduce correctly?
   - Dimensional analysis: do equations have correct dimensions?
   - Symmetry checks: do results respect declared symmetries?
   - Self-consistency: are different parts of the derivation compatible?

   ### Comparison Validation
   - Compare candidate against known L2 results
   - If contradiction found, record it explicitly

3. **Write a validation review** at `L4/reviews/<candidate-id>.md`:

   ```markdown
   ---
   candidate_id: level-spacing-wigner
   reviewer: ai_agent
   status: pass
   reviewed: 2026-04-19
   ---

   # Validation Review: Level Spacing Distribution

   ## Checks Performed
   - [x] Limiting case: reduces to Poisson in integrable limit
   - [x] Dimensional analysis: dimensionless ratio
   - [x] Numerical comparison: chi-squared test vs GOE

   ## Results
   [Detailed findings]

   ## Gaps Remaining
   - [Any unresolved issues]
   ```

4. **Update candidate status** based on results:
   - If passed: read the candidate .md, update frontmatter `status: validated`
   - If failed: update `status: revision_needed`, explain what needs fixing
   - If stuck: update `status: blocked`, explain what is missing

5. **If candidate passes**, update topic status:
   ```
   aitp_update_status(topics_root, topic_slug, status="validated")
   ```

## Rules

- **L4 does NOT write to L2 directly.** All results return through L3-R.
- Do not weaken validation criteria to make a candidate pass.
- Record what was checked, how, and what passed/failed.
- If you cannot complete validation (missing capability/source), record it honestly.
  Do not fake closure.

## Validation Outcomes

| Outcome | Meaning | Next Step |
|---------|---------|-----------|
| `pass` | All criteria met | Route to promotion |
| `partial_pass` | Some criteria met | Determine if partial result is useful |
| `fail` | Criteria not met | Return to L3 for revision |
| `contradiction` | Contradicts known results | Open gap, investigate |
| `blocked` | Cannot complete | Record blocker, escalate if needed |
