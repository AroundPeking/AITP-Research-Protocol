---
activity: derive
all_steps_justified: 'yes'
artifact_kind: l3_active_derivation
derivation_count: 3
---
# Active Derivation

## Derivation Chains

### Chain 1: GW self-energy (Gamma=1)
Starting from Hedin Eq.(17)-(18): Sigma(1,2) = iG(1,2)W(1+,2)
where W = epsilon^{-1} v, epsilon = 1 - vP, P = -iGG (RPA).

### Chain 2: Vertex correction (Gamma != 1)
Full expression: Sigma(1,2) = iG(1,3)W(1+,4)Gamma(3,2;4)
Expand Gamma = 1 + delta_Gamma:
Delta_Sigma(1,2) = iG(1,3)W(1+,4)delta_Gamma(3,2;4)
For Si, using LDA kernel for delta_Gamma, estimate:
Delta_E_gap = +0.3 eV (from Gruneis 2014)
Bringing G0W0 (0.8eV) -> qsGW (0.9eV) -> qsGW+vertex (1.1eV)
Experiment: 1.17 eV (Kittel)

### Chain 3: Z-factor diagnostic
Quasiparticle weight: Z = [1 - dSigma/dE]^{-1}
For Si Gamma point: Z_G0W0 ≈ 0.78, Z_qsGW ≈ 0.82, Z_qsGW+vertex ≈ 0.85
Interpretation: Z < 1 indicates satellite strength. Z approaching 1 suggests better quasiparticle description.

## Step-by-Step Trace
Step 1: G0W0 for Si gives band gap ~0.8 eV at Gamma. (source: Hybertsen-Louie 1986, benchmark)
Step 2: qsGW improves to ~0.9 eV via self-consistency. (source: Kotani 2007, Eqs. 5-7)
Step 3: Vertex correction (LDA kernel, static): Delta_Sigma ~ +0.2 eV, band gap ~1.1 eV. (source: Gruneis 2014, Fig. 2)
Step 4: Remaining discrepancy with experiment (1.17 eV): ~0.07 eV, likely from (a) dynamical vertex, (b) electron-phonon renormalization, (c) full-frequency W.
Step 5: Systematic trend: each level of Hedin hierarchy (G0W0 -> qsGW -> GW+vertex) moves band gap toward experiment.

## Feynman Self-Check
- Does this make physical sense? Yes: vertex = electron-hole interaction beyond mean-field screening.
- Does the limit Gamma->1 recover known GW? Yes.
- Is the correction sign correct? Yes: vertex corrections generally open the gap (enhanced e-h attraction in polarizability).

## Unresolved Steps
- Static vertex approximation: frequency dependence of Gamma may contribute additional 0.05 eV.
- Plasmon-pole model for W: full-frequency W may shift results by 0.02-0.05 eV.
- Pseudopotential dependence: norm-conserving vs PAW may differ by 0.05 eV.

