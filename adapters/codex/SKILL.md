---
name: aitp-runtime
description: Route substantial research work through the installed `aitp` CLI so Codex follows the AITP charter and protocol surface.
---

# AITP Runtime

## Required entry

1. Start topic work with `aitp bootstrap ...`, `aitp resume ...`, or `aitp loop ...`.
2. Read the generated `runtime_protocol.generated.md`, `agent_brief.md`,
   `operator_console.md`, and `conformance_report.md`.
3. Register reusable operations when needed.
4. For numerical or model-building topics, register a benchmark-validation operation before the first target-model claim and keep benchmark reproduction separate from target-model inference.
5. End with `aitp audit --topic-slug <topic_slug> --phase exit`.

## Runtime lanes and maturity

Treat AITP as serving three distinct research lanes rather than one uniform capability.

1. Toy-model numerics
- Current maturity: strongest lane. When a matching public or analytic benchmark exists, AITP can already support `benchmark -> target scan -> benchmark-driven recheck -> bounded conclusion`.

2. Formal theory and derivation
- Current maturity: active but not closed. AITP can organize derivation recovery, proof obligations, and semi-formal packets, but automated proof closure remains immature.

3. Code-backed algorithm development
- Current maturity: active but not closed. AITP can support bounded reproduction and implementation validation work, but it should not yet be described as a general turnkey replacement for sustained large-codebase research development.

## Hard rules

- If conformance fails, the run does not count as AITP work.
- Prefer durable control notes and contracts over hidden heuristics.
- Do not treat a new method as trusted before the relevant gates are satisfied.
- For a new numerical observable, the minimum trust gate is a benchmark in the same observable family whenever a finite-size public or analytic benchmark exists.
- Benchmark reproduction and target-model inference must be logged separately, even when one implementation produces both.
- If benchmark reproduction uncovers a definition mismatch, the earlier target-model result is demoted to exploratory until the corrected recheck is written back.
- When reporting status, name the active research lane and state whether that lane is currently end-to-end capable or still partial.
