---
name: aitp-runtime
description: Route OpenCode through the AITP runtime so substantial research work stays auditable, resumable, and conformance-checked.
---

# AITP Runtime For OpenCode

## Required entry

1. In a bare `opencode` research session, do not start with direct browsing or free-form synthesis; enter through the installed `/aitp`, `/aitp-resume`, or `/aitp-loop` commands, or call `aitp bootstrap ...`, `aitp resume ...`, or `aitp loop ...` directly.
2. Read `runtime_protocol.generated.md` first, then follow `Must read now` before deeper work.
3. Expand deferred surfaces only when the named trigger in the runtime bundle fires.
4. Register reusable operations with `aitp operation-init ...`.
5. For human-reviewed `L2`, use `aitp request-promotion ...` and wait for `aitp approve-promotion ...`.
6. For theory-formal `L2_auto`, materialize coverage/consensus artifacts with `aitp coverage-audit ...` and then use `aitp auto-promote ...`.
7. End with `aitp audit --topic-slug <topic_slug> --phase exit`.

For numerical or model-building topics, insert an explicit benchmark phase before the first target-model claim:

8. Register a benchmark-validation operation before the first target-model scan.
9. Keep benchmark reproduction and target-model inference as separate operations even when they reuse the same code path.
10. If the benchmark forces a convention change, queue a benchmark-driven recheck before treating the earlier target-model result as trusted again.

## Installed command surfaces

- `/aitp` — enter the AITP runtime for a new or existing research task
- `/aitp-resume` — resume an existing topic from the installed `aitp` CLI
- `/aitp-loop` — run the safe AITP auto-continue loop for an active topic
- `/aitp-audit` — refresh conformance on exit

If the command bundle is unavailable, call the raw `aitp` CLI directly.

## Runtime lanes and maturity

Treat AITP as serving three distinct research lanes rather than one uniform capability.

1. Toy-model numerics
- Current maturity: strongest lane. When a matching public or analytic benchmark exists, AITP can already support `benchmark -> target scan -> benchmark-driven recheck -> bounded conclusion`.

2. Formal theory and derivation
- Current maturity: active but not closed. AITP can organize derivation recovery, proof obligations, and semi-formal packets, but automated proof closure remains immature.

3. Code-backed algorithm development
- Current maturity: active but not closed. AITP can support bounded reproduction and implementation validation work, but it should not yet be described as a general turnkey replacement for sustained large-codebase research development.

## Hard rules

- If the conformance audit fails, the run does not count as AITP work.
- If the task is theoretical-physics research rather than plain coding, staying inside AITP is mandatory.
- Prefer durable control notes and contract files over hidden heuristics.
- Every reusable operation must pass through `aitp trust-audit ...` before AITP treats it as trusted.
- If a new numerical backend or diagnostic is being trusted, scaffold a baseline first with `aitp baseline ...`.
- For a new numerical observable, the minimum trust gate is a benchmark in the same observable family whenever a finite-size public or analytic benchmark exists.
- Benchmark reproduction and target-model inference must be logged separately, even when one implementation produces both.
- If benchmark reproduction uncovers a definition mismatch, the earlier target-model result is demoted to exploratory until the corrected recheck is written back.
- If a derivation-heavy method is being claimed as understood, scaffold atomic understanding first with `aitp atomize ...`.
- If there is a capability gap, prefer `aitp loop ... --skill-query ...` so discovery becomes runtime state instead of ad hoc browsing.
- Human-reviewed Layer 2 promotion is blocked until `promotion_gate.json` says `approved` and `aitp promote ...` records the writeback.
- Theory-formal `L2_auto` promotion is blocked until `coverage_ledger.json` passes and `agent_consensus.json` is ready.
- When reporting status, name the active research lane and state whether that lane is currently end-to-end capable or still partial.

## Common commands

```bash
aitp loop --topic-slug <topic_slug> --human-request "<task>" --skill-query "<capability gap>"
aitp resume --topic-slug <topic_slug> --human-request "<task>"
aitp coverage-audit --topic-slug <topic_slug> --candidate-id <candidate_id> --source-section <section> --covered-section <section>
aitp request-promotion --topic-slug <topic_slug> --candidate-id <candidate_id> --backend-id backend:theoretical-physics-knowledge-network
aitp approve-promotion --topic-slug <topic_slug> --candidate-id <candidate_id>
aitp promote --topic-slug <topic_slug> --candidate-id <candidate_id> --target-backend-root <tpkn_root>
aitp auto-promote --topic-slug <topic_slug> --candidate-id <candidate_id> --target-backend-root <tpkn_root>
aitp operation-init --topic-slug <topic_slug> --run-id <run_id> --title "<operation>" --kind numerical
aitp operation-update --topic-slug <topic_slug> --run-id <run_id> --operation "<operation>" --baseline-status passed
aitp trust-audit --topic-slug <topic_slug> --run-id <run_id>
aitp capability-audit --topic-slug <topic_slug>
aitp audit --topic-slug <topic_slug> --phase exit
aitp baseline --topic-slug <topic_slug> --run-id <run_id> --title "<baseline title>" --reference "<source>" --agreement-criterion "<criterion>"
aitp atomize --topic-slug <topic_slug> --run-id <run_id> --method-title "<method title>"
```

Kernel root default: determined by the installed AITP runtime.
