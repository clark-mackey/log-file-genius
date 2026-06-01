# Token-Efficient Log File System for AI-Assisted Projects

**Purpose:** A five-document system (PRD, CHANGELOG, DEVLOG, STATE, ADRs) that provides complete project context to AI agents while consuming <5% of their context window.

**Target Audience:** Development teams using AI coding assistants (Claude, GitHub Copilot, etc.) who need to maintain project history without exhausting token budgets.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [The Five-Document System](#the-five-document-system)
3. [Context Layers - Progressive Disclosure](#context-layers---progressive-disclosure)
4. [Cross-Linking Best Practices](#cross-linking-best-practices)
5. [File Structure](#file-structure)
6. [Entry Formats](#entry-formats)
7. [Update Cadence](#update-cadence---when-to-update-each-document)
8. [Maintenance Workflow](#maintenance-workflow)
9. [Updating Log File Genius](#updating-log-file-genius)
10. [Token Budget Management](#token-budget-management)
11. [Problem/Solution Pairs](#problemsolution-pairs)
12. [Examples Directory](#examples-directory)
13. [Starter Templates](#starter-templates)

---

## System Overview

### The Problem

Traditional project documentation becomes verbose over time:
- **Verbose logs:** 90-110k tokens (45-55% of AI context window)
- **Result:** AI agents can't load full project history
- **Impact:** Agents lack context, make uninformed decisions, repeat past mistakes

### The Solution

A token-efficient five-document system:
- **PRD:** What we're building (requirements, features, goals)
- **CHANGELOG.md:** What changed (facts, files, versions)
- **DEVLOG.md:** Why it changed (narrative, reasoning, insights)
- **STATE.md:** What's happening now (current work, blockers, priorities)
- **ADRs:** How we decided (detailed architectural decisions)

**Result:** Complete project context in ~5-10k tokens (<5% of context window) for logs, plus PRD loaded on-demand

### Key Principles

1. **Separation of Concerns:** Requirements (PRD) vs. Facts (CHANGELOG) vs. Story (DEVLOG) vs. Decisions (ADRs)
2. **Progressive Disclosure:** Concise logs with links to detailed ADRs and PRD
3. **Token Efficiency:** Single-line entries, structured bullets, no redundancy
4. **Cross-Linking:** Bidirectional navigation between all documents with exact relative paths
5. **Narrative Preservation:** DEVLOG tells the story, just more quickly
6. **Zero-Search Navigation:** Agents find related documents instantly without wasting tokens

---

## The Five-Document System

### Overview

The complete documentation system consists of five interconnected documents:

1. **PRD (Product Requirements Document)** - "What we're building"
2. **CHANGELOG.md** - "What changed"
3. **DEVLOG.md** - "Why it changed"
4. **STATE.md** - "What's happening now"
5. **ADRs (Architectural Decision Records)** - "How we decided"

**Critical:** Every document must include cross-linked frontmatter with exact relative paths to all other documents. This enables AI agents to navigate instantly without wasting tokens searching for files.

### PRD - "What We're Building"

**Purpose:** Source of truth for product requirements, features, and specifications
**Format:** Structured document with requirements, user stories, acceptance criteria
**Audience:** Product managers, developers, stakeholders, AI agents
**Token Target:** Variable (typically 10-20k tokens, loaded when needed)

**Characteristics:**
- ✅ Defines what the product should do
- ✅ User stories and acceptance criteria
- ✅ Non-functional requirements
- ✅ Success metrics
- ✅ Cross-links to CHANGELOG, DEVLOG, ADRs
- ❌ Not a technical implementation guide
- ❌ Not a historical record

**Location:** `project/specs/PRD.md` or `project/specs/PRD-[Project-Name].md` (outside `logs/`; loaded on-demand)

### CHANGELOG.md - "What Changed"

**Purpose:** Technical record of changes to the codebase  
**Format:** Single-line entries with file paths  
**Audience:** Developers, AI agents needing facts  
**Token Target:** <10,000 tokens

**Characteristics:**
- ✅ Factual, concise, technical
- ✅ Lists affected files
- ✅ Cross-references ADRs
- ✅ Follows semantic versioning
- ❌ No narratives or explanations
- ❌ No code examples
- ❌ No "why" or reasoning

**Example Entry:**
```markdown
- Unified error response format - All API endpoints now return structured JSON error envelopes. Files: `middleware/errors.py`, `tests/test_error_responses.py`. See: [ADR-002](../adr/002-unified-error-model.md)
```

### DEVLOG.md - "Why It Changed"

**Purpose:** Narrative chronicle of the project journey  
**Format:** Situation/Challenge/Decision/Impact/Files structure  
**Audience:** Team members, future maintainers, AI agents needing context  
**Token Target:** <15,000 tokens

**Characteristics:**
- ✅ Tells the story
- ✅ Explains reasoning
- ✅ Captures insights
- ✅ Preserves context
- ❌ No verbose narratives
- ❌ No excessive code examples
- ❌ No redundant explanations

**Example Entry:**
```markdown
### 2025-10-29: Migrating to Unified Error Responses

**Situation:** API had grown to 40+ endpoints, each with its own error format. Clients were doing fragile string matching to parse errors.

**Challenge:** Standardize without breaking existing integrations or requiring a major version bump.

**Decision:** Introduced a unified error envelope (`{ error: { code, message, details } }`) via middleware. Old endpoints return the new format alongside legacy fields during a transition period. Codified in ADR-002.

**Why This Approach:** A hard cutover would break mobile clients on older versions. The middleware approach means endpoints don't need individual changes — just the middleware wraps responses.

**Impact:** All new endpoints use the standard format automatically. Legacy endpoints have a 90-day transition window. Client SDK updated to parse both formats.

**Files:** `middleware/errors.py`, `tests/test_error_responses.py`, `docs/api/error-handling.md`
```

### STATE.md - "What's Happening Now"

**Purpose:** The single source of truth for current project state — owns Current Context (version, branch, phase, objectives, risks) AND the Last Session handoff. STATE is a first-class document, not optional.
**Format:** Structured sections (Current Context, Active Work, Blockers, Recently Completed, Next Priorities, Last Session)
**Audience:** AI agents, developers — anyone starting or resuming work
**Token Target:** <500 tokens (ultra-lightweight)

**Characteristics:**
- ✅ Owns Current Context: version, branch, phase, objectives, key risks
- ✅ Owns Last Session handoff: what was done, what's next, any context to carry forward
- ✅ Updated at start and end of every work session
- ✅ Shows last 2-4 hours of activity
- ✅ Lists active work, blockers, and priorities
- ✅ Includes branch status for git workflows
- ✅ Old "Recently Completed" items archived to CHANGELOG after 24 hours
- ❌ Not a historical record (that's CHANGELOG/DEVLOG)
- ❌ Not a narrative log (that's DEVLOG)

**When to Update STATE.md:**
- **Start of work session:** Read it first; add yourself to "Active Work"; confirm Current Context is accurate
- **Every 30-60 minutes:** Update progress during active work
- **When blocked:** Immediately add to "Blockers" section
- **End of work session:** Move task to "Recently Completed"; update Last Session with handoff notes
- **Version/branch/phase changes:** Update Current Context immediately
- **After 24 hours:** Archive old "Recently Completed" items to CHANGELOG

**Use Cases:**
- **Session start:** Every agent reads STATE first — no guessing about version, branch, or what was last worked on
- **Multi-agent coordination:** Prevents duplicate work and merge conflicts
- **Handoffs:** New agents/developers resume instantly without reading CHANGELOG or DEVLOG
- **Single developer:** Still the right place for current context — lightweight enough to always maintain

**Location:** `logs/STATE.md`

### ADRs - "Architectural Decisions"

**Purpose:** Detailed records of significant architectural decisions
**Format:** Structured template (Context, Decision, Consequences, Alternatives)
**Audience:** Architects, senior developers, auditors
**Token Target:** Variable (loaded on-demand via links)

**Characteristics:**
- ✅ Stable IDs (ADR-001, ADR-002, etc.)
- ✅ Immutable once written
- ✅ Detailed context and rationale
- ✅ Alternatives considered
- ✅ Consequences documented
- ❌ Not for minor decisions
- ❌ Not for implementation details

**When to Create an ADR:**
- Technology choices (database, framework, architecture)
- Security/privacy decisions
- API design choices
- Breaking changes
- Decisions with long-term impact

### Incident Reports

**Purpose:** A standalone, detailed record of a significant incident — ADR-parallel,
loaded on-demand, never token-budgeted.

The **default** is still the lightweight inline `🚨 INCIDENT` DEVLOG entry. Escalate
to a standalone report only when the rubric flags a **major** incident — security
exposure, data loss, repeated/silent failure, or a regression.

**To escalate:**
1. Copy `logs/incidents/TEMPLATE.md` to `logs/incidents/YYYY-MM-DD-slug.md`
   (date-prefixed filename) and fill it in.
2. Link both ways: from the DEVLOG entry (`→ logs/incidents/YYYY-MM-DD-slug.md`)
   and back to DEVLOG from the report's frontmatter/Files section.
3. Run `python .log-file-genius/product/scripts/lfg.py incidents-index` to
   regenerate the index at `logs/incidents/README.md`.

**The index command:**

```bash
python .log-file-genius/product/scripts/lfg.py incidents-index   # [--dir <path>]
```

`lfg incidents-index` rebuilds `logs/incidents/README.md` (a newest-first table of
Date / Severity / Status / Incident) from whatever report files are present. It is
idempotent and uses a tolerant parser: the date comes from the filename's
`YYYY-MM-DD` prefix, headers are read leniently, and missing fields fall back to a
placeholder. **Reports from older versions are picked up automatically — no
reformatting needed.** It resolves the directory from `.logfile-config.yml`
(`paths.incidents_dir`, default `logs/incidents`); `--dir` overrides. A
hand-written `README.md` is backed up to `README.md.bak` before the generated index
replaces it.

**Characteristics:**
- ✅ Standalone, on-demand (like ADRs) — never counted against token budgets
- ✅ Date-prefixed filename (`YYYY-MM-DD-slug.md`) is the authoritative date
- ✅ Linked from and to the inline DEVLOG `🚨 INCIDENT` entry
- ❌ Not for routine incidents — those stay inline in DEVLOG

---

## Context Layers - Progressive Disclosure

### Overview

The five-document system supports a **progressive disclosure strategy** where AI agents load only the context they need for their current task. This dramatically reduces token usage while maintaining access to deep context when needed.

**Key Principle:** Start with minimal context, expand only when necessary.

### The Four Context Layers

#### Layer 1: Immediate Context (<500 tokens)

**What to load:** STATE.md only

**When to use:**
- Starting a new work session
- Quick status check
- Multi-agent coordination
- Checking for blockers before starting work

**Token budget:** <500 tokens

**Example use case:**
> Agent starts work → Reads STATE.md → Sees no conflicts → Proceeds with task

#### Layer 2: Recent History (<2,000 tokens)

**What to load:** STATE.md (Current Context + Last Session) + CHANGELOG Unreleased section + recent DEVLOG entries

**When to use:**
- Understanding current project state
- Checking recent changes before making edits
- Understanding active branch and phase
- Reviewing recent decisions

**Token budget:** <2,000 tokens

**Example use case:**
> Agent needs to add feature → Reads STATE Current Context for version/stack/standards → Reads recent CHANGELOG for related changes → Implements feature following conventions

#### Layer 3: Full Project Context (<10,000 tokens)

**What to load:** STATE.md + Full DEVLOG + Full CHANGELOG + ADR index

**When to use:**
- Major refactoring or architectural changes
- Understanding project evolution and history
- Investigating why past decisions were made
- Comprehensive code review

**Token budget:** <10,000 tokens

**Example use case:**
> Agent investigates bug → Reads full DEVLOG for context → Finds related ADR → Understands architectural constraints → Fixes bug properly

#### Layer 4: Deep Dive (On-Demand)

**What to load:** Everything from Layer 3 + PRD + Specific ADRs + Archives

**When to use:**
- Planning major features
- Architectural decision-making
- Comprehensive project analysis
- Onboarding new team members

**Token budget:** Variable (10,000-30,000 tokens)

**Example use case:**
> Agent plans new feature → Reads PRD for requirements → Reads full DEVLOG for context → Reads relevant ADRs → Proposes implementation aligned with project goals

### Progressive Loading Strategy

**Start minimal, expand as needed:**

```
1. Read STATE.md — Current Context + Last Session (Layer 1)
   ↓
   Need more context?
   ↓
2. Read STATE + Recent CHANGELOG + Recent DEVLOG entries (Layer 2)
   ↓
   Still need more?
   ↓
3. Read Full DEVLOG + Full CHANGELOG (Layer 3)
   ↓
   Planning major changes?
   ↓
4. Read PRD + Specific ADRs (Layer 4)
```

### Token Savings with Context Layers

**Traditional approach:** Load everything upfront
- Total: ~90,000-110,000 tokens
- Result: Can't fit in context window

**Layer 1 (Quick tasks):**
- Total: ~500 tokens
- Savings: 99.5% reduction

**Layer 2 (Most tasks):**
- Total: ~2,000 tokens
- Savings: 98% reduction

**Layer 3 (Complex tasks):**
- Total: ~10,000 tokens
- Savings: 90% reduction

**Layer 4 (Major planning):**
- Total: ~25,000 tokens
- Savings: 75% reduction

### When to Use Each Layer

| Task Type | Recommended Layer | Token Budget |
|-----------|------------------|--------------|
| Quick status check | Layer 1 | <500 |
| Bug fix | Layer 2 | <2,000 |
| Feature implementation | Layer 2-3 | <10,000 |
| Refactoring | Layer 3 | <10,000 |
| Architectural decision | Layer 4 | <30,000 |
| New feature planning | Layer 4 | <30,000 |
| Onboarding | Layer 4 | <30,000 |

### Implementation Tips

1. **AI agents should ask:** "What layer of context do I need for this task?"
2. **Start small:** Begin with Layer 1, expand only if needed
3. **Use cross-links:** Navigate to specific ADRs/sections on-demand
4. **Archive aggressively:** Keep current files small so layers stay efficient
5. **Update STATE.md frequently:** Keep Layer 1 fresh and accurate

---

## Cross-Linking Best Practices

### Why Cross-Linking Matters

**Token Efficiency:** When an AI agent reads one document, it should instantly know where to find related information without:
- ❌ Searching the file system
- ❌ Guessing file paths
- ❌ Reading multiple files to find the right one
- ❌ Wasting tokens on trial-and-error navigation

**Solution:** Every document includes frontmatter with exact relative paths to all related documents.

### Navigation Matrix

From any document, agents can navigate to any other document using these exact relative paths:

| From Document | To PRD | To CHANGELOG | To DEVLOG | To STATE | To ADRs |
|---------------|--------|--------------|-----------|----------|---------|
| **PRD** (`project/specs/PRD.md`) | - | `../../logs/CHANGELOG.md` | `../../logs/DEVLOG.md` | `../../logs/STATE.md` | `../../logs/adr/README.md` |
| **CHANGELOG** (`logs/CHANGELOG.md`) | `../project/specs/PRD.md` | - | `./DEVLOG.md` | `./STATE.md` | `./adr/README.md` |
| **DEVLOG** (`logs/DEVLOG.md`) | `../project/specs/PRD.md` | `./CHANGELOG.md` | - | `./STATE.md` | `./adr/README.md` |
| **STATE** (`logs/STATE.md`) | `../project/specs/PRD.md` | `./CHANGELOG.md` | `./DEVLOG.md` | - | `./adr/README.md` |
| **ADR README** (`logs/adr/README.md`) | `../../project/specs/PRD.md` | `../CHANGELOG.md` | `../DEVLOG.md` | `../STATE.md` | - |
| **Individual ADR** (`logs/adr/001-title.md`) | `../../project/specs/PRD.md` | `../CHANGELOG.md` | `../DEVLOG.md` | `../STATE.md` | `./README.md` |

> **Note:** Actual relative paths depend on where your project root places `logs/` and `project/specs/`. Agents resolve paths from `.logfile-config.yml` → `paths`, with `logs/` as the fallback default. Always verify paths match your layout.

### Standard Frontmatter Template

**For PRD (`project/specs/PRD.md`):**
```markdown
---
Related Documents:
- [CHANGELOG](../../logs/CHANGELOG.md) - Technical changes and version history
- [DEVLOG](../../logs/DEVLOG.md) - Why changes were made (narrative)
- [STATE](../../logs/STATE.md) - Current context and session handoff
- [ADRs](../../logs/adr/README.md) - Architectural decision records
---
```

**For CHANGELOG (`logs/CHANGELOG.md`):**
```markdown
---
Related Documents:
- [PRD](../project/specs/PRD.md) - Product requirements and specifications
- [DEVLOG](./DEVLOG.md) - Why changes were made (narrative)
- [STATE](./STATE.md) - Current context and session handoff
- [ADRs](./adr/README.md) - Architectural decision records
---
```

**For DEVLOG (`logs/DEVLOG.md`):**
```markdown
---
Related Documents:
- [PRD](../project/specs/PRD.md) - Product requirements and specifications
- [CHANGELOG](./CHANGELOG.md) - Technical changes and version history
- [STATE](./STATE.md) - Current context and session handoff
- [ADRs](./adr/README.md) - Architectural decision records
---
```

**For STATE (`logs/STATE.md`):**
```markdown
---
Related Documents:
- [PRD](../project/specs/PRD.md) - Product requirements and specifications
- [CHANGELOG](./CHANGELOG.md) - Technical changes and version history
- [DEVLOG](./DEVLOG.md) - Development narrative
- [ADRs](./adr/README.md) - Architectural decision records
---
```

**For ADR README (`logs/adr/README.md`):**
```markdown
---
Related Documents:
- [PRD](../../project/specs/PRD.md) - Product requirements and specifications
- [CHANGELOG](../CHANGELOG.md) - Technical changes and version history
- [DEVLOG](../DEVLOG.md) - Why changes were made (narrative)
- [STATE](../STATE.md) - Current context and session handoff
---
```

**For Individual ADRs (`logs/adr/001-title.md`):**
```markdown
---
Related Documents:
- [ADR Index](./README.md) - All architectural decisions
- [PRD](../../project/specs/PRD.md) - Product requirements
- [CHANGELOG](../CHANGELOG.md) - Technical changes
- [DEVLOG](../DEVLOG.md) - Development narrative
- [STATE](../STATE.md) - Current context
---
```

### Cross-Linking Rules

1. **Always use relative paths** - Never use absolute paths or assume working directory
2. **Test all links** - Verify links work after any file reorganization
3. **Include descriptions** - Help agents understand what they'll find (e.g., "Technical changes and version history")
4. **Be consistent** - Use the same frontmatter structure in all documents
5. **Link to indexes** - Link to `ADR README.md`, not individual ADRs (unless specific reference)
6. **Bidirectional links** - If A links to B, B should link to A

### Agent Navigation Pattern

When an AI agent needs information:

1. **Start with PRD** - Understand what's being built
2. **Check CHANGELOG** - See what's been implemented
3. **Read DEVLOG** - Understand why decisions were made
4. **Follow ADR links** - Get detailed context on specific decisions

**Example Agent Workflow:**
```
Agent reads: "See: [ADR-002](../adr/002-conservative-metadata-management.md)"
Agent navigates: Opens ADR-002 for detailed context
Agent returns: Uses back-link to return to CHANGELOG/DEVLOG
```

**Token Savings:** Direct navigation saves 50-100 tokens per lookup (no searching, no trial-and-error).

---

## File Structure

### Recommended Directory Layout

```
project-root/
├── logs/                         # All runtime logs (resolved from .logfile-config.yml → paths)
│   ├── CHANGELOG.md              # What changed (facts)
│   ├── DEVLOG.md                 # Why it changed (story)
│   ├── STATE.md                  # Current context + session handoff (the now)
│   ├── adr/
│   │   ├── README.md             # ADR index
│   │   ├── 001-decision-title.md
│   │   ├── 002-decision-title.md
│   │   └── ...
│   ├── incidents/                # Standalone incident reports (escalated from DEVLOG)
│   │   ├── README.md             # Incident index (lfg incidents-index)
│   │   ├── TEMPLATE.md           # Incident report template
│   │   ├── 2025-11-19-slug.md    # YYYY-MM-DD-slug.md per report
│   │   └── ...
│   └── archive/                  # Old entries (if needed)
│       ├── CHANGELOG-2024-Q4.md
│       └── DEVLOG-2024-Q4.md
├── project/
│   └── specs/
│       ├── PRD.md                # Product requirements (loaded on-demand)
│       └── ...
└── .log-file-genius/             # LFG submodule (the toolkit — for updates)
    └── product/scripts/
        ├── lfg.py                # The CLI: validate, archive, prime, promote, generate, ...
        ├── archive.py            # Work-aware archival engine
        ├── migrate_state.py      # Brownfield STATE migration
        └── ...                   # validators, generator, secret detection
```

> **Path resolution:** Agents look for `paths` in `.logfile-config.yml` first; if not present, `logs/` is the default. Templates ship in the submodule at `.log-file-genius/product/templates/` (not copied to your project root).

### Document Relationships

**The Five Documents Work Together:**

```
┌─────────────────────────────────────────────────────────────┐
│                         PRD (Specs)                         │
│              "What we're building and why"                  │
│         Requirements, features, success metrics             │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌────────────────────────────┐
│   CHANGELOG (logs/)    │◄────►│     DEVLOG (logs/)         │
│   "What changed"       │      │     "Why it changed"       │
│   Facts, files, dates  │      │  Story, reasoning, context │
└────────┬───────────────┘      └──────────┬─────────────────┘
         │                                  │
         │         ┌────────────────────────┘
         │         │
         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                      ADRs (Decisions)                       │
│              "How we decided (detailed)"                    │
│     Architectural decisions with context & consequences     │
└─────────────────────────────────────────────────────────────┘
         ▲
         │
         │ (referenced from all documents)
         │
┌─────────────────────────────────────────────────────────────┐
│                    STATE.md (Current)                       │
│              "What's happening right now"                   │
│    Active work, blockers, priorities (last 2-4 hours)       │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Flow:**
- PRD → CHANGELOG/DEVLOG (see what's been implemented)
- CHANGELOG → ADRs (get details on specific changes)
- DEVLOG → ADRs (understand decision context)
- ADRs → PRD/CHANGELOG/DEVLOG (see impact of decisions)
- STATE → All documents (get context for current work)
- All documents → STATE (check current status before making changes)

---

## Entry Formats

### CHANGELOG Entry Format

**Template:**
```markdown
- Feature name - Brief description. Files: path/to/file.ext. [Optional: See: [ADR-XXX](../adr/XXX-title.md)]
```

**Rules:**
- Single line per entry
- Start with feature/change name
- Include affected files
- Link to ADR if applicable
- No code examples
- No multi-paragraph explanations

### DEVLOG Entry Format

**Template:**
```markdown
### YYYY-MM-DD: Entry Title

**Situation:** What was the context? What prompted this work?

**Challenge:** What problem needed solving? What constraints existed?

**Decision:** What did you decide to do? What approach did you take?

**Why [Decision Name]:** What was the reasoning? Why this approach over alternatives?

**Impact:** What changed as a result? What's now possible/easier/better?

**Files:** `file1.py`, `file2.js`, `docs/guide.md`
```

**Rules:**
- Use structured bullets (Situation/Challenge/Decision/Impact/Files)
- Keep each section to 1-2 sentences
- Preserve reasoning and insights
- No verbose narratives
- No excessive code examples
- Link to ADRs for detailed decisions

### STATE.md Entry Format

**Template:**
```markdown
# Current State

**Last Updated:** YYYY-MM-DD HH:MM UTC
**Updated By:** Agent-1 (main branch)

## Active Work

- **Agent-1** (feature/auth): Adding OAuth2 PKCE flow with token rotation
- **Developer-1** (main): Fixing critical bug in payment processing

## Blockers

- Database migration script needs DBA review before deployment (blocks Agent-1)
- Waiting for design mockups for dashboard UI (blocks Developer-2)

## Recently Completed (Last 2-4 Hours)

- ✅ OAuth2 PKCE flow implemented and tested (Agent-1, 14:30)
- ✅ Payment bug fixed, deployed to staging (Developer-1, 15:00)

## Next Priorities

1. Merge feature/auth-flow after OAuth2 tests pass
2. Review and approve database migration script
3. Complete API v2 endpoint refactoring

## Branch Status

- **main**: Clean, all tests passing (last updated: 15:30)
- **feature/auth**: 5 commits ahead, tests passing, ready for review
- **hotfix/payment-bug**: Merged to main at 15:00
```

**Rules:**
- Update at start and end of work sessions
- Keep under 500 tokens (ultra-lightweight)
- Show only last 2-4 hours of activity
- Archive "Recently Completed" items older than 24 hours to CHANGELOG
- Be specific about who's working on what
- Include timestamps for completed items
- List blockers immediately when they occur

### ADR Entry Format

**Template:**
```markdown
# ADR-XXX: Decision Title

**Status:** Accepted | Rejected | Superseded by ADR-YYY
**Date:** YYYY-MM-DD
**Deciders:** Names or roles

## Context

What is the issue we're facing? What factors are relevant?

## Decision

What did we decide to do?

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Tradeoff 1
- Tradeoff 2

### Neutral
- Side effect 1

## Alternatives Considered

### Alternative 1: Name
- Description
- Why rejected

### Alternative 2: Name
- Description
- Why rejected

## References

- Link to related documents
- Link to discussions
- Link to code
```

---

## Update Cadence - When to Update Each Document

### Overview

Different documents have different update frequencies based on their purpose. Understanding when to update each document ensures they stay current without creating unnecessary overhead.

### CHANGELOG.md - Update Frequently

**Update Trigger:** Almost any code change

**Update Frequency:** Multiple times per day during active development

**Update When:**
- ✅ **Feature added** - New functionality implemented
- ✅ **Bug fixed** - Any bug fix, major or minor
- ✅ **Code refactored** - Significant restructuring
- ✅ **Dependencies updated** - Package/library version changes
- ✅ **Configuration changed** - Environment, build, or deployment config
- ✅ **Breaking changes** - API changes, signature changes
- ✅ **Deprecations** - Features marked for removal
- ✅ **Performance improvements** - Optimization work
- ✅ **Security fixes** - Any security-related change
- ✅ **Documentation updates** - Significant doc changes

**Update Format:** Single-line entry per change
```markdown
- Feature name - Brief description. Files: path/to/file.ext
```

**Best Practice:** Update CHANGELOG immediately after committing code changes. Don't batch updates at end of day.

**Why Frequent Updates:** CHANGELOG is the technical record. If you changed code, update CHANGELOG. This keeps the "what changed" record accurate and prevents forgetting details.

**⚠️ CHANGELOG does NOT own Current Context.**

Current Context (version, branch, phase, objectives, stack) lives exclusively in **`logs/STATE.md`**. CHANGELOG is facts-only: what changed, which files, which version. No Current Context section belongs here.

When you need to update version, branch, phase, or objectives — update **STATE.md**, not CHANGELOG.

> See [STATE.md - Update Continuously During Active Work](#statemd---update-continuously-during-active-work) for the full update workflow.

---

### DEVLOG.md - Update Strategically

**Update Trigger:** Completion of meaningful work units with a story

**Update Frequency:** 1-5 times per week during active development

**Update When:**
- ✅ **Epic completed** - Major feature or initiative finished
- ✅ **Key bug fixed** - Bug that required investigation, had interesting root cause, or taught a lesson
- ✅ **Architectural change made** - Significant design or structure decision
- ✅ **PRD section completed** - Major requirement or feature spec finished
- ✅ **Major milestone reached** - Version release, deployment, launch
- ✅ **Pivot or strategy change** - Direction change, scope adjustment
- ✅ **Learning moment** - Discovered something important, failed experiment, insight gained
- ✅ **Technical decision made** - Chose between alternatives (may warrant ADR)
- ✅ **User feedback integrated** - Feedback that changed direction or approach
- ✅ **Problem solved** - Overcame significant challenge or blocker

**Update Format:** Situation/Challenge/Decision/Impact/Files structure
```markdown
### YYYY-MM-DD: Entry Title

**Situation:** Context and prompt for work
**Challenge:** Problem that needed solving
**Decision:** What you decided to do
**Impact:** What changed as a result
**Files:** Affected files
```

**Best Practice:** Update DEVLOG when you have a story to tell. Group related changes under a single narrative entry. Don't create entries for routine changes.

**Why Strategic Updates:** DEVLOG is the narrative record. It tells the story of WHY, not just WHAT. Only update when there's meaningful context, reasoning, or insight to capture.

**Don't Update DEVLOG For:**
- ❌ Routine bug fixes with no interesting story
- ❌ Minor refactoring or cleanup
- ❌ Dependency updates (unless they caused issues)
- ❌ Typo fixes or formatting changes
- ❌ Changes already well-documented in CHANGELOG

**⚠️ DEVLOG does NOT own Current Context.**

Current Context (version, branch, phase, objectives, stack, ADR index) lives exclusively in **`logs/STATE.md`**. DEVLOG is narrative-only: the story of why decisions were made. No Current Context section belongs here.

When multiple agents work on the same codebase, they read **STATE.md** — not DEVLOG — to synchronize on version, branch, and objectives. This keeps coordination lightweight (<500 tokens) and separates the "now" from the historical narrative.

**Coordination workflow (multi-agent):**

```markdown
# Agent A:
1. Read STATE.md (verify version, branch, objectives, last session notes)
2. Do work
3. Update STATE.md Current Context + Last Session if anything changed
4. Commit changes

# Agent B (starting work later):
1. Read STATE.md (sees Agent A's updates)
2. Knows current state without asking
3. Continues work with correct context
```

> See [STATE.md - Update Continuously During Active Work](#statemd---update-continuously-during-active-work) for the full update workflow.

---

### PRD - Update Daily (Minimum)

**Update Trigger:** Any change to requirements, scope, or specifications

**Update Frequency:** At least once per day during active development; immediately for significant changes

**Update When:**
- ✅ **End of each day** - Capture any requirement clarifications or scope changes
- ✅ **Epic completed** - Mark Epic as done, update status
- ✅ **Section finished** - Complete a major PRD section (requirements, user stories, etc.)
- ✅ **Requirements clarified** - Stakeholder feedback, user research, team discussion
- ✅ **Scope changed** - Features added, removed, or modified
- ✅ **User stories added/modified** - New stories or acceptance criteria changes
- ✅ **Success metrics updated** - KPIs, targets, or measurement criteria change
- ✅ **Planned structure evolved** - Roadmap, phases, or timeline adjusted
- ✅ **Dependencies identified** - New technical or business dependencies discovered
- ✅ **Risks identified** - New risks or constraints discovered
- ✅ **Stakeholder feedback** - Input from product, business, or users

**Update Format:** Depends on PRD structure (requirements, user stories, acceptance criteria, etc.)

**Best Practice:**
- **Minimum:** Review and update PRD at end of each day
- **Ideal:** Update PRD immediately when requirements change
- **Critical:** Update PRD before starting implementation of new features

**Why Daily Updates:** PRD is the source of truth for "what we're building." It must stay current so the team (and AI agents) always know the current requirements and scope.

**Version Control:** Consider versioning PRD sections (v1.0, v1.1, etc.) for major changes.

---

### STATE.md - Update Continuously During Active Work

**Update Trigger:** Start/end of work sessions, progress updates, blockers

**Update Frequency:** Every 30-60 minutes during active development

**Update When:**
- ✅ **Start of work session** - Add yourself to "Active Work" section
- ✅ **Every 30-60 minutes** - Update progress during active work
- ✅ **When blocked** - Immediately add to "Blockers" section
- ✅ **When unblocked** - Remove from "Blockers" section
- ✅ **End of work session** - Move task to "Recently Completed" with timestamp
- ✅ **After 24 hours** - Archive "Recently Completed" items to CHANGELOG
- ✅ **Branch status changes** - Update when pushing commits or merging

**Update Format:** Bullet points with agent/developer name, branch, and specific task
```markdown
- **Agent-1** (feature/auth): Adding OAuth2 PKCE flow with token rotation
```

**Best Practice:**
- Read STATE.md FIRST before starting any work
- Update immediately, don't batch updates
- Be specific about what you're working on
- Include timestamps for completed items
- Keep under 500 tokens (archive old items to CHANGELOG)

**Why Continuous Updates:** STATE.md is the single source for current context. It prevents duplicate work and merge conflicts, and it means any agent — solo or in a multi-agent setup — can resume work instantly without reading CHANGELOG or DEVLOG history.

---

### ADRs - Create When Needed, Rarely Update

**Update Trigger:** Significant architectural decisions

**Update Frequency:** 1-10 times per project (infrequent)

**Create ADR When:**
- ✅ **Technology choice** - Database, framework, language, platform
- ✅ **Architecture pattern** - Microservices, monolith, event-driven, etc.
- ✅ **Security decision** - Authentication, authorization, encryption approach
- ✅ **API design** - REST vs GraphQL, versioning strategy, contract design
- ✅ **Data model decision** - Schema design, normalization, storage strategy
- ✅ **Integration approach** - How to integrate with external systems
- ✅ **Breaking change** - Change that affects existing functionality or contracts
- ✅ **Performance strategy** - Caching, optimization, scaling approach
- ✅ **Deployment model** - Cloud provider, hosting, CI/CD strategy

**Update ADR When:**
- ✅ **Status changes** - Accepted → Superseded, Proposed → Rejected
- ✅ **Superseded by new ADR** - Add reference to new ADR
- ⚠️ **Rarely modify content** - ADRs are historical records, not living documents

**Update Format:** ADRs are mostly immutable. Create new ADRs to supersede old ones rather than editing.

**Best Practice:**
- Create ADR before or immediately after making the decision
- Link to ADR from CHANGELOG and DEVLOG entries
- Update ADR index (README.md) when creating new ADRs

**Why Infrequent:** ADRs document point-in-time decisions. They're historical records, not evolving specifications. Create new ADRs to supersede old ones rather than editing existing ADRs.

---

### Update Workflow Summary

| Document | Frequency | Trigger | Update Immediately? |
|----------|-----------|---------|---------------------|
| **CHANGELOG** | Multiple/day | Any code change | ✅ Yes - after each commit |
| **DEVLOG** | 1-5/week | Epic/milestone/decision | ⚠️ When story is complete |
| **STATE** | Every 30-60 min | Work session start/end/progress | ✅ Yes - during active work |
| **PRD** | Daily minimum | Requirements change | ✅ Yes - or end of day |
| **ADR** | 1-10/project | Architectural decision | ✅ Yes - when decision made |

### Daily Workflow Example

**Morning:**
1. **Read STATE.md** - Check current work, blockers, and priorities
2. Review PRD - What are we building today?
3. Check CHANGELOG - What changed recently?
4. Read DEVLOG - Why did we make recent decisions?
5. **Update STATE.md** - Add yourself to "Active Work" section

**During Development:**
1. Make code changes
2. Commit code
3. **Update CHANGELOG** - Add entry for what changed
4. **Update STATE.md** - Update progress every 30-60 minutes
5. Continue working

**End of Day:**
1. **Update STATE.md** - Move your work to "Recently Completed" with timestamp
2. **Update PRD** - Capture any requirement changes or clarifications
3. **Update DEVLOG** (if applicable) - If you completed an Epic, fixed a key bug, or made an architectural decision
4. **Create ADR** (if applicable) - If you made a significant architectural decision
5. Commit all documentation updates

**End of Week:**
1. Review all five documents for consistency
2. Verify cross-links are working
3. Check token counts (if approaching limits)
4. Archive old STATE.md "Recently Completed" items to CHANGELOG

---

## Maintenance Workflow

### When to Archive/Condense Logs

**Triggers:**
1. **Token count exceeds budget** (>25,000 tokens combined for CHANGELOG + DEVLOG)
2. **File length exceeds threshold** (>1,500 lines)
3. **Quarterly maintenance** (every 3 months)
4. **Before major milestones** (releases, audits)

### How to Condense

The deterministic, work-aware way to shed old context is `lfg archive` (see the
[Archival section](#archival-lfg-archive) below) — it moves the right entries to
`logs/archive/` for you and protects in-flight work. Use this manual workflow only
for one-off content rewrites the CLI doesn't cover (e.g. rewording verbose legacy
entries or extracting ADRs).

**Step 1: Create Safety Snapshot**
```bash
git add logs/CHANGELOG.md logs/DEVLOG.md
git commit -m "Pre-transformation snapshot: CHANGELOG + DEVLOG"
```

**Step 2: Archive Old Entries**
```bash
python .log-file-genius/product/scripts/lfg.py archive --dry-run   # preview
python .log-file-genius/product/scripts/lfg.py archive             # apply
```

**Step 3: Transform Remaining Entries (manual, optional)**
- **CHANGELOG:** Convert verbose entries to single-line format
- **DEVLOG:** Convert long narratives to Situation/Challenge/Decision/Impact/Files format
- **Extract ADRs:** Move significant decisions to separate ADR files

**Step 4: Verify**
```bash
python .log-file-genius/product/scripts/lfg.py validate   # reports token counts + budget status
```

**Step 5: Commit**
```bash
git add logs/
git commit -m "Log transformation: Reduced from X to Y tokens"
```

### Archival Cadence

| File | Archive Trigger | What's Kept |
|------|----------------|-------------|
| CHANGELOG.md | >10,000 tokens | `[Unreleased]` + newest released versions that fit `keep_fraction * budget` |
| DEVLOG.md | >15,000 tokens | Newest entries that fit `keep_fraction * budget` (fit-the-budget) |
| STATE.md | Never archives | Trim/overwrite — STATE is a snapshot |
| ADRs | Never archive | All (loaded on-demand) |

### Archival (`lfg archive`)

Archival in LFG is **deterministic and work-aware**. When validators flag overage (CHANGELOG >10k, DEVLOG >15k, combined >25k), don't move entries manually — run:

```bash
python .log-file-genius/product/scripts/lfg.py archive --dry-run
```

The dry-run prints a plan: which version blocks (CHANGELOG) and which old entries (DEVLOG) would move, where they'd land, and what the new token counts would be. Review the plan, then apply with `lfg archive` (it'll prompt for confirmation), or `lfg archive --force` in scripts.

**What's protected:**
- CHANGELOG's `## [Unreleased]` section is **never** archived (it's in-flight work).
- DEVLOG keeps the **newest entries** that fit within 80% of its budget (`keep_fraction` in `archival:` block of `.logfile-config.yml`). Older entries go to the archive.
- STATE.md is a snapshot — it doesn't archive, it gets trimmed/overwritten.
- ADRs are decisions — they never archive.

**Archive files** land in `logs/archive/` with self-documenting names:
- `CHANGELOG-v0.1.0-to-v0.1.5.md` — version range moved.
- `DEVLOG-2025-10-15-to-2025-12-20.md` — entry date range.

Each source file retains a `## Archive` section with one bullet per archive file (relative link + summary).

**If `[Unreleased]` alone exceeds budget**, `lfg archive` refuses with exit 2 — you trim Unreleased manually. There is no `--force-include-unreleased` flag by design.

---

## Updating Log File Genius

Updates are **brownfield-safe**: the updater never clobbers content you own. Pull the
submodule and run the bundled updater:

```bash
cd .log-file-genius && git pull && cd ..
./.log-file-genius/product/scripts/update.sh      # update.ps1 on Windows
```

### AGENTS.md is merged, not overwritten

`AGENTS.md` (introduced in v0.3.0) is now maintained as a **marker-delimited managed
block** inside whatever `AGENTS.md` lives at your project root. Install and update merge
the LFG block; they no longer replace the file. The markers are HTML comments (invisible
in rendered markdown):

```
<!-- LFG:BEGIN v0.4.0 — DO NOT EDIT BETWEEN THESE MARKERS -->
...LFG-generated rules...
<!-- LFG:END -->
```

- **Anything outside the markers is yours** and is preserved across updates.
- **Do not edit between the markers** — that region is regenerated from `product/rules/`
  on every update; your edits there would be overwritten.
- If you already had a hand-authored `AGENTS.md` (e.g., a Codex/Aider file), the LFG block
  is prepended above your content. If you had a prior LFG-generated `AGENTS.md` (no
  markers — e.g. from v0.3.0), its body is regenerated; because there are no markers to
  tell your additions apart from old LFG content, the original is **saved to
  `AGENTS.md.bak` first** so anything you added can be recovered. After your first
  update the file has markers, so later updates only touch the marked region.

The merge runs automatically during install/update. You can also run it directly:

```bash
python .log-file-genius/product/scripts/lfg.py merge-agents-md --to AGENTS.md
```

It is idempotent — re-running on an up-to-date file writes nothing.

### Migrating a pre-v0.4.0 STATE.md

v0.3.0+ enforces a stricter STATE.md spec (canonical sections: Current Context, Active
Work, Blockers, etc.). If you upgraded from an older project, the updater may print:

```
STATE.md needs migration to v0.4.0 spec. Preview with: lfg migrate-state --dry-run
```

`lfg migrate-state` brings STATE.md into compliance deterministically — it keeps the
canonical sections and archives any extra content into a single one-time DEVLOG snapshot
entry (`### YYYY-MM-DD: STATE snapshot pre-v0.4.0 migration`) so nothing is lost. Preview,
then apply:

```bash
python .log-file-genius/product/scripts/lfg.py migrate-state --dry-run   # preview the plan
python .log-file-genius/product/scripts/lfg.py migrate-state             # confirm + apply
```

It is **one-shot**: once STATE.md is compliant (or the DEVLOG snapshot already exists),
re-running is a no-op. Use `--force` to skip the confirmation prompt in scripts.

### Where templates live

Templates ship in the submodule at `.log-file-genius/product/templates/` only — the
updater no longer creates a `templates/` directory at your project root. If a prior LFG
version left an LFG-installed root `templates/` behind, the updater moves it into
`.log-file-genius/.backups/` (user-authored templates that don't match shipped versions
are left untouched).

---

## Token Budget Management

### Target Budgets

| Document | Target | Hard Max | % of 200k Context |
|----------|--------|----------|-------------------|
| CHANGELOG.md | 5,000-8,000 | 10,000 | 2.5-4% |
| DEVLOG.md | 8,000-12,000 | 15,000 | 4-6% |
| STATE.md | <500 | 500 | <0.25% |
| Combined (CHANGELOG + DEVLOG) | 13,000-20,000 | 25,000 | 6.5-10% |
| ADRs (on-demand) | Variable | N/A | Loaded as needed |

### Token Estimation

**Rule of thumb:** 1 token ≈ 4 characters

**Calculation:**
```python
def estimate_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    char_count = len(content)
    return char_count // 4
```

### Monitoring

You don't need a DIY script — LFG ships token-budget validation. Run:

```bash
python .log-file-genius/product/scripts/lfg.py validate
```

It reports per-file token counts (CHANGELOG, DEVLOG, STATE) against their budgets
and flags anything over, using the same `chars / 4` heuristic shown above. When it
flags an overage, run `lfg archive --dry-run` to preview a fix.

---

## Problem/Solution Pairs

### Problem 1: Verbose Logs Exhaust Token Budget

**Symptoms:**
- CHANGELOG + DEVLOG consume 90-110k tokens
- AI agents can't load full project history
- Agents lack context for decisions

**Solution:**
- Transform to single-line entries (CHANGELOG)
- Use structured bullets (DEVLOG)
- Extract detailed decisions to ADRs
- **Result:** 94% token reduction (100k → 5k tokens)

### Problem 2: Losing Narrative Context

**Symptoms:**
- After condensing, logs become just facts
- Reasoning and insights are lost
- Can't understand "why" decisions were made

**Solution:**
- Preserve narrative in DEVLOG using Situation/Challenge/Decision/Impact format
- Keep reasoning and insights, remove redundancy
- Link to ADRs for detailed context
- **Result:** Story preserved, just told more quickly

### Problem 3: No Clear Distinction Between Documents

**Symptoms:**
- CHANGELOG and DEVLOG contain duplicate information
- Unclear which document to update
- Redundant entries across files

**Solution:**
- **CHANGELOG:** Facts only (what changed, which files)
- **DEVLOG:** Story only (why it changed, reasoning)
- **ADRs:** Decisions only (detailed architectural records)
- **Result:** Clear separation of concerns, no redundancy

### Problem 4: Broken Cross-Links

**Symptoms:**
- Links between documents don't work
- Relative paths incorrect
- Navigation broken

**Solution:**
- Use exact relative paths (`../adr/001-title.md`, not `ADR-001`)
- Test all links after transformation
- Add cross-linked frontmatter to all documents
- **Result:** Bidirectional navigation works perfectly

### Problem 5: Unknown When to Archive

**Symptoms:**
- Logs grow indefinitely
- No clear archival policy
- Token budget creeps up over time

**Solution:**
- Let the validators flag overage (`lfg validate` reports budget status)
- Run `lfg archive` — it keeps the newest entries that fit the budget and moves the rest
- Monitor monthly with `lfg validate`
- **Result:** Sustainable long-term maintenance

### Problem 6: Transformation Breaks Git History

**Symptoms:**
- After condensing, can't find old detailed entries
- Git history shows massive deletions
- No way to recover original content

**Solution:**
- Create git snapshot before transformation
- Commit with descriptive message
- Keep archive/ folder in git
- **Result:** Full history preserved, rollback possible

---

## Examples Directory

### Purpose

The `/examples` directory contains realistic, working examples of the log file system in action. These examples demonstrate best practices and provide reference implementations for your own projects.

### What's Included

**Sample Project: Task Management API**

A complete example showing 3 weeks of development on a REST API project:
- **CHANGELOG.md** - Realistic version history with features, fixes, and refactoring
- **DEVLOG.md** - Narrative entries showing project evolution and decision-making
- **STATE.md** - Current snapshot of active work and priorities
- **ADRs** - Architectural decisions (PostgreSQL choice, JWT auth, optimistic locking)

**Location:** `/examples/sample-project/`

### How to Use Examples

#### For Learning

1. **Read the narrative:** Start with `DEVLOG.md` to understand the project journey
2. **Study the structure:** See how entries are formatted and cross-linked
3. **Check token efficiency:** Notice how concise entries preserve meaning
4. **Review cross-links:** See how documents reference each other

#### For Reference

- **Copy entry formats:** Use as templates for your own entries
- **Understand conventions:** See naming, numbering, and organization patterns
- **Learn archival strategy:** See how old entries are moved to archives
- **Study ADR structure:** See how architectural decisions are documented

#### For Onboarding

- **New team members:** Point them to examples to learn the system quickly
- **AI agents:** Reference examples when formatting entries
- **Stakeholders:** Show how the system maintains history efficiently

### Key Takeaways from Examples

**CHANGELOG:**
- Single-line entries with file paths and PR links
- Categorized by Added/Changed/Fixed/Deprecated/Removed
- Archive entries older than 30 days

**DEVLOG:**
- Narrative structure: Situation → Challenge → Decision → Impact
- Entries are 150-250 words (concise but meaningful)
- Narrative-only; current context lives in STATE.md
- Links to ADRs for detailed decisions

**STATE.md:**
- Updated at start and end of work sessions
- Shows last 2-4 hours of activity
- Includes active work, blockers, and next priorities
- Kept under 500 tokens

**ADRs:**
- One decision per file with unique number
- Context, decision, consequences clearly separated
- Alternatives considered are documented
- Status tracked (Proposed, Accepted, Deprecated, Superseded)

### Adapting Examples for Your Project

1. **Copy the structure:** Use the same file organization and sections
2. **Customize content:** Replace with your project's actual data
3. **Adjust token budgets:** Scale up/down based on your project size
4. **Modify update cadence:** Adapt to your team's workflow

**See:** `/examples/README.md` for detailed guidance on using the examples

---

## Starter Templates

### Minimal CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../project/specs/PRD.md)** - Product requirements and specifications  
📖 **[DEVLOG](./DEVLOG.md)** - Why changes were made (narrative)  
🗂️ **[STATE](./STATE.md)** - Current context and session handoff  
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** This file contains facts about what changed. For current version/branch/objectives, read STATE.md. For reasoning and context, see DEVLOG.md.

---

## Version History

### [Unreleased]

#### Added
- Initial project setup

---

## References

- **PRD:** `../project/specs/PRD.md`
- **DEVLOG:** `./DEVLOG.md`
- **STATE:** `./STATE.md`
- **ADRs:** `./adr/README.md`
```

### Minimal DEVLOG.md

```markdown
# Development Log (DEVLOG)

A narrative chronicle of the project journey - the decisions, discoveries, and insights that shaped this project.

## Related Documents

📋 **[PRD](../project/specs/PRD.md)** - Product requirements and specifications  
📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history  
🗂️ **[STATE](./STATE.md)** - Current context and session handoff  
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** This file tells the story of *why* decisions were made. For current version/branch/objectives, read STATE.md first. For technical details of *what* changed, see CHANGELOG.md. For architectural decisions, see ADRs.

---

## Decisions (ADR Index) - Newest First

- **ADR-001 (YYYY-MM-DD):** [Decision Title] - [One-line summary] [→ Full ADR](./adr/001-decision-title.md)

---

## Daily Log - Newest First

### YYYY-MM-DD: Project Kickoff

**Situation:** [What was the context?]

**Challenge:** [What problem needed solving?]

**Decision:** [What did you decide to do?]

**Impact:** [What changed as a result?]

**Files:** `file1.py`, `file2.js`

---

## Version History

- **0.1.0** (YYYY-MM-DD) - Initial project setup

---

## References

- **PRD:** `../project/specs/PRD.md`
- **CHANGELOG:** `./CHANGELOG.md`
- **STATE:** `./STATE.md`
- **ADRs:** `./adr/README.md`
```

### Minimal STATE.md

```markdown
# Current State

**Last Updated:** YYYY-MM-DD HH:MM UTC
**Updated By:** [Your name/agent name] (main branch)

---

## Related Documents

📋 **[PRD](../project/specs/PRD.md)** - Product requirements and specifications
📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
📖 **[DEVLOG](./DEVLOG.md)** - Development narrative and decision rationale
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** Read this FIRST before starting any work. This file owns Current Context (version, branch, phase, objectives) and Last Session handoff. Update at the START and END of each work session.

---

## Current Context

**Version:** v0.1.0
**Branch:** main
**Phase:** Initial development

**Stack:**
- [Your tech stack here]

**Current Objectives:**
- [What you're working on now]

**Entry Points:**
- [Key files/modules here]

---

## Active Work

- **[Your name]** (main): [What you're currently working on]

---

## Blockers

- [List any blockers here, or write "None currently"]

---

## Recently Completed (Last 2-4 Hours)

- ✅ [Completed task] ([Your name], HH:MM)

---

## Next Priorities

1. [Next priority task]
2. [Second priority task]
3. [Third priority task]

---

## Branch Status

- **main**: Clean, all tests passing
- **[feature-branch]**: [X commits ahead, status]

---

## Last Session

**Date:** YYYY-MM-DD
**Completed:** [What was finished]
**In Progress:** [What was left in flight]
**Next:** [Recommended starting point]
**Notes:** [Any context to carry forward]

---

## Notes

- Keep this file under 500 tokens total
- Update every 30-60 minutes during active work
- Archive "Recently Completed" items older than 24 hours to CHANGELOG
- Current Context is owned here, not in CHANGELOG or DEVLOG
```

### Minimal ADR README.md

```markdown
# Architectural Decision Records (ADRs)

This directory contains records of architectural decisions made during the project.

## What is an ADR?

An Architectural Decision Record (ADR) captures an important architectural decision made along with its context and consequences.

## When to Create an ADR

Create an ADR for decisions that:
- Affect the structure, non-functional characteristics, dependencies, interfaces, or construction techniques
- Are difficult or expensive to reverse
- Have long-term impact on the project
- Involve significant tradeoffs

## ADR Index

### Active Decisions

- **[ADR-001](./001-decision-title.md)** (YYYY-MM-DD) - [One-line summary]

### Superseded Decisions

- None yet

## Template

See [ADR_template.md](../templates/ADR_template.md) for the standard format (path may vary; check your `.logfile-config.yml`).

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
```

---

## AI Assistant Rules — How They're Built

LFG ships AI assistant rules as **canonical fragments** in `product/rules/`. Each
fragment carries YAML frontmatter with a `targets` list (e.g., `claude-code`,
`augment`) that tells the installer which per-tool directories to write the rule
into. The installer walks every fragment and routes it automatically — no
per-tool copies to maintain.

The top-level `product/AGENTS.md` is **generated** (not hand-edited) by running
`python product/scripts/lfg.py generate`. Contributors edit fragments under
`product/rules/`, then regenerate; CI enforces this with `lfg generate --check`
on every PR. If you want per-tool output to change, edit the fragment and
regenerate — that's the only command you need.

---

## Quick Start Checklist

- [ ] Create directory structure (`logs/`, `logs/adr/`, `project/specs/`)
- [ ] Copy starter templates (CHANGELOG.md, DEVLOG.md, STATE.md, ADR README.md)
- [ ] Set token budget targets (CHANGELOG <10k, DEVLOG <15k, combined <25k, STATE <500)
- [ ] Add cross-links to all documents (frontmatter with relative paths)
- [ ] Monitor token budgets with `lfg validate` (ships with LFG — no DIY script needed)
- [ ] Configure `.logfile-config.yml` with your `paths` if not using `logs/` default
- [ ] Schedule quarterly maintenance (calendar reminder)
- [ ] Document project-specific conventions in templates

---

## Maintenance Schedule

| Task | Frequency | Action |
|------|-----------|--------|
| Check token counts | Monthly | Run `lfg validate` |
| Condense if needed | As needed | Run `lfg archive --dry-run` when >25k tokens combined (CHANGELOG + DEVLOG) |
| Archive old entries | Quarterly | Move entries >6 months old |
| Review ADR index | Quarterly | Update status, add cross-links |
| Update templates | Annually | Refine based on experience |

---

## Success Metrics

- ✅ CHANGELOG < 10,000 tokens; DEVLOG < 15,000 tokens; combined < 25,000 tokens
- ✅ AI agents can load full project history in <5% of context window
- ✅ All cross-links working
- ✅ Narrative preserved in DEVLOG
- ✅ Facts preserved in CHANGELOG
- ✅ Decisions documented in ADRs
- ✅ No redundancy between documents

---

**Last Updated:** 2026-06-01 (tracks Log File Genius v0.4.0)  
**License:** CC0 (Public Domain)


