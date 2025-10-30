# Architectural Decision Records (ADRs)

This directory contains records of architectural decisions made during the development of the Task Management API.

---

## What is an ADR?

An Architectural Decision Record (ADR) captures an important architectural decision along with its context and consequences. ADRs help teams:

- **Remember why** decisions were made months or years later
- **Onboard new team members** by explaining the reasoning behind the architecture
- **Avoid revisiting** settled decisions without new information
- **Document tradeoffs** so future changes can be made with full context

---

## Active ADRs

- **[ADR-003](003-optimistic-locking.md)** - Optimistic Locking for Task Updates (2025-10-27)
- **[ADR-002](002-jwt-authentication.md)** - JWT Authentication with Refresh Tokens (2025-10-21)
- **[ADR-001](001-postgresql-choice.md)** - PostgreSQL Over MongoDB (2025-10-15)

---

## Superseded ADRs

None yet.

---

## Deprecated ADRs

None yet.

---

## Creating a New ADR

1. **Copy the template:** Use `/templates/ADR_template.md` as your starting point
2. **Number sequentially:** Next number is `004`
3. **Name descriptively:** `004-short-title-in-kebab-case.md`
4. **Fill in all sections:** Context, Decision, Consequences, Alternatives
5. **Link from DEVLOG:** Reference the ADR in your DEVLOG entry
6. **Update this README:** Add to the Active ADRs list

---

## When to Create an ADR

Create an ADR when a decision:
- Has long-term consequences (affects architecture for months/years)
- Is hard to reverse (database choice, framework, authentication pattern)
- Affects multiple parts of the system (error handling, API versioning)
- Will be questioned later ("Why did we choose X over Y?")
- Has significant tradeoffs (performance vs. simplicity, cost vs. features)

---

## ADR Lifecycle

1. **Proposed** - Under discussion, not yet decided
2. **Accepted** - Decision made and being implemented
3. **Deprecated** - No longer relevant but kept for historical context
4. **Superseded** - Replaced by a newer ADR (reference the new one)

---

## Related Documents

📋 **[PRD](../../../specs/PRD.md)** - Product requirements and specifications  
📊 **[CHANGELOG](../CHANGELOG.md)** - Technical changes and version history  
📖 **[DEVLOG](../DEVLOG.md)** - Development narrative and decision rationale  
🔄 **[STATE](../STATE.md)** - Current project state and active work

