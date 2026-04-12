# Development Task Contract

## Purpose

Define a feature development task for ABACUS, LibRPA, LibRI, or related tools,
including code location, build configuration, and validation criteria.

## Minimum fields

- `task_id`
- `target`: `abacus`, `librpa`, `libri`, or `other`
- `feature_description`
- `motivation`
- `code_location`:
  - `repo`
  - `branch`
  - `key_files`
  - `depends_on`: list of dependency objects (name, version_constraint)
- `build_config`:
  - `cmake_profile`
  - `toolchain`: e.g., `mpiicpx`, `gcc`
  - `dependency_paths`: map of dependency name to path
- `validation`:
  - `unit_tests`
  - `integration_tests`
  - `physical_correctness`: benchmark_system, expected_result, tolerance
  - `regression_against`: baseline version or result reference

## Why it matters

Feature development in scientific software couples code changes to physical
correctness. Without explicit validation criteria, a feature can compile and
pass unit tests while producing wrong physics results.
