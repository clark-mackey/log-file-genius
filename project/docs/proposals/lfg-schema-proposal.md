# LFG Schema Proposal: Machine-Parseable Structure for Log File Genius

**Author:** Clark Mackey
**Date:** 2026-02-02
**Status:** Draft → **REVISED** (Code-Police Review 2026-02-02)
**Target Version:** LFG v0.3.0
**Epic:** 8 (AI Context Optimization)

---

## Mission Alignment

**Mission:** "Help AI agents not get lost, not waste tokens"

**How this proposal aligns:**
- ✅ Enables AI agents to query log files semantically (not just keyword search)
- ✅ Reduces token waste by allowing targeted retrieval instead of full-file scans
- ✅ Cross-references help AI traverse decision→change→incident chains

**Scope limitation (per Code-Police review):**
- ⛔ NO CLI tools (developer convenience, not AI benefit)
- ⛔ NO VS Code extensions (developer experience, not AI benefit)
- ⛔ NO external index files (adds complexity, token cost)

---

## Problem Statement

Current LFG files are human-readable prose with inconsistent structure. AI agents cannot reliably:
- Query "all decisions with status Accepted"
- Find "changes affecting file X"
- Search "objectives by completion state"
- Cross-reference entries across projects

Each project's logs are idiosyncratic, making multi-project search impractical.

---

## Design Principles

1. **Additive, not breaking** - Existing files remain valid; schema is opt-in
2. **Human readable first** - Raw markdown must remain clean and scannable
3. **Tiered metadata** - Simple entries inline, complex entries condensed block
4. **Consistent IDs** - Enforced format for cross-referencing
5. **No external dependencies** - Plain markdown, no databases, no tooling required
6. **AI-first** - Every feature must pass mission test: reduce tokens OR help AI navigate

---

## Schema Definitions

### File-Level Frontmatter

Every LFG file MAY include YAML frontmatter with these fields:

```yaml
---
lfg_version: "0.3"           # Schema version (required if using schema)
file_type: devlog            # devlog | changelog | state | adr | incident
project: agent-blitzer       # Project identifier (for multi-project search)
last_updated: 2026-02-02     # ISO date
---
```

### Entry Types

Each entry within a file has a type that determines its schema:

| Type | Used In | Purpose |
|------|---------|---------|
| `decision` | DEVLOG, ADR | Architectural choices with rationale |
| `milestone` | DEVLOG | Significant accomplishments |
| `incident` | DEVLOG, incidents/ | Problems and resolutions |
| `task` | STATE | Active/completed work items |
| `change` | CHANGELOG | Code changes with file references |
| `context` | DEVLOG | Current project state (source of truth) |

---

## Entry Schemas (Tiered Approach)

**Principle:** Simple entries use inline metadata. Complex entries use condensed block.

### Tier 1: Inline Metadata (CHANGELOG, simple entries)

For entries with ≤4 fields, use end-of-line comments:

```markdown
- Fixed login bug. Files: `src/auth.js`. Commit: `abc123` <!-- id:CHG-2026-02-01-001 cat:fixed -->
- Added user dashboard. Files: `src/dashboard.js`. <!-- id:CHG-2026-02-01-002 cat:added refs:DEC-001 -->
```

**Inline format:** `<!-- id:{ID} cat:{category} refs:{refs} -->`

### Tier 2: Condensed Block (DEVLOG decisions, milestones, incidents)

For entries with 5+ fields, use single-line block:

```markdown
<!-- lfg id:DEC-2026-02-01-001 status:accepted tags:security,auth refs:ADR-006 -->
### 2026-02-01: Decision - Use JWT Tokens
**Status:** Accepted
**Rationale:** Industry standard, stateless, works with our API gateway.
```

**Block format:** `<!-- lfg id:{ID} status:{status} tags:{csv} refs:{csv} -->`

### Tier 3: Full Block (Context section only)

Only the Current Context section uses multi-line YAML (one per file):

```yaml
<!-- lfg:context
version: v0.1.0
phase: development
branch: main
updated: 2026-02-01
-->
```

---

## Entry Type Reference

### Change Entry (CHANGELOG) - Tier 1 Inline

```markdown
- Description. Files: `path`. Commit: `hash` <!-- id:CHG-2026-02-01-001 cat:fixed refs:INC-001 -->
```

| Field | Format | Required |
|-------|--------|----------|
| `id` | CHG-DATE-SEQ | YES |
| `cat` | added/changed/fixed/removed/security | YES |
| `refs` | comma-separated IDs | NO |

### Decision Entry (DEVLOG) - Tier 2 Block

```markdown
<!-- lfg id:DEC-2026-02-01-001 status:accepted tags:security refs:ADR-006 -->
### 2026-02-01: Decision Title
```

| Field | Format | Required |
|-------|--------|----------|
| `id` | DEC-DATE-SEQ | YES |
| `status` | proposed/accepted/deprecated/superseded | YES |
| `tags` | comma-separated | NO |
| `refs` | comma-separated IDs | NO |

### Milestone Entry (DEVLOG) - Tier 2 Block

```markdown
<!-- lfg id:MIL-2026-02-01-001 tags:deployment,infrastructure refs:DEC-001 -->
### 2026-02-01: Milestone Title
```

### Incident Entry (DEVLOG) - Tier 2 Block

```markdown
<!-- lfg id:INC-2026-02-01-001 sev:high status:resolved refs:CHG-001 -->
### 2026-02-01: Incident Title
```

| Field | Format | Required |
|-------|--------|----------|
| `id` | INC-DATE-SEQ | YES |
| `sev` | low/medium/high/critical | YES |
| `status` | open/investigating/resolved | YES |
| `refs` | comma-separated IDs | NO |

### Task Entry (STATE) - Tier 1 Inline

```markdown
- [ ] Task description <!-- id:TSK-2026-02-01-001 status:in_progress -->
```

### Task Entry (STATE)

```yaml
<!-- lfg:entry
id: TSK-2026-02-01-001
type: task
status: in_progress       # not_started | in_progress | blocked | complete
assignee: blitz
branch: feature/mcp-tools
blockers: [TSK-2026-01-31-002]
-->
```

### Context Entry (DEVLOG - Current Context section)

```yaml
<!-- lfg:context
version: v0.1.0-dev
phase: deployed
branch: main
updated: 2026-02-01
-->
```

---

## ID Format (REQUIRED)

All IDs MUST follow the pattern: `{TYPE}-{DATE}-{SEQUENCE}`

| Component | Format | Example | Validation Regex |
|-----------|--------|---------|------------------|
| TYPE | 3 uppercase letters | DEC, MIL, INC | `[A-Z]{3}` |
| DATE | ISO date | 2026-02-01 | `\d{4}-\d{2}-\d{2}` |
| SEQUENCE | 3 digits | 001, 002 | `\d{3}` |

**Full ID regex:** `^(DEC|MIL|INC|CHG|TSK|ADR)-\d{4}-\d{2}-\d{2}-\d{3}$`

**Valid examples:**
- `DEC-2026-02-01-001` - First decision on Feb 1, 2026
- `INC-2026-02-01-002` - Second incident on Feb 1, 2026

**Exception:** ADR files MAY use legacy format `ADR-NNN` for backward compatibility.

**Invalid examples (MUST reject):**
- `DEC001` - Missing date and sequence
- `decision-2026-02-01` - Wrong type format
- `DEC-2026-2-1-1` - Wrong date/sequence format

---

## Cross-References

The `refs` field enables linking between entries:

```yaml
refs: [ADR-006, DEC-2026-01-31-001, INC-2026-02-01-001]
```

Agents can traverse these references to understand:
- Which decisions led to which changes
- Which incidents triggered which fixes
- Which milestones depend on which tasks

---

## Example: Before and After

### CHANGELOG Example (Tier 1 - Inline)

**Before:**
```markdown
### Fixed
- Fixed login timeout bug. Files: `src/auth.js`. Commit: `abc123`
- Fixed null pointer in dashboard. Files: `src/dashboard.js`. Commit: `def456`
```

**After:**
```markdown
### Fixed
- Fixed login timeout bug. Files: `src/auth.js`. Commit: `abc123` <!-- id:CHG-2026-02-01-001 cat:fixed -->
- Fixed null pointer in dashboard. Files: `src/dashboard.js`. Commit: `def456` <!-- id:CHG-2026-02-01-002 cat:fixed refs:INC-001 -->
```

**Impact:** +15-20 tokens per entry. Human readability preserved.

---

### DEVLOG Example (Tier 2 - Condensed Block)

**Before:**
```markdown
## 2026-02-01: Agentic Loop Complete

**Milestone:** AgentRunner with approval gates - Blitz is now an autonomous agent

### What was built
Gap analysis revealed we had all infrastructure...
```

**After:**
```markdown
<!-- lfg id:MIL-2026-02-01-001 tags:agent,infrastructure refs:DEC-001,ADR-006 -->
## 2026-02-01: Agentic Loop Complete

**Milestone:** AgentRunner with approval gates - Blitz is now an autonomous agent

### What was built
Gap analysis revealed we had all infrastructure...
```

**Impact:** +1 line, ~25 tokens. Minimal visual noise.

---

### Side-by-Side Comparison

| Approach | Lines Added | Tokens Added | Human Readable |
|----------|-------------|--------------|----------------|
| Original block (6-line YAML) | 6 | ~45 | ❌ Cluttered |
| Condensed block (1-line) | 1 | ~25 | ✅ Acceptable |
| Inline (end of line) | 0 | ~18 | ✅ Clean |

---

## Querying Examples

With this schema, agents can use regex to query:

```python
# Find all accepted decisions
import re
pattern = r'<!-- lfg id:(DEC-[^ ]+) status:accepted'
decisions = re.findall(pattern, devlog_content)

# Find all changes referencing an incident
pattern = r'<!-- id:(CHG-[^ ]+).*refs:.*INC-001'
changes = re.findall(pattern, changelog_content)

# Find all high-severity incidents
pattern = r'<!-- lfg id:(INC-[^ ]+) sev:high'
incidents = re.findall(pattern, devlog_content)
entries = lfg.query_all(type="decision", tags__contains="security")
```

---

## Appendix: Full Field Reference

### File-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lfg_version` | string | Yes* | Schema version (e.g., "0.3") |
| `file_type` | enum | No | devlog, changelog, state, adr, incident |
| `project` | string | No | Project identifier for multi-project search |
| `last_updated` | date | No | ISO date of last update |

*Required only if using schema features

### Entry Fields (All Types)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (TYPE-DATE-SEQ format) |
| `type` | enum | Yes | decision, milestone, incident, change, task, context |
| `date` | date | No | ISO date of entry |
| `tags` | array | No | Searchable tags |
| `files` | array | No | Affected file paths |
| `refs` | array | No | Cross-references to other entries |

### Decision-Specific Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `status` | enum | proposed, accepted, deprecated, superseded | Decision status |
| `supersedes` | string | Entry ID | ID of decision this supersedes |

### Incident-Specific Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `severity` | enum | low, medium, high, critical | Impact level |
| `status` | enum | open, investigating, resolved | Resolution status |
| `root_cause` | string | Free text | Brief root cause description |

### Change-Specific Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `category` | enum | added, changed, fixed, deprecated, removed, security | Change type |
| `commit` | string | Git hash | Associated commit |

### Task-Specific Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `status` | enum | not_started, in_progress, blocked, complete | Task status |
| `assignee` | string | Agent/person name | Who owns this task |
| `branch` | string | Git branch | Associated branch |
| `blockers` | array | Entry IDs | Tasks blocking this one |

### Context-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Current project version |
| `phase` | string | Current project phase |
| `branch` | string | Active git branch |
| `updated` | date | Last context update |

---

## Validation Rules

### YAML Syntax Validation

Entry metadata MUST be valid YAML. Invalid YAML MUST be rejected:

```yaml
<!-- lfg:entry
id: DEC-2026-02-01-001    ✅ Valid
type: decision
-->

<!-- lfg:entry
id: DEC-2026-02-01-001
type: decision            ❌ Invalid - missing closing -->
```

### Reference Validation

The `refs` field MUST contain valid entry IDs:
- Each reference MUST match ID format regex OR legacy ADR format
- References to non-existent entries: WARN (not error, for cross-project refs)

### Required vs Optional Fields

| Field | Required | Default |
|-------|----------|---------|
| `id` | YES | - |
| `type` | YES | - |
| `date` | NO | Entry creation date |
| `status` | NO | Type-specific default |
| `tags` | NO | `[]` |
| `files` | NO | `[]` |
| `refs` | NO | `[]` |

---

## Acceptance Criteria

### Must Have (for v0.3.0 acceptance)

1. **AI Parsing Verified:** Claude, GPT-4, and Gemini can parse HTML comment YAML without errors
2. **Backward Compatible:** Existing LFG files without schema pass validation
3. **Token Budget Met:** Overhead ≤5% for typical DEVLOG (10 entries)
4. **Navigation Improvement Measured:** AI agents can answer targeted queries 50% faster than full-file scan

### Must NOT Have (rejected scope)

- ❌ CLI query tools (developer convenience)
- ❌ VS Code/IDE extensions (developer experience)
- ❌ External index files (complexity, token cost)
- ❌ Auto-migration tools (developer tooling)

---

## Migration Path

### Phase 1: Schema Specification (v0.3.0) - THIS PROPOSAL

1. Define schema with validation rules ✅
2. Update LFG templates to include metadata examples
3. Test AI agent parsing capabilities
4. Measure navigation improvement vs token cost
5. Document in LFG v0.3.0 release

### ~~Phase 2: Tooling~~ ❌ REJECTED

~~CLI tools, VS Code extensions~~ - Rejected per Code-Police review. Serves developers, not AI agents.

### ~~Phase 3: Multi-project~~ ⏸️ DEFERRED

~~Index files, cross-project search~~ - Deferred until Phase 1 proves AI navigation benefits.

---

## Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| File without frontmatter | Valid, treated as untyped |
| Entry without metadata | Valid, not queryable |
| Unknown fields in metadata | Preserved, ignored by parser |
| Old LFG version reads new file | Works (metadata in HTML comments) |
| Invalid YAML in comment | ERROR - must fix before commit |

**Compatibility Test Required:** Run against 10+ existing LFG projects before release.

---

## Token Impact (Revised with Tiered Approach)

| Tier | Component | Tokens Added |
|------|-----------|--------------|
| 3 | File frontmatter | ~30 tokens (1 per file) |
| 3 | Context block | ~25 tokens (1 per file) |
| 2 | Condensed block (decision/milestone) | ~25 tokens each |
| 1 | Inline metadata (change/task) | ~18 tokens each |

### Comparison: Original vs Tiered

| Scenario | Original Block | Tiered Approach | Savings |
|----------|----------------|-----------------|---------|
| CHANGELOG (10 changes) | ~400 tokens | ~180 tokens | **55%** |
| DEVLOG (5 decisions, 3 milestones, 2 incidents) | ~400 tokens | ~250 tokens | **37%** |
| Combined typical project | ~800 tokens | ~430 tokens | **46%** |

**Tiered approach cuts token overhead nearly in half** while preserving queryability.

**Net token impact:** Likely NEGATIVE (saves more than it costs) for agents doing targeted queries.

---

## Open Questions

1. ~~**Index file format**~~ - Deferred (no index files in Phase 1)
2. **Auto-generation** - Should AI agents auto-generate IDs, or require manual entry?
3. **Validation strictness** - Warn vs error on invalid metadata?

---

## Next Steps

1. ✅ Review proposal with Code-Police agent (DONE - 2026-02-02)
2. ✅ Revised to tiered approach for human readability (DONE - 2026-02-02)
3. Test AI agent parsing (Claude, GPT-4, Gemini) with sample metadata
4. Update LFG templates with tiered schema examples
5. Measure navigation improvement vs baseline
6. If acceptance criteria met → merge into Epic 8

---

## Review History

| Date | Reviewer | Verdict | Notes |
|------|----------|---------|-------|
| 2026-02-02 | Code-Police v2 | REVISE | Accept Phase 1, reject Phase 2/3, add validation rules |
| 2026-02-02 | Augment Agent | REVISE | Applied Code-Police recommendations |
| 2026-02-02 | Clark Mackey | REVISE | Tiered approach for human readability |
