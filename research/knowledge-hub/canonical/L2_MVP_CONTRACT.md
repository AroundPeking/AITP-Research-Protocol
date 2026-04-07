# L2 MVP Contract

## Purpose

This document freezes the minimum Layer 2 semantic contract for M1.
Its job is to define the smallest reusable node and edge families that M1 may rely on across canonical storage, runtime summaries, and retrieval-facing docs without implying a wider graph ontology than the implementation currently supports.

## MVP node families

M1 freezes the following node families as the Layer 2 MVP surface:

- `concept`
- `theorem_card`
- `method`
- `assumption_card`
- `physical_picture`
- `warning_note`

Within the current contract sources, `concept`, `theorem_card`, `method`,
`assumption_card`, and `warning_note` are the active typed vocabulary already
represented by the current canonical-unit schema and Layer 2 typed-family docs.

`physical_picture` is RESERVED by the M1 contract and is NOT yet active in the
current canonical-unit schema or the current typed L2 vocabulary. M1 freezes it
as intended vocabulary only, so downstream docs can name the target shape
without claiming present-day canonical storage support.

## Immediate next extension family

The first extension family after the M1 freeze is:

- `negative_result`

`negative_result` is also RESERVED by the M1 contract as a next-extension /
deferred family. It is NOT yet active in the current canonical-unit schema or
the current typed L2 vocabulary, and it is not activated as required populated
graph data in M1.

## MVP edge families

M1 freezes the following edge families:

- `depends_on`
- `uses_method`
- `valid_under`
- `warns_about`
- `contradicts`
- `analogy_to`
- `derived_from_source`

These edge families are the minimum reusable relation set for semantically meaningful topic summaries and later graph traversal.

## Activation rule

M1 freezes the contract.
That means the node and edge families above are the declared intended Layer 2
MVP vocabulary, but M1 does not claim that every reserved family already has
current schema support, current object-family support, seeded graph data,
traversal infrastructure, or populated retrieval built around it.

M2 activates schema/object-family support plus seeded graph data, traversal,
and populated retrieval on top of this frozen contract.
Until then, new work may reference the frozen vocabulary, but it should not
silently expand the contract or imply current canonical storage support without
an explicit follow-on decision.
