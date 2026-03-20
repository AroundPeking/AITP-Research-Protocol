# AITP Command Harness

These OpenCode commands route work through the installed `aitp` CLI instead of
letting topic work drift into ad hoc browsing.

Required pattern:

1. enter through `aitp loop` whenever the topic already exists
2. use `aitp bootstrap` only to create a new topic shell, then return to `aitp loop`
3. read `runtime_protocol.generated.md` first, then follow `Must read now`
4. expand deferred surfaces only when the named trigger in the runtime bundle fires
5. register reusable operations with `aitp operation-init`
6. do the actual work
7. request human approval before any human-reviewed `L2` promotion with `aitp request-promotion ...`
8. for theory-formal `L2_auto`, materialize `coverage-audit` artifacts before `aitp auto-promote ...`
9. close with `aitp audit --phase exit`

If method trust is missing:

- use `aitp baseline ...` for numerical backends
- use `aitp atomize ...` for theory-method understanding
- use `aitp trust-audit ...` before reusing an operation as if it were established
