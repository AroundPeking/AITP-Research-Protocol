---
name: aitp-push-after-feature
description: Use when editing files in the AITP-Research-Protocol repo — after any feature or sub-feature completes, before reporting "done" to the user
---

# AITP Push After Feature

## Rule

**After completing any feature or coherent sub-feature in the AITP repo, you MUST:**

1. `git add` the changed files
2. `git commit` with a descriptive message
3. `git push origin main`

**Before telling the user "done," verify `git push` succeeded.**

## Why

AITP repo state was lost when `.git` was deleted and multiple sessions of work
existed only as local commits. Push is the only durable backup.

## When to push

Push after EACH of these boundaries, not just at the end of a session:

- A new MCP tool function is complete and smoke-tested
- A gate or state-machine change compiles and passes its contract checks
- A spec document or protocol document is finished
- A batch of related test updates is done
- Any `git commit` has been made (push immediately after)

## No exceptions

- Not "I'll push at the end of the session"
- Not "this is too small to push"
- Not "let me do one more thing first"
- Not "the remote might be ahead" (pull first, then push)

## Red flags — STOP and push now

- You just typed `git commit`
- You're about to tell the user something is "done"
- You're about to start a new task in the same repo
- The session has been running for more than 20 minutes with file edits

**Every one of these means: commit and push now, then continue.**
