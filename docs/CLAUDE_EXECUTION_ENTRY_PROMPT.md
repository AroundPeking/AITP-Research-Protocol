# AITP v2 Execution Entry Prompt For Claude

Copy everything below the line into Claude.

---

You are implementing the AITP v2 refactor in:

`D:\BaiduSyncdisk\repos\aitp-v2-refactor`

Your job is to execute the approved research-flow redesign **wave by wave**.
Do not redesign the architecture again unless you discover a contradiction with
the existing approved specs and plans.

## First, read these files in order

### Governing specs

1. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\AGENTS.md`
2. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\specs\2026-04-20-physicist-centered-l1-l5-research-flow-design.md`
3. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\specs\2026-04-20-l3-subplane-brain-gated-progressive-disclosure-design.md`

### Execution roadmap

4. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-physicist-centered-research-flow-roadmap.md`

### Wave plans, in this exact order

5. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-foundation-safety-hardening.md`
6. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-brain-l1-research-flow-wave1.md`
7. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-l3-subplanes-and-flow-tex.md`
8. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-knowledge-base-ingest-query-lint.md`
9. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-l4-l2-physics-adjudication-and-memory.md`
10. `D:\BaiduSyncdisk\repos\aitp-v2-refactor\docs\superpowers\plans\2026-04-20-l5-writing-and-real-topic-e2e.md`

## Core execution rules

1. Execute **one wave at a time**.
2. Do **not** skip ahead to a later wave before the current wave's verification
   gate passes.
3. Use TDD inside each task:
   - write failing test
   - run test and observe failure
   - implement minimal fix
   - rerun tests
4. Keep commits scoped to one wave or smaller coherent sub-slices.
5. Never overwrite unrelated local edits you did not make.
6. If the repo is dirty, inspect carefully and work around existing changes.
7. If a plan step conflicts with actual repo state, make the smallest honest
   adaptation and record it in your final note for that step.

## Hard architectural intent

You are **not** implementing a generic wiki.
You are implementing a physicist-centered layered research system.

Preserve these distinctions:

- `L0`: raw source substrate
- `L1`: source-grounded framing, question bounding, notation and convention lock
- `L3`: derivation / exploration notebook with hard subplanes
- `L4`: adjudication and validation
- `L2`: reusable promoted global memory
- `L5`: writing and communication

Preserve these authority boundaries:

- source-grounded != derived
- derived != validated
- validated != promoted
- query/writeback may not bypass `L2` promotion discipline

## Critical bugs that must be fixed early

These are already known and should be treated as priority items:

### P0

1. Path contract inconsistency:
   `brain/mcp_server.py` vs hooks disagree on whether topics live at
   `<topics_root>/<slug>` or `<topics_root>/topics/<slug>`.
2. Promotion gate bypass:
   agent must not be able to promote directly by mutating candidate status.
3. `topic_slug` path traversal:
   reject `..`, absolute paths, or multi-component unsafe slugs.

### P1

- `_infer_status` is incomplete and falls back too easily
- missing transition tools
- stop/session continuity writes are too broad
- file I/O is non-atomic
- `L2` promotion target is not normalized/global
- global `L2` needs version/conflict/merge receipts

### P2

- stale `aitp_get_popup` references
- repeated YAML parsing / duplicated `_SKILL_MAP` logic
- append-only derivation log scalability
- trust classification should move to `basis x scope`

## Knowledge-base operating model to preserve

Absorb the useful part of `LLM wiki` workflows, but only in AITP form:

- `raw sources` -> `L0`
- layered `wiki-like` human surfaces -> `L1/L3/L4/L2`
- `schema` -> Charter, SPEC, protocols, templates

Implement first-class:

- `ingest`
- `query`
- `lint`
- topic/global `index.md`
- topic/global `log.md`

But never collapse all layers into one undifferentiated wiki.

## TeX / notebook rule

This is especially important:

After **each completed research flow**, before paper writing, the system must
emit a TeX notebook in the spirit of the old `L3` flow output.

Expected path shape:

- `topics/<slug>/L3/tex/flow_notebook.tex`

This flow-end TeX is **not** the same thing as the final paper draft.
It is the research-flow archive and the main inspection surface for end-to-end
scientific coherence before `L5`.

## End-to-end acceptance rule

Real-topic E2E testing must use the flow-end TeX output as the main output
check.

At the end of the full program, run real-topic tests for at least:

- one `formal_theory` topic
- one `toy_numeric` topic
- one `code_method` topic

The E2E check should verify that the emitted TeX includes, at minimum:

- `Research Question`
- `Conventions And Regime`
- `Derivation Route`
- `Validation And Checks`
- `Current Claim Boundary`
- `Failures And Open Problems`

## How to proceed

1. Start with Wave 0:
   `2026-04-20-foundation-safety-hardening.md`
2. Implement it task by task.
3. Run its verification gate.
4. Summarize what changed and what still blocks the next wave.
5. Only then move to Wave 1.
6. Continue in roadmap order until all waves are complete.

## Expected working style

- Be conservative with architecture changes not already in spec.
- Be explicit when you make a local adaptation.
- Prefer small, reviewable diffs.
- Treat this as a protocol implementation project, not a free-form prototype.
- Review outputs from the perspective of a theoretical physicist:
  are regime, assumptions, notation, validation logic, and non-claims actually visible?

## Final instruction

Begin by reading the files listed above, summarize the execution order in 5-10
lines, inspect the current git status, and start implementing **Wave 0 only**.

