# Focused Review: 4 P0/P1 Issues — Fix Proposals

## Issue 1: Domain Slug Fallback Over-Matching

### Location
- `brain/state_model.py:42-48` — `_SLUG_FALLBACK_PATTERNS`
- `brain/state_model.py:136-141` — legacy slug fallback logic in `resolve_domain_prerequisites`

### Impact
Slug `"nl-test-qsgw"` contains the substring `"qsgw"`, which matches the pattern at line 46 (`"qsgw": "skill-librpa"`). This causes **any topic whose slug happens to contain "qsgw"** to be bound to `skill-librpa`, even if the topic is about the general qsGW method rather than the LibRPA implementation. The fallback uses bare `in` substring matching (`pattern in slug_lower`), so partial matches like `qsgw` inside `test-qsgw-convergence` also trigger.

The priority chain (contracts → state → slug fallback) means this only fires when no domain manifest exists, but that is exactly the case for newly created topics before the agent has written a manifest.

### Fix Proposal

**Option A — Word-boundary matching (recommended)**

Replace the bare `in` check with a regex word-boundary match. This prevents `"qsgw"` from matching inside compound words while still matching standalone segments:

```python
# In resolve_domain_prerequisites, lines 137-141:
if not skills and topic_slug:
    slug_lower = topic_slug.lower()
    for pattern, skill in _SLUG_FALLBACK_PATTERNS.items():
        if re.search(rf'(?<![a-z]){re.escape(pattern)}(?![a-z])', slug_lower):
            if skill not in skills:
                skills.append(skill)
```

The negative lookbehind/lookahead `(?<![a-z])...(?![a-z])` matches when the pattern is bordered by non-letter characters (hyphens, underscores, start/end of string). `"qsgw"` still matches `"my-qsgw-topic"` but not `"test-qsgwlike-bla"`.

**Option B — Prefix gate for generic terms**

Move `qsgw` out of `_SLUG_FALLBACK_PATTERNS` entirely. Add it to `DOMAIN_ID_TO_SKILL` as `"qsgw": "skill-librpa"` and require a domain manifest to activate it. This is cleaner but breaks topics created before the manifest system that relied on slug matching.

### Risk
- **Option A**: Low risk. Existing topics with clean slug segments (`"librpa-test"`, `"crpa-verification"`) continue to match. Only compound-word false positives are eliminated. `re` is already imported at file top.
- **Option B**: Medium risk. Any pre-existing topic whose slug contains `"qsgw"` but lacks a domain manifest will silently lose its skill binding.

---

## Issue 2: `_QUESTION_STEMS` Missing Research Verbs

### Location
- `brain/state_model.py:484-488` — `_QUESTION_STEMS` list
- `brain/state_model.py:491-550` — `_check_question_semantic_validity`

### Impact
The current 14 stems omit common research verbs: `verify`, `test`, `examine`, `investigate`, `show`, `demonstrate`, `characterize`, `measure`, `simulate`, `model`. Questions like `"Verify that the quasiparticle weight Z ≈ 0.9 for this system"` fail the stem check, producing a false-negative validation error. The agent must rephrase, wasting a clarification round.

### Fix Proposal

**Option A — Extend the list (recommended)**

Add the missing verbs directly:

```python
_QUESTION_STEMS = [
    "what", "how does", "why", "under what conditions",
    "derive", "compute", "estimate", "prove", "calculate",
    "determine", "predict", "explain", "compare", "evaluate",
    "verify", "test", "examine", "investigate",
    "show", "demonstrate", "characterize",
    "measure", "simulate", "model", "analyze",
    "is it true", "does", "can",
]
```

Pro: zero added complexity, deterministic matching, easy to audit. Con: list grows over time; each new verb needs a code change.

**Option B — Semantic matching via embedding similarity**

Replace substring matching with a small embedding model that checks if the question opening is semantically close to "asking a research question." Pro: handles paraphrases. Con: adds a model dependency, non-deterministic, much harder to debug when a question is incorrectly rejected. Overkill for a validation gate.

**Option C — Regex on imperative verb form**

Instead of substring matching, parse the first word of the question and check if it's an imperative verb in a curated set. Pro: handles any verb conjugation. Con: English imperative detection is non-trivial; false negatives on questions starting with auxiliary verbs ("Can we...", "Does the...").

### Risk
- **Option A**: Minimal. The matching logic at line 506 (`any(stem in question for stem in _QUESTION_STEMS)`) is pure substring containment — adding more stems cannot break existing matches, only reduce false negatives. The only risk is stems that match unintended substrings (e.g., `"is"` inside `"this"`), but short stems like `"is"` should be checked as `question.startswith(stem)` or with word-boundary logic.
- For safety, add a length gate: stems shorter than 3 characters should be matched at word start only.

---

## Issue 3: SymPy Dimension System — Half-Integer Dimensions

### Location
- `brain/sympy_verify.py:22-73` — `_DIMENSION_MAP` (tuple of `int`)
- `brain/sympy_verify.py:60` — `wavefunction` entry with comment `"dim L^{-d/2}: half-int not representable; 1D approximation"`
- `brain/sympy_verify.py:389` — `total[i] += int(dim[i] * exp_val)` — the `int()` cast truncates fractional results

### Root Cause Analysis

The dimension system uses `tuple[int, int, int, int, int]` for 5 base dimensions. Every entry is integer exponents. This is fundamentally correct for most classical quantities but breaks for:

1. **Wavefunction dimensionality**: In 3D, `|ψ|²` has dimension `L^{-3}`, so `ψ` has dimension `L^{-3/2}`. The current map approximates this as `L^{-1}` (line 60, 1D approximation).

2. **Fractional exponent propagation**: Line 389 casts `dim[i] * exp_val` to `int()`. If `exp_val` is a non-integer (e.g., `0.5` from a square root), the result is silently truncated. For example, `sqrt(area)` should be `L^1`, but if `area = (0,2,0,0,0)` and `exp_val = 0.5`, then `int(2 * 0.5) = 1` which happens to be correct. But `wavefunction^2` with `wavefunction = (0,-1,0,0,0)` gives `int(-1 * 2) = -2`, which is wrong for 3D (should be `-3`).

3. **Subtraction in dimension check**: The `_parse_dimension` composite parser (lines 100-133) uses `int(exp_str)` for exponents, so `"length^-3/2"` would parse `exp_str` as `"-3"` (stops at `/`), not `-1.5`.

### Fix Proposal

**Phase 1 — Change internal representation to `Fraction`**

```python
from fractions import Fraction

# Change type to tuple of Fractions
_DIMENSION_MAP: dict[str, tuple[Fraction, ...]] = {
    "wavefunction": (Fraction(0), Fraction(-3, 2), Fraction(0), Fraction(0), Fraction(0)),
    # ... rest converted to Fraction(n) for integers
}
```

Line 389 changes from `int(dim[i] * exp_val)` to `dim[i] * Fraction(exp_val).limit_denominator(10)`.

The equality check at line 197 (`dim == lhs_dim`) works unchanged because `Fraction` supports `==`.

**Phase 2 — Update `_parse_dimension` composite parser**

Allow fractional exponents in the regex: `r'([a-z_]+)(\^?)(-?\d+(?:/\d+)?)'` instead of the current `r'([a-z_]+)(\^?)(-?\d*)'`.

**Phase 3 — Update `_dim_to_str`**

Render `Fraction(-3, 2)` as `"length^{-3/2}"`.

### Fix Difficulty
- **Moderate** (~80-120 lines changed). The core arithmetic is simple; the main work is converting all 50+ `_DIMENSION_MAP` entries and ensuring `Fraction` propagates through `_parse_expression_dimension`, `_split_terms`, and the parenthesized sub-expression handler.
- All downstream consumers (`check_dimensions` return values, `_dim_to_str`) need to handle `Fraction` instead of `int`.
- Tests: dimension tuples currently compared with `==` which works for `Fraction`. Integration with `aitp_verify_dimensions` MCP tool should be transparent since it returns strings.

### Risk
- **Medium**. The `Fraction` type is hashable and supports `==`, so dict lookups and comparisons work. However, any code that does `int()` casts on dimension components (e.g., serialization, MCP response formatting) will break until updated. A grep for `int(dim` or `total[i]` is essential before merging.

---

## Issue 4: L4 `PHYSICS_CHECK_FIELDS` Completeness

### Location
- `brain/state_model.py:1243-1249` — `PHYSICS_CHECK_FIELDS` list
- `brain/state_model.py:1274-1456` — `evaluate_l4_stage` (uses the fields in review validation)
- `skills/skill-validate.md:56, 105-108` — documents the expected check fields

### Impact
The current 5 fields are:
1. `dimensional_consistency`
2. `symmetry_compatibility`
3. `limiting_case_check`
4. `conservation_check`
5. `correspondence_check`

Missing fields that should be present for physics correctness:
- **`unitarity_check`**: Required for any quantum-mechanical result involving S-matrices, evolution operators, or probability conservation. Without it, a candidate claiming a unitary evolution passes L4 even if the evolution operator is not unitary.
- **`causality_check`**: Required for relativistic theories, response functions, and Green's functions. Ensures no superluminal propagation or acausal advanced potentials.
- **`approximation_validity_check`**: The highest-value addition. Most physics errors come from using approximations outside their regime (e.g., perturbation theory at strong coupling). The L4 gate should explicitly require the reviewer to check that each approximation in the derivation is valid within the claimed regime.

### Fix Proposal

**Step 1 — Extend the list in `state_model.py:1243-1249`**:

```python
PHYSICS_CHECK_FIELDS = [
    "dimensional_consistency",
    "symmetry_compatibility",
    "limiting_case_check",
    "conservation_check",
    "correspondence_check",
    "approximation_validity_check",
    "unitarity_check",
    "causality_check",
]
```

**Step 2 — Update `evaluate_l4_stage` review parsing**

The function currently doesn't validate that reviews contain entries for all `PHYSICS_CHECK_FIELDS`. It only checks for counterargument sections (lines 1369-1393). Add a check after the counterargument gate:

```python
# After the counterargument check (~line 1393):
# Verify physics checks are present
for cand_path in submitted:
    slug = cand_path.stem
    review_path = review_dir / f"{slug}.md"
    if review_path.exists():
        rfm, _ = parse_md(review_path)
        check_results = rfm.get("check_results", {})
        if isinstance(check_results, dict):
            missing_checks = [
                f for f in PHYSICS_CHECK_FIELDS
                if f not in check_results
            ]
            if missing_checks:
                return StageSnapshot(
                    stage="L4", posture="verify", lane=lane,
                    gate_status="blocked_missing_field",
                    required_artifact_path=str(review_path),
                    missing_requirements=[
                        f"L4 review for {slug} missing physics check: {mc}"
                        for mc in missing_checks
                    ],
                    next_allowed_transition="L3",
                    skill="skill-validate",
                )
```

**Step 3 — Update `skills/skill-validate.md`**

Add the 3 new fields to the example `check_results` block (currently at lines 105-108).

### Risk
- **Low to Medium**. Adding fields is backward-compatible: existing reviews that don't include the new fields will simply fail the new gate check. This is intentional — they should be updated. However, this means **all existing L4 reviews will become blocked** until they add the new fields. Mitigation: gate the new check behind a feature flag or apply only to topics created after the change date.
- For `unitarity_check` and `causality_check`: these are not relevant to all domains (e.g., thermodynamics, classical mechanics). Consider making the required set **lane-dependent**: formal_theory requires all 8, toy_numeric requires only the original 5, code_method requires `approximation_validity_check` but not `causality_check`.

---

## Summary Priority

| # | Issue | Severity | Fix Effort | Recommended Priority |
|---|-------|----------|------------|---------------------|
| 1 | Slug over-matching | P0 — active misrouting | 5 lines | Fix first, Option A |
| 2 | Missing question stems | P1 — false negatives | 3 lines | Fix with Issue 1 |
| 3 | Half-integer dimensions | P1 — wrong results for QM | ~100 lines | Phase after 1&2 |
| 4 | L4 check fields | P1 — incomplete validation | ~30 lines | Can parallel with 3 |
