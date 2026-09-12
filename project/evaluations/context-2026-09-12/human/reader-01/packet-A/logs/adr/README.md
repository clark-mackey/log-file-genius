# Decisions

- [001](001.md)

<!-- LFG:ROUTES:BEGIN -->
Source SHA-256: c8c0953c3228d01a135dd3bd81ff82dc289b7300ce5f870da7be7a6cc2d90bf4

Read globals and every path/task match. Follow replacements; search sources on a miss. Report unread scope.

| Decision / status | Read when | Applies to | Constraint |
|---|---|---|---|
| [ADR-001: Preserve receipt amounts](001.md) (accepted) | Preserve receipt amounts | project-wide | Keep amounts as integer minor units; never introduce float conversion. |
<!-- LFG:ROUTES:END -->
