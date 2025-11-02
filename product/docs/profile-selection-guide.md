# Profile Selection Guide

**Version:** 1.0  
**Last Updated:** 2025-11-02

This guide helps you choose the right Log File Genius profile for your project and shows you how to customize it for your specific needs.

---

## Quick Decision Tree

```
Are you working alone?
├─ YES → Are you building an MVP/prototype?
│         ├─ YES → Use **startup** profile
│         └─ NO  → Use **solo-developer** profile (default)
│
└─ NO  → Is this a public open-source project?
          ├─ YES → Use **open-source** profile
          └─ NO  → Use **team** profile
```

---

## Profile Comparison

| Feature | Solo Developer | Team | Open Source | Startup |
|---------|---------------|------|-------------|---------|
| **Best For** | Individual developers | 2+ developers | Public projects | MVPs, prototypes |
| **Validation** | Warnings only | Errors | Strict | Warnings only |
| **Required Files** | CHANGELOG only | CHANGELOG, DEVLOG, ADR | CHANGELOG only | CHANGELOG only |
| **CHANGELOG Limit** | 10,000 tokens | 10,000 tokens | 10,000 tokens | 7,500 tokens |
| **DEVLOG Limit** | 15,000 tokens | 15,000 tokens | 15,000 tokens | 10,000 tokens |
| **Combined Limit** | 25,000 tokens | 25,000 tokens | 25,000 tokens | 17,500 tokens |
| **Archive After** | 30 days | 60 days | 90 days | 14 days |
| **Update Frequency** | Flexible | Consistent | Public-facing | Minimal |
| **AI Checklist** | Yes | Yes | Yes | No (speed) |

---

## Detailed Profile Descriptions

### 1. Solo Developer (Default)

**Use this profile if:**
- You're working alone on a personal or side project
- You want flexibility without strict enforcement
- You prefer warnings over hard failures
- You're learning the Log File Genius method

**Key Characteristics:**
- **Validation:** Warnings-only (never blocks commits)
- **Required Files:** CHANGELOG only (DEVLOG optional for milestones)
- **Token Targets:** Standard limits (10k CHANGELOG, 15k DEVLOG, 25k combined)
- **Archival:** 30-day retention, auto-archive on errors
- **AI Assistant:** Proactive updates, shows checklist, suggests validation

**When to Upgrade:**
- Switch to **team** when you add collaborators
- Switch to **open-source** when you make the project public
- Switch to **startup** if you need maximum speed

**Example `.logfile-config.yml`:**
```yaml
profile: solo-developer

# Optional: Customize for larger projects
overrides:
  archival:
    changelog_age_days: 60  # Keep more history
```

---

### 2. Team

**Use this profile if:**
- You have 2+ developers working together
- You need consistent documentation across the team
- You want to catch errors before they're committed
- You value communication and shared context

**Key Characteristics:**
- **Validation:** Error-level (fails on errors, allows warnings)
- **Required Files:** CHANGELOG, DEVLOG (for significant changes), ADR (for decisions)
- **Token Targets:** Standard limits (10k CHANGELOG, 15k DEVLOG, 25k combined)
- **Archival:** 60-day retention (longer team history)
- **AI Assistant:** Proactive updates, shows checklist, suggests validation

**When to Upgrade:**
- Switch to **open-source** when you make the project public
- Switch to **startup** if you're in rapid prototyping mode

**Example `.logfile-config.yml`:**
```yaml
profile: team

# Optional: Customize for large teams
overrides:
  validation:
    strictness: strict  # Fail on warnings for high-quality docs
  archival:
    changelog_age_days: 90  # Keep even more history
```

---

### 3. Open Source

**Use this profile if:**
- Your project is public on GitHub/GitLab
- Contributors need clear, well-formatted documentation
- You want to maintain high documentation quality
- You care about first impressions and contributor experience

**Key Characteristics:**
- **Validation:** Strict (fails on warnings AND errors)
- **Required Files:** CHANGELOG only (DEVLOG/ADR optional, STATE optional)
- **Token Targets:** Standard limits (10k CHANGELOG, 15k DEVLOG, 25k combined)
- **Archival:** 90-day retention, manual archival only (no auto-archive)
- **AI Assistant:** Proactive updates, shows checklist, suggests validation

**Special Considerations:**
- CHANGELOG is public-facing (required, strict formatting)
- DEVLOG/ADR can be private (in `.gitignore`) or public
- STATE.md useful for coordinating multiple contributors
- Manual archival prevents accidental loss of public history

**When to Downgrade:**
- Switch to **team** if you make the project private
- Switch to **solo-developer** if you're the only maintainer

**Example `.logfile-config.yml`:**
```yaml
profile: open-source

# Optional: Customize for high-visibility projects
overrides:
  token_targets:
    changelog_error: 12000  # Allow more detailed public changelog
  validation:
    crosslink_validation: true  # Ensure all links work
```

---

### 4. Startup

**Use this profile if:**
- You're building an MVP or prototype
- Speed is more important than documentation perfection
- You're in rapid iteration mode
- You want minimal overhead

**Key Characteristics:**
- **Validation:** Warnings-only (never blocks commits)
- **Required Files:** CHANGELOG only (everything else optional)
- **Token Targets:** Reduced limits (7.5k CHANGELOG, 10k DEVLOG, 17.5k combined)
- **Archival:** Aggressive (14-day CHANGELOG, 7-day DEVLOG), auto-archive on warnings
- **AI Assistant:** No checklist, no validation suggestions (speed over quality)

**When to Upgrade:**
- Switch to **team** after finding product-market fit
- Switch to **solo-developer** when you want more documentation
- Switch to **open-source** when you open-source the project

**Example `.logfile-config.yml`:**
```yaml
profile: startup

# Optional: Customize for hackathons (even more aggressive)
overrides:
  token_targets:
    changelog_error: 5000  # Even stricter limits
  archival:
    changelog_age_days: 7  # Archive weekly
  validation:
    strictness: disabled  # Skip validation entirely
```

---

## Switching Profiles

### How to Switch

1. **Edit `.logfile-config.yml`:**
   ```yaml
   profile: team  # Change from solo-developer to team
   ```

2. **Review new requirements:**
   - Check if new profile requires additional files (e.g., team requires DEVLOG)
   - Review token targets (e.g., startup has lower limits)
   - Understand validation changes (e.g., open-source is strict)

3. **Run validation:**
   ```bash
   ./product/scripts/validate-log-files.ps1  # Windows
   ./product/scripts/validate-log-files.sh   # Mac/Linux
   ```

4. **Address any issues:**
   - Archive old entries if over new token limits
   - Create missing required files
   - Fix formatting issues if switching to stricter validation

### Common Migration Paths

**Solo → Team (Adding Collaborators):**
```yaml
# Before
profile: solo-developer

# After
profile: team

# What changes:
# - DEVLOG becomes required for significant changes
# - ADR becomes required for architectural decisions
# - Validation fails on errors (not just warnings)
# - Archival retention increases to 60 days
```

**Team → Open Source (Going Public):**
```yaml
# Before
profile: team

# After
profile: open-source

# What changes:
# - Validation becomes strict (fails on warnings)
# - Archival retention increases to 90 days
# - Auto-archive disabled (manual only)
# - CHANGELOG formatting must be perfect
```

**Startup → Team (Post-PMF):**
```yaml
# Before
profile: startup

# After
profile: team

# What changes:
# - Token limits increase (more documentation allowed)
# - DEVLOG and ADR become required
# - Validation fails on errors
# - Archival retention increases to 60 days
# - AI assistant shows checklist and validation
```

---

## Customization Examples

### Example 1: Solo Developer with Strict Validation

```yaml
profile: solo-developer

overrides:
  validation:
    strictness: strict  # Fail on warnings (personal quality standard)
```

### Example 2: Team with Aggressive Archival

```yaml
profile: team

overrides:
  archival:
    changelog_age_days: 30  # Archive more frequently
    auto_archive_on_warning: true  # Auto-archive when approaching limits
```

### Example 3: Open Source with Extended Limits

```yaml
profile: open-source

overrides:
  token_targets:
    changelog_error: 12000  # Allow more detailed changelog
    devlog_error: 20000     # Allow more detailed devlog
```

### Example 4: Startup with Validation Disabled

```yaml
profile: startup

overrides:
  validation:
    strictness: disabled  # Skip all validation (hackathon mode)
```

---

## Frequently Asked Questions

### Q: Can I use multiple profiles in one project?

**A:** No, you can only use one profile at a time. However, you can customize any profile using the `overrides` section to get the exact behavior you need.

### Q: What happens if I don't create a config file?

**A:** The validation scripts default to the **solo-developer** profile, which is the most flexible and forgiving.

### Q: Can I create my own custom profile?

**A:** In v1.0, you can't create custom profile files, but you can heavily customize any existing profile using `overrides`. Custom profiles may be added in a future version.

### Q: How do I know which settings my profile is using?

**A:** Run validation with the `--verbose` flag:
```bash
./product/scripts/validate-log-files.ps1 --verbose
./product/scripts/validate-log-files.sh --verbose
```

This will show the loaded profile name and applied settings.

### Q: Can I disable validation entirely?

**A:** Yes, set `strictness: disabled` in your config:
```yaml
profile: solo-developer
overrides:
  validation:
    strictness: disabled
```

### Q: What if my team wants different settings than the team profile?

**A:** Use the `overrides` section to customize the team profile:
```yaml
profile: team
overrides:
  validation:
    strictness: warnings-only  # More relaxed than default
  archival:
    changelog_age_days: 90     # Keep more history
```

---

## Related Documentation

- **[Profile Schema](profile-schema.md)** - Complete technical specification
- **[Validation Guide](validation-guide.md)** - How validation works
- **[Log File How-To](log_file_how_to.md)** - Core methodology
- **[Migration Guide](MIGRATION_GUIDE.md)** - Brownfield installation

---

## Need Help?

- **Can't decide which profile?** Start with **solo-developer** (default) and switch later
- **Profile too strict?** Use `overrides` to relax specific settings
- **Profile too lenient?** Use `overrides` to tighten specific settings
- **Still unsure?** Open an issue on GitHub with your use case

