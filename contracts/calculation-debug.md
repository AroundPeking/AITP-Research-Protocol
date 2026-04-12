# Calculation Debug Contract

## Purpose

Record the diagnosis and fix of a failed first-principles computation,
capturing error classification, root cause, and learned knowledge for future
reuse.

## Minimum fields

- `debug_id`
- `original_workflow_id`
- `failure_stage`: `scf`, `df`, `nscf`, `librpa`, or `postprocess`
- `error_classification`:
  - `category`: `convergence`, `numerical`, `input`, `build`,
    `shrink_mismatch`, `keyword_deprecated`, or `other`
  - `error_log_excerpt`
  - `root_cause`
- `fix_actions`: list of objects, each with:
  - `action`: description
  - `target`: `input_patch`, `rebuild`, `parameter_change`, or `code_fix`
  - `details`
- `verification`:
  - `re_run_status`: `pending`, `passed`, or `still_failing`
  - `smoke_test_passed`: boolean
- `learned_knowledge`: string — to be promoted to L2 as experience knowledge
  card

## Why it matters

Debug knowledge is the most frequently lost asset in computational physics.
Recording error patterns and fixes creates reusable experience that accelerates
future debugging and prevents repeated mistakes.
