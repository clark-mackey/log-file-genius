# Profile Configuration Schema

**Version:** 1.0  
**Status:** Draft  
**Related:** ADR-007 (Agent OS-Inspired Enhancements), Epic 8 (Profile System)

---

## Overview

The profile system enables different project types to use optimized configurations of the Log File Genius methodology. Profiles configure token targets, required files, update frequency, validation strictness, and archival thresholds to match different development contexts.

**Design Principles:**
- **Simple:** Single YAML file, 3-4 predefined profiles
- **Modular:** Users can customize any setting
- **Optional:** Default profile works for everyone
- **Lightweight:** No complex configuration management

---

## Configuration File Location

**Default location:** `project-root/.logfile-config.yml`

**Alternative locations** (checked in order):
1. `.logfile-config.yml` (project root)
2. `config/logfile.yml`
3. `.config/logfile.yml`

If no config file exists, the system uses the **default profile** (solo-developer).

---

## Schema Definition

### Top-Level Structure

```yaml
# Profile selection
profile: solo-developer  # Options: solo-developer, team, open-source, startup

# Optional: Override specific settings
overrides:
  token_targets:
    changelog_warning: 8000
    changelog_error: 10000
  required_files:
    - CHANGELOG
    - DEVLOG
  validation:
    strictness: warnings-only
```

---

## Profile Settings

Each profile configures the following settings:

### 1. Token Targets

Token limits for each file type, with warning (80%) and error (100%) thresholds.

```yaml
token_targets:
  # CHANGELOG limits
  changelog_warning: 8000      # Warn at 80% of target
  changelog_error: 10000       # Error at 100% of target
  
  # DEVLOG limits
  devlog_warning: 12000        # Warn at 80% of target
  devlog_error: 15000          # Error at 100% of target
  
  # Combined limits (CHANGELOG + DEVLOG)
  combined_warning: 20000      # Warn at 80% of target
  combined_error: 25000        # Error at 100% of target
  
  # STATE limits (optional file)
  state_warning: 400           # Warn at 80% of target
  state_error: 500             # Error at 100% of target
```

**Rationale:** Different project types have different documentation needs. Solo developers can be more flexible, while teams need consistency.

---

### 2. Required Files

Which of the 5 core files are mandatory vs. optional.

```yaml
required_files:
  - CHANGELOG      # Always required (all profiles)
  - DEVLOG         # Required for team/open-source, optional for solo/startup
  - STATE          # Optional (all profiles)
  - ADR            # Required for team/open-source, optional for solo/startup
  - PRD            # Optional (all profiles)
```

**Options:**
- `CHANGELOG` - Always required (all profiles)
- `DEVLOG` - Required or optional depending on profile
- `STATE` - Optional (all profiles)
- `ADR` - Required or optional depending on profile
- `PRD` - Optional (all profiles)

**Rationale:** Solo developers and startups can skip DEVLOG for minor changes. Teams and open-source projects need consistent documentation.

---

### 3. Update Frequency

How often each file should be updated.

```yaml
update_frequency:
  changelog: every-commit       # Options: every-commit, daily, weekly
  devlog: significant-changes   # Options: every-commit, significant-changes, milestones-only, optional
  state: daily                  # Options: every-commit, daily, weekly, optional
  adr: as-needed                # Options: as-needed (always)
  prd: as-needed                # Options: as-needed (always)
```

**Options:**
- `every-commit` - Update on every commit
- `daily` - Update at least once per day
- `weekly` - Update at least once per week
- `significant-changes` - Update for features, breaking changes, major fixes
- `milestones-only` - Update only for major milestones
- `optional` - Update when relevant
- `as-needed` - Update when creating/modifying (ADR, PRD)

**Rationale:** Different files have different update cadences. CHANGELOG is always updated per commit, but DEVLOG frequency varies by project type.

---

### 4. Validation Strictness

How strictly to enforce validation rules.

```yaml
validation:
  strictness: errors            # Options: strict, errors, warnings-only, disabled
  
  # Format validation
  format_validation: true       # Validate CHANGELOG/DEVLOG format
  
  # Token validation
  token_validation: true        # Validate token counts
  
  # Cross-link validation
  crosslink_validation: false   # Validate cross-references (future)
  
  # Fail on warnings
  fail_on_warnings: false       # Treat warnings as errors
```

**Strictness Options:**
- `strict` - Enforce all rules, fail on warnings
- `errors` - Enforce format and token errors, allow warnings
- `warnings-only` - Show warnings but never fail validation
- `disabled` - Skip validation entirely

**Rationale:** Solo developers want flexibility (warnings-only), teams need consistency (errors), open-source needs strict formatting (strict).

---

### 5. Archival Thresholds

When to archive old entries to maintain token efficiency.

```yaml
archival:
  # Time-based archival
  changelog_age_days: 30        # Archive CHANGELOG entries older than X days
  devlog_age_days: 14           # Archive DEVLOG entries older than X days
  
  # Token-based archival
  auto_archive_on_warning: false  # Automatically archive when hitting warning threshold
  auto_archive_on_error: true     # Automatically archive when hitting error threshold
  
  # Archive location
  archive_directory: project/planning/archive  # Where to store archived entries
```

**Rationale:** Different projects have different archival needs. Fast-moving startups archive more frequently, established projects keep longer history.

---

### 6. AI Assistant Behavior

How AI assistants should behave when maintaining log files.

```yaml
ai_assistant:
  # Proactive updates
  proactive_updates: true       # AI should proactively update planning files
  
  # Confirmation required
  require_confirmation: false   # Ask before updating planning files
  
  # Show pre-commit checklist
  show_checklist: true          # Display checklist before commits
  
  # Suggest validation
  suggest_validation: true      # Suggest running validation before commits
```

**Rationale:** Teams may want confirmation before AI updates docs, solo developers want speed.

---

## Predefined Profiles

### Solo Developer Profile

**Use case:** Individual developer working alone, needs flexibility and speed.

```yaml
profile: solo-developer

token_targets:
  changelog_warning: 8000
  changelog_error: 10000
  devlog_warning: 12000
  devlog_error: 15000
  combined_warning: 20000
  combined_error: 25000
  state_warning: 400
  state_error: 500

required_files:
  - CHANGELOG
  # DEVLOG optional for minor changes
  # ADR optional
  # STATE optional
  # PRD optional

update_frequency:
  changelog: every-commit
  devlog: milestones-only
  state: optional
  adr: as-needed
  prd: as-needed

validation:
  strictness: warnings-only
  format_validation: true
  token_validation: true
  crosslink_validation: false
  fail_on_warnings: false

archival:
  changelog_age_days: 30
  devlog_age_days: 14
  auto_archive_on_warning: false
  auto_archive_on_error: true
  archive_directory: project/planning/archive

ai_assistant:
  proactive_updates: true
  require_confirmation: false
  show_checklist: true
  suggest_validation: true
```

---

### Team Profile

**Use case:** Team collaboration, needs consistency and clear communication.

```yaml
profile: team

token_targets:
  changelog_warning: 8000
  changelog_error: 10000
  devlog_warning: 12000
  devlog_error: 15000
  combined_warning: 20000
  combined_error: 25000
  state_warning: 400
  state_error: 500

required_files:
  - CHANGELOG
  - DEVLOG      # Required for significant changes
  - ADR         # Required for architectural decisions
  # STATE optional
  # PRD optional

update_frequency:
  changelog: every-commit
  devlog: significant-changes
  state: daily
  adr: as-needed
  prd: as-needed

validation:
  strictness: errors
  format_validation: true
  token_validation: true
  crosslink_validation: false
  fail_on_warnings: false

archival:
  changelog_age_days: 60
  devlog_age_days: 30
  auto_archive_on_warning: false
  auto_archive_on_error: true
  archive_directory: project/planning/archive

ai_assistant:
  proactive_updates: true
  require_confirmation: false
  show_checklist: true
  suggest_validation: true
```

---

## Future Extensions

**Potential additions** (not in v1.0):

1. **Custom profiles:** Allow users to define their own profiles
2. **Profile inheritance:** Extend existing profiles with overrides
3. **Per-file overrides:** Different settings for different files
4. **Conditional rules:** Different settings based on branch, environment, etc.
5. **Team-specific settings:** Different settings per team member
6. **Integration settings:** Configure integrations with external tools

**Principle:** Keep it simple. Only add complexity when there's clear user demand.

---

## Implementation Notes

### Validation Script Integration

Validation scripts should:
1. Check for config file in standard locations
2. Load profile settings
3. Apply overrides if present
4. Use profile-specific thresholds for validation
5. Respect strictness setting when reporting errors

### AI Assistant Integration

AI assistant rules should:
1. Read profile settings at session start
2. Respect `required_files` when deciding what to update
3. Follow `update_frequency` guidance
4. Show/hide checklist based on `show_checklist` setting
5. Suggest validation based on `suggest_validation` setting

### Backward Compatibility

If no config file exists:
- Use **solo-developer** profile as default
- System works exactly as it does today
- No breaking changes for existing users

---

## References

- **ADR-007:** Agent OS-Inspired Enhancements
- **Epic 8:** Profile System
- **Validation Guide:** `product/docs/validation-guide.md`
- **Log File How-To:** `product/docs/log_file_how_to.md`

