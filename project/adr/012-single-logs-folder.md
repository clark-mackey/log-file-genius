# ADR-012: Single /logs/ Folder for All Log Files

**Status:** Accepted
**Date:** 2025-11-04
**Deciders:** Clark Mackey
**Related:** ADR-011 (Single Folder Installation), ADR-010 (Hidden Source Folder), ADR-008 (Product/Project Separation)

---

## Context

The current installation creates log files in multiple locations based on user configuration (brownfield support). This creates several problems:

1. **Cognitive overhead** - Users must remember where each log file lives
2. **AI complexity** - AI rules need config-based path resolution, consuming tokens
3. **Installation errors** - Windows PowerShell errors, duplicate folder creation
4. **Troubleshooting difficulty** - Scattered files make debugging harder
5. **Inconsistent experience** - Brownfield vs greenfield installations differ significantly

The installer also created both `product/` and `project/` folders in `.log-file-genius/`, polluting the hidden folder with development meta-files that users don't need.

**User feedback:** "The install script errored on Windows and created both project and product folders. When I ran the installer from inside the new project, it duplicated everything."

---

## Decision

**Consolidate all log files into a single `/logs/` folder in the project root.**

### Standard Structure
```
logs/
  ├── CHANGELOG.md
  ├── DEVLOG.md
  ├── STATE.md
  ├── adr/
  │   └── *.md
  └── incidents/
      └── *.md
```

### Simplified Hidden Folder
```
.log-file-genius/
  ├── templates/
  ├── scripts/
  ├── ai-rules/
  ├── profiles/
  └── docs/
```

### AI Rules
- **No path configuration needed** - Always reference `/logs/CHANGELOG.md`, `/logs/DEVLOG.md`, etc.
- **Simpler rules** - Remove config-based path resolution logic
- **Fewer tokens** - Hardcoded paths are more efficient than dynamic lookups

### Brownfield Migration
- **User decides** - Installer does not attempt automatic migration
- **Migration guide provided** - Documentation explains how to move existing logs
- **No automatic detection** - Removes complexity from installer

---

## Consequences

### Positive
- **Single source of truth** - "All logs in `/logs/`" is easy to remember and communicate
- **Simpler AI rules** - No config-based path resolution, fewer tokens consumed
- **Cleaner root** - Only 3 items: `.log-file-genius/`, `/logs/`, `.logfile-config.yml`
- **Easier troubleshooting** - One place to look for all log files
- **Better AI performance** - Simpler rules = faster execution, fewer errors
- **Fixes Windows errors** - Simpler installer = fewer edge cases
- **Consistent experience** - Same structure for all users (greenfield and brownfield)
- **Cleaner hidden folder** - No `project/` meta-files in `.log-file-genius/`

### Negative
- **Breaking change** - Existing users must migrate (but we're pre-v1.0)
- **Less flexible** - Cannot customize log file locations (acceptable tradeoff)
- **Migration effort** - Users with existing installations must manually move files

### Neutral
- **Opinionated structure** - Some users may prefer different organization (but simplicity wins)
- **Folder proliferation** - Adds one folder to root (but consolidates multiple scattered files)

---

## Alternatives Considered

### Alternative 1: Keep config-based paths (current approach)
**Rejected because:**
- Too complex for the value provided
- Caused Windows installer errors
- Required more tokens in AI rules
- Created inconsistent user experience
- Harder to troubleshoot

### Alternative 2: Flat structure in root (no /logs/ folder)
**Rejected because:**
- Pollutes project root with 5+ files
- Harder to .gitignore as a group
- No clear "this is where logs live" signal
- Conflicts with user's existing files

### Alternative 3: Use project/ folder (like source code)
**Rejected because:**
- Confusing - "project" implies source code
- Conflicts with our own `project/` meta-directory
- Not intuitive for non-developers

### Alternative 4: Multiple folders (docs/, planning/, adr/)
**Rejected because:**
- Scatters related files across multiple locations
- Harder to remember where each file lives
- More complex .gitignore rules
- Defeats the "single source of truth" goal

---

## Notes

- This decision supersedes the brownfield path configuration from ADR-011
- The `.logfile-config.yml` file is simplified - no `paths` section needed
- All template frontmatter uses relative paths (already true, becomes even simpler)
- Installer scripts rewritten to be simpler and more robust
- Migration guide created for existing users
- This aligns with the "modular, lightweight, durable" design principle

**Implementation:**
- Flatten `product/` structure into `.log-file-genius/` root
- Remove `project/` from distribution entirely
- Update all templates to assume `/logs/` destination
- Rewrite install.sh and install.ps1 (simpler, no brownfield detection)
- Update AI rules to reference `/logs/` paths
- Update validation scripts for new structure
- Create migration guide

**Related Issues:**
- Windows PowerShell installer errors (fixed by simplification)
- Duplicate folder creation (fixed by removing `project/` from distribution)
- Token efficiency in AI rules (improved by removing config-based paths)

