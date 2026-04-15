# Phase 172.1 Target

## Promoted Positive Target

- **Fresh topic slug:** `hs-like-finite-size-chaos-window-core`
- **Fresh topic mode:** `toy_model`
- **Reference candidate id:** `candidate:hs-chaos-window-finite-size-core`
- **Reference candidate type:** `claim_card`
- **Authoritative target unit id:** `claim:hs-like-chaos-window-finite-size-core`
- **Canonical mirror path:** `canonical/claim-cards/claim_card--hs-like-chaos-window-finite-size-core.json`

## Human-Gated Promotion Route

- `request_promotion(...)`
- `approve_promotion(...)`
- `promote_candidate(...)`

All three steps must preserve the CLI-side actor fields:
`requested_by`, `approved_by`, `rejected_by`, `promoted_by`.

## Consultation Proof

- **Query text:** `HS-like finite-size chaos window robust core`
- **Expected canonical ids include:** `claim:hs-like-chaos-window-finite-size-core`

## Negative Comparator To Preserve

- **Comparator entry id:** `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`
- **Meaning:** exact HS `alpha = 2` remains a staged negative comparator, not
  part of the promoted positive unit
