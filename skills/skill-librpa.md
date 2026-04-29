---
name: skill-librpa
description: Domain skill for ABACUS+LibRPA topics. Injects workflow lanes, domain invariants, and concrete validation criteria. Protocol-level concerns (derive-first, externalized spec, execution environment, error classification) are handled by existing AITP skills — this file adds only LibRPA-specific knowledge.
trigger: domain == "abacus-librpa"
---

# ABACUS + LibRPA Domain Skill

Loaded when the topic's domain is `abacus-librpa`, detected via:
1. `contracts/domain-manifest.abacus-librpa.json` in the topic directory
2. `domains: [abacus-librpa]` in `state.md` frontmatter
3. Legacy slug-pattern fallback (slug contains "librpa", "crpa", etc.)

**This skill is additive.** AITP's protocol skills already handle:
- Derive-first discipline → `skill-l3-analyze.md` + Feature Development Playbook Gate G0
- Externalized spec → `EXTERNALIZED_SPEC_PROTOCOL.md`
- Execution environment → `skill-l3-plan.md` (MANDATORY for code_method lanes)
- Operation routing → domain manifest `operations` + `routing.intent_patterns`
- Error classification → domain manifest `skill_hooks.on_error_classify`
- Invariant checking at L4 → Feature Development Playbook Phase 4
- Devil's advocate → `skill-validate.md`

This file provides only what those generic mechanisms don't cover.

## Workflow Lanes

```
Molecule GW:      SCF -> LibRPA
Periodic GW:      SCF -> pyatb -> NSCF -> preprocess -> LibRPA
Periodic GW sym:  SCF(symmetry=1,rpa=1,no SOC) -> copy sidecars -> pyatb -> NSCF(symmetry=-1) -> preprocess -> LibRPA(symmetry flags)
RPA:              SCF -> LibRPA
```

## Domain Invariants

| Invariant | Check method |
|-----------|-------------|
| `shrink_consistency` | ABFS_ORBITAL files match `use_shrink_abfs` in `librpa.in` |
| `same_libri` | ABACUS and LibRPA compiled against same LibRI version |
| `keyword_compat` | No deprecated ABACUS keywords in INPUT |
| `smoke_first` | Minimal test passed before full calculation |
| `toolchain_consistency` | Build and runtime environments match |

When running L4 validation for a `code_method` lane topic, verify all 5 before submitting `outcome="pass"`.

## Target Codes

`abacus`, `librpa`, `libri`, `libcomm`, `pyatb`

## Smoke Test Criteria

Bulk Si 2×2×2, low ecutwfc. Must pass all stages:
SCF → DF → NSCF → LibRPA, with no NaN and `gw_band.dat` existing.

## Escape Hatches

- Domain manifest missing from project: clone from GitHub, copy into `contracts/`, register via `aitp_register_source`.
- `formal_theory` lane: L3/L4 computational requirements are advisory, not blocking.
- User says "skip domain checks": record the skip, mark validation as `partial_pass` (not `pass`).

## Hard Domain Rules

These rules are auto-injected into the execution brief for any topic with domain
`abacus-librpa` or `oh-my-librpa`. Violating them produces physically wrong results.

### When replace_w_head = t (head-wing enabled)

- `pyatb_librpa_df` MUST be generated on the full regular k-grid, NOT from IBZ or star-weights.
- Root `band_out`, `k_path_info`, `velocity_matrix`, and `KS_eigenvector_*.dat` must be
  consistent with the symmetry-sidecar view used by LibRPA.
- Never overwrite root files with full-BZ `pyatb_librpa_df/*` copies unless the user
  explicitly requests a root-level replacement and understands the symmetry mismatch risk.

### ABACUS INPUT Parameters

**SCF (periodic GW with shrink):**
- `rpa = 1`
- `symmetry = 1` (for symmetry lane; use `-1` for SOC)
- `out_mat_hs2 = 1` — output H and S matrices (needed by pyatb)
- `out_mat_r = 1` — output position matrix (needed by pyatb for velocity)
- `out_mat_xc = 1` — output Vxc matrix (needed by QSGW for non-diagonal elements)
- `out_chg = 1` — output charge density (needed by NSCF)
- `exx_pca_threshold = 10` — large-basis path (NOT `1e-3` legacy)
- `shrink_abfs_pca_thr = 1e-4`
- `shrink_lu_inv_thr = 1e-3`
- `exx_cs_inv_thr = 1e-5`
- `exx_separate_loop = 1`
- `exx_singularity_correction = massidda` (NOT `exx_use_ewald`)
- `rpa_ccp_rmesh_times = 6`
- `exx_ccp_rmesh_times = 3`
- `latname = user_defined_lattice` — explicit lattice vectors required

**NSCF (periodic GW band):**
- `calculation = nscf`
- `symmetry = -1` — REQUIRED even if SCF used `symmetry = 1`
- `init_chg = file`
- `out_mat_xc = 1` — Vxc matrix for QSGW
- `out_eband_terms = 1`
- `out_wfc_lcao = 1`
- `rpa = 1` is COMMENTED OUT in NSCF

**Molecule GW (short route):**
- No `out_chg`, no `out_mat_r`, no `out_mat_hs2`
- `exx_pca_threshold = 1e-6` (small-basis path)
- No pyatb, no NSCF
- `replace_w_head = f`

### QSGW vs G0W0 (librpa.in)

- G0W0 band: `task = g0w0_band`, no `max_iter`
- QSGW band mode-A: `task = qsgw_band0`, needs `max_iter = N`
- QSGW band mode-B: `task = qsgw_band`
- Molecular QSGW: `task = qsgw`
- Head+wing enabled: `option_dielect_func = 3`, `replace_w_head = t`

### librpa.in Default Presets

For periodic GW:
- `task = g0w0_band` (or `qsgw_band0` for QSGW)
- `nfreq = 16`
- `option_dielect_func = 3`
- `replace_w_head = t` (periodic) / `f` (molecule)
- `use_scalapack_gw_wc = t`
- `parallel_routing = libri`
- `vq_threshold = 0`
- `sqrt_coulomb_threshold = 0`
- `use_shrink_abfs = t`
- `use_abacus_exx_symmetry = t`
- `use_abacus_gw_symmetry = t`
- `use_fullcoul_exx = t`

### Smoke Test

- System: Bulk Si 2x2x2
- ecutwfc: low (50-100 Ry)
- Pipeline: SCF → pyatb → NSCF → preprocess → LibRPA
- Pass criteria: all stages complete, no NaN, `gw_band.dat` exists

## References

- oh-my-LibRPA: https://github.com/AroundPeking/oh-my-LibRPA
- Domain manifest: `registry/domain-manifest.abacus-librpa.json`
