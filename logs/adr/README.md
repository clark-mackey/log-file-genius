---
type: ADR Index
doc: ADR-INDEX
---

# Decisions

[Template](../../product/templates/ADR_template.md) · [Notes](../../project/archive/context/adr-index-before-routing.md).

<!-- LFG:ROUTES:BEGIN -->
Source SHA-256: 42f895ec7e7b65ee729f8ad427b70560e21b416418fb7c3d0201b8dfee4db888

Read globals and every path/task match. Follow replacements; search sources on a miss. Report unread scope.

| Decision / status | Read when | Applies to | Constraint |
|---|---|---|---|
| [ADR-015: Portable Context and Routing](015-portable-context-discovery.md) (accepted) | Changing context or distribution | project-wide | Keep context local and low-dependency; preserve ownership and history; report unread or unverified scope. |

| Partition | Read when | Applies to |
|---|---|---|
| [ADR-007](routes/adr-007.md) | Considering feature scope, profiles or workflows | product/profiles/*, product/scripts/* |
| [ADR-009](routes/adr-009.md) | Promoting releases or changing branches | product/VERSION.json, project/WORKFLOW.md |
| [ADR-010](routes/adr-010.md) | Installing or updating the source checkout | .gitmodules, product/scripts/install.*, product/scripts/update.* |
| [ADR-013](routes/adr-013.md) | Considering composable installers or hook extensibility | product/scripts/install.*, product/scripts/update.* |
| [ADR-014](routes/adr-014.md) | Changing development branch log locations | logs/*, project/* |

Superseded history (follow replacements): [ADR-008](routes/adr-008.md), [ADR-011](routes/adr-011.md), [ADR-012](routes/adr-012.md).
<!-- LFG:ROUTES:END -->
