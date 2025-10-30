# Architectural Decision Records (ADRs)

This directory contains records of architectural decisions made during the development of Log File Genius.

---

## What is an ADR?

An Architectural Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

**When to create an ADR:**
- Making architectural decisions with long-term impact
- Choosing between multiple viable alternatives
- Establishing patterns that will be used across the codebase
- Making security or performance tradeoffs
- Deciding on external dependencies or frameworks

**When NOT to create an ADR:**
- Routine bug fixes
- Obvious implementation details
- Temporary workarounds
- Decisions that can be easily reversed

---

## ADR Index - Newest First

- (No ADRs yet - will be created as architectural decisions are made)

---

## ADR Template

Use the template at `../../templates/ADR_template.md` to create new ADRs.

**Naming convention:** `NNN-short-title-in-kebab-case.md`

Examples:
- `001-github-pages-deployment.md`
- `002-template-repository-structure.md`
- `003-multi-platform-ai-support.md`

---

## Status Values

- **Proposed:** Decision is under discussion
- **Accepted:** Decision is approved and being implemented
- **Deprecated:** Decision is no longer recommended but may still be in use
- **Superseded by ADR-XXX:** Decision has been replaced by a newer ADR

---

## Related Documents

📋 **[PRD](../prd.md)** - Product requirements and specifications (in BMAD context)
📖 **[DEVLOG](../planning/DEVLOG.md)** - Development narrative and decision rationale
📊 **[CHANGELOG](../planning/CHANGELOG.md)** - Technical changes and version history

---

## How to Use ADRs

1. **Before making a significant architectural decision:**
   - Copy `../../templates/ADR_template.md` to `docs/adr/NNN-title.md`
   - Fill in the context, decision, consequences, and alternatives
   - Set status to "Proposed"
   - Discuss with team/stakeholders

2. **After decision is approved:**
   - Update status to "Accepted"
   - Add entry to this README index
   - Link to ADR from DEVLOG entry
   - Reference ADR in CHANGELOG when implemented

3. **When implementing the decision:**
   - Reference the ADR in code comments where relevant
   - Update CHANGELOG with "Per ADR-NNN" notation

4. **If decision is superseded:**
   - Update old ADR status to "Superseded by ADR-XXX"
   - Create new ADR explaining the change
   - Update this index

---

## Token Efficiency

ADRs are designed to be:
- **Concise but complete** - Aim for 300-500 words per ADR
- **Scannable** - Use bullet points and clear structure
- **Linked, not duplicated** - Reference external docs instead of copying
- **Focused** - One decision per ADR

**Target:** Each ADR should consume ~400-600 tokens when loaded by AI.

---

## Further Reading

- **[ADR How-To Guide](../ADR_how_to.md)** - Comprehensive guide to creating and using ADRs
- **[ADR Template](../../templates/ADR_template.md)** - Template for new ADRs
- **[Log File How-To](../log_file_how_to.md)** - How ADRs fit into the overall log file system

