---
description: Run the safe AITP auto-continue loop for an active topic
subtask: false
---
# aitp-loop Command

Before doing substantial work, read `./AITP_COMMAND_HARNESS.md`.

Arguments: $ARGUMENTS

Run:

```bash
aitp loop $ARGUMENTS
```

Then read `runtime_protocol.generated.md` first, follow `Must read now`, and only expand deferred surfaces when the named trigger fires.
Inspect `loop_state.json` after the runtime contract if you need loop-exit status.
If the loop surfaces a promotion-ready candidate, use `aitp request-promotion ...` for human-reviewed `L2`, or `aitp coverage-audit ...` before `aitp auto-promote ...` for theory-formal `L2_auto`.
