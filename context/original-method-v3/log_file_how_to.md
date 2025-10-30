# Token-Efficient Log File System for AI-Assisted Projects

**Purpose:** A four-document system (PRD,CHANGELOG, DEVLOG, ADRs) that provides complete project context to AI agents while consuming <5% of their context window.

**Target Audience:** Development teams using AI coding assistants (Claude, GitHub Copilot, etc.) who need to maintain project history without exhausting token budgets.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [The Four-Document System](#the-four-document-system)
3. [Cross-Linking Best Practices](#cross-linking-best-practices)
4. [File Structure](#file-structure)
5. [Entry Formats](#entry-formats)
6. [Update Cadence](#update-cadence---when-to-update-each-document)
7. [Maintenance Workflow](#maintenance-workflow)
8. [Token Budget Management](#token-budget-management)
9. [Problem/Solution Pairs](#problemsolution-pairs)
10. [Starter Templates](#starter-templates)

---

## System Overview

### The Problem

Traditional project documentation becomes verbose over time:
- **Verbose logs:** 90-110k tokens (45-55% of AI context window)
- **Result:** AI agents can't load full project history
- **Impact:** Agents lack context, make uninformed decisions, repeat past mistakes

### The Solution

A token-efficient four-document system:
- **PRD:** What we're building (requirements, features, goals)
- **CHANGELOG.md:** What changed (facts, files, versions)
- **DEVLOG.md:** Why it changed (narrative, reasoning, insights)
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

## The Four-Document System

### Overview

The complete documentation system consists of four interconnected documents:

1. **PRD (Product Requirements Document)** - "What we're building"
2. **CHANGELOG.md** - "What changed"
3. **DEVLOG.md** - "Why it changed"
4. **ADRs (Architectural Decision Records)** - "How we decided"

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

**Location:** `docs/specs/PRD.md` or `docs/specs/PRD-[Project-Name].md`

### CHANGELOG.md - "What Changed"

**Purpose:** Technical record of changes to the codebase  
**Format:** Single-line entries with file paths  
**Audience:** Developers, AI agents needing facts  
**Token Target:** ~1,500-2,000 tokens

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
- Conservative metadata parsing - `enhance_skill` reads body OR metadata; preserves unknown fields. Files: `enhance_skill.py`, `test_frontmatter_compliance.py`. See: [ADR-002](../adr/002-conservative-metadata-management.md)
```

### DEVLOG.md - "Why It Changed"

**Purpose:** Narrative chronicle of the project journey  
**Format:** Situation/Challenge/Decision/Impact/Files structure  
**Audience:** Team members, future maintainers, AI agents needing context  
**Token Target:** ~3,000-4,000 tokens

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
### 2025-10-29: Customer Onboarding with Existing Skills

**Situation:** First customer signed up with 15 existing skills created with other tools. Skills worked but didn't follow our conventions.

**Challenge:** Onboard without breaking existing skills, losing data, interfering with other tools, or requiring manual edits.

**Decision:** Built conservative metadata fallback parsing. `enhance_skill` reads from body (preferred) OR metadata (fallback). Critically, we only manage our fields and never delete unknown metadata. Codified in ADR-002.

**Why Conservative:** If we deleted unknown metadata, we'd break customers using other tools on the same skill files. Conservative approach enables ecosystem compatibility.

**Impact:** Smooth onboarding - bulk register with `register_all_skills`, optionally migrate with `enhance_skill`. No data loss, no manual editing.

**Files:** `enhance_skill.py`, `test_frontmatter_compliance.py`, `docs/pilot/onboarding-existing-skills.md`
```

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

| From Document | To PRD | To CHANGELOG | To DEVLOG | To ADRs | To Templates |
|---------------|--------|--------------|-----------|---------|--------------|
| **PRD** (`docs/specs/PRD.md`) | - | `../planning/CHANGELOG.md` | `../planning/DEVLOG.md` | `../adr/README.md` | `../planning/templates/` |
| **CHANGELOG** (`docs/planning/CHANGELOG.md`) | `../specs/PRD.md` | - | `./DEVLOG.md` | `../adr/README.md` | `./templates/` |
| **DEVLOG** (`docs/planning/DEVLOG.md`) | `../specs/PRD.md` | `./CHANGELOG.md` | - | `../adr/README.md` | `./templates/` |
| **ADR README** (`docs/adr/README.md`) | `../specs/PRD.md` | `../planning/CHANGELOG.md` | `../planning/DEVLOG.md` | - | `../planning/templates/` |
| **Individual ADR** (`docs/adr/001-title.md`) | `../specs/PRD.md` | `../planning/CHANGELOG.md` | `../planning/DEVLOG.md` | `./README.md` | `../planning/templates/` |

### Standard Frontmatter Template

**For PRD (`docs/specs/PRD.md`):**
```markdown
---
Related Documents:
- [CHANGELOG](../planning/CHANGELOG.md) - Technical changes and version history
- [DEVLOG](../planning/DEVLOG.md) - Why changes were made (narrative)
- [ADRs](../adr/README.md) - Architectural decision records
---
```

**For CHANGELOG (`docs/planning/CHANGELOG.md`):**
```markdown
---
Related Documents:
- [PRD](../specs/PRD.md) - Product requirements and specifications
- [DEVLOG](./DEVLOG.md) - Why changes were made (narrative)
- [ADRs](../adr/README.md) - Architectural decision records
- [Template](./templates/Changelog_template.md) - Entry format guide
---
```

**For DEVLOG (`docs/planning/DEVLOG.md`):**
```markdown
---
Related Documents:
- [PRD](../specs/PRD.md) - Product requirements and specifications
- [CHANGELOG](./CHANGELOG.md) - Technical changes and version history
- [ADRs](../adr/README.md) - Architectural decision records
- [Template](./templates/Devlog_template.md) - Entry format guide
---
```

**For ADR README (`docs/adr/README.md`):**
```markdown
---
Related Documents:
- [PRD](../specs/PRD.md) - Product requirements and specifications
- [CHANGELOG](../planning/CHANGELOG.md) - Technical changes and version history
- [DEVLOG](../planning/DEVLOG.md) - Why changes were made (narrative)
- [Template](../planning/templates/ADR_template.md) - Entry format guide
---
```

**For Individual ADRs (`docs/adr/001-title.md`):**
```markdown
---
Related Documents:
- [ADR Index](./README.md) - All architectural decisions
- [PRD](../specs/PRD.md) - Product requirements
- [CHANGELOG](../planning/CHANGELOG.md) - Technical changes
- [DEVLOG](../planning/DEVLOG.md) - Development narrative
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
├── docs/
│   ├── planning/
│   │   ├── CHANGELOG.md          # What changed (facts)
│   │   ├── DEVLOG.md             # Why it changed (story)
│   │   ├── templates/
│   │   │   ├── Changelog_template.md
│   │   │   ├── Devlog_template.md
│   │   │   └── ADR_template.md
│   │   └── archive/              # Old entries (if needed)
│   │       ├── CHANGELOG-2024-Q4.md
│   │       └── DEVLOG-2024-Q4.md
│   ├── adr/
│   │   ├── README.md             # ADR index
│   │   ├── 001-decision-title.md
│   │   ├── 002-decision-title.md
│   │   └── ...
│   └── specs/
│       ├── PRD.md                # Product requirements
│       └── ...
└── scripts/
    ├── condense_changelog.py     # Transformation script
    ├── condense_devlog.py        # Transformation script
    └── check_token_counts.py    # Monitoring script
```

### Document Relationships

**The Four Documents Work Together:**

```
┌─────────────────────────────────────────────────────────────┐
│                         PRD (Specs)                         │
│              "What we're building and why"                  │
│         Requirements, features, success metrics             │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌────────────────────────────┐
│   CHANGELOG (Planning) │◄────►│     DEVLOG (Planning)      │
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
```

**Navigation Flow:**
- PRD → CHANGELOG/DEVLOG (see what's been implemented)
- CHANGELOG → ADRs (get details on specific changes)
- DEVLOG → ADRs (understand decision context)
- ADRs → PRD/CHANGELOG/DEVLOG (see impact of decisions)

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

**⚠️ CRITICAL - Update Current Context Section:**

The **Current Context** section at the top of CHANGELOG.md must be kept current at all times, especially in multi-tenant development environments with multiple agents or developers working simultaneously.

**Update Current Context When:**
- ✅ **Version changes** - Immediately update version number after release/tag
- ✅ **Branch changes** - Update when switching primary development branch
- ✅ **Phase changes** - Update when moving to new development phase (alpha → beta → production)
- ✅ **Stack changes** - Update when adding/removing major technologies
- ✅ **Entry points change** - Update when key files/modules are added/moved/renamed
- ✅ **Objectives change** - Update when current work focus shifts

**Why This Matters in Multi-Agent Environments:**

When multiple agents or developers work on the same codebase:
- Agent A might be working on v0.6.4 while Agent B starts v0.7.0
- Agent A might be in "main" branch while Agent B is in "feature/new-api"
- Without current context, agents make assumptions based on stale information
- Stale context leads to merge conflicts, duplicate work, and wasted tokens

**Example Current Context Section:**
```markdown
## Current Context

**Version:** v0.6.4
**Branch:** main
**Phase:** Pilot customer onboarding

**Stack:**
- Python 3.11+ (MCP server, tools, scripts)
- Supabase (PostgreSQL + RLS for multi-tenant analytics)
- Claude Desktop (MCP client)

**Current Objectives:**
- Onboard 10 pilot customers with existing skills
- Collect feedback data for analytics

**Entry Points:**
- MCP Server: `core/mcp-server/src/server.py`
- Tools: `core/mcp-server/src/tools/`
- Database: `core/database/schema.sql`
```

**Update Frequency for Current Context:**
- **Minimum:** Daily review and update if anything changed
- **Ideal:** Immediately when version/branch/phase/objectives change
- **Critical:** Before starting new work session (verify context is current)

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

**⚠️ CRITICAL - Update Current Context Section:**

The **Current Context** section at the top of DEVLOG.md must be kept current at all times, especially in multi-tenant development environments with multiple agents or developers working simultaneously.

**Update Current Context When:**
- ✅ **Version changes** - Immediately update version number after release/tag
- ✅ **Branch changes** - Update when switching primary development branch
- ✅ **Phase changes** - Update when moving to new development phase
- ✅ **Stack changes** - Update when adding/removing major technologies
- ✅ **Objectives change** - Update when current work focus shifts
- ✅ **Entry points change** - Update when key files/modules are added/moved/renamed
- ✅ **ADRs created** - Update Decisions (ADR Index) section with new ADRs

**Why This Matters in Multi-Agent Environments:**

When multiple agents or developers work on the same codebase:
- **Context synchronization:** All agents need to know current version, branch, and objectives
- **Avoid duplicate work:** Agent A shouldn't start work Agent B just finished
- **Correct decision context:** Agents need to know which ADRs are active/superseded
- **Accurate objectives:** Agents should work toward current goals, not outdated ones
- **Token efficiency:** Stale context wastes tokens on incorrect assumptions

**Example Current Context Section:**
```markdown
## Current Context

**Version:** v0.6.4
**Branch:** main
**Phase:** Pilot customer onboarding & feedback loop optimization

**Stack:**
- Python 3.11+ (MCP server, tools, scripts)
- Supabase (PostgreSQL + RLS for multi-tenant analytics)
- Claude Desktop (MCP client)
- pytest (testing framework)

**Key Architectural Decisions:**
- [ADR-001](../adr/001-no-claude-file-system-access.md) - No Claude file system access
- [ADR-002](../adr/002-conservative-metadata-management.md) - Conservative metadata management
- [ADR-003](../adr/003-feedback-integration-into-workflow.md) - Feedback integration into workflow

**Current Objectives:**
- Onboard 10 pilot customers with existing skills
- Collect feedback data for skill improvement analytics
- Validate feedback loop with real usage

**Entry Points:**
- MCP Server: `core/mcp-server/src/server.py`
- Tools: `core/mcp-server/src/tools/`
- Database: `core/database/schema.sql`
- Scripts: `scripts/`
```

**Update Frequency for Current Context:**
- **Minimum:** Daily review and update if anything changed
- **Ideal:** Immediately when version/branch/phase/objectives/ADRs change
- **Critical:** Before starting new work session (verify context is current)
- **Multi-Agent:** Before and after each agent's work session

**Coordination in Multi-Agent Environments:**

```markdown
# Example workflow for Agent A:
1. Read DEVLOG Current Context (verify version, branch, objectives)
2. Do work
3. Update DEVLOG Current Context if anything changed (version, objectives, ADRs)
4. Commit changes

# Agent B (starting work later):
1. Read DEVLOG Current Context (sees Agent A's updates)
2. Knows current state without asking
3. Continues work with correct context
```

**Token Savings:** Keeping Current Context updated saves 100-200 tokens per agent session by eliminating the need to search for current state, ask clarifying questions, or make incorrect assumptions.

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
| **PRD** | Daily minimum | Requirements change | ✅ Yes - or end of day |
| **ADR** | 1-10/project | Architectural decision | ✅ Yes - when decision made |

### Daily Workflow Example

**Morning:**
1. Review PRD - What are we building today?
2. Check CHANGELOG - What changed recently?
3. Read DEVLOG - Why did we make recent decisions?

**During Development:**
1. Make code changes
2. Commit code
3. **Update CHANGELOG** - Add entry for what changed
4. Continue working

**End of Day:**
1. **Update PRD** - Capture any requirement changes or clarifications
2. **Update DEVLOG** (if applicable) - If you completed an Epic, fixed a key bug, or made an architectural decision
3. **Create ADR** (if applicable) - If you made a significant architectural decision
4. Commit all documentation updates

**End of Week:**
1. Review all four documents for consistency
2. Verify cross-links are working
3. Check token counts (if approaching limits)

---

## Maintenance Workflow

### When to Archive/Condense Logs

**Triggers:**
1. **Token count exceeds budget** (>25,000 tokens combined)
2. **File length exceeds threshold** (>1,500 lines)
3. **Quarterly maintenance** (every 3 months)
4. **Before major milestones** (releases, audits)

### How to Condense

**Step 1: Create Safety Snapshot**
```bash
git add docs/planning/CHANGELOG.md docs/planning/DEVLOG.md
git commit -m "Pre-transformation snapshot: CHANGELOG + DEVLOG"
```

**Step 2: Archive Old Entries (Optional)**
- Move entries >6 months old to `archive/` folder
- Keep recent entries (last 30-90 days) in main files
- Update cross-links

**Step 3: Transform Entries**
- **CHANGELOG:** Convert verbose entries to single-line format
- **DEVLOG:** Convert long narratives to Situation/Challenge/Decision/Impact/Files format
- **Extract ADRs:** Move significant decisions to separate ADR files

**Step 4: Verify**
```bash
python scripts/check_token_counts.py
```

**Step 5: Commit**
```bash
git add docs/
git commit -m "Log transformation: Reduced from X to Y tokens"
```

### Archival Cadence

| File | Archive Trigger | Keep in Main File |
|------|----------------|-------------------|
| CHANGELOG.md | >1,500 lines OR >2,000 tokens | Last 30-90 days |
| DEVLOG.md | >2,000 lines OR >4,000 tokens | Last 30-90 days |
| ADRs | Never archive | All (loaded on-demand) |

---

## Token Budget Management

### Target Budgets

| Document | Token Target | Max Tokens | % of 200k Context |
|----------|-------------|------------|-------------------|
| CHANGELOG.md | 1,500-2,000 | 3,000 | 1-1.5% |
| DEVLOG.md | 3,000-4,000 | 6,000 | 1.5-2% |
| Combined | 5,000-6,000 | 10,000 | 2.5-3% |
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

### Monitoring Script

Create `scripts/check_token_counts.py`:
```python
import os

def estimate_tokens(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(content) // 4

changelog_tokens = estimate_tokens('docs/planning/CHANGELOG.md')
devlog_tokens = estimate_tokens('docs/planning/DEVLOG.md')
total_tokens = changelog_tokens + devlog_tokens

print(f"CHANGELOG.md: ~{changelog_tokens:,} tokens")
print(f"DEVLOG.md: ~{devlog_tokens:,} tokens")
print(f"Total: ~{total_tokens:,} tokens")
print(f"Target: <10,000 tokens")
print(f"Status: {'✅ GOOD' if total_tokens < 10000 else '⚠️ NEEDS CONDENSING'}")
```

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
- Set clear triggers (token count, line count, time-based)
- Archive entries >6 months old
- Keep recent entries (30-90 days) in main files
- Monitor monthly with `check_token_counts.py`
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

## Starter Templates

### Minimal CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../specs/PRD.md)** - Product requirements and specifications  
📖 **[DEVLOG](./DEVLOG.md)** - Why changes were made (narrative)  
⚖️ **[ADRs](../adr/README.md)** - Architectural decision records  
📝 **[Template](./templates/Changelog_template.md)** - Entry format guide

> **For AI Agents:** This file contains facts about what changed. For reasoning and context, see DEVLOG.md.

---

## Current Context

**Version:** v0.1.0  
**Branch:** main  
**Phase:** Initial development

**Stack:**
- [Your tech stack here]

**Entry Points:**
- [Key files/modules here]

---

## Version History

### [Unreleased]

#### Added
- Initial project setup

---

## References

- **PRD:** `../specs/PRD.md`
- **DEVLOG:** `./DEVLOG.md`
- **ADRs:** `../adr/README.md`
- **Template:** `./templates/Changelog_template.md`
```

### Minimal DEVLOG.md

```markdown
# Development Log (DEVLOG)

A narrative chronicle of the project journey - the decisions, discoveries, and insights that shaped this project.

## Related Documents

📋 **[PRD](../specs/PRD.md)** - Product requirements and specifications  
📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history  
⚖️ **[ADRs](../adr/README.md)** - Architectural decision records

> **For AI Agents:** This file tells the story of *why* decisions were made. For technical details of *what* changed, see CHANGELOG.md. For architectural decisions, see ADRs.

---

## Current Context

**Version:** v0.1.0  
**Branch:** main  
**Phase:** Initial development

**Stack:**
- [Your tech stack here]

**Key Architectural Decisions:**
- [Link to ADRs as they're created]

**Current Objectives:**
- [What you're working on now]

**Entry Points:**
- [Key files/modules here]

---

## Decisions (ADR Index) - Newest First

- **ADR-001 (YYYY-MM-DD):** [Decision Title] - [One-line summary] [→ Full ADR](../adr/001-decision-title.md)

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

- **PRD:** `../specs/PRD.md`
- **CHANGELOG:** `./CHANGELOG.md`
- **ADRs:** `../adr/README.md`
- **Template:** `./templates/Devlog_template.md`
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

See [ADR_template.md](../planning/templates/ADR_template.md) for the standard format.

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
```

---

## Quick Start Checklist

- [ ] Create directory structure (`docs/planning/`, `docs/adr/`, `docs/specs/`)
- [ ] Copy starter templates (CHANGELOG.md, DEVLOG.md, ADR README.md)
- [ ] Create template files (`templates/Changelog_template.md`, etc.)
- [ ] Set up monitoring script (`scripts/check_token_counts.py`)
- [ ] Add cross-links to all documents
- [ ] Set token budget targets (CHANGELOG <2k, DEVLOG <4k)
- [ ] Schedule quarterly maintenance (calendar reminder)
- [ ] Document project-specific conventions in templates

---

## Maintenance Schedule

| Task | Frequency | Action |
|------|-----------|--------|
| Check token counts | Monthly | Run `check_token_counts.py` |
| Condense if needed | As needed | When >10k tokens combined |
| Archive old entries | Quarterly | Move entries >6 months old |
| Review ADR index | Quarterly | Update status, add cross-links |
| Update templates | Annually | Refine based on experience |

---

## Success Metrics

- ✅ Combined CHANGELOG + DEVLOG < 10,000 tokens
- ✅ AI agents can load full project history in <5% of context window
- ✅ All cross-links working
- ✅ Narrative preserved in DEVLOG
- ✅ Facts preserved in CHANGELOG
- ✅ Decisions documented in ADRs
- ✅ No redundancy between documents

---

**Last Updated:** 2025-10-29  
**Version:** 1.0  
**License:** CC0 (Public Domain)

