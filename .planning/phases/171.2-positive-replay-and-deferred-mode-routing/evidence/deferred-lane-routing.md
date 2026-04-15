# Deferred Lane Routing: After v1.97

## Lane convergence

After `v1.97`, the roadmap should stay converged to these three directions:

1. `formal_theory` — now closed as the baseline positive-L2 proof
2. `toy_model` — user-requested `HS model` lane
3. `first_principles / code_method / large-codebase` — user-requested
   `LibRPA QSGW` lane

## Formal theory

### Status

- Baseline closed in `v1.97`
- Reference topic family: Jones / von Neumann algebras
- Trusted replay surfaces:
  - `run_formal_positive_l2_acceptance.py`
  - `run_positive_negative_l2_coexistence_acceptance.py`

### Next use

- Treat this lane as the authoritative L2 baseline for widening other modes.

## Toy model

### User-aligned target

- `HS model` quantum-chaos lane

### Honest current blocker

- `v1.96` only proved an honest negative-result route for the HS-model OTOC
  failure; it did not land a positive authoritative toy-model unit in `L2`.
- There is still no bounded positive target chosen for the HS lane that is
  distinct from the already-proven negative OTOC mismatch route.
- There is still no convergence/benchmark contract proving that the positive
  toy-model result is numerically trustworthy before promotion.

### Next bounded actions

1. Choose one bounded positive HS-model target that is promotion-worthy and
   honest at finite size.
2. Add a convergence/benchmark acceptance surface for that target before any
   L2 promotion claim.
3. Promote one positive toy-model unit into repo-local canonical `L2`, then
   rerun the coexistence pattern against the existing HS negative-result route.

## First principles / code-method / large codebase

### User-aligned target

- `LibRPA QSGW` large-codebase / first-principles lane

### Honest current blocker

- `v1.96` proved a front-door bootstrap for `first_principles`, but it did not
  close a positive authoritative `L2` landing.
- There is still no durable `first_principles -> code_method` mapping in L2
  that ties the computational result to codebase-backed method memory.
- There is still no bounded positive target chosen for the LibRPA/QSGW lane
  that can be promoted honestly before full workflow widening.

### Next bounded actions

1. Ingest the LibRPA / QSGW codebase into L2 as first-class method/workflow
   memory for the algorithm-development lane.
2. Choose one bounded positive result that couples the code-method surface and
   a real first-principles receipt.
3. Add an isolated acceptance lane that proves the codebase-backed
   first-principles route can land one authoritative unit in repo-local
   canonical `L2`.

## Recommended next milestone shape

- Start from the stronger L2 baseline now proved in `v1.97`.
- Widen next to:
  1. `toy_model` positive-L2 closure on `HS model`
  2. `first_principles / code_method` positive-L2 closure on `LibRPA QSGW`
