# Issue Ledger

Use this ledger during the real-topic E2E run.

One row per discovered issue.

Severity:

- `P0` blocks the real-topic run completely or corrupts trust-critical state
- `P1` allows partial progress but blocks the intended bounded route
- `P2` creates serious friction, confusion, or wrong defaults without full blockage
- `P3` is polish or clarity debt discovered during the run

Destination rule:

- `current-milestone-decimal` for urgent blockers that should be fixed before the E2E milestone closes
- `next-milestone-candidate` for important but non-blocking follow-up
- `backlog` for useful but deferred work

Status rule:

- `open`
- `triaged`
- `routed`
- `resolved`
- `deferred`

| issue_id | severity | category | front_door | topic_slug | summary | expected | actual | evidence_ref | discovered_during | proposed_gsd_destination | status |
|----------|----------|----------|------------|------------|---------|----------|--------|--------------|-------------------|--------------------------|--------|
| issue:template-001 | P2 | ux / runtime / protocol / docs / adapter | codex / claude-code / opencode | demo-topic | Describe the issue clearly. | What should have happened. | What actually happened. | path/to/artifact | command or step | backlog / current-milestone-decimal / next-milestone-candidate | open |

## Notes

- Keep one issue per row.
- Do not merge unrelated symptoms into one row just because they were discovered in the same session.
- Always prefer durable artifact refs over prose-only descriptions.
- If one issue causes another, keep separate rows and link them in the summary text.
