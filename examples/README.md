# Log File System Examples

This directory contains realistic examples of the log file system in action. These examples demonstrate how to use CHANGELOG, DEVLOG, STATE, and ADRs together to maintain project context efficiently.

---

## What's Included

### Sample Project: Task Management API

A realistic example showing 3 weeks of development on a REST API project for task management. This example demonstrates:

- **CHANGELOG.md** - 3 weeks of version history with realistic feature additions, bug fixes, and refactoring
- **DEVLOG.md** - 7 narrative entries showing project evolution, challenges, and decision-making
- **STATE.md** - Current snapshot showing active work, blockers, and next priorities
- **ADRs** - Architectural decision records for key technical choices

**Project Context:** A team building a task management REST API with user authentication, real-time updates, and mobile app support. The example shows realistic challenges like database performance issues, API versioning decisions, and authentication flow changes.

---

## How to Use These Examples

### For Learning

1. **Start with DEVLOG.md** - Read the narrative to understand the project journey
2. **Check CHANGELOG.md** - See how technical changes are documented concisely
3. **Review STATE.md** - Understand the current state snapshot format
4. **Read ADRs** - See how architectural decisions are documented in detail

### For Reference

- **Entry formats** - Copy the structure and style for your own projects
- **Token efficiency** - See how to keep entries concise while preserving meaning
- **Cross-linking** - Notice how documents reference each other
- **Archival strategy** - See how old entries are moved to archives

### For Onboarding

- **New team members** - Point them to these examples to understand the system
- **AI agents** - Use as reference for how to format entries
- **Stakeholders** - Show how the system maintains project history efficiently

---

## Key Takeaways from the Examples

### CHANGELOG Best Practices

- ✅ Single-line entries with file paths and PR links
- ✅ Categorized by Added/Changed/Fixed/Deprecated/Removed
- ✅ Version numbers follow semantic versioning
- ✅ Archive entries older than 30 days

### DEVLOG Best Practices

- ✅ Narrative structure: Situation → Challenge → Decision → Impact
- ✅ Entries are 150-250 words (concise but meaningful)
- ✅ Current Context section updated weekly
- ✅ Links to ADRs for detailed decisions
- ✅ Archive entries older than 14 days

### STATE.md Best Practices

- ✅ Updated at start and end of work sessions
- ✅ Shows last 2-4 hours of activity
- ✅ Includes active work, blockers, and next priorities
- ✅ Kept under 500 tokens for quick loading
- ✅ Recently completed items archived to CHANGELOG after 24 hours

### ADR Best Practices

- ✅ One decision per file with unique number
- ✅ Context, decision, consequences clearly separated
- ✅ Alternatives considered are documented
- ✅ Status tracked (Proposed, Accepted, Deprecated, Superseded)
- ✅ Cross-referenced from DEVLOG and CHANGELOG

---

## Token Budget Comparison

### Traditional Verbose Logs
- **Total:** ~90,000-110,000 tokens (45-55% of AI context window)
- **Result:** AI agents can't load full project history

### This System (Example Project)
- **CHANGELOG:** ~2,800 tokens
- **DEVLOG:** ~4,200 tokens
- **STATE:** ~450 tokens
- **ADRs (3 files):** ~2,100 tokens
- **Total:** ~9,550 tokens (<5% of AI context window)
- **Savings:** ~93% reduction in token usage

---

## Adapting for Your Project

### Single Developer Projects

- **STATE.md** - Optional, use DEVLOG Current Context instead
- **CHANGELOG** - Essential for version tracking
- **DEVLOG** - Essential for narrative and decision context
- **ADRs** - Use for significant architectural decisions only

### Multi-Agent Environments

- **STATE.md** - Critical for coordination
- **CHANGELOG** - Essential, update after every commit
- **DEVLOG** - Essential, update after milestones
- **ADRs** - Use for all architectural decisions

### Large Teams

- **STATE.md** - Update every 30-60 minutes during active work
- **CHANGELOG** - Automated via CI/CD if possible
- **DEVLOG** - Weekly updates to Current Context, daily entries for significant events
- **ADRs** - Formal review process before acceptance

---

## Next Steps

1. **Copy templates** from `/templates` directory
2. **Customize** for your project structure and workflow
3. **Start small** - Begin with CHANGELOG and DEVLOG, add STATE.md and ADRs as needed
4. **Iterate** - Adjust entry formats and update cadence based on your team's needs

---

## Questions?

See the full documentation: [Log File System How-To](../docs/log_file_how_to.md)

