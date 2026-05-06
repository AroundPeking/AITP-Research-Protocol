---
activity: gap-audit
artifact_kind: l3_active_gaps
blocking_gaps: none
gap_count: 5
---
# Active Gap Audit

## Unstated Assumptions
- (severity: important) GW assumes Gamma=1, which neglects ALL vertex corrections simultaneously. This is never formally justified beyond "perturbation theory suggests Gamma=1+O(r_s)".
- (severity: minor) qsGW assumes the quasiparticle picture is valid (well-defined peaks in spectral function). For Z<0.7, this breaks down.
- (severity: minor) Plane-wave basis assumes perfect crystals. Defect physics would break this.

## Approximation Regimes
- GW (Gamma=1): Valid for r_s < ~4 (moderate density). Breaks down for low-density (r_s > 5) where vertex corrections become O(1).
- qsGW self-consistency: Converges to a fixed point. No formal proof of uniqueness. Multiple solutions possible for strongly correlated cases.
- Static vertex (LDA kernel): Assumes frequency-independent vertex. Misses dynamical screening effects in vertex.

## Correspondence Check
- GW should reduce to Hartree-Fock in the static limit (W -> v). CHECK: Yes, Sigma = iGv is the HF exchange.
- qsGW should reduce to G0W0 for first iteration. CHECK: Yes, first iteration uses G0, W0 from DFT.
- GW+vertex should reduce to GW when Gamma=1. CHECK: Yes, by construction.
- qsGW band gap should approach experimental value for simple semiconductors. STATUS: G0W0 is close (~0.8eV for Si), qsGW improves slightly, GW+vertex closer to experiment (1.17eV).

## Prerequisite Gaps
- (severity: important) L2 missing: analytic proof that Gamma=1 is the leading approximation. Needs: diagrammatic analysis of vertex function in HEG.
- (severity: minor) L2 missing: numerical benchmark dataset for vertex corrections across materials.

## Severity Assessment
| Gap | Severity | Blocks? | Resolution |
|Gamma=1 justification gap | important | no | Flag as open question, document known O(r_s) expansion |
|qsGW uniqueness | minor | no | Practical convergence is sufficient for Si |
|Static vertex frequency | minor | no | Known limitation, small effect for Si |
|Analytic Gamma proof in L2 | important | no | Defer to L2 enrichment |
|Vertex benchmark dataset in L2 | minor | no | Defer |

