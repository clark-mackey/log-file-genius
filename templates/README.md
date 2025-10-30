# Log File System Templates

This directory contains templates for the token-efficient log file system. Copy these templates to start using the system in your own projects.

---

## Available Templates

### 1. CHANGELOG_template.md

**Purpose:** Technical record of changes to the codebase

**What it's for:**
- Tracking version history
- Recording what changed in each release
- Documenting file paths and PR links
- Maintaining semantic versioning

**Key features:**
- Single-line entries for token efficiency
- Categorized by Added/Changed/Fixed/Deprecated/Removed/Security
- Includes file paths and PR links
- Archive strategy for entries older than 30 days

**Token target:** <10,000 tokens (with archival)

**When to update:**
- After every commit (add to Unreleased section)
- When releasing a new version (move Unreleased to versioned section)

---

### 2. DEVLOG_template.md

**Purpose:** Narrative chronicle of the project journey

**What it's for:**
- Explaining why decisions were made
- Capturing insights and lessons learned
- Preserving project context and reasoning
- Telling the story of the project evolution

**Key features:**
- Situation/Challenge/Decision/Impact/Files structure
- Current Context section (source of truth for project state)
- ADR index for quick reference
- Narrative entries (150-250 words each)

**Token target:** <15,000 tokens (with archival)

**When to update:**
- After significant milestones or decisions
- Weekly update to Current Context section
- When completing epics or major features

---

### 3. ADR_template.md

**Purpose:** Detailed records of architectural decisions

**What it's for:**
- Documenting technology choices
- Recording security/privacy decisions
- Explaining API design choices
- Capturing tradeoffs and alternatives considered

**Key features:**
- Structured format (Context, Decision, Consequences, Alternatives)
- Immutable once written (status can change)
- Stable IDs (ADR-001, ADR-002, etc.)
- Status tracking (Proposed, Accepted, Deprecated, Superseded)

**Token target:** 400-600 tokens per ADR (loaded on-demand)

**When to create:**
- Technology choices (database, framework, architecture)
- Security/privacy decisions
- API design choices
- Breaking changes
- Decisions with long-term impact

---

### 4. STATE_template.md

**Purpose:** At-a-glance snapshot of current project state

**What it's for:**
- Multi-agent coordination
- Preventing duplicate work and merge conflicts
- Showing active work, blockers, and priorities
- Quick status checks

**Key features:**
- Ultra-lightweight (<500 tokens)
- Updated at start and end of work sessions
- Shows last 2-4 hours of activity
- Includes branch status for git workflows
- Recently completed items archived to CHANGELOG after 24 hours

**Token target:** <500 tokens

**When to update:**
- Start of work session (add to Active Work)
- Every 30-60 minutes during active work
- When blocked (add to Blockers)
- End of work session (move to Recently Completed)

**Note:** STATE.md is optional for single-developer projects. For multi-agent environments, it's highly recommended.

---

## How to Use These Templates

### Quick Start

1. **Copy templates to your project:**
   ```bash
   cp templates/CHANGELOG_template.md docs/planning/CHANGELOG.md
   cp templates/DEVLOG_template.md docs/planning/DEVLOG.md
   cp templates/STATE_template.md docs/planning/STATE.md
   cp templates/ADR_template.md docs/adr/ADR_template.md
   ```

2. **Customize the frontmatter:**
   - Update cross-links to match your directory structure
   - Adjust relative paths based on your file locations

3. **Remove template guidelines:**
   - Delete the "Template Guidelines" section at the bottom of each file
   - Keep only the actual template content

4. **Start documenting:**
   - Add your first CHANGELOG entry
   - Write your first DEVLOG entry
   - Create your first ADR when needed
   - Update STATE.md if using multi-agent workflow

### Directory Structure

Recommended file locations:

```
project-root/
├── docs/
│   ├── planning/
│   │   ├── CHANGELOG.md
│   │   ├── DEVLOG.md
│   │   └── STATE.md (optional)
│   ├── adr/
│   │   ├── README.md
│   │   └── 001-first-decision.md
│   └── specs/
│       └── PRD.md
└── templates/ (optional - keep for reference)
```

---

## Customization Tips

### Adjust Token Budgets

Scale token targets based on your project size:

**Small projects (<10k LOC):**
- CHANGELOG: <5,000 tokens
- DEVLOG: <8,000 tokens
- STATE: <300 tokens

**Medium projects (10k-100k LOC):**
- CHANGELOG: <10,000 tokens
- DEVLOG: <15,000 tokens
- STATE: <500 tokens

**Large projects (>100k LOC):**
- CHANGELOG: <15,000 tokens
- DEVLOG: <20,000 tokens
- STATE: <800 tokens

### Adjust Update Cadence

Adapt to your team's workflow:

**Solo developer:**
- CHANGELOG: After each commit
- DEVLOG: After milestones
- STATE: Optional (use DEVLOG Current Context instead)

**Small team (2-5 people):**
- CHANGELOG: After each commit
- DEVLOG: Weekly Current Context updates, entries after milestones
- STATE: Optional but helpful

**Multi-agent environment:**
- CHANGELOG: After each commit
- DEVLOG: Weekly Current Context updates, entries after milestones
- STATE: Critical - update every 30-60 minutes during active work

---

## Examples

See `/examples/sample-project/` for realistic examples of these templates in use:
- **CHANGELOG.md** - 3 weeks of version history
- **DEVLOG.md** - 7 narrative entries showing project evolution
- **STATE.md** - Current snapshot of active work
- **ADRs** - Architectural decisions with full context

---

## Documentation

For complete documentation on the log file system:

📖 **[Log File System How-To](../docs/log_file_how_to.md)** - Complete guide to the system

Key sections:
- [The Five-Document System](../docs/log_file_how_to.md#the-five-document-system)
- [Context Layers](../docs/log_file_how_to.md#context-layers---progressive-disclosure)
- [Entry Formats](../docs/log_file_how_to.md#entry-formats)
- [Update Cadence](../docs/log_file_how_to.md#update-cadence---when-to-update-each-document)
- [Token Budget Management](../docs/log_file_how_to.md#token-budget-management)

---

## Questions?

- **What's the difference between DEVLOG and CHANGELOG?**
  - CHANGELOG = What changed (facts only)
  - DEVLOG = Why it changed (narrative and reasoning)

- **When should I create an ADR?**
  - For decisions with long-term impact that are hard to reverse
  - Technology choices, security decisions, API design
  - Not for bug fixes or minor implementation details

- **Do I need STATE.md?**
  - Optional for solo developers (use DEVLOG Current Context instead)
  - Recommended for teams and multi-agent environments
  - Critical for preventing conflicts in concurrent workflows

- **How often should I archive old entries?**
  - CHANGELOG: Archive entries older than 30 days
  - DEVLOG: Archive entries older than 14 days
  - STATE: Archive to CHANGELOG after 24 hours

---

## License

These templates are released under CC0 (Public Domain). Use them freely in your projects.

