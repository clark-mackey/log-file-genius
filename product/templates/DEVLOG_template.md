# Development Log

A narrative chronicle of the project journey - the decisions, discoveries, and pivots that shaped the work.

---

## Related Documents

📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records
📈 **[STATE](./STATE.md)** - Current project state and metrics

> **For AI Agents:** This file tells the story of *why* decisions were made. Before starting work, read **Current Context** and **Decisions (ADR)** sections. For technical details of *what* changed, see CHANGELOG.md.

---

## Current Context (Source of Truth)

**Last Updated:** 2025-10-29

### Project State
- **Project:** [Your Project Name]
- **Current Version:** v0.7.0-dev
- **Active Branch:** `feature/analytics-dashboard`
- **Phase:** Pre-launch (pilot testing)

### Stack & Tools
- **Backend:** Python 3.11, FastAPI, Uvicorn
- **Database:** Supabase (Postgres 15)
- **Frontend:** React 18, TypeScript, Tailwind CSS
- **Deployment:** Railway (staging), TBD (production)
- **Testing:** pytest, coverage >90% required

### Standards & Conventions
- **Code Style:** `black` (Python), `prettier` (JS/TS)
- **Commits:** Conventional Commits format
- **Decisions:** ADRs required for architectural choices
- **Testing:** All new features require tests before merge
- **API:** RESTful, versioned (`/v1/`), follows ADR-002 error model

### Key Architectural Decisions
- **ADR-003 (2025-10-29):** Conservative Metadata Management [→ Full ADR](../docs/adr/003-conservative-metadata-management.md)
- **ADR-002 (2025-10-25):** Unified API Error Model [→ Full ADR](../docs/adr/002-unified-error-model.md)
- **ADR-001 (2025-10-18):** PKCE Auth Flow [→ Full ADR](../docs/adr/001-pkce-auth-flow.md)

### Constraints & Requirements
- **Performance:** P95 latency < 250ms for all API endpoints
- **Security:** All endpoints require authentication except `/health`
- **Data:** Never delete user data without explicit consent
- **Compatibility:** Support Claude Desktop 1.2024.10.29+

### Current Objectives (Week of Oct 27)
- [x] Ship v0.6.4 with metadata fallback parsing
- [ ] Complete analytics dashboard UI foundation
- [ ] Draft ADR for feature flag service architecture
- [ ] Onboard 5 pilot customers with existing skills

### Known Risks & Blockers
- **Blocker:** The `chart.js` library integration is proving difficult with our reactive state management. Investigating alternatives (Recharts, Victory).
- **Risk:** Railway deployment may hit memory limits at scale. Monitoring usage patterns in pilot.
- **Risk:** Feedback sampling (20%) may not capture enough data for rare edge cases.

### Entry Points (For Code Navigation)
- **Backend Main:** `core/mcp-server/src/main.py`
- **API Routes:** `core/mcp-server/src/routes/`
- **Database Schema:** `core/database/schema.sql`
- **Frontend App:** `web/src/App.tsx`

---

## Decisions (ADR Index) - Newest First

- **ADR-003 (2025-10-29):** Conservative Metadata Management - Only manage CSF fields; preserve unknown metadata [→ Full ADR](../docs/adr/003-conservative-metadata-management.md)
- **ADR-002 (2025-10-25):** Unified API Error Model - Standardize error responses across all v1 endpoints [→ Full ADR](../docs/adr/002-unified-error-model.md)
- **ADR-001 (2025-10-18):** PKCE Auth Flow - Use PKCE + token rotation for security [→ Full ADR](../docs/adr/001-pkce-auth-flow.md)

---

## Daily Log - Newest First

### 2025-10-29: Shipping v0.6.4 - The Onboarding Challenge

**The Situation:** We had our first customer sign up with 15 existing Claude Skills created with other tools. These skills worked, but didn't follow CSF conventions - fields were in metadata instead of the body, missing our tracking fields, non-compliant YAML structure.

**The Challenge:** How do we onboard these customers without breaking their existing skills or forcing manual edits of 15+ files?

**The Decision:** We built conservative metadata fallback parsing. The `enhance_skill` tool now reads from body content (our standard) OR metadata (fallback for compatibility). Critically, we only manage our own fields (`alias`, `version`, `id`) and never delete metadata we don't own. This is codified in ADR-003.

**Why This Matters:** If we had taken the aggressive approach (delete unknown metadata), we'd become a hidden cause of breakage for customers using other tools on the same skill files. The conservative approach enables ecosystem compatibility.

**The Implementation:** Enhanced `_parse_skill_md` with fallback logic, added 3 new tests for metadata scenarios, created comprehensive onboarding documentation for customers with existing skills.

**The Result:** Smooth onboarding flow - customers can bulk register all skills with `register_all_skills`, then optionally migrate to CSF standards with `enhance_skill`. No data loss, no manual editing required.

**Files Changed:** `enhance_skill.py`, `test_frontmatter_compliance.py`, `docs/pilot/onboarding-existing-skills.md`

**Shipped:** v0.6.4

---

### 2025-10-28: The Feedback Loop That Actually Works

**The Problem:** We had built the entire feedback infrastructure - database, `rate_skill` tool, authentication - but Claude never asked for feedback when testing skills.

**The Investigation:** Downloaded a packaged skill and examined the SKILL.md file. The feedback instructions were there, but buried at the very end after a horizontal rule. Claude was treating it as optional supplementary information, not part of the core workflow.

**The Realization:** Feedback collection needs to be **the final step in the workflow itself**, not an afterthought in a separate section.

**The Fix:** Integrated feedback as step 4 in the workflow: "Get rating: Ask 'Rate this 1-5?' → When user responds, IMMEDIATELY call `rate_skill`..."

**The Second Problem:** When users typed "5", Claude took 5-7 seconds to respond. It was overthinking a simple rating! The instruction said "When user responds" but didn't say "immediately" or "don't overthink."

**The Second Fix:** Added explicit instruction: "IMMEDIATELY call `rate_skill`... Don't overthink - just capture and call."

**The Result:** Instant feedback collection, no delay. The word "IMMEDIATELY" cut response time from 5-7 seconds to <1 second.

**The Insight:** When working with AI agents, explicit instructions about timing and simplicity matter. "When user responds" ≠ "immediately when user responds."

**Files Changed:** `create_skill.py`, `templates/feedback-section-template.md`

---

### 2025-10-27: Roadmap Pivot - Railway First

**The Context:** Original roadmap had Railway deployment in "post-launch V3" phase. Current tester onboarding required Python install, venv setup, Supabase credentials, environment variables.

**The Realization:** Hosted onboarding is 10x easier - just add one URL to Claude Desktop config. More testers = better feedback before we build the analytics dashboard.

**The Decision:** Move Railway deployment from post-launch to v0.6.0 (next priority after v0.6.4).

**The Tradeoff:** Delays analytics dashboard by ~1 week, but the feedback we'll get from easier onboarding is more valuable than early analytics.

**Updated Roadmap:**
- v0.5.0 - Feedback Loop ✅
- v0.6.0 - Railway Deployment 🚀 (moved up)
- v0.7.0 - Analytics Dashboard
- v0.8.0 - Web Interface
- v0.9.0 - Public Marketplace
- v1.0.0 - Production Launch

**Documents Updated:** PRD roadmap, progress report timeline, created `V0.6.0-Railway-Deployment-Plan.md`

---

### 2025-10-26: YAML Frontmatter Compliance Crisis

**The Crisis:** Skills were failing to upload to Claude Desktop with cryptic YAML parsing errors.

**The Investigation:** Claude's Agent Skills spec only allows specific top-level YAML keys: `name`, `description`, `license`, `allowed-tools`, `metadata`. We were adding `alias`, `version`, and `id` as top-level keys.

**The Root Cause:** We had assumed YAML frontmatter was flexible, but Claude has a strict schema for skill files.

**The Fix:** Moved our fields into the `metadata` block where custom fields belong. Updated all tools to read/write from `metadata.alias`, `metadata.version`, `metadata.id`.

**The Verification:** Created test skills, uploaded to Claude Desktop - all successful.

**The Lesson:** Always validate against the official spec, even when something "should" work. YAML flexibility doesn't mean arbitrary schemas are accepted.

**Files Changed:** `create_skill.py`, `enhance_skill.py`, `package_skill.py`, all tests

**Shipped:** v0.6.3 (hotfix)

---

## Archive

**Entries older than 14 days** are archived for token efficiency:
- [DEVLOG-2025-10-W3.md](../archive/DEVLOG-2025-10-W3.md) - Week of Oct 20-26
- [DEVLOG-2025-10-W2.md](../archive/DEVLOG-2025-10-W2.md) - Week of Oct 13-19
- [DEVLOG-2025-10-W1.md](../archive/DEVLOG-2025-10-W1.md) - Week of Oct 6-12

---

## Template Guidelines (Remove this section in actual use)

### Entry Format for Daily Log

Each entry should tell a story with this structure:

```markdown
### YYYY-MM-DD: Title - The Core Theme

**The Situation/Problem/Context:** Set the scene (1-2 sentences)

**The Challenge/Investigation/Realization:** What you discovered (1-3 sentences)

**The Decision/Fix/Solution:** What you did about it (1-3 sentences)

**Why This Matters/The Insight/The Lesson:** The takeaway (1-2 sentences)

**The Result/Impact/Outcome:** What happened (1 sentence)

**Files Changed:** `file1.py`, `file2.py`

**Shipped:** vX.Y.Z (if applicable)
```

### Best Practices for AI Efficiency

1. **Current Context is sacred** - Update it weekly or when major changes occur
2. **Keep daily entries focused** - One main story per day, not multiple mini-stories
3. **Use ADRs for decisions** - Link to them, don't duplicate the full rationale
4. **Archive aggressively** - Move entries >14 days to `/archive/DEVLOG-YYYY-MM-Wn.md`
5. **Link to files** - Help AI locate relevant code
6. **Preserve the narrative** - This is a story, not a bullet list
7. **But be concise** - Aim for 150-250 words per entry, not 500+

### What Belongs in DEVLOG vs CHANGELOG

**DEVLOG (this file):**
- Why decisions were made
- What you discovered/learned
- Context and rationale
- The story arc of the project
- Challenges and how you solved them

**CHANGELOG:**
- What changed (facts only)
- Version numbers
- File paths
- PR/issue links
- One-line descriptions

**ADRs (separate files):**
- Architectural decisions with long-term impact
- Tradeoffs and alternatives considered
- Formal decision records

### Token Efficiency Targets

- **Current Context section:** ~500-800 tokens (updated weekly)
- **ADR Index:** ~50-100 tokens (grows slowly)
- **Daily entry:** ~150-250 tokens each
- **Entire file:** <15,000 tokens with 14-day archive strategy
- **Archive trigger:** Entries older than 14 days

### Narrative Tips for Token Efficiency

- ✅ "The feedback instructions were buried at the end, so Claude treated them as optional."
- ❌ "We had built the entire feedback infrastructure - the `rate_skill` tool, the Supabase database, the authentication system. Everything was in place. But when we tested it with a real skill, Claude never asked for feedback. We were confused and frustrated. We downloaded the skill ZIP file and examined the SKILL.md file carefully..."

- ✅ "Added explicit 'IMMEDIATELY' instruction, cutting response time from 5-7 seconds to <1 second."
- ❌ "But then we noticed something frustrating. When the user typed '5' to rate the output, Claude took 5-7 seconds to respond. We could see it in the UI: 'Thinking about the significance of the number 5...' What?! Claude was overthinking a simple rating!"

**The difference:** Same story, same insights, 60-70% fewer tokens.

