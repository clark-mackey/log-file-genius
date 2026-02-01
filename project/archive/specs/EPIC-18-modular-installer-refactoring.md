# Epic 18: Modular Installer Refactoring

**Status:** Not Started  
**Priority:** P0 - CRITICAL (Blocker for Epic 12-17 implementation)  
**Estimated Effort:** 1-2 hours  
**Dependencies:** None (foundational refactoring)  
**Related:** ADR-013 (Composable Installer Architecture)

---

## Epic Goal

Refactor the installer to use a composable architecture where new features can be added without modifying installer code. This enables Epic 12-17 to be implemented by simply adding files, not editing the installer.

**Problem Statement:** The current installer contains feature-specific logic that must be modified for every new feature. This is brittle, violates DRY principles, and will cause the installer to grow from ~450 lines to 1000+ lines after Epic 12-17.

**Inspiration:** UNIX philosophy of small, composable pieces. Patterns like `rc.d/`, `systemd/*.d/`, `cron.d/` where features are auto-discovered.

---

## Success Criteria

- [ ] Git hooks use composable `pre-commit.d/` pattern
- [ ] Installer is a "dumb copier" with no feature-specific logic
- [ ] Existing validation hook still works after refactoring
- [ ] Adding Epic 12 (Security) requires zero installer changes
- [ ] Both Bash and PowerShell installers refactored
- [ ] Documentation updated with new architecture
- [ ] All tests pass on Linux, macOS, Windows

---

## Task List

### Task 18.1: Create Composable Git Hooks Structure

**Goal:** Refactor git hooks to use dispatcher pattern with auto-discovered feature hooks.

**Steps:**
- [ ] Create `product/git-hooks/pre-commit.d/` directory
- [ ] Create main `product/git-hooks/pre-commit` dispatcher script (Bash):
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
- [ ] Create PowerShell version of dispatcher (`pre-commit.ps1`)
- [ ] Move existing validation logic to `pre-commit.d/01-validation.sh`
- [ ] Move existing validation logic to `pre-commit.d/01-validation.ps1`
- [ ] Make hook scripts executable (`chmod +x`)
- [ ] Test that validation still works

**Acceptance Criteria:**
- Main hook is <20 lines (dispatcher only)
- Validation hook runs automatically
- Adding new hooks requires no changes to main hook

---

### Task 18.2: Organize AI Rules with Clear Sections

**Goal:** Reorganize AI rules to use clear section markers for modularity.

**Steps:**
- [ ] Update `product/ai-rules/augment/log-file-maintenance.md`:
  - Add `## Core Rules (Always Active)` section
  - Add `## Security Rules (Epic 12)` placeholder section
  - Add `## Validation Rules (Epic 13)` placeholder section
  - Add `## Governance Rules (Epic 15)` placeholder section
- [ ] Update `product/ai-rules/claude-code/project_instructions.md` with same structure
- [ ] Add comments explaining section purpose
- [ ] Verify AI can still read and understand rules

**Acceptance Criteria:**
- Rules file has clear section markers
- Each section is self-contained
- Adding new sections requires no changes to existing sections

---

### Task 18.3: Simplify Installer to "Dumb Copier"

**Goal:** Remove feature-specific logic from installer, make it a generic directory copier.

**Steps:**
- [ ] Update `product/scripts/install.sh`:
  - Remove feature-specific copy logic
  - Replace with recursive directory copying
  - Copy `git-hooks/` directory (including `pre-commit.d/`)
  - Copy `ai-rules/` directory
  - Copy `templates/`, `scripts/`, `docs/` directories
- [ ] Update `product/scripts/install.ps1` with same changes
- [ ] Verify installer is <400 lines (down from ~450)
- [ ] Test installation on clean project
- [ ] Verify all files are copied correctly

**Acceptance Criteria:**
- Installer has no feature-specific logic
- Installer is <400 lines
- All existing features still work
- Installation passes validation

---

### Task 18.4: Add Profile-Based Feature Control (Optional)

**Goal:** Allow profiles to enable/disable features via executable permissions.

**Steps:**
- [ ] Add `features:` section to profile YAML template:
  ```yaml
  features:
    core: true          # Always enabled
    security: true      # Epic 12
    validation: true    # Epic 13
    governance: false   # Epic 15 (optional for solo)
  ```
- [ ] Update installer to read `features:` from profile
- [ ] Set executable permissions based on feature flags:
  ```bash
  if [ "$SECURITY_ENABLED" = "true" ]; then
      chmod +x "$HOOK_DIR/02-security.sh"
  else
      chmod -x "$HOOK_DIR/02-security.sh"
  fi
  ```
- [ ] Test enabling/disabling features via profile
- [ ] Document feature flags in profile guide

**Acceptance Criteria:**
- Profile can enable/disable features
- Disabled features don't run (not executable)
- Solo vs team profiles have different defaults

---

### Task 18.5: Update Documentation

**Goal:** Document the new composable architecture for future contributors.

**Steps:**
- [ ] Create `product/docs/architecture.md`:
  - Explain composable hooks pattern
  - Show directory structure
  - Provide examples of adding new features
  - Document profile-based feature control
- [ ] Update `INSTALL.md` with new structure
- [ ] Update `product/docs/how-to-add-features.md` (new file):
  - Step-by-step guide for adding features
  - Example: Adding Epic 12 (Security)
  - Show that no installer changes are needed
- [ ] Update `README.md` with architecture overview
- [ ] Add architecture diagram (optional)

**Acceptance Criteria:**
- Documentation explains composable architecture
- Clear guide for adding new features
- Examples show zero installer changes needed

---

### Task 18.6: Test Refactored Installer

**Goal:** Verify refactored installer works on all platforms.

**Steps:**
- [ ] Test on Linux (Ubuntu):
  - Fresh install on clean project
  - Verify all files copied
  - Verify validation hook runs
  - Run validation script
- [ ] Test on macOS:
  - Fresh install on clean project
  - Verify Bash 3.2 compatibility
  - Verify hooks run correctly
- [ ] Test on Windows:
  - Fresh install on clean project
  - Verify PowerShell installer works
  - Verify hooks run correctly
- [ ] Test profile-based feature control:
  - Install with `security: false`
  - Verify security hook is not executable
  - Enable security, verify hook runs
- [ ] Run CI/CD tests (GitHub Actions)
- [ ] Verify all tests pass

**Acceptance Criteria:**
- All platforms pass installation tests
- Validation hook runs on all platforms
- Profile-based control works
- CI/CD tests pass

---

### Task 18.7: Verify Epic 12 Readiness

**Goal:** Confirm that Epic 12 (Security) can be added without installer changes.

**Steps:**
- [ ] Create mock `pre-commit.d/02-security.sh` script:
  ```bash
  #!/usr/bin/env bash
  echo "Security check: PASS (mock)"
  exit 0
  ```
- [ ] Copy to `product/git-hooks/pre-commit.d/02-security.sh`
- [ ] Make executable (`chmod +x`)
- [ ] Run installer on test project
- [ ] Verify security hook runs automatically
- [ ] Verify NO installer changes were needed
- [ ] Delete mock script

**Acceptance Criteria:**
- Security hook runs without installer changes
- Dispatcher auto-discovers new hook
- Epic 12 can proceed with zero installer modifications

---

## Definition of Done

Per [DEFINITION-OF-DONE.md](DEFINITION-OF-DONE.md), this epic is complete when:

### Code Complete
- [ ] All tasks (18.1-18.7) completed
- [ ] Installer refactored to <400 lines
- [ ] Git hooks use composable pattern
- [ ] AI rules have clear section markers
- [ ] Profile-based feature control implemented

### Testing Complete
- [ ] Installation tested on Linux, macOS, Windows
- [ ] Existing validation hook still works
- [ ] Mock Epic 12 hook runs without installer changes
- [ ] CI/CD tests pass on all platforms
- [ ] Profile-based control tested

### Documentation Complete
- [ ] `product/docs/architecture.md` created
- [ ] `product/docs/how-to-add-features.md` created
- [ ] `INSTALL.md` updated
- [ ] `README.md` updated with architecture overview
- [ ] ADR-013 marked as "Accepted"

### Planning Files Updated
- [ ] CHANGELOG.md updated with refactoring entry
- [ ] DEVLOG.md updated with decision rationale
- [ ] Roadmap updated to mark Epic 18 complete
- [ ] Planning files committed with code changes

### Validation
- [ ] Validation script passes
- [ ] No secrets in logs
- [ ] Token counts within limits
- [ ] All files formatted correctly

---

## Risks & Mitigation

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Refactoring breaks existing validation | High | Thorough testing, keep backup | Planned |
| PowerShell dispatcher more complex | Medium | Use same pattern as Bash | Planned |
| Profile control adds complexity | Low | Make it optional, document well | Planned |
| CI/CD tests fail on macOS | Medium | Test locally first, fix line endings | Planned |

---

## Dependencies

**Blocks:**
- Epic 12 (Security) - Needs composable hooks
- Epic 13 (Validation) - Needs composable hooks
- Epic 15 (Governance) - Needs modular AI rules
- Epic 17 (Incidents) - Needs modular structure

**Blocked By:**
- None (foundational refactoring)

---

## Timeline

**Estimated Effort:** 1-2 hours (solo developer)

**Breakdown:**
- Task 18.1 (Composable Hooks): 30 minutes
- Task 18.2 (AI Rules): 15 minutes
- Task 18.3 (Installer): 30 minutes
- Task 18.4 (Profile Control): 15 minutes (optional)
- Task 18.5 (Documentation): 20 minutes
- Task 18.6 (Testing): 20 minutes
- Task 18.7 (Epic 12 Readiness): 10 minutes

**Total:** ~2.5 hours (with buffer)

---

## Success Metrics

- [ ] Installer reduced from ~450 lines to <400 lines
- [ ] Zero installer changes needed for Epic 12-17
- [ ] All tests pass on Linux, macOS, Windows
- [ ] Documentation clearly explains new architecture
- [ ] Epic 12 can proceed immediately after completion

---

## Notes

- **Quick win:** This is a small refactoring with huge long-term benefits
- **Pays for itself:** Saves 30+ minutes per epic (Epic 12-17 = 2+ hours saved)
- **Low risk:** Existing validation hook is the only feature to migrate
- **High impact:** Enables all future epics to be feature-focused, not installer-focused

**Related:**
- ADR-013: Composable Installer Architecture
- Epic 12-17: All benefit from this refactoring
- User request: "I want to touch the installers as little as possible"

