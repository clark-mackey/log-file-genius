## 2024-12-15 - Added Native Claude Code Support

**Context:** Log File Genius had Augment support but lacked native Claude Code integration, despite Claude Code being a primary target audience.

**Narrative:** 
Analyzed Claude Code best practices from Anthropic's engineering blog and community resources. Key insight: Claude Code uses a hierarchical memory system with CLAUDE.md at root, .claude/rules/ for conditional rules, and .claude/commands/ for slash commands. 

The existing Augment rules pattern translates well, but Claude Code offers additional capabilities:
- Progressive disclosure via `@` imports reduces context bloat
- Conditional rules with `paths` frontmatter load only when relevant
- Hooks automate log maintenance workflows
- Slash commands provide direct access to logging operations

Implemented four slash commands matching core log operations. Added hooks for session lifecycle to enforce STATE.md discipline. Rules use paths frontmatter to only load when editing log files.

**Decisions Made:**
- Used `.claude/` directory (not root CLAUDE.md only) for full feature access
- Kept hooks lightweight - prompts over enforcement
- Slash commands mirror existing workflow, not new patterns

**Related:**
- CHANGELOG: [Add entry for file additions]
- ADR: Consider ADR for choosing hooks.json structure
