# L1 vault protocol

Status: draft

This file defines the bounded three-layer vault used for `L1` topic
compilation.

## 1. Why this exists

`L1` already records source-backed intake through the active research question
contract and runtime status surfaces.

What was still missing was one explicit vault structure that separates:

- immutable raw inputs,
- human-browsable wiki compilation,
- and derived query products with explicit flowback.

The goal is to make `L1` easier to browse and resume without creating another
hidden truth surface.

## 2. Core stance

The `L1` vault is:

- compiled,
- topic-scoped,
- inspectable on disk,
- and explicitly non-authoritative.

It helps the operator and agent read the current intake state.
It does not replace:

- `source-layer` as the raw source truth,
- runtime control surfaces,
- or later `L2` promotion rules.

## 3. Three-layer layout

Each topic may materialize:

- `intake/topics/<topic_slug>/vault/raw/`
- `intake/topics/<topic_slug>/vault/wiki/`
- `intake/topics/<topic_slug>/vault/output/`

### Raw

The raw layer anchors immutable source inputs.

Rules:

- raw must point back to existing `source-layer` inputs
- raw may use manifests and pointers
- raw must not become a second writable knowledge copy

### Wiki

The wiki layer is the human-browsable compiled `L1` surface.

Rules:

- use lowercase filenames
- use frontmatter
- use Obsidian-compatible wikilinks
- keep page types and naming rules explicit in a local schema page

Typical page types:

- home page
- source intake page
- open questions page
- runtime bridge page

### Output

The output layer stores derived query products.

Rules:

- output is downstream of raw/wiki state
- output may highlight useful summaries, active read paths, and question-state
  digests
- output-to-wiki synchronization must be recorded explicitly through a
  flowback ledger

## 4. Flowback rule

Flowback is allowed only when the output layer writes an explicit receipt that
names:

- the source output artifact
- the target wiki page
- the reason for the sync
- and the applied status

Silent wiki rewrites without receipts are not acceptable.

## 5. Compatibility rule

The `L1` vault must preserve and link the existing runtime compatibility
surfaces:

- `runtime/topics/<topic_slug>/research_question.contract.json|md`
- `runtime/topics/<topic_slug>/control_note.md`
- `runtime/topics/<topic_slug>/operator_console.md`

The new vault may contextualize them.
It may not pretend they no longer exist.

## 6. Authority rule

The `L1` vault is not canonical `L2` memory.

It must not:

- bypass `L0` recovery,
- bypass `L4` validation,
- or silently promote compiled wiki notes into reusable `L2` truth.

## 7. One-line doctrine

`L1` vault surfaces should make provisional intake easier to read without
changing what counts as authoritative evidence.
