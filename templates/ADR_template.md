# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [Names or team]
**Related:** [PR #XXX, Issue #XXX, ADR-XXX]

---

## Context

What is the issue or situation that motivates this decision? What constraints exist? What is the background that someone needs to understand this decision?

Keep this section concise but complete. An AI agent or future developer should be able to understand the problem space in 2-3 sentences.

**Example:**
> We need to support customers migrating existing skills from other tools. These skills may contain metadata fields that CSF doesn't recognize or use. If we delete unknown metadata, we risk breaking other tools that rely on those fields.

---

## Decision

What is the change that we're proposing or have agreed to? State it clearly and directly.

**Example:**
> The `enhance_skill` tool will only manage CSF-owned fields: `alias`, `version`, and `id` in the metadata block. All other metadata fields will be preserved exactly as-is and never deleted or modified.

---

## Consequences

What becomes easier or harder as a result of this decision? What are the tradeoffs?

### Positive
- Benefit 1
- Benefit 2
- Benefit 3

### Negative
- Drawback 1
- Drawback 2

### Neutral
- Side effect or consideration that is neither clearly positive nor negative

**Example:**

### Positive
- Ecosystem compatibility - other tools can use the same skill files without conflict
- No hidden breakage for customers using multiple tools
- Smooth onboarding for customers with existing skills from other sources

### Negative
- Slightly more complex parsing logic (must check multiple locations)
- Metadata may accumulate stale or redundant fields over time
- Cannot enforce a "clean" metadata structure

### Neutral
- Customers may need guidance on which fields are CSF-managed vs. their own

---

## Alternatives Considered

What other options did you evaluate? Why were they rejected?

**Example:**

### Alternative 1: Delete all non-CSF metadata
**Rejected because:** This would break other tools that rely on custom metadata fields, creating hidden failures for customers.

### Alternative 2: Require manual metadata cleanup
**Rejected because:** Poor user experience; customers shouldn't need to manually edit files to use CSF.

### Alternative 3: Maintain a whitelist of known third-party fields
**Rejected because:** Impossible to maintain; we can't predict all tools that might use skill files.

---

## Notes

Any additional context, links to discussions, or implementation details that don't fit above.

**Example:**
- See discussion in Issue #156 about customer onboarding challenges
- Implementation details in PR #1240
- Related to the broader "ecosystem compatibility" philosophy discussed in the Oct 28 team meeting

---

## Template Guidelines (Remove this section in actual ADRs)

### When to Create an ADR

Create an ADR when a decision:
1. **Has long-term consequences** (affects architecture for months/years)
2. **Is hard to reverse** (database choice, framework, authentication pattern)
3. **Affects multiple parts of the system** (error handling, API versioning, data model)
4. **Will be questioned later** ("Why did we choose X over Y?")
5. **Has significant tradeoffs** (performance vs. simplicity, cost vs. features)

### When NOT to Create an ADR

Don't create an ADR for:
- Bug fixes (use CHANGELOG and commit messages)
- Refactoring (unless it changes architecture)
- UI tweaks (unless they affect UX patterns system-wide)
- Dependency updates (unless they change how the system works)
- Implementation details (unless they set a precedent)

### Numbering Convention

- Use sequential numbers: `001`, `002`, `003`, etc.
- Never reuse numbers, even if an ADR is superseded
- Pad with zeros for sortability: `001` not `1`

### Status Values

- **Proposed:** Under discussion, not yet decided
- **Accepted:** Decision made and being implemented
- **Deprecated:** No longer relevant but kept for historical context
- **Superseded:** Replaced by a newer ADR (reference the new one)

### File Naming

- Format: `NNN-short-title-in-kebab-case.md`
- Examples:
  - `001-use-fastapi-framework.md`
  - `002-unified-error-model.md`
  - `003-conservative-metadata-management.md`

### Writing Tips

1. **Be concise but complete** - Aim for 200-400 words total
2. **Use concrete examples** - Show, don't just tell
3. **State tradeoffs clearly** - Every decision has costs
4. **Link to related resources** - PRs, issues, docs, other ADRs
5. **Write for future readers** - Assume they don't have your context
6. **Update status** - Mark as Deprecated or Superseded when appropriate

### Token Efficiency

- **Target:** 400-600 tokens per ADR
- **Benefit:** AI loads only relevant ADRs on demand, not all at once
- **Strategy:** Keep Context and Decision sections tight; expand Consequences and Alternatives only as needed

