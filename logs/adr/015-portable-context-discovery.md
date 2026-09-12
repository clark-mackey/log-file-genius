---
type: Architecture Decision
doc: ADR
title: Portable project context with explicit routing
---

# ADR-015: Portable Context and Routing

**Status:** Accepted
**Date:** 2026-09-12
**Deciders:** Clark Mackey (reviewed workplan and explicit execution request)
**Supersedes:** ADR-008, ADR-011 and ADR-012 installation/context conventions; retains their directory separation and single-logs intent.

## Routing

**Read when:** Changing context or distribution
**Applies to:** project-wide
**Constraint:** Keep context local and low-dependency; preserve ownership and history; report unread or unverified scope.

## Context

LFG provides durable context for any human, LLM or agent working on an ongoing
software project. Existing ADRs helped when found, but startup omitted their index,
full rules used about 4,093 estimated tokens before knowledge retrieval, and native
loader conventions varied. The reviewed workplan replaces those conventions.

## Decision

Keep Markdown + Git and optional Python standard-library tooling. Separate
distributable `product/` from development documentation in `project/` and our own
`logs/`. Consumers normally use one `logs/` collection and the hidden
`.log-file-genius/` source checkout, without a second visible copy of product files.
Custom configured paths remain supported. Preserve ADR-009's development/main split;
selectively promote distributables rather than merging development into main.

ADR bodies own Read when, Applies to and Constraint routing metadata; their existing
Status owns authority. Generate navigational views deterministically. Read global
and every matching path/task route, follow supersession, and report unknown/unread
scope. Curated README prose and historical decision bodies remain preserved.

Startup is a compact pointer/protocol; procedures are read on demand. Native
adapters refer to shared guidance and preserve project instructions. Log meaningful
changes and handoffs without automatic amend or mandatory conversational checklists.
STATE records branch/code baseline and factual evidence; dates alone do not verify it.
Priming retains the subagent contract and adds explicit selections plus a neutral role.

OKF metadata migration is additive and optional, with a defined bundle boundary,
exact-byte recovery, and no fabricated verification. YAML representation conformance,
native discovery, model application, and human retrieval require separate evidence.
Host/model support and release claims wait for their scoped acceptance gates.

## Consequences

Readers spend fewer tokens before reaching project knowledge, but must still make
semantic relevance judgments. Old custom instruction files may duplicate guidance;
only known shipped bytes are retired automatically. Unsupported metadata is preserved
for explicit migration. Per-file atomic writes do not provide cross-process locking
or a whole-bundle transaction. Deterministic tests do not establish behavioral reliability.

## Evidence

- [Reviewed workplan](../../project/specs/WORKPLAN-context-discovery-and-portability.md)
- [Execution record and baseline](../../project/specs/context-execution.md)
- [Reading, maintenance and recovery protocol](../../product/docs/context-guide.md)
