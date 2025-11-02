# ADR-011: Single Folder Installation Structure

**Status:** Accepted  
**Date:** 2025-11-02  
**Deciders:** Clark Mackey  
**Tags:** #installation #ux #architecture

---

## Context

After implementing the automated installation system (ADR-010), users reported that the installation created too many items at the project root, reducing discoverability and cleanliness:

**Previous installation structure:**
```
project-root/
├── .log-file-genius/     (source submodule - hidden)
├── .augment/             (AI rules - required at root)
├── templates/            (templates - visible)
├── scripts/              (validation scripts - visible)
├── .git-hooks/           (git hooks - hidden)
└── .logfile-config.yml   (config - hidden)
```

**Total: 5-6 items at root** (depending on AI assistant)

### Problems Identified

1. **Root Folder Pollution:** Too many folders at project root reduces cleanliness
2. **Discoverability:** Users couldn't easily find what was installed
3. **Brownfield Support:** No way to specify existing log file locations
4. **Inconsistent Paths:** AI rules assumed fixed paths (`project/planning/` or `docs/planning/`)

### User Feedback

> "I don't like that it litters the root with new folder names. What is the fewest and smartest folder setup here?"

---

## Decision

**Install all distributable files to a single `log-file-genius/` folder at project root.**

### New Installation Structure

```
project-root/
├── .log-file-genius/          (source submodule - hidden, for updates)
├── log-file-genius/           (installed files - visible, ONE folder)
│   ├── templates/             (customizable templates)
│   ├── scripts/               (validation scripts)
│   └── git-hooks/             (git hook templates)
├── .logfile-config.yml        (config with paths - at root)
└── .augment/ or .claude/      (AI rules - required at root)
```

**Total: 3 items at root** (down from 5-6) ✅

### Key Changes

1. **Single Installation Folder:**
   - All distributable files go to `log-file-genius/` folder
   - Templates: `log-file-genius/templates/`
   - Scripts: `log-file-genius/scripts/`
   - Git hooks: `log-file-genius/git-hooks/`

2. **Brownfield Path Prompts:**
   - Installer prompts user for log file locations during installation
   - Defaults: `docs/planning/CHANGELOG.md`, `docs/planning/DEVLOG.md`, etc.
   - User can specify custom paths for existing projects

3. **Config-Based Paths:**
   - `.logfile-config.yml` includes `paths` section:
     ```yaml
     installation:
       folder: log-file-genius
     
     paths:
       changelog: docs/planning/CHANGELOG.md
       devlog: docs/planning/DEVLOG.md
       adr: docs/adr
       state: docs/STATE.md
     ```

4. **AI Rules Read Config:**
   - AI assistant rules read `.logfile-config.yml` to find log file locations
   - No more hardcoded paths in rules
   - Supports brownfield projects with existing documentation

### Items That Stay at Root

**Required at root (cannot be moved):**
- `.augment/` or `.claude/` - AI assistants require these at project root
- `.logfile-config.yml` - Config file (standard location)
- `.log-file-genius/` - Source submodule (hidden, for updates)

---

## Consequences

### Positive

1. **Cleaner Root:** Only 3 items at root instead of 5-6
2. **Better Discoverability:** All installed files in one obvious location
3. **Brownfield Support:** Users can specify existing log file locations
4. **Flexibility:** Config-based paths support any project structure
5. **Easier Updates:** Single folder to update/replace
6. **Clearer Ownership:** `log-file-genius/` folder clearly belongs to the system

### Negative

1. **Longer Paths:** Users type `log-file-genius/templates/` instead of `templates/`
   - **Mitigation:** Most users copy templates once, then customize
2. **Breaking Change:** Existing installations need migration
   - **Mitigation:** Cleanup script removes old folders, installer creates new structure
3. **Config Complexity:** AI rules must read config file
   - **Mitigation:** Clear documentation, default paths if config missing

### Neutral

1. **Folder Name:** Chose `log-file-genius/` (visible) over `.logfile/` (hidden)
   - **Rationale:** Users should see what's installed, not hide it
   - **Alternative considered:** `.logfile/` (hidden, minimal) - rejected as too hidden

---

## Alternatives Considered

### Option 1: Minimal Root (Reference Submodule Directly)

**Structure:**
```
.log-file-genius/          (source - contains everything)
.logfile-config.yml        (config with paths)
.augment/                  (AI rules)
```

**Total: 2-3 items at root** ✅

**Pros:**
- Absolute minimum at root
- No duplication

**Cons:**
- Users can't customize templates (they're in hidden `.log-file-genius/`)
- Harder to discover what's available
- Validation scripts harder to run (long paths)

**Rejected:** Too minimal, reduces customizability

### Option 2: Single Folder Installation (CHOSEN)

See "Decision" section above.

### Option 3: CLI Wrapper

**Structure:**
```
.log-file-genius/          (source)
.logfile-config.yml        (config)
.augment/                  (AI rules)
```

**Usage:**
```bash
logfile init              # Initialize log files
logfile validate          # Run validation
logfile template CHANGELOG  # Copy template
```

**Pros:**
- Cleanest root (2-3 items)
- Professional CLI experience
- Easy to use

**Cons:**
- Requires global npm/pip package installation
- More complex to maintain
- Overkill for simple file copying

**Rejected:** Too complex for the problem

### Option 4: Current Approach (Multiple Root Folders)

**Structure:**
```
templates/
scripts/
.git-hooks/
.augment/
.logfile-config.yml
.log-file-genius/
```

**Total: 5-6 items at root** ❌

**Rejected:** User feedback indicated this was too cluttered

---

## Implementation

### Files Changed

**Installer Scripts:**
- `product/scripts/install.ps1` - Updated to create `log-file-genius/` folder
- `product/scripts/install.sh` - Updated to create `log-file-genius/` folder
- Both scripts now prompt for log file paths and add to config

**AI Rules:**
- `product/starter-packs/augment/.augment/rules/log-file-maintenance.md` - Read config for paths
- `product/starter-packs/claude-code/.claude/rules/log-file-maintenance.md` - Read config for paths
- `product/starter-packs/claude-code/.claude/project_instructions.md` - Updated paths

**Documentation:**
- `README.md` - Updated "What gets installed" section
- `product/starter-packs/augment/README.md` - Updated paths
- `product/starter-packs/claude-code/README.md` - Updated paths

**Config Templates:**
- `product/starter-packs/augment/.logfile-config.yml` - Installer adds `paths` section dynamically
- `product/starter-packs/claude-code/.logfile-config.yml` - Installer adds `paths` section dynamically

### Migration Path

**For existing installations:**
1. Run cleanup script: `./.log-file-genius/product/scripts/cleanup.ps1`
2. Re-run installer: `./.log-file-genius/product/scripts/install.ps1`
3. Installer will prompt for log file locations
4. Old folders removed, new structure created

---

## Related

- **ADR-010:** Automated Installation System - Introduced the installer that this ADR improves
- **ADR-008:** Product/Project Separation - Established `/product/` for distribution
- **ADR-009:** Two-Branch Strategy - Established `main` branch for distribution

---

## Notes

- This decision was driven by direct user feedback during beta testing
- The single folder approach balances cleanliness with discoverability
- Brownfield support was a key requirement from enterprise users
- Config-based paths enable future flexibility (e.g., monorepo support)

---

**Last Updated:** 2025-11-02

