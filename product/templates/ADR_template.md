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
> Our API currently returns errors as plain strings with HTTP status codes. As the API grows, clients need consistent error responses with machine-readable codes, human-readable messages, and optional field-level details for validation errors.

---

## Decision

What is the change that we're proposing or have agreed to? State it clearly and directly.

**Example:**
> All API errors will use a unified JSON envelope: `{ "error": { "code": "VALIDATION_FAILED", "message": "...", "details": [...] } }`. HTTP status codes follow RFC 7231. Client SDKs will parse this format automatically.

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
- Consistent error handling across all endpoints
- Client SDKs can parse errors programmatically without string matching
- Validation errors include field-level details for better UX

### Negative
- Requires updating all existing error responses (migration effort)
- Slightly larger response payloads for simple errors

### Neutral
- Third-party integrations will need to update their error parsing logic

---

## Alternatives Considered

What other options did you evaluate? Why were they rejected?

**Example:**

### Alternative 1: Return errors as plain text strings
**Rejected because:** Clients can't reliably parse error types without fragile string matching. No support for field-level validation details.

### Alternative 2: Use HTTP status codes only (no response body)
**Rejected because:** Status codes alone don't provide enough context. A 400 could mean missing field, invalid format, or business rule violation.

### Alternative 3: Use a third-party error standard (Problem Details RFC 7807)
**Rejected because:** Added complexity without clear benefit for our use case. Our simpler format covers all current needs.

---

## Notes

Any additional context, links to discussions, or implementation details that don't fit above.

**Example:**
- See discussion in Issue #42 about inconsistent error handling across endpoints
- Implementation details in PR #58
- Related to the API versioning decision in ADR-002

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

