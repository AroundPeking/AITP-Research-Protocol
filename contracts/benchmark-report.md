# Benchmark Report Contract

## Purpose

Record the validation results of a new feature against known benchmark
systems, including convergence tests and pass/fail verdict.

## Minimum fields

- `report_id`
- `feature`
- `target_version`
- `baseline_version`
- `test_systems`: list of objects, each with:
  - `name`
  - `system_type`: `molecule`, `solid`, or `2D`
  - `configuration`: parameter map
  - `results`: new_value, baseline_value, deviation, pass boolean
- `convergence_tests`: list of objects, each with:
  - `parameter`: e.g., `k_points`, `ecutwfc`, `abfs_radius`
  - `values`: list of tested values
  - `observed_convergence`: boolean
- `verdict`: `pass`, `partial`, `fail`, or `blocked`
- `ready_for_production`: boolean

## Why it matters

A new feature in a physics code is not trustworthy just because it compiles.
Benchmark reports provide the evidence chain from implementation to validated
physical correctness.
