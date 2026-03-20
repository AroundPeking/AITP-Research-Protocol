---
description: Enter the AITP runtime for a new or existing research task
subtask: false
---
# aitp Command

Before doing substantial work, read `./AITP_COMMAND_HARNESS.md`.

User request: $ARGUMENTS

1. If the topic already exists, run `aitp loop --topic-slug <topic_slug> --human-request "$ARGUMENTS"`.
2. If the topic is new, run `aitp bootstrap --topic "<topic>" --statement "$ARGUMENTS"` and then `aitp loop --topic-slug <topic_slug> --human-request "$ARGUMENTS"`.
3. Read `runtime_protocol.generated.md` first, then follow `Must read now`.
4. Expand deferred surfaces only when the named trigger in `runtime_protocol.generated.md` fires.
5. If the work is heading toward human-reviewed `L2`, use `aitp request-promotion ...` and wait for a durable approval gate.
6. If the work is heading toward theory-formal `L2_auto`, use `aitp coverage-audit ...` before `aitp auto-promote ...`.
7. Continue the task only after the runtime artifacts exist and conformance passes.
