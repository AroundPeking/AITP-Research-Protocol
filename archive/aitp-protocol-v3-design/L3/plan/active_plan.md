---
plan_statement: 'Phase E: Update tests for removed tools, verify existing topic compatibility, and commit all changes.'
derivation_route: 'Test audit → Update tests → Verify topics → Commit'
artifact_kind: l3_active_plan
subplane: planning
---

# Active Plan

## Plan Statement

Phase E (final phase): Update the test suite to remove references to the 15 deleted tools, verify that all 7 existing AITP topics remain navigable with the reduced tool set, and commit the refactored protocol to the MCP server repo.

## Derivation Route

1. **Audit test files** — identify all references to deleted tools in `tests/` directory
2. **Update or remove broken tests** — tests for deleted tools get removed; tests for remaining tools get verified they still pass
3. **Verify topic compatibility** — run `aitp_health_check` and spot-check each existing topic with the new tool set
4. **Commit MCP server changes** — commit with message documenting the v3 refactor

## Expected Outcomes

- Test suite passes for all 36 remaining tools (down from 49)
- All 7 existing topics report healthy in `aitp_health_check`
- MCP server repo has clean, documented commits
- Main workspace has updated skill files and topic artifacts (L3 complete through distillation)

## Milestones

1. Test audit complete
2. Tests updated and passing
3. Topic verification complete
4. All changes committed
