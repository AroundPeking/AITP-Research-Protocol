# Computation Workflow Contract

## Purpose

Define the stages, status, and invariants of a first-principles computation
chain (GW or RPA) from structure input through LibRPA output.

## Minimum fields

- `workflow_id`
- `computation_type`: `gw` or `rpa`
- `system_type`: `molecule`, `solid`, or `2D`
- `structure_file`
- `stages`: ordered list of stage objects, each with:
  - `name`: `scf`, `df`, `nscf`, or `librpa`
  - `status`: `pending`, `running`, `passed`, `failed`
  - `input_files`
  - `output_artifacts`
  - `depends_on`: list of upstream stage names
  - `validation`: list of boolean checks
- `basis_integrity`: pseudopotential, NAO orbital, and ABFS orbital file lists
  plus `shrink_invariant` boolean
- `compute`: location (local/server), server alias, MPI configuration

## Stage-specific validations

- `scf`: convergence_reached, energy_change_below_threshold
- `df`: coulomb_matrices_exist, shrink_consistency
- `nscf` (GW only): band_structure_readable
- `librpa`: gw_band_output_exists (GW) or rpa_converged (RPA)

## Why it matters

GW/RPA computations involve chained dependent stages where each stage's output
feeds the next. Without explicit stage tracking, failures propagate silently
and diagnosis becomes guesswork.
