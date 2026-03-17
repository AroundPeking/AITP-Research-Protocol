# Candidate Split Protocol

Use this protocol when one Layer 3 candidate is too wide, too mixed, or only
partly reusable.

Do not push a mixed candidate directly toward Layer 2 just because part of it is
good.

## Contract path

- `feedback/topics/<topic_slug>/runs/<run_id>/candidate_split.contract.json`

## Purpose

- declare which child candidates are ready to proceed,
- declare which fragments must be parked into the deferred runtime buffer,
- keep parent/child lineage durable instead of relying on prose-only notes.

## Minimal shape

```json
{
  "contract_version": 1,
  "policy_note": "Why the parent candidate must be split before promotion.",
  "splits": [
    {
      "source_candidate_id": "candidate:wide-parent",
      "reason": "The parent mixes a reusable definition with an unresolved caveat.",
      "child_candidates": [
        {
          "candidate_id": "candidate:narrow-definition",
          "candidate_type": "definition_card",
          "title": "Narrow Definition",
          "summary": "The reusable definition extracted from the parent.",
          "origin_refs": [],
          "question": "Can this bounded definition be promoted independently?",
          "assumptions": ["Keep the source-local scope explicit."],
          "proposed_validation_route": "bounded-smoke",
          "intended_l2_targets": ["definition:narrow-definition"]
        }
      ],
      "deferred_fragments": [
        {
          "entry_id": "deferred:wide-parent-caveat",
          "title": "Unresolved Caveat",
          "summary": "Park the caveat until a cited follow-up paper is ingested.",
          "reason": "The current source delegates the caveat to external literature.",
          "reactivation_conditions": {
            "source_ids_any": ["paper:followup-paper"]
          }
        }
      ]
    }
  ]
}
```

## Rules

- `source_candidate_id` must already exist in `candidate_ledger.jsonl`.
- `child_candidates` are the reusable parts that can continue through `L3 -> L4`.
- `deferred_fragments` are not promoted; they move into the runtime deferred
  buffer instead.
- If a deferred fragment includes `reactivation_candidate`, the runtime may
  reactivate it automatically once its declared conditions are satisfied.
- The runtime may mark the parent candidate as `split_into_children` or
  `deferred_buffered`, but the contract is still the source of truth for why the
  split happened.
