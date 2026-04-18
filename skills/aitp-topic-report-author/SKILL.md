---
name: aitp-topic-report-author
description: Use when an AITP topic should be compiled into a physicist-readable report with a clear scientific main text and appendix-style audit material.
---

# AITP Topic Report Author

## Environment gate (mandatory first step)

- Confirm the topic already has durable runtime and L3 surfaces.
- Read `research_report.active.md` when it exists; otherwise derive from the current runtime artifacts.

## When to use

- A topic needs a human-facing report.
- The notebook should read like a theoretical-physics research memo instead of a flat runtime log.
- Main results and appendices need clearer separation.

## Workflow

Arrange the main text in this order:

1. `Research question and background`
2. `Setup, notation, and regime`
3. `Working ideas and candidate routes`
4. `Iterative L3-L4 research record`
5. `Current claims and stable results`
6. `Consolidated derivation`
7. `Conclusion and open problems`

Move provenance maps, full catalogs, strategy memory, and full logs into appendices.

## Hard rules

- Main text should tell the scientific story first.
- Appendices should preserve the audit trail without overwhelming the report.
- Keep `what is established` separate from `what remains open`.

