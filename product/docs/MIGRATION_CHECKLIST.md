# Migration Checklist

Copy this checklist to track your migration progress. Check off items as you complete them.

---

## Pre-Migration Assessment

### Current State
- [ ] Inventoried existing documentation
- [ ] Counted current token usage: _________ tokens
- [ ] Identified migration scenario (A/B/C/D)
- [ ] Read relevant section of [Migration Guide](MIGRATION_GUIDE.md)

### Safety
- [ ] Created git commit with current state
- [ ] Created git tag: `pre-log-file-migration`
- [ ] Backed up important documentation locally before starting (even if in git)
- [ ] You have approval from the right other people to make changes to your log files and process
- [ ] Another human knows I am doing this

---

## Phase 1: Setup Structure

### Directory Structure
- [ ] Created `docs/planning/` directory
- [ ] Created `docs/adr/` directory
- [ ] Created `docs/planning/archive/` directory (if needed)
- [ ] Created `templates/` directory (if copying templates)

### Copy Templates
- [ ] Copied `CHANGELOG_template.md` → `docs/planning/CHANGELOG.md` (or kept existing)
- [ ] Copied `DEVLOG_template.md` → `docs/planning/DEVLOG.md` (or created new)
- [ ] Copied `STATE_template.md` → `docs/planning/STATE.md` (optional)
- [ ] Copied `ADR_template.md` → `docs/adr/ADR-template.md`

---

## Phase 2: Migrate/Create Documents

### CHANGELOG.md
- [ ] Exists or created from template
- [ ] Converted to single-line format
- [ ] Added file paths to all entries
- [ ] Added cross-references to ADRs
- [ ] Archived old entries (if >2,000 tokens)
- [ ] Verified token count: _________ tokens (target: <2,000)

### DEVLOG.md
- [ ] Exists or created from template
- [ ] Converted to Situation/Challenge/Decision/Impact format
- [ ] Entries are 150-250 words each
- [ ] Added file paths to all entries
- [ ] Added cross-references to ADRs
- [ ] Archived old entries (if >4,000 tokens)
- [ ] Verified token count: _________ tokens (target: <4,000)

### STATE.md (Optional)
- [ ] Created from template
- [ ] Populated with current state
- [ ] Set up update routine (every 30-60 minutes)
- [ ] Verified token count: _________ tokens (target: <500)

### PRD (If Applicable)
- [ ] Exists or created
- [ ] Follows standard structure
- [ ] Added cross-links to other documents
- [ ] Updated with current requirements

### ADRs
- [ ] Identified 3-5 major decisions to extract
- [ ] Created ADR files for each decision
- [ ] Added ADR index (README.md in `docs/adr/`)
- [ ] Linked ADRs from CHANGELOG/DEVLOG

---

## Phase 3: Cross-Linking

### Navigation Links
- [ ] Added navigation section to CHANGELOG
- [ ] Added navigation section to DEVLOG
- [ ] Added navigation section to STATE (if applicable)
- [ ] Added navigation section to PRD (if applicable)
- [ ] Added navigation section to ADR README
- [ ] Verified all relative paths are correct
- [ ] Tested all links (clicked through)

### Cross-References
- [ ] CHANGELOG entries reference ADRs where applicable
- [ ] DEVLOG entries reference ADRs where applicable
- [ ] ADRs reference related CHANGELOG/DEVLOG entries
- [ ] PRD references ADRs for major decisions

---

## Phase 4: Validation

### Token Budget Check
- [ ] Ran token counter script
- [ ] CHANGELOG: _________ tokens (target: <2,000)
- [ ] DEVLOG: _________ tokens (target: <4,000)
- [ ] STATE: _________ tokens (target: <500)
- [ ] **TOTAL: _________ tokens (target: <10,000)**

### Format Validation

**CHANGELOG:**
- [ ] Single-line entries
- [ ] File paths included
- [ ] Semantic versioning used
- [ ] Cross-references to ADRs

**DEVLOG:**
- [ ] Situation/Challenge/Decision/Impact format
- [ ] 150-250 words per entry
- [ ] File paths included
- [ ] Cross-references to ADRs

**STATE (if applicable):**
- [ ] Current work section populated
- [ ] Blockers section populated
- [ ] Recently completed section populated
- [ ] Next priorities section populated

**ADRs:**
- [ ] Follow standard template
- [ ] Include context, decision, consequences
- [ ] Include status (Accepted/Superseded/Deprecated)
- [ ] Include date

---

## Phase 5: Setup Maintenance

### AI Assistant Integration
- [ ] Copied `.augment/` directory (if using Augment)
- [ ] Copied `.claude/` directory (if using Claude Code)
- [ ] Tested AI assistant can read documents
- [ ] Verified AI assistant follows maintenance rules

### Automation (Optional)
- [ ] Created git hooks for CHANGELOG updates
- [ ] Added PR template with log file reminders
- [ ] Created token counter script
- [ ] Set up weekly token budget check

### Team Onboarding
- [ ] Documented maintenance process for team
- [ ] Added to team onboarding checklist
- [ ] Scheduled training session (if needed)
- [ ] Created quick reference guide

---

## Phase 6: Post-Migration

### Verification
- [ ] Committed all changes
- [ ] Pushed to remote repository
- [ ] Verified files appear correctly on GitHub
- [ ] Tested AI assistant with new structure

### Cleanup
- [ ] Removed old documentation (if replaced)
- [ ] Updated README to reference new docs
- [ ] Archived pre-migration snapshot (if no longer needed)
- [ ] Deleted temporary files

### Establish Routine
- [ ] Set reminder to update CHANGELOG after commits
- [ ] Set reminder to update DEVLOG after decisions
- [ ] Set reminder to update STATE every 30-60 minutes (if using)
- [ ] Set reminder to archive old entries monthly
- [ ] Set reminder to check token budgets weekly

---

## Success Criteria

Migration is complete when:

- ✅ All five documents exist (or four if skipping STATE)
- ✅ Token budget is <10,000 tokens for CHANGELOG + DEVLOG + STATE
- ✅ All documents follow standard format
- ✅ Cross-links work between all documents
- ✅ AI assistant can successfully use the system
- ✅ Team understands maintenance process

---

## Troubleshooting

### If token budget is still too high:
1. Archive more old entries
2. Condense entries further
3. Extract more decisions to ADRs
4. Remove redundant information

### If AI assistant isn't using docs:
1. Verify file paths are correct
2. Check AI assistant rules are loaded
3. Test with explicit prompts ("read DEVLOG")
4. Verify token budgets allow loading

### If team isn't maintaining:
1. Simplify to just CHANGELOG initially
2. Add automation (git hooks, PR templates)
3. Show token savings to demonstrate value
4. Make it part of definition of done

---

## Next Steps After Migration

1. **Monitor for 2 weeks:** Track token usage and maintenance burden
2. **Adjust as needed:** Fine-tune token budgets and formats
3. **Archive regularly:** Move old entries when files exceed targets
4. **Iterate:** Improve process based on team feedback
5. **Smile more** When you are way too far into a token window and still getting good output

---

**Migration Date:** _______________
**Completed By:** _______________
**Total Time:** _______________
**Token Reduction:** _______________% (from _______ to _______ tokens)

---

**See Also:**
- [Migration Guide](MIGRATION_GUIDE.md) - Detailed step-by-step instructions
- [Log File How-To](log_file_how_to.md) - Complete methodology
- [Examples](../examples/) - Sample implementations

