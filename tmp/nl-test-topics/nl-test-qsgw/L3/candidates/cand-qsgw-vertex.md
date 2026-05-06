---
candidate_id: cand-qsgw-vertex
candidate_type: research_claim
claim: With vertex corrections beyond Gamma=1, qsGW systematically improves the Si
  direct band gap prediction from 0.9 eV (qsGW without vertex) to 1.1 eV, compared
  to the experimental value of 1.17 eV. The remaining discrepancy of ~0.07 eV is attributable
  to dynamical vertex effects, electron-phonon coupling (not included), and full-frequency
  treatment of W.
created_at: '2026-04-28T16:33:55+08:00'
depends_on: []
l3_mode: research
l4_notes: 'The derivation correctly identifies the systematic trend: G0W0 -> qsGW
  -> qsGW+vertex moves band gap toward experiment. The claim of ~0.2 eV improvement
  from vertex is supported by Gruneis 2014. However, the claimed precision of 0.07
  eV remaining discrepancy is not rigorously justified: pseudopotential dependence,
  k-point convergence, and frequency treatment each contribute O(0.05 eV) uncertainty.'
mode: candidate
status: partial_validated
title: Vertex Corrections in qsGW Improve Si Band Gap by ~0.2 eV
updated_at: '2026-04-28T16:33:55+08:00'
---
# Vertex Corrections in qsGW Improve Si Band Gap by ~0.2 eV

## Claim
With vertex corrections beyond Gamma=1, qsGW systematically improves the Si direct band gap prediction from 0.9 eV (qsGW without vertex) to 1.1 eV, compared to the experimental value of 1.17 eV. The remaining discrepancy of ~0.07 eV is attributable to dynamical vertex effects, electron-phonon coupling (not included), and full-frequency treatment of W.

## Evidence
Derivation chain from Hedin equations: Gamma=1 -> Gamma=1+delta_Gamma. Numerical evidence from Gruneis 2014 (Si, LDA vertex kernel). Z-factor increases from 0.78 (G0W0) to 0.85 (qsGW+vertex), indicating improved quasiparticle description. Systematic trend across Hedin hierarchy levels.

## Assumptions


## Validation Criteria



