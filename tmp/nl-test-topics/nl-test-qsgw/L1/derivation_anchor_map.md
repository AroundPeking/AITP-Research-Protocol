---
anchor_count: 3
artifact_kind: l1_derivation_anchor_map
stage: L1
starting_anchors: Hedin Eq.(18) Sigma=GW, Hedin Eq.(20) W Dyson, Kotani Eq.(5) qsGW
  condition
---
# Derivation Anchor Map

## Source Anchors
- Hedin Eq.(18): Sigma(1,2) = iG(1,2)W(1+,2)
- Hedin Eq.(20): W = v + vPW
- Kotani Eq.(5): qsGW self-consistency condition

## Dependency Graph
Hedin(18) -> Kotani(5) -> Vertex extension (Gamma != 1)

## Missing Steps
- Hedin pentagon to GW approximation
- Why Kotani qsGW condition is optimal
- Analytic structure of vertex corrections in HEG limit

## Candidate Starting Points
1. Hedin Eq.(18) expand Gamma around 1
2. Kotani Eq.(5) compute Delta_Sigma from delta_Gamma
3. Compare GW vs GW+vertex band gap for Si

