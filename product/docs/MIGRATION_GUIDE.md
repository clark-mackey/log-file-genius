# Migration Guide: Integrating Log File Genius into Existing Projects

**Purpose:** Step-by-step guide for adding the Log File Genius system to projects with existing documentation.

**Target Audience:** Developers with existing projects who want to adopt the token-efficient log file system without starting from scratch.

***BACK UP YOUR LOG FILES BEFORE STARTING!***
---

## Table of Contents

1. [Quick Assessment](#quick-assessment)
2. [Migration Scenarios](#migration-scenarios)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Incremental Adoption](#incremental-adoption)
5. [Common Challenges](#common-challenges)
6. [Validation & Testing](#validation--testing)

**📋 [Download Migration Checklist](MIGRATION_CHECKLIST.md)** - Track your progress step-by-step

---

## Quick Assessment

Answer these questions to determine your migration path:

### 1. What documentation do you currently have?

- [ ] **CHANGELOG.md** (or similar version history)
- [ ] **Development log/journal** (any format)
- [ ] **PRD or requirements doc**
- [ ] **Architecture Decision Records (ADRs)**
- [ ] **README with project history**
- [ ] **Git commit messages only**
- [ ] **Nothing formal**

### 2. What's your current token situation?

Run this quick check:
```bash
# Count tokens in your existing docs (rough estimate: 1 token ≈ 4 characters)
wc -c docs/**/*.md | awk '{print $1/4 " tokens"}'
```

**Token Budget:**
- ✅ **<10,000 tokens:** You're in good shape, just need structure
- ⚠️ **10,000-50,000 tokens:** Need condensing + restructuring
- 🚨 **>50,000 tokens:** Significant condensing required

### 3. What's your goal?

- [ ] **Full adoption:** Implement complete 5-document system
- [ ] **Partial adoption:** Add missing pieces to existing docs
- [ ] **Gradual migration:** Start small, expand over time
- [ ] **Cleanup only:** Condense existing docs without major restructuring

---

## Migration Scenarios

### Scenario A: No Existing Documentation

**Situation:** You have git history but no formal documentation.

**Migration Path:** ✅ **Easiest** - Start fresh with templates

**Steps:**
1. Copy templates from `templates/` directory
2. Backfill recent history (last 2-4 weeks) from git commits
3. Start maintaining going forward

**Time Estimate:** 1-2 hours

**See:** [Scenario A: Fresh Start](#scenario-a-fresh-start)

---

### Scenario B: Have CHANGELOG, Need Everything Else

**Situation:** You maintain a CHANGELOG but lack DEVLOG, PRD, or ADRs.

**Migration Path:** ⚠️ **Moderate** - Add missing documents + condense CHANGELOG

**You backed up your files already, right? Pause and do it now**

**Steps:**
1. Assess and condense existing CHANGELOG
2. Create DEVLOG from recent significant decisions
3. Add PRD if planning new features
4. Extract ADRs from major decisions

**Time Estimate:** 3-6 hours

**See:** [Scenario B: Expand from CHANGELOG](#scenario-b-expand-from-changelog)

---

### Scenario C: Have Verbose Documentation

**Situation:** You have docs but they're consuming too many tokens (>50k).

**Migration Path:** 🚨 **Complex** - Condense + restructure

**You know why squirrels bury so many nuts? So they have backups. You have a backup, right?**

**Steps:**
1. Create safety snapshot (git commit)
2. Archive old entries (>6 months)
3. Transform entries to token-efficient format
4. Extract detailed decisions to ADRs
5. Verify token counts

**Time Estimate:** 1-2 days

**See:** [Scenario C: Condense Existing Docs](#scenario-c-condense-existing-docs)

---

### Scenario D: Partial Implementation

**Situation:** You're already using parts of this system but not all of it.

**Migration Path:** ✅ **Straightforward** - Fill gaps + standardize

**Steps:**
1. Identify missing documents
2. Standardize existing documents to match format
3. Add cross-links between documents
4. Verify token budgets

**Time Estimate:** 2-4 hours

**See:** [Scenario D: Complete Partial Implementation](#scenario-d-complete-partial-implementation)

---

## Step-by-Step Migration

### Scenario A: Fresh Start

**Best for:** Projects with no formal documentation

#### Step 1: Copy Templates

```bash
# Copy all templates to your project
cp templates/CHANGELOG_template.md docs/planning/CHANGELOG.md
cp templates/DEVLOG_template.md docs/planning/DEVLOG.md
cp templates/STATE_template.md docs/planning/STATE.md
cp templates/ADR_template.md docs/adr/ADR-template.md
```

#### Step 2: Backfill Recent History

**CHANGELOG (from git commits):**
```bash
# Get last 20 commits
git log --oneline -20 > recent_commits.txt
```

Transform to CHANGELOG format:
```markdown
## [Unreleased]

### Added
- Feature X - Brief description. Files: `path/to/file.py`
- Feature Y - Brief description. Files: `path/to/file.js`

### Changed
- Updated Z - Brief description. Files: `path/to/file.md`
```

**DEVLOG (from memory/notes):**

Add 2-3 recent significant decisions:
```markdown
### 2025-10-28: Chose PostgreSQL Over MongoDB

**Situation:** Needed database for user data with complex relationships.

**Challenge:** MongoDB offered flexibility, PostgreSQL offered ACID guarantees.

**Decision:** Chose PostgreSQL for data integrity and relational queries.

**Impact:** Simplified user relationship queries, enabled transactions.

**Files:** `database/schema.sql`, `config/database.py`
```

#### Step 3: Start Maintaining

- Update CHANGELOG after every commit
- Update DEVLOG after significant decisions
- Update STATE every 30-60 minutes (optional)

**Done!** ✅

---

### Scenario B: Expand from CHANGELOG

**Best for:** Projects with CHANGELOG but missing other documents

#### Step 1: Assess Current CHANGELOG

Check token count:
```bash
wc -c docs/CHANGELOG.md | awk '{print $1/4 " tokens"}'
```

**If >2,000 tokens:** Condense first (see Scenario C)

#### Step 2: Create DEVLOG from CHANGELOG

Review your CHANGELOG for entries that need "why" context:

**CHANGELOG entry:**
```markdown
- Switched from REST to GraphQL - Files: `api/`, `schema.graphql`
```

**Becomes DEVLOG entry:**
```markdown
### 2025-10-15: Migrated API from REST to GraphQL

**Situation:** Frontend needed to fetch nested user data, causing N+1 queries.

**Challenge:** REST required multiple round trips, slowing page loads.

**Decision:** Migrated to GraphQL for efficient nested queries.

**Impact:** Reduced API calls by 70%, improved page load by 2 seconds.

**Files:** `api/graphql/`, `schema.graphql`, `resolvers/`
```

#### Step 3: Add Missing Documents

**PRD (if planning features):**
- Copy `templates/PRD_template.md` (if available) or create minimal version
- Document current goals and upcoming features

**ADRs (for major decisions):**
- Extract 3-5 most important decisions from DEVLOG
- Create separate ADR files with full context

#### Step 4: Add Cross-Links

Update all documents with navigation links (see `docs/log_file_how_to.md` → Navigation Matrix)

**Done!** ✅

---

### Scenario C: Condense Existing Docs

**Best for:** Projects with verbose documentation (>50k tokens)

#### Step 1: Create Safety Snapshot

```bash
git add docs/
git commit -m "Pre-migration snapshot: Existing documentation"
git tag pre-log-file-migration
```

#### Step 2: Measure Current State

```bash
# Count tokens in all docs
find docs -name "*.md" -exec wc -c {} + | awk '{sum+=$1} END {print sum/4 " tokens"}'
```

#### Step 3: Archive Old Entries

**Create archive directory:**
```bash
mkdir -p docs/planning/archive
```

**Move old entries:**
- CHANGELOG: Entries >6 months old → `archive/CHANGELOG-YYYY-MM.md`
- DEVLOG: Entries >6 months old → `archive/DEVLOG-YYYY-MM.md`

#### Step 4: Transform Entries

**CHANGELOG transformation:**

**Before (verbose):**
```markdown
## [1.2.0] - 2025-09-15

### Added
- Implemented user authentication system with JWT tokens. This was a major
  undertaking that required significant refactoring of the API layer. We
  chose JWT because it's stateless and scales well. The implementation
  includes token refresh, blacklisting, and role-based access control.
  Files modified: auth/jwt.py, api/middleware.py, models/user.py, and
  about 15 other files.
```

**After (condensed):**
```markdown
## [1.2.0] - 2025-09-15

### Added
- JWT authentication with refresh, blacklisting, RBAC. Files: `auth/jwt.py`, `api/middleware.py`, `models/user.py`. See: [ADR-003](../adr/003-jwt-authentication.md)
```

**DEVLOG transformation:**

**Before (verbose):**
```markdown
We spent a lot of time discussing authentication approaches. Initially we
considered session-based auth but realized it wouldn't scale well with our
microservices architecture. We also looked at OAuth2 but it seemed too
complex for our needs. After much debate, we settled on JWT tokens because
they're stateless, widely supported, and work well with our React frontend.
The implementation took about 2 weeks and involved refactoring a lot of
the API layer...
```

**After (structured):**
```markdown
### 2025-09-15: Chose JWT Over Session-Based Auth

**Situation:** Needed authentication for microservices architecture.

**Challenge:** Session-based auth doesn't scale across services; OAuth2 too complex.

**Decision:** Implemented JWT tokens for stateless, scalable auth.

**Impact:** Enabled horizontal scaling, simplified frontend integration.

**Files:** `auth/jwt.py`, `api/middleware.py`. See: [ADR-003](../adr/003-jwt-authentication.md)
```

#### Step 5: Extract ADRs

Create ADR files for major decisions referenced in CHANGELOG/DEVLOG:

```bash
cp templates/ADR_template.md docs/adr/003-jwt-authentication.md
```

Fill in with full context, alternatives considered, consequences.

#### Step 6: Verify Token Counts

```bash
# Check new token counts
find docs/planning -name "*.md" ! -path "*/archive/*" -exec wc -c {} + | awk '{sum+=$1} END {print sum/4 " tokens"}'
```

**Target:** <10,000 tokens for CHANGELOG + DEVLOG + STATE combined

**Done!** ✅

---

### Scenario D: Complete Partial Implementation

**Best for:** Projects already using parts of this system

#### Step 1: Inventory Current State

Create a checklist:

```markdown
## Current Documentation

- [x] CHANGELOG.md (exists, needs formatting)
- [ ] DEVLOG.md (missing)
- [x] PRD.md (exists, good format)
- [ ] STATE.md (missing)
- [x] ADRs (have 2, need more)

## Format Compliance

- [ ] CHANGELOG uses single-line entries
- [ ] DEVLOG uses Situation/Challenge/Decision/Impact format
- [ ] Cross-links between documents
- [ ] Token budgets met
```

#### Step 2: Add Missing Documents

Copy templates for missing documents:
```bash
[ ! -f docs/planning/DEVLOG.md ] && cp templates/DEVLOG_template.md docs/planning/DEVLOG.md
[ ! -f docs/planning/STATE.md ] && cp templates/STATE_template.md docs/planning/STATE.md
```

#### Step 3: Standardize Existing Documents

**CHANGELOG:**
- Convert to single-line format (if needed)
- Add file paths to all entries
- Add cross-references to ADRs

**DEVLOG:**
- Convert to Situation/Challenge/Decision/Impact format
- Keep entries 150-250 words
- Add cross-references

**PRD:**
- Ensure it follows standard structure
- Add cross-links to other docs

#### Step 4: Add Cross-Links

Update navigation in all documents (see Navigation Matrix in `docs/log_file_how_to.md`)

#### Step 5: Verify Token Budgets

```bash
wc -c docs/planning/CHANGELOG.md | awk '{print "CHANGELOG: " $1/4 " tokens"}'
wc -c docs/planning/DEVLOG.md | awk '{print "DEVLOG: " $1/4 " tokens"}'
wc -c docs/planning/STATE.md | awk '{print "STATE: " $1/4 " tokens"}'
```

**Targets:**
- CHANGELOG: <2,000 tokens
- DEVLOG: <4,000 tokens
- STATE: <500 tokens
- **Combined: <10,000 tokens**

**Done!** ✅

---

## Incremental Adoption

Don't want to migrate everything at once? Here's a gradual path:

### Phase 1: Start with CHANGELOG (Week 1)
- Create or standardize CHANGELOG.md
- Update after every commit
- Get comfortable with single-line format

### Phase 2: Add DEVLOG (Week 2)
- Create DEVLOG.md
- Add entries for significant decisions only
- Practice Situation/Challenge/Decision/Impact format

### Phase 3: Add STATE (Week 3)
- Create STATE.md (optional)
- Update every 30-60 minutes during active work
- Use for multi-agent coordination

### Phase 4: Extract ADRs (Week 4)
- Identify 3-5 major decisions from DEVLOG
- Create ADR files with full context
- Add cross-references

### Phase 5: Add PRD (Ongoing)
- Create PRD when planning new features
- Link to CHANGELOG/DEVLOG/ADRs
- Keep updated as requirements evolve

---

## Common Challenges

### Challenge 1: "My CHANGELOG is 100k tokens!"

**Solution:**
1. Archive everything >6 months old
2. Keep only last 2-4 weeks in main file
3. Transform remaining entries to single-line format
4. Extract major decisions to ADRs

**Expected reduction:** 90-95%

### Challenge 2: "I don't remember why we made past decisions"

**Solution:**
1. Don't try to backfill everything
2. Focus on last 2-4 weeks of significant decisions
3. For older decisions, add brief entries or skip
4. Going forward, maintain DEVLOG consistently

### Challenge 3: "My team won't maintain this"

**Solution:**
1. Start with just CHANGELOG (easiest)
2. Automate with git hooks or CI
3. Make it part of PR template
4. Show token savings to demonstrate value

### Challenge 4: "I have multiple projects to migrate"

**Solution:**
1. Start with one pilot project
2. Create project-specific migration script
3. Document lessons learned
4. Apply to other projects incrementally

---

## Validation & Testing

### Token Budget Check

```bash
# Create a simple token counter script
cat > scripts/check_tokens.sh << 'EOF'
#!/bin/bash
echo "=== Token Budget Check ==="
echo "CHANGELOG: $(wc -c < docs/planning/CHANGELOG.md | awk '{print int($1/4)}') tokens"
echo "DEVLOG: $(wc -c < docs/planning/DEVLOG.md | awk '{print int($1/4)}') tokens"
echo "STATE: $(wc -c < docs/planning/STATE.md | awk '{print int($1/4)}') tokens"
echo "---"
echo "TOTAL: $(cat docs/planning/{CHANGELOG,DEVLOG,STATE}.md | wc -c | awk '{print int($1/4)}') tokens"
echo "TARGET: <10,000 tokens"
EOF
chmod +x scripts/check_tokens.sh
```

Run after migration:
```bash
./scripts/check_tokens.sh
```

### Format Validation

**CHANGELOG checklist:**
- [ ] Single-line entries
- [ ] File paths included
- [ ] Semantic versioning
- [ ] Cross-references to ADRs

**DEVLOG checklist:**
- [ ] Situation/Challenge/Decision/Impact format
- [ ] 150-250 words per entry
- [ ] File paths included
- [ ] Cross-references to ADRs

**Cross-linking checklist:**
- [ ] All documents have navigation section
- [ ] Relative paths are correct
- [ ] Links work (test by clicking)

---

## Next Steps

After migration:

1. **Read the full methodology:** [`docs/log_file_how_to.md`](log_file_how_to.md)
2. **Set up AI assistant rules:** Copy `.augment/` or `.claude/` directory
3. **Establish maintenance routine:** Update CHANGELOG after commits, DEVLOG after decisions
4. **Monitor token budgets:** Run token check weekly
5. **Archive regularly:** Move old entries when files exceed 10k tokens

---

## Support

- 🐛 [Report migration issues](https://github.com/clark-mackey/log-file-genius/issues)
- 💬 [Ask questions](https://github.com/clark-mackey/log-file-genius/discussions)
- 📖 [Read the methodology](log_file_how_to.md)

---

**Last Updated:** 2025-10-31

