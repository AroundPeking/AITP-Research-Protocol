# Cross-Lane Readiness Report: v2.0 Real-Topic Natural-Language Dialogue E2E

## Scope

This report compares the three user-requested research directions after the
real natural-language dialogue proofs completed in milestone `v2.0`.

## Comparative table

| Lane | Fresh dialogue topic | Authoritative L2 unit | Steering artifacts preserved | Honest current boundary | Next widening decision |
|------|----------------------|-----------------------|------------------------------|-------------------------|------------------------|
| Formal theory | `Fresh Jones finite-dimensional factor closure` | `theorem:jones-ch4-finite-product` | `interaction_state.json`, `research_question.contract.json` | bounded to one already-proved Jones / von Neumann algebra theorem; formal closure path still uses an isolated-kernel workaround | widen only after removing the formal audit workaround and proving a second bounded theorem route |
| Toy model numerical + derivation | `Fresh HS-like chaos-window finite-size core` | `claim:hs-like-chaos-window-finite-size-core` | `interaction_state.json`, `research_question.contract.json` | bounded to the robust finite-size `0.4 <= alpha <= 1.0` core; weak shoulder and exact HS comparator remain excluded | widen only after a new benchmark or continuation contract justifies larger-system or broader-regime claims |
| Large codebase / first-principles / algorithm development | `Fresh LibRPA QSGW deterministic-reduction consistency core` | `claim:librpa-qsgw-deterministic-reduction-consistency-core` | `interaction_state.json`, `research_question.contract.json` | bounded to deterministic-reduction thread consistency on `H2O/really_tight iter=10`; broader convergence and whole-stack claims remain excluded | widen only after a bounded convergence proof beyond thread consistency is landed honestly |

## Hidden-seed assessment

- Removed across all three lanes:
  - each proof starts from a fresh topic slug
  - each proof preserves a fresh natural-language request on runtime steering artifacts
  - each proof lands on the same authoritative `L2` unit as its already-closed bounded baseline
- Remaining environment-specific assumptions:
  - the formal lane still needs an isolated-kernel workaround around the Jones closure path
  - the first-principles lane still depends on real local codebase and workflow-anchor artifacts being present on disk
  - the toy-model lane is the cleanest mechanically, but it is still intentionally bounded to the finite-size positive core

## Readiness conclusion

- Formal lane: ready for bounded real-dialogue entry proof, not ready for broad formalization claims
- Toy lane: ready for bounded real-dialogue entry proof, not ready for thermodynamic or larger-system widening
- First-principles lane: ready for bounded real-dialogue entry proof, not ready for full convergence or whole-stack deployment claims

## Explicit next routing

1. Route any formal widening work to a bounded follow-up milestone that first removes the isolated-kernel workaround and proves another formal unit without hidden scaffolding.
2. Route any toy-model widening work to a bounded benchmark milestone focused on continuation beyond the finite-size HS-like core.
3. Route any first-principles widening work to a bounded convergence milestone that proves more than deterministic-reduction thread consistency.
