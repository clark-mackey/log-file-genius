# Decisions

- [001](001.md)
- [002](002.md)

<!-- LFG:ROUTES:BEGIN -->
Source SHA-256: b57efdfff6b50f2bd622295c351c096287abee5cb37ea1a034638c5d5a765477

Read globals and every path/task match. Follow replacements; search sources on a miss. Report unread scope.

| Decision / status | Read when | Applies to | Constraint |
|---|---|---|---|
| [ADR-001: Preserve receipt amounts](001.md) (accepted) | Preserve receipt amounts | project-wide | Keep amounts as integer minor units; never introduce float conversion. |
| [ADR-002: Retry receipt submission](002.md) (accepted) | Retry receipt submission | api/* | Reuse the same request identifier after timeout; do not generate a new key. |
<!-- LFG:ROUTES:END -->
