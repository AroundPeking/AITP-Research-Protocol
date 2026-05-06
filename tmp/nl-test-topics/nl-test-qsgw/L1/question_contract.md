---
artifact_kind: l1_question_contract
bounded_question: How do vertex corrections beyond the GW approximation systematically
  modify the quasi-particle band gap predicted by qsGW in moderately correlated materials?
competing_hypotheses: (a) Vertex corrections are small (<0.1eV) and qsGW is already
  sufficient; (b) Vertex corrections systematically increase band gaps toward experiment;
  (c) Vertex+self-consistency effects cancel, leaving qsGW unchanged; (d) Vertex corrections
  alone are insufficient, need DMFT-level local correlations
scope_boundaries: 'One-shot vertex corrections (Gamma != 1) to the self-energy within
  the GW framework. Does NOT consider: finite-temperature effects, spin-orbit coupling,
  magnetic ordering, or full self-consistent vertex corrections.'
stage: L1
target_quantities: Direct band gap at Gamma point (eV), quasi-particle weight Z, self-energy
  correction Delta_Sigma
---
# Question Contract

## Bounded Question
How do vertex corrections beyond the GW approximation systematically modify the quasi-particle band gap predicted by qsGW in moderately correlated materials?

## Competing Hypotheses
(a) Vertex corrections are small (<0.1eV) and qsGW is already sufficient.
(b) Vertex corrections systematically increase band gaps toward experiment.
(c) Vertex+self-consistency effects cancel, leaving qsGW unchanged.
(d) Vertex corrections alone are insufficient, need DMFT-level local correlations.

## Scope Boundaries
One-shot vertex corrections (Gamma != 1) to the self-energy within the GW framework. Does NOT consider: finite-temperature effects, spin-orbit coupling, magnetic ordering, or full self-consistent vertex corrections.

## Forbidden Proxies
Band gap from LDA/GGA as baseline. Eigenvalue self-consistency without vertex as comparison point.

## Target Quantities Or Claims
Direct band gap at Gamma point (eV), quasi-particle weight Z, self-energy correction Delta_Sigma.

## Deliverables
Validated claim about vertex correction magnitude for Si band gap.

## Acceptance Criteria
Numerical estimate of vertex correction to band gap within 0.1 eV.

## Non-Success Conditions
If vertex correction is smaller than 0.05 eV (within numerical noise), the claim of systematic improvement is falsified.

## Uncertainty Markers
Pseudopotential dependence, k-point convergence, plasmon-pole vs full-frequency treatment.

