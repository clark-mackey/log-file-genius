# Epic 15: Governance & Review Workflows (Simplified for Solo/Teams)

**Status:** Not Started  
**Priority:** P1 - HIGH (Important for teams, nice-to-have for solo)  
**Estimated Effort:** 1 week (simplified version)  
**Dependencies:** Epic 13 (Validation)  
**Source:** Red Team Analysis (context/research/Red Team Analysis_ (REVISED) (1).md)

---

## Epic Goal

Add lightweight review processes for AI-generated documentation, focusing on critical decisions (ADRs) and preventing AI from making unilateral changes without human oversight.

**Problem Statement:** AI assistants can unilaterally modify documentation without review. For critical decisions (ADRs, archival, major changes), humans should approve. This is especially important for teams where documentation is a source of truth.

**Inspiration:** Red Team Analysis identified this as "Critical Failure #3" - no governance or conflict resolution. This is a simplified version focused on solo developers and small teams, not full enterprise workflows.

---

## Success Criteria

- [ ] ADRs require human approval before being marked "Accepted"
- [ ] AI asks permission before critical actions (archival, ADR creation)
- [ ] Clear process for reviewing AI-generated documentation
- [ ] Simple rollback procedure for incorrect entries
- [ ] Works for solo developers (optional) and teams (recommended)

---

## Task List

### Task 15.1: Add ADR Lifecycle
- [ ] Update `product/docs/ADR_how_to.md` with lifecycle:
  - **Proposed** - AI or human creates draft ADR
  - **Under Review** - Team reviews (via PR comments or discussion)
  - **Accepted** - Approved and merged
  - **Deprecated** - Superseded by newer ADR
- [ ] Add rule: AI always creates ADRs with status "Proposed"
- [ ] Add rule: AI never changes status to "Accepted" without human approval
- [ ] Update ADR template with status field

### Task 15.2: Add Human-in-the-Loop Rules
- [ ] Update `log-file-maintenance.md` with human approval section
- [ ] AI must ASK before:
  - Creating or modifying an ADR
  - Archiving DEVLOG entries (>30 days old)
  - Changing token budget targets
  - Modifying frontmatter structure
  - Making breaking changes to log format
- [ ] Add approval prompt format:
  ```
  🧑 HUMAN APPROVAL REQUIRED
  
  Action: [Create ADR / Archive DEVLOG / etc.]
  Reason: [Why this action is needed]
  Impact: [What will change]
  
  Proceed? (yes/no)
  ```
- [ ] Update both starter packs with approval rules

### Task 15.3: Create PR Review Checklist
- [ ] Create `product/docs/pr-review-checklist.md`
- [ ] Add checklist for reviewing AI-generated documentation:
  - [ ] CHANGELOG entries match code changes
  - [ ] DEVLOG entries accurately describe decisions
  - [ ] ADRs are well-reasoned and complete
  - [ ] No secrets or sensitive data in logs
  - [ ] Cross-links are valid
  - [ ] Token budgets are within limits
- [ ] Add to PR template (optional)
- [ ] Document in validation guide

### Task 15.4: Add Rollback Procedure
- [ ] Create `product/docs/rollback-guide.md`
- [ ] Document how to fix incorrect entries:
  - **For recent commits:** Amend commit and force push (solo only)
  - **For merged PRs:** Add correction entry to CHANGELOG/DEVLOG
  - **For ADRs:** Create new ADR that supersedes incorrect one
  - **For archived entries:** Add correction note, don't modify archive
- [ ] Add examples of common rollback scenarios
- [ ] Document in validation guide

### Task 15.5: Create Conflict Resolution Guide (Teams)
- [ ] Create `product/docs/conflict-resolution-guide.md`
- [ ] Document how to resolve conflicts:
  - **Two AI agents create conflicting ADRs:** Human decides, mark one as superseded
  - **AI makes bad decision:** Human reviews, creates correction ADR
  - **Human disagrees with AI documentation:** Human edits, AI learns from feedback
- [ ] Add examples of common conflicts
- [ ] Keep it simple (not full enterprise governance)

### Task 15.6: Add Review Workflow Examples
- [ ] Create `product/examples/governance/` directory
- [ ] Add example PR with AI-generated documentation
- [ ] Add example review comments
- [ ] Add example ADR approval workflow
- [ ] Add example rollback scenario
- [ ] Document in governance guide

### Task 15.7: Update Starter Packs
- [ ] Add governance rules to both starter packs
- [ ] Add PR review checklist template
- [ ] Update READMEs with governance setup
- [ ] Add governance examples

### Task 15.8: Test Governance System
- [ ] Test ADR lifecycle with AI assistants
- [ ] Test human-in-the-loop prompts
- [ ] Test rollback procedures
- [ ] Test with solo developer workflow
- [ ] Test with team workflow (2-3 developers)
- [ ] Document test results

---

## Deliverables

1. **ADR Lifecycle:**
   - Updated `product/docs/ADR_how_to.md`
   - Updated ADR template with status field

2. **AI Rules:**
   - Updated `log-file-maintenance.md` with human approval section
   - Approval prompt format

3. **Documentation:**
   - `product/docs/pr-review-checklist.md`
   - `product/docs/rollback-guide.md`
   - `product/docs/conflict-resolution-guide.md`

4. **Examples:**
   - `product/examples/governance/` with review/rollback examples

5. **Starter Pack Integration:**
   - Governance rules in both starter packs
   - Updated READMEs

---

## Technical Notes

### ADR Status Workflow

**Solo Developer:**
1. AI creates ADR with status "Proposed"
2. Developer reviews ADR
3. Developer manually changes status to "Accepted" (or asks AI to do it)
4. ADR is committed

**Team:**
1. AI creates ADR with status "Proposed"
2. AI creates PR with ADR
3. Team reviews via PR comments
4. After approval, status changed to "Accepted"
5. PR merged

### Human Approval Prompts

**Example: Creating ADR**
```
🧑 HUMAN APPROVAL REQUIRED

Action: Create ADR-009: Switch from REST to GraphQL
Reason: Significant architectural decision with long-term impact
Impact: New ADR file created, referenced in DEVLOG

Proceed? (yes/no)
```

**Example: Archiving DEVLOG**
```
🧑 HUMAN APPROVAL REQUIRED

Action: Archive DEVLOG entries older than 30 days
Reason: Token budget exceeded (18,500 / 15,000 tokens)
Impact: 12 entries moved to archive/DEVLOG-2025-10.md

Proceed? (yes/no)
```

### Rollback Examples

**Scenario 1: Incorrect CHANGELOG entry (recent commit)**
```bash
# Solo developer, not yet pushed
git commit --amend
# Edit CHANGELOG.md to fix entry
git add project/planning/CHANGELOG.md
git commit --amend --no-edit
```

**Scenario 2: Incorrect DEVLOG entry (already merged)**
```md
### 2025-11-03: Correction to Previous Entry

**Correction:** The entry dated 2025-11-02 incorrectly stated we chose 
PostgreSQL for performance reasons. The actual reason was team familiarity 
and existing infrastructure. See ADR-003 for accurate rationale.
```

**Scenario 3: Incorrect ADR (already merged)**
```md
# ADR-010: Supersedes ADR-009 (GraphQL Decision)

**Status:** Accepted  
**Supersedes:** ADR-009

**Context:** ADR-009 incorrectly recommended GraphQL. After further analysis...
```

---

## Simplified vs. Enterprise

**This Epic (Simplified for Solo/Teams):**
- ✅ ADR lifecycle (Proposed → Accepted)
- ✅ Human approval for critical actions
- ✅ Simple rollback procedures
- ✅ Basic conflict resolution
- ❌ No formal approval workflows
- ❌ No multi-level review processes
- ❌ No audit trails or compliance features

**Future Enterprise Version (Epic 16+):**
- Full approval workflows with multiple reviewers
- Audit trails for compliance
- Integration with JIRA/Confluence
- Role-based permissions
- Automated compliance checks

---

## Testing Strategy

1. **Solo Testing:** Test with single developer workflow
2. **Team Testing:** Test with 2-3 developers collaborating
3. **AI Testing:** Verify AI asks for approval correctly
4. **Rollback Testing:** Test all rollback scenarios
5. **Conflict Testing:** Test conflict resolution procedures

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI ignores approval prompts | High | Make prompts mandatory, test extensively |
| Rollback procedures too complex | Medium | Keep simple, provide clear examples |
| Teams find governance too lightweight | Low | Document as "simplified", plan enterprise version later |
| Solo developers find it too heavy | Medium | Make governance optional for solo, recommended for teams |

---

## Dependencies

- Epic 13 (Validation) - Governance builds on validation
- Epic 8 (Profile System) - Different governance for solo vs. team profiles

---

## Notes

**Why This is P1 (Not P0):**

This is important for teams but optional for solo developers. Unlike security (P0) and validation (P0), you can use the system without governance - it just won't have review processes.

**Target Users:**
- Teams (2+ developers) - RECOMMENDED
- Solo developers - OPTIONAL (nice to have for critical decisions)

**Success Metric:**
Teams report clear review processes for AI-generated documentation.

