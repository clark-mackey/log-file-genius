# ADR-008: Product/Project Directory Separation

**Status:** Accepted
**Date:** 2025-11-02
**Deciders:** Clark Mackey, PM Agent (John)
**Related:** Epic: Architectural Clarity Refactoring

---

## Context

Log File Genius is a documentation repository that teaches developers how to use token-efficient log files for AI assistants. The project also dogfoods its own methodology - it uses CHANGELOG, DEVLOG, ADRs, and PRD to track its own development.

This creates a critical meta-problem: AI agents consistently confuse "the product we're building" (templates, documentation, examples for distribution) with "the project building it" (our working logs, our PRD, our ADRs).

**Evidence of the problem:**
- When asked "what's next in the PRD?", AI agents read `docs/prd.md` (which describes the 6 epics for building the product) and start analyzing it as if implementing those features, rather than understanding it as the requirements document for THIS project
- When asked to "update logs", agents sometimes update templates instead of working logs
- When asked for "example CHANGELOG", agents sometimes show the project's actual CHANGELOG instead of the template

**Current mitigation attempts:**
- `.augment/rules/log-file-confusion-guard.md` (~425 tokens, always-on)
- `.augment/rules/avoid-log-file-confusion.md` (~840 tokens, manual)

These rules are reactive (tell agents "don't confuse these") rather than preventive (make confusion structurally impossible).

---

## Decision

Restructure the repository into two top-level directories that create clear physical and cognitive boundaries:

```
log-file-genius/
├── product/                    # THE PRODUCT (what we distribute)
│   ├── templates/              # Clean templates for users
│   ├── docs/                   # How-to guides
│   ├── examples/               # Sample projects
│   └── starter-packs/          # Pre-configured setups
│
├── project/                    # THE PROJECT (our development)
│   ├── planning/               # Our CHANGELOG, DEVLOG, STATE
│   ├── adr/                    # Our architectural decisions
│   └── specs/                  # Our PRD (the 6 epics)
│
└── .project-identity.yaml      # Explicit meta-problem documentation
```

Additionally, create `.project-identity.yaml` at the repository root that explicitly documents the meta-problem and provides a decision tree for common scenarios.

---

## Consequences

### Positive
- **Structural clarity** - Path names become self-documenting (`project/planning/CHANGELOG.md` is unambiguously THIS project's log)
- **Cognitive load reduction** - AI agents can use directory name as primary signal
- **Scalability** - As the project grows, the separation remains clear
- **Onboarding** - New contributors immediately understand the distinction
- **Rule simplification** - Augment rules can reference structure rather than listing files
- **Confusion elimination** - Physical separation makes confusion structurally difficult

### Negative
- **Migration effort** - All file paths change, requiring updates to:
  - Documentation cross-references
  - Augment/Claude Code rules
  - Validation scripts
  - Git hooks
  - Starter pack references
- **Breaking change** - Anyone who has cloned the repo will see moved files
- **Git history complexity** - File moves create noise in git log (mitigated by using `git mv`)
- **Learning curve** - Users familiar with old structure need to adapt

### Neutral
- **File count unchanged** - Same files, different locations
- **Content unchanged** - Only paths change, not content
- **Git history preserved** - Using `git mv` maintains file history

---

## Alternatives Considered

### Alternative 1: Keep current structure, improve rules only
**Rejected because:** Rules are reactive, not preventive. They rely on AI interpretation and can be ignored or misunderstood. The fundamental ambiguity remains.

### Alternative 2: Use prefixes instead of directories (e.g., `PRODUCT-templates/`, `PROJECT-planning/`)
**Rejected because:** Less clean, doesn't leverage directory hierarchy, still requires reading prefix to understand context.

### Alternative 3: Separate repositories (one for product, one for project)
**Rejected because:** Dogfooding is valuable - we want to use our own system. Separation would lose this benefit and complicate development workflow.

### Alternative 4: Use `.meta/` directory for project files
**Rejected because:** "Meta" is vague and doesn't clearly communicate "this project's development files". `project/` is more explicit.

---

## Notes

- Migration will be done in feature branch `refactor/product-project-separation`
- All file moves will use `git mv` to preserve history
- Link checker will verify zero broken references before merge
- AI agent confusion test scenarios will validate effectiveness
- This ADR itself will move to `project/adr/008-product-project-directory-separation.md`
- Related DEVLOG entry will document the implementation process
- Success metric: Zero confusion incidents after migration

---

