# Architectural Decision Records (ADRs)

This directory contains records of architectural decisions made during the project. Each ADR captures the context, decision, consequences, and alternatives for significant technical choices.

---

## Related Documents

📋 **[PRD](../specs/PRD-Safe-Remote-Agent-Architecture.md)** - Product requirements and specifications
📊 **[CHANGELOG](../planning/CHANGELOG.md)** - Technical changes and version history
📖 **[DEVLOG](../planning/DEVLOG.md)** - Development narrative and decisions
📝 **[Template](../planning/templates/ADR_template.md)** - Template for creating new ADRs

> **For AI Agents:** ADRs document architectural decisions with stable IDs. See DEVLOG for the ADR index and decision timeline.

---

## Active Decisions

### ADR-001: No Claude File System Access
**Date:** 2025-10-27
**Status:** Accepted
**Summary:** Claude Skills Factory MCP server will NOT access Claude Desktop's file system. All skill management happens through MCP tools with explicit user consent.
**[→ Full ADR](./001-no-claude-file-system-access.md)**

### ADR-002: Conservative Metadata Management
**Date:** 2025-10-29
**Status:** Accepted
**Summary:** Only manage CSF fields (`alias`, `version`, `id`). Preserve all other metadata fields to enable ecosystem compatibility with other tools.
**[→ Full ADR](./002-conservative-metadata-management.md)**

### ADR-003: Feedback Integration Into Workflow
**Date:** 2025-10-28
**Status:** Accepted
**Summary:** Make feedback collection the final step in the workflow itself (not a separate section). Use direct action-oriented instructions to prevent Claude from overthinking.
**[→ Full ADR](./003-feedback-integration-into-workflow.md)**

---

## What is an ADR?

An **Architectural Decision Record** (ADR) is a document that captures an important architectural decision along with its context and consequences. ADRs help teams:

- Remember why decisions were made months or years later
- Onboard new team members quickly
- Avoid relitigating settled decisions
- Provide stable references for AI code assistants ("Follow ADR-003")

---

## When to Create an ADR

Create an ADR when a decision:

1. **Has long-term consequences** - Affects architecture for months or years
2. **Is hard to reverse** - Database choice, framework, authentication pattern
3. **Affects multiple parts of the system** - Error handling standard, API versioning, data model
4. **Will be questioned later** - "Why did we choose X over Y?"
5. **Has significant tradeoffs** - Performance vs. simplicity, cost vs. features

**Examples that warrant ADRs:**
- ✅ "Use PKCE for OAuth flow" (security pattern, affects all auth)
- ✅ "Conservative metadata management" (data integrity philosophy)
- ✅ "Railway for deployment vs. AWS" (infrastructure choice)
- ✅ "Standardize on unified error model" (API contract)

**Examples that DON'T need ADRs:**
- ❌ "Fixed bug in YAML parser" (implementation detail)
- ❌ "Updated button color" (trivial change)
- ❌ "Added logging to handler" (incremental improvement)
- ❌ "Refactored function names" (code quality, not architecture)

---

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [Names or team]
**Related:** [PR #XXX, Issue #XXX, ADR-XXX]

## Context
[What is the issue or situation that motivates this decision?]

## Decision
[What is the change we're proposing or have agreed to?]

## Consequences
[What becomes easier or harder as a result?]

## Alternatives Considered
[What other options did we evaluate and why were they rejected?]
```

See [`ADR_template.md`](../planning/templates/ADR_template.md) for a complete template with examples.

---

## Naming Convention

- **Format:** `NNN-short-title-in-kebab-case.md`
- **Numbering:** Sequential, zero-padded (`001`, `002`, `003`, etc.)
- **Never reuse numbers**, even if an ADR is superseded

**Examples:**
- `001-use-fastapi-framework.md`
- `002-unified-error-model.md`
- `003-conservative-metadata-management.md`

---

## Status Values

- **Proposed:** Under discussion, not yet decided
- **Accepted:** Decision made and being implemented
- **Deprecated:** No longer relevant but kept for historical context
- **Superseded:** Replaced by a newer ADR (reference the new one in the file)

---

## How ADRs Work with Other Logs

### DEVLOG.md
The DEVLOG contains a lightweight index of ADRs at the top:

```markdown
## Decisions (ADR Index) - Newest First

- **ADR-003 (2025-10-29):** Conservative Metadata Management [→ Full ADR](./003-conservative-metadata-management.md)
- **ADR-002 (2025-10-25):** Unified API Error Model [→ Full ADR](./002-conservative-metadata-management.md)
```

This gives AI agents a quick scan of what decisions exist with links to full context on demand.

### CHANGELOG.md
The CHANGELOG references ADRs when relevant:

```markdown
### Changed
- API error responses - Aligned all endpoints with ADR-002. Files: `routes/*.py`
```

### AI Prompts
You can reference ADRs directly in prompts to AI assistants:

```
"Before modifying the metadata handling logic, read ADR-003 
(Conservative Metadata Management) to understand our approach."
```

---

## Token Efficiency Benefits

**Without ADRs:** Decision rationale scattered through 2,000-line DEVLOG narrative. AI must read everything to find relevant context.

**With ADRs:**
- DEVLOG has a 3-line index (~50 tokens)
- Each ADR is ~400-600 tokens
- AI loads only relevant ADRs on demand
- Stable IDs enable precise references

**Example:**
- "Follow ADR-003" → AI loads one 500-token file
- vs. searching 2,000-line DEVLOG → AI loads 40,000+ tokens

---

## Getting Started

1. Copy [`ADR_TEMPLATE.md`](ADR_TEMPLATE.md) to a new file in this directory
2. Name it using the next sequential number: `NNN-short-title.md`
3. Fill in the sections with your decision context
4. Set status to "Proposed" initially
5. Update to "Accepted" once the decision is finalized
6. Add a reference to the ADR index above
7. Link to the ADR from DEVLOG.md and relevant CHANGELOG entries

---

## Resources

- [ADR GitHub Organization](https://adr.github.io/) - Community resources and examples
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Original blog post by Michael Nygard
- [ADR Template](ADR_TEMPLATE.md) - Template file in this directory

