# ADR-013: Composable Installer Architecture

**Status:** Proposed
**Date:** 2025-11-06
**Deciders:** Clark Mackey
**Related:** ADR-010 (Hidden Source Folder), Epic 12-15 (upcoming features)

---

## Context

The current installer (`product/scripts/install.sh` and `install.ps1`) contains feature-specific logic that must be modified every time a new feature is added. This creates a brittle, non-modular architecture that violates DRY principles.

**Current Problems:**

1. **Every new feature requires installer changes:**
   - Epic 12 (Security): Must add code to copy `detect-secrets.sh`, update git hooks
   - Epic 13 (Validation): Must add code to copy `lint-logs.py`, update git hooks
   - Epic 15 (Governance): Must add code to copy new docs, update AI rules
   - Epic 17 (Incidents): Must add code to copy incident templates

2. **Git hooks are monolithic:**
   - Single `pre-commit` file contains all validation logic
   - Adding security checks requires editing the hook file
   - Can't selectively enable/disable features

3. **AI rules are monolithic:**
   - Single `log-file-maintenance.md` contains all rules
   - Adding new rules requires editing the file
   - Difficult to maintain as features grow

4. **Installer complexity grows linearly with features:**
   - Currently ~450 lines
   - Will exceed 1000 lines after Epic 12-17
   - Harder to maintain, test, and debug

**Goal:** Create a modular architecture where new features can be added without modifying the installer.

---

## Decision

We will adopt a **composable architecture** using the UNIX philosophy of small, independent pieces:

### 1. Composable Git Hooks (pre-commit.d/ Pattern)

**Main Hook** (`.git-hooks/pre-commit`) becomes a dispatcher that never changes:

```bash
#!/usr/bin/env bash
# Discovers and runs all hook scripts in pre-commit.d/

HOOK_DIR=".log-file-genius/product/git-hooks/pre-commit.d"

if [ -d "$HOOK_DIR" ]; then
    for hook in "$HOOK_DIR"/*.sh; do
        if [ -x "$hook" ]; then
            echo "Running $(basename "$hook")..."
            "$hook" || exit 1
        fi
    done
fi
```

**Feature Hooks** are auto-discovered:
- `pre-commit.d/01-validation.sh` - Existing validation (Epic 7)
- `pre-commit.d/02-security.sh` - Secrets detection (Epic 12)
- `pre-commit.d/03-lint.sh` - Log linting (Epic 13)

**Adding a new feature:** Just drop a new script in `pre-commit.d/`. No installer changes needed.

### 2. Modular AI Rules (Keep Monolithic with Clear Sections)

**Decision:** Keep AI rules in a single file but use clear section markers:

```markdown
# Log File Maintenance Rules

## Core Rules (Always Active)
[Base CHANGELOG/DEVLOG rules]

## Security Rules (Epic 12)
[Secrets detection, redaction guidance]

## Validation Rules (Epic 13)
[Post-commit verification, self-assessment]

## Governance Rules (Epic 15)
[Human-in-the-loop, ADR lifecycle]
```

**Rationale:** AI assistants read the entire file anyway, so splitting into includes adds complexity without benefit. Clear sections are sufficient for organization.

### 3. Installer as "Dumb Copier"

**Installer logic becomes:**

```bash
# Copy all templates
cp -r "$SOURCE_ROOT/templates/"* "$PROJECT_ROOT/logs/"

# Copy all scripts (validation, security, etc.)
cp -r "$SOURCE_ROOT/scripts/"* "$PROJECT_ROOT/.log-file-genius/product/scripts/"

# Copy all docs
cp -r "$SOURCE_ROOT/docs/"* "$PROJECT_ROOT/.log-file-genius/product/docs/"

# Copy git hooks (dispatcher + feature hooks)
cp -r "$SOURCE_ROOT/git-hooks/"* "$PROJECT_ROOT/.git-hooks/"

# Copy AI rules
cp -r "$SOURCE_ROOT/ai-rules/$AI_ASSISTANT/"* "$PROJECT_ROOT/.$AI_ASSISTANT/"
```

**No feature-specific logic.** Just recursive directory copying.

### 4. Profile-Based Feature Control (Optional)

Profiles can control which hooks are executable:

```yaml
# .logfile-config.yml
profile: solo-developer

features:
  core: true          # Always enabled
  security: true      # Epic 12
  validation: true    # Epic 13
  governance: false   # Epic 15 (optional for solo)
```

Installer reads profile and sets executable permissions accordingly:

```bash
# Enable/disable hooks based on profile
if [ "$SECURITY_ENABLED" = "true" ]; then
    chmod +x "$PROJECT_ROOT/.git-hooks/pre-commit.d/02-security.sh"
else
    chmod -x "$PROJECT_ROOT/.git-hooks/pre-commit.d/02-security.sh"
fi
```

---

## Consequences

### Positive

- **Zero installer changes for new features** - Just add files to `pre-commit.d/` or update AI rules
- **Modular and composable** - Features are self-contained and independent
- **Easier to test** - Each hook can be tested independently
- **Easier to debug** - Clear separation of concerns
- **Profile-aware** - Solo devs vs teams can enable different features
- **Follows UNIX philosophy** - Small, composable pieces
- **Familiar pattern** - `pre-commit.d/` is standard practice (systemd, cron, etc.)

### Negative

- **Requires refactoring** - Must restructure existing code (1-2 hours)
- **More files** - Multiple hook scripts instead of one monolithic file
- **Slightly more complex directory structure** - `pre-commit.d/` adds a level of nesting

### Neutral

- **AI rules stay monolithic** - Simpler than includes, but still organized
- **Installer is simpler** - But requires initial refactoring effort

---

## Alternatives Considered

### Alternative 1: Manifest-Based Architecture

**Approach:** Each feature has a `manifest.yml` describing what to install:

```yaml
# product/features/security/manifest.yml
name: security
files:
  scripts: [detect-secrets.sh, detect-secrets.ps1]
  docs: [SECURITY.md, security-redaction-guide.md]
  git-hooks: [pre-commit-security.sh]
```

**Rejected because:**
- Over-engineering for a lightweight tool
- Adds YAML parsing complexity
- Requires maintaining manifests in addition to files
- Not significantly better than composable hooks

### Alternative 2: Keep Monolithic (Status Quo)

**Approach:** Continue modifying installer for each new feature.

**Rejected because:**
- Installer will exceed 1000 lines after Epic 12-17
- Violates DRY and modularity principles
- Makes testing and debugging harder
- User explicitly requested modular architecture

### Alternative 3: Feature Flags Only

**Approach:** Use profile YAML to control which files to copy:

```yaml
features:
  security: true
  validation: true
```

Installer reads flags and conditionally copies files.

**Rejected because:**
- Still requires installer changes for new file types
- Doesn't solve the monolithic hook problem
- Less flexible than composable hooks

### Alternative 4: Install Hooks (Feature Self-Install)

**Approach:** Each feature has its own `install.sh` that handles copying:

```
product/features/security/install.sh
product/features/validation/install.sh
```

Main installer discovers and runs feature installers.

**Rejected because:**
- More complex than composable hooks
- Multiple scripts to maintain
- Harder to ensure consistency across features
- Over-engineering for current needs

---

## Notes

- **Implementation effort:** 1-2 hours to refactor existing code
- **Testing:** Verify existing validation hook still works after refactoring
- **Documentation:** Update `product/docs/architecture.md` with new structure
- **Epic 12-17 benefit:** Each epic just adds files, no installer changes
- **Inspiration:** UNIX `rc.d/`, systemd `*.d/`, git hooks, cron.d/

**Related Discussions:**
- User request: "I want to touch the installers as little as possible"
- Upcoming features in Epic 12-15 all require installer modifications
- Goal: Modular, lightweight, durable architecture

---

## Implementation Checklist

When implementing this ADR (Epic 18):

- [ ] Create `product/git-hooks/pre-commit.d/` directory
- [ ] Move existing validation to `01-validation.sh`
- [ ] Update main `pre-commit` to be a dispatcher
- [ ] Update installer to copy new structure
- [ ] Test that existing validation still works
- [ ] Update documentation with new architecture
- [ ] Verify PowerShell installer has same changes
- [ ] Update AI rules with clear section markers
- [ ] Test installation on clean project
- [ ] Update CHANGELOG and DEVLOG

