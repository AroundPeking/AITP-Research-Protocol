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

These families are the reusable semantic center for the M1 topic result brief and related canonical writeback surfaces.

## Immediate next extension family

The first extension family after the M1 freeze is:

- `negative_result`

It is intentionally seeded as the immediate next extension family, but it is not activated as required populated graph data in M1.

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
That means the node and edge families above are the declared Layer 2 MVP vocabulary, but M1 does not require seeded graph data, traversal infrastructure, or populated retrieval built around those families.

M2 activates seeded graph data, traversal, and populated retrieval on top of this frozen contract.
Until then, new work may reference the vocabulary, but it should not silently expand the contract without an explicit follow-on decision.
