---
artifact_kind: l4_review
candidate_id: cand-qsgw-vertex
check_results:
  conservation_check: 'pass: charge conservation maintained (GW is conserving in Baym-Kadanoff
    sense with Gamma=1; with vertex, conservation requires consistent Phi-derivable
    approximation)'
  correspondence_check: 'partial_pass: G0W0 for Si (0.8 eV) matches Hybertsen-Louie
    benchmark; qsGW result matches Kotani; vertex correction direction matches Gruneis
    but magnitude uncertainty ~0.05 eV'
  dimensional_consistency: 'pass: energy differences have correct energy dimensions'
  limiting_case_check: 'pass: Gamma=1 recovers standard qsGW, Si at large lattice
    constant recovers atomic limit'
  symmetry_compatibility: 'pass: band gap is scalar, Gamma point has full tetrahedral
    symmetry'
devils_advocate: 'LOAD-BEARING ASSUMPTION: The static LDA vertex kernel. If the dynamical
  (frequency-dependent) vertex contributes more than 0.1 eV, the entire quantitative
  claim about "0.2 eV improvement" is ambiguous — it could be 0.15 eV (static) or
  0.35 eV (static+dynamical).


  FALSIFICATION SCENARIO: Compute Si band gap with full-frequency W AND dynamical
  vertex (e.g., using Bethe-Salpeter equation or cumulant expansion). If the result
  is 1.17 eV (exact experiment match), the vertex correction is confirming experiment
  rather than predicting it. If the result is 1.25 eV, the vertex correction overshoots.


  UNTESTED REGIME: Only Si (diamond structure, sp3 bonding) is considered. Different
  bonding types (ionic: MgO, layered: MoS2, molecular: C60) may show different vertex
  sensitivity. The claim generalizes from one material.


  ALTERNATIVE EXPLANATION: The 0.2 eV improvement could be from (a) better description
  of screening in qsGW vs G0W0 (NOT from vertex), or (b) error cancellation between
  vertex and pseudopotential effects. Without turning off vertex while keeping other
  improvements, causation is not isolated.


  HIDDEN APPROXIMATION: Plasmon-pole model for W assumes single plasmon peak. Real
  materials (especially Si) have plasmon+particle-hole continuum structure that a
  single pole cannot capture. This is equivalent to assuming a specific form of vertex
  correction implicitly.'
l4_cycle: 1
outcome: partial_pass
reviewed_at: '2026-04-28T16:33:55+08:00'
stage: L4
verification_evidence:
  result:
    lhs_dimension: energy
    pass: true
    rhs_dimensions:
    - energy
    - energy
  tool: aitp_verify_dimensions
---
# Review: cand-qsgw-vertex

## Outcome
partial_pass

## Notes
The derivation correctly identifies the systematic trend: G0W0 -> qsGW -> qsGW+vertex moves band gap toward experiment. The claim of ~0.2 eV improvement from vertex is supported by Gruneis 2014. However, the claimed precision of 0.07 eV remaining discrepancy is not rigorously justified: pseudopotential dependence, k-point convergence, and frequency treatment each contribute O(0.05 eV) uncertainty.

## Devil's Advocate
LOAD-BEARING ASSUMPTION: The static LDA vertex kernel. If the dynamical (frequency-dependent) vertex contributes more than 0.1 eV, the entire quantitative claim about "0.2 eV improvement" is ambiguous — it could be 0.15 eV (static) or 0.35 eV (static+dynamical).

FALSIFICATION SCENARIO: Compute Si band gap with full-frequency W AND dynamical vertex (e.g., using Bethe-Salpeter equation or cumulant expansion). If the result is 1.17 eV (exact experiment match), the vertex correction is confirming experiment rather than predicting it. If the result is 1.25 eV, the vertex correction overshoots.

UNTESTED REGIME: Only Si (diamond structure, sp3 bonding) is considered. Different bonding types (ionic: MgO, layered: MoS2, molecular: C60) may show different vertex sensitivity. The claim generalizes from one material.

ALTERNATIVE EXPLANATION: The 0.2 eV improvement could be from (a) better description of screening in qsGW vs G0W0 (NOT from vertex), or (b) error cancellation between vertex and pseudopotential effects. Without turning off vertex while keeping other improvements, causation is not isolated.

HIDDEN APPROXIMATION: Plasmon-pole model for W assumes single plasmon peak. Real materials (especially Si) have plasmon+particle-hole continuum structure that a single pole cannot capture. This is equivalent to assuming a specific form of vertex correction implicitly.

## SymPy Verification Evidence
Tool: aitp_verify_dimensions

```
{'pass': True, 'lhs_dimension': 'energy', 'rhs_dimensions': ['energy', 'energy']}
```

## Check Results
- dimensional_consistency: pass: energy differences have correct energy dimensions
- symmetry_compatibility: pass: band gap is scalar, Gamma point has full tetrahedral symmetry
- limiting_case_check: pass: Gamma=1 recovers standard qsGW, Si at large lattice constant recovers atomic limit
- correspondence_check: partial_pass: G0W0 for Si (0.8 eV) matches Hybertsen-Louie benchmark; qsGW result matches Kotani; vertex correction direction matches Gruneis but magnitude uncertainty ~0.05 eV
- conservation_check: pass: charge conservation maintained (GW is conserving in Baym-Kadanoff sense with Gamma=1; with vertex, conservation requires consistent Phi-derivable approximation)

