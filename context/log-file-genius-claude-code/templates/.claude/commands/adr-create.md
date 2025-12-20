# Create Architecture Decision Record (ADR)

Create a new ADR for significant technical decisions.

## When to Create an ADR
- Choosing between competing technologies/approaches
- Significant architectural changes
- Decisions that will be hard to reverse
- Choices that future developers will question

## Instructions

1. Determine the next ADR number by checking `logs/adr/`
2. Create `logs/adr/ADR-[NUMBER]-[slug].md` with this structure:

```markdown
# ADR-[NUMBER]: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
[What becomes easier or more difficult to do because of this change?]

## Alternatives Considered
- **[Alternative 1]:** [Why rejected]
- **[Alternative 2]:** [Why rejected]

## Related
- DEVLOG: [link to related devlog entry]
- CHANGELOG: [link to related changelog entry]
```

## Quality Checklist
- [ ] Context clearly explains the problem
- [ ] Decision is specific and actionable
- [ ] Consequences include both positive and negative
- [ ] Alternatives show due diligence
- [ ] Bidirectional links added

$ARGUMENTS contains the decision topic or context.
