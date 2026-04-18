---
name: aitp-current-claims-auditor
description: Use when an AITP topic needs a clear statement of what is currently believed, what is only provisional, what is blocked, and what still needs work.
---

# AITP Current Claims Auditor

## Environment gate (mandatory first step)

- Read the current candidate ledger, derivation records, comparison receipts, and latest L3 synthesis before auditing claims.

## When to use

- The notebook needs a stable results section.
- It is unclear what the topic currently claims.
- A reader needs to know what is established versus merely suggestive.

## Workflow

For each current claim, record:

1. `Claim`
2. `Status`
3. `Support`
4. `Limitation`
5. `Next action`

## Hard rules

- Do not label a claim as stable if the comparison receipt still exposes a real caveat.
- Do not hide blocked claims by omitting them.
- Always distinguish source reconstruction, current working result, and rejected route.

