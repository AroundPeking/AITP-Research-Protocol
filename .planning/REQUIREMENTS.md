# Requirements: v1.66 PyPI Publishable Package

## Milestone Goal

Replace repo-clone plus editable-install onboarding with a versioned `pip
install aitp` path while preserving honest migration and contributor workflows.

## Active Requirements

### Packaging Contract

- [ ] `REQ-PKG-01`: the public distribution builds as `aitp` wheel and sdist
  artifacts rather than a repo-local `aitp-kernel` editable-install contract.
- [ ] `REQ-PKG-02`: package metadata, `aitp --version`, and install diagnostics
  expose one shared semver from a single source of truth.
- [ ] `REQ-PKG-03`: built distributions include the runtime assets needed for
  `aitp doctor`, `bootstrap`, and the shared first-run path outside a git
  checkout.

### Public Install And Migration

- [ ] `REQ-PUB-01`: a clean Python 3.10+ environment on Linux and Windows can
  `pip install aitp` and then run `aitp --version` plus `aitp doctor`.
- [ ] `REQ-PUB-02`: newcomer-facing docs and READMEs default to the PyPI
  install path, while editable install remains documented as a contributor /
  local-dev lane.
- [ ] `REQ-PUB-03`: the repository documents a repeatable release workflow for
  building and publishing versioned distributions.

### Verification

- [ ] `REQ-VERIFY-01`: the milestone closes with distribution build
  verification, clean-install smoke coverage, and regression coverage for
  migrated install diagnostics.

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-PKG-01 | Phase 131 | Pending |
| REQ-PKG-02 | Phase 131 | Pending |
| REQ-PKG-03 | Phase 131 | Pending |
| REQ-PUB-01 | Phase 132 | Pending |
| REQ-PUB-02 | Phase 132 | Pending |
| REQ-PUB-03 | Phase 132 | Pending |
| REQ-VERIFY-01 | Phase 133 | Pending |
