# Log File Genius - Product Requirements Document (PRD)

## Goals and Background Context

### Goals

**Primary Mission: Help AI agents not get lost, not waste tokens.**

- **Stop context rot:** Reduce AI context bloat by 93% (90-110k → 7-10k tokens) so AI has room for actual code
- **Give AI genius-level memory:** Structured 5-document system (PRD, CHANGELOG, DEVLOG, STATE, ADRs) separates facts from narrative
- **Zero-search navigation:** Bidirectional frontmatter linking so AI never wastes tokens searching for files
- **Prevent AI confusion:** Token-based archival keeps logs lean, AI always has fresh relevant context
- **Multi-agent coordination:** STATE.md prevents agent collisions and duplicated work
- **Tool agnostic:** Works with any AI assistant (Augment, Claude Code, Cursor, Copilot)

### Background Context

AI coding assistants like Augment, Claude Code, and GitHub Copilot are increasingly used in software development, but they struggle when project context grows large. Traditional documentation approaches consume too much of the AI's context window, leaving less room for actual coding work. Clark Mackey developed a 5-document system (PRD, CHANGELOG, DEVLOG, STATE, ADRs) that provides complete project context while consuming less than 5% of an AI's context window. The system has proven effective in his own projects, reducing token usage by 93% (from ~90-110k to ~7-10k tokens) while maintaining full project history, current state, and decision rationale. This PRD defines a project to package this method into an installable GitHub repository with clear documentation and AI assistant rules, making it accessible to the broader developer community.

### Current State (As of December 2025)

**Repository Status:** ✅ Live on GitHub - 8 stars, public repository

**What's Working:**
- ✅ Augment starter pack complete (`.augment/rules/`, config, validation)
- ✅ Claude Code starter pack complete (`.claude/`, project instructions, rules)
- ✅ Working installer scripts (`install.ps1`, `install.sh`) - cross-platform
- ✅ Profile system (`.logfile-config.yml`) with 4 profiles (solo-developer, team, open-source, startup)
- ✅ Validation scripts (profile-aware, token counting)
- ✅ Core templates (CHANGELOG, DEVLOG, STATE, ADR)
- ✅ Git hooks for automated validation

**Known Issues (Priority Order):**
1. **Archival logic broken** - Uses date-based rules ("older than 2 weeks") instead of token/size-based limits
2. **Rule adherence inconsistent** - Augment Code doesn't consistently follow the maintenance rules
3. **Claude Code parity incomplete** - Needs to be as reliable as Augment (when Augment works)
4. **Documentation gaps** - Missing brownfield migration guides, troubleshooting, real-world examples

**What's Deferred:**
- ❌ Cursor support (deferred to post-MVP)
- ❌ Advanced features from context (hooks, slash commands) - alternative approach for future consideration

**Real-World Usage Insights:**
After several weeks of production use, the core methodology works but automation reliability needs improvement. The biggest pain points are archival automation and ensuring AI agents consistently follow the rules.

### Change Log

| Date       | Version | Description                                                                                                  | Author         |
|------------|---------|--------------------------------------------------------------------------------------------------------------|----------------|
| 2025-10-30 | 0.1     | Initial PRD draft                                                                                            | John (PM Agent) |
| 2025-12-20 | 0.2     | Updated with current state, known issues, and real-world usage insights                                      | John (PM Agent) |
| 2026-01-22 | 0.3     | Added Epic 8 (MCP Server), Epic 9 (CLI Tooling), enhanced Epic 7, Future Considerations section             | John (PM Agent) |
| 2026-02-01 | 0.4     | Added Epic 10 (Claude Code Subagent Integration), promoted from Future Considerations to HIGH VALUE priority | Augment Agent  |
| 2026-02-01 | 0.5     | MAJOR REFOCUS: Rejected Epics 9/10/11 (mission drift). New Epic 8 for AI context optimization. Epic 7 refined. | Augment Agent  |
| 2026-02-01 | 0.6     | Added Epics 12/13/17/19 to Epic List. Deferred Epic 15, rejected Epic 18. Aligned all epics with mission.   | Augment Agent  |

---

## Requirements

### Functional Requirements

- **FR1:** The repository shall include all five core template files (CHANGELOG template, DEVLOG template, STATE template, ADR template, PRD template) with proper cross-linking structure
- **FR2:** The repository shall include the log_file_how_to.md documentation explaining the complete 5-document system and usage patterns
- **FR3:** The repository shall include example AI assistant rules (update-planning-docs, status-update, log-file-maintenance-rule) for Augment and Claude Code that users can customize for their projects
- **FR4:** The repository shall provide a clear installation guide explaining how to copy files and configure them for a new project
- **FR5:** The repository shall include the ADR_how_to.md file explaining how to create and maintain Architectural Decision Records
- **FR6:** The repository shall provide example/starter content in each template showing proper formatting and structure
- **FR7:** The repository shall include a file structure recommendation showing where to place each document type
- **FR8:** The repository shall provide guidance on customizing relative paths for different project structures
- **FR9:** The repository shall include examples of archived log files demonstrating the archival process
- **FR10:** The repository shall provide a checklist or quick-start guide for first-time setup
- **FR11:** The repository shall include a comprehensive migration guide for integrating the system into existing projects (brownfield integration)

### Non-Functional Requirements

- **NFR1:** Documentation must be clear enough for developers unfamiliar with the system to install and configure it within 15 minutes
- **NFR2:** All template files must use relative paths to ensure portability across different project structures
- **NFR3:** The repository README must include before/after metrics (token usage reduction, documentation quality improvements) to demonstrate value
- **NFR4:** All documentation must be in Markdown format for maximum compatibility with AI coding assistants
- **NFR5:** The repository must be licensed appropriately for public use and modification (e.g., MIT License)
- **NFR6:** File naming conventions must be consistent and self-explanatory
- **NFR7:** The system must work with multiple AI coding assistants (Augment, Claude Code, Cursor, etc.), not just one specific tool

---

## Technical Assumptions

### Repository Structure: Monorepo

Single repository containing all templates, documentation, examples, and Augment rules in a clear folder structure.

### Service Architecture

Not applicable - this is a static documentation/template repository with no runtime services or deployment requirements.

### Testing Requirements

**Manual validation only** - No automated testing required. Quality assurance will be through:
- Manual review of template completeness
- Verification that all cross-links work correctly
- Testing installation process with fresh projects
- Validation that Augment rules load correctly

### Additional Technical Assumptions and Requests

- **Version Control:** GitHub repository with clear versioning (semantic versioning for releases)
- **Documentation Format:** All files in Markdown (.md) format for maximum AI assistant compatibility
- **File Organization:** Clear folder structure separating templates, examples, documentation, and Augment rules
- **License:** MIT License to allow free use, modification, and distribution
- **Dependencies:** Zero dependencies - pure Markdown files that work out of the box
- **Compatibility:** Designed to work with Augment, Claude Code, Cursor, and other AI coding assistants that support custom rules/instructions
- **Example Project:** Include a sample project structure showing the system in use
- **Maintenance Guide:** Documentation on how to keep the log files updated and when to archive old entries

---

## Epic List

### Epic 1: Repository Foundation & Core Templates ✅ MOSTLY COMPLETE
**Goal:** Establish the GitHub repository with all core template files, proper structure, and basic documentation so users can clone and start using the system.
**Status:** Core templates, installer, and starter packs complete. Some documentation gaps remain.

### Epic 2: Brownfield Installation Guide ⚠️ IN PROGRESS
**Goal:** Provide comprehensive guidance for adding the log file system to existing projects with existing documentation, enabling developers to migrate or integrate without starting from scratch.
**Status:** Basic guidance exists, but comprehensive migration strategies and content conversion guides are incomplete.

### Epic 3: Augment & Claude Code Platform Support ✅ MOSTLY COMPLETE
**Goal:** Deliver production-ready starter packs for Augment and Claude Code with feature parity and equal reliability.
**Status:** Both starter packs exist and work, but reliability issues (rule adherence, archival) need fixing. Cursor support deferred.

### Epic 4: Documentation & Usage Guides ⚠️ IN PROGRESS
**Goal:** Provide comprehensive documentation including installation guides, usage examples, and the complete log_file_how_to.md so users understand how to implement and maintain the system.
**Status:** Basic documentation exists, but troubleshooting, best practices, and real-world examples are incomplete.

### Epic 5: AI Assistant Integration & Automation ✅ COMPLETE
**Goal:** Deliver ready-to-use configuration files for Augment and Claude Code so users can automate log file maintenance.
**Status:** Starter packs complete with rules, validation scripts, and git hooks.

### Epic 6: Examples & Community Resources ⚠️ NOT STARTED
**Goal:** Provide real-world examples, sample projects, and community contribution guidelines so users can see the system in action and contribute improvements.
**Status:** Minimal examples exist. Need before/after comparisons, success stories, and community guidelines.

### Epic 7: Core Reliability & Bug Fixes 🔴 HIGH PRIORITY
**Goal:** Fix critical reliability issues to ensure AI agents get consistent, token-efficient context without confusion.
**Status:** REFINED - Stories reordered: 7.2 (Rule Adherence) → 7.3 (Parity) → 7.1 (Archival) → 7.4 (Validation) → 7.5 (Git Hooks). Stories 7.1-7.5 only.

### Epic 8: AI Context Optimization 🧠 NEW - MISSION CRITICAL
**Goal:** Build features that directly help AI agents not get lost and not waste tokens - smart summarization, token monitoring, AI-optimized formatting.
**Status:** EXPANDED - Stories 8.1-8.5 (original), Stories 8.6-8.11 (agent-first gaps: handoff, token self-assessment, verbosity, navigation, staleness, archival index). All new stories are rule/template changes only - zero new dependencies.

### Epic 12: Security & Secrets Detection 🔒 P0
**Goal:** Prevent AI agents from leaking secrets (passwords, API keys, PII) into logs. AI must learn what NOT to document.
**Status:** Planned. Spec: `project/specs/EPIC-12-security-secrets-detection.md`

### Epic 13: Validation & Reliability ✅ P0
**Goal:** Verify AI agents maintain logs correctly with automated validation and self-assessment.
**Status:** Planned. Spec: `project/specs/EPIC-13-validation-reliability.md`

### Epic 17: Incident Reports & Learning 📋 P1
**Goal:** Teach AI agents to create structured incident reports when failures occur - documenting what went wrong and how to prevent recurrence.
**Status:** Planned. Template WIP in `project/templates/`. Spec: `project/specs/EPIC-17-incident-reports-learning.md`

### ~~Epic 15: Governance & Review~~ ⏸️ DEFERRED
**Goal:** ~~Human review workflows for AI-generated documentation.~~
**Status:** DEFERRED - Team process feature, not direct AI benefit. Revisit after core epics complete.

### ~~Epic 18: Modular Installer~~ ❌ REJECTED
**Goal:** ~~Refactor installer to composable architecture.~~
**Status:** REJECTED - Developer tooling, zero AI benefit. Same category as Epics 9-11.

### Epic 19: Dogfooding Migration ✅ COMPLETE
**Goal:** Migrate this project to use /logs/ structure we distribute to users.
**Status:** COMPLETE - Migrated Nov 2025. Spec: `project/specs/EPIC-19-dogfooding-logs-migration.md`

### ~~Epic 9: CLI Tooling~~ ❌ REJECTED
**Goal:** ~~Provide CLI tools for developer convenience.~~
**Status:** REJECTED - Serves human developers, not AI agents. Does not reduce tokens or improve AI navigation. Moved to Rejected Ideas.

### ~~Epic 10: Claude Code Subagents~~ ❌ REJECTED
**Goal:** ~~Create subagents for autonomous documentation.~~
**Status:** REJECTED - Adds complexity that confuses AI agents. No proven architecture. Moved to Rejected Ideas.

### ~~Epic 11: Advanced Automation~~ ❌ REJECTED
**Goal:** ~~Git hook auto-population, CI enforcement.~~
**Status:** REJECTED - Serves development process, not AI memory. Zero AI benefit. Moved to Rejected Ideas.

---

## Epic 1: Repository Foundation & Core Templates

**Epic Goal:** Establish the GitHub repository with all core template files, proper structure, and basic documentation so users can clone and start using the system immediately.

### Story 1.1: Initialize Repository Structure ✅ COMPLETE

**As a** developer wanting to share the log file system,
**I want** a well-organized GitHub repository with clear folder structure,
**so that** users can easily navigate and understand where each component belongs.

#### Acceptance Criteria
1. ✅ Repository created with MIT License
2. ✅ Root README.md exists with project overview and quick-start instructions
3. ✅ Folder structure created: `/product/templates`, `/product/starter-packs`, `/product/docs`, `/product/scripts`
4. ✅ .gitignore file configured appropriately
5. ⚠️ Repository includes a CONTRIBUTING.md file for future contributors (PARTIAL - needs expansion)

**Status:** Complete. Repository is live on GitHub with 8 stars.

### Story 1.2: Create Core Template Files ✅ COMPLETE

**As a** developer adopting the log file system,
**I want** all five core template files (CHANGELOG, DEVLOG, STATE, ADR, PRD) with proper formatting,
**so that** I can copy them into my project and start using them immediately.

#### Acceptance Criteria
1. ✅ `CHANGELOG_template.md` created with proper Keep a Changelog format and cross-links
2. ✅ `DEVLOG_template.md` created with Current Context section and decision tracking structure
3. ✅ `STATE_template.md` created with active work, blockers, and priorities sections (<500 tokens)
4. ✅ `ADR_template.md` created with standard ADR format (Context, Decision, Consequences)
5. ✅ `PRD_template.md` created (or reference to external PRD template if using BMad)
6. ✅ All templates include placeholder cross-reference links using relative paths
7. ✅ Each template includes inline comments explaining how to customize it
8. ✅ Templates stored in `/product/templates` folder

**Status:** Complete. All core templates exist and are in use.

### Story 1.3: Create ADR How-To Documentation

**As a** developer new to Architectural Decision Records,  
**I want** clear documentation on what ADRs are and how to use them,  
**so that** I can create effective ADRs for my project decisions.

#### Acceptance Criteria
1. `ADR_how_to.md` file created in `/docs` folder
2. Document explains what ADRs are and when to create them
3. Document includes examples of good vs. poor ADRs
4. Document explains the ADR index structure and how to maintain it
5. Document includes guidance on ADR statuses (Proposed, Accepted, Deprecated, Superseded)
6. Document cross-references the ADR template file

### Story 1.4: Create File Structure Recommendation Guide

**As a** developer setting up the log file system,  
**I want** clear guidance on where to place each file type in my project,  
**so that** I can organize my documentation consistently and ensure cross-links work correctly.

#### Acceptance Criteria
1. File structure guide created showing recommended directory layout
2. Guide includes multiple example structures (monorepo, polyrepo, different project types)
3. Guide explains how to adjust relative paths for different structures
4. Guide includes a decision tree or flowchart for choosing structure
5. Guide stored in `/docs/file-structure-guide.md`

### Story 1.5: Create Quick-Start Installation Checklist

**As a** developer installing the log file system for the first time,  
**I want** a step-by-step checklist to follow,  
**so that** I don't miss any critical setup steps.

#### Acceptance Criteria
1. Quick-start checklist created in `/docs/quick-start.md`
2. Checklist includes: clone repo, copy templates, customize paths, verify cross-links, configure AI assistant rules
3. Checklist includes estimated time for each step
4. Checklist includes troubleshooting tips for common issues
5. Checklist references other documentation for detailed guidance
6. Root README.md links to the quick-start checklist prominently

---

## Epic 2: Brownfield Installation Guide

**Epic Goal:** Provide comprehensive guidance for adding the log file system to existing projects with existing documentation, enabling developers to migrate or integrate without starting from scratch.

### Story 2.1: Create Brownfield Assessment Guide

**As a** developer with an existing project,
**I want** guidance on assessing my current documentation,
**so that** I can determine the best migration strategy for my situation.

#### Acceptance Criteria
1. Assessment guide created in `/docs/brownfield-assessment.md`
2. Guide includes questionnaire to evaluate current documentation state (none, scattered, structured, comprehensive)
3. Guide identifies common documentation patterns (README-only, wiki-based, doc folders, inline comments)
4. Guide provides decision tree for choosing migration approach (full migration, gradual adoption, hybrid)
5. Guide includes effort estimates for different migration strategies
6. Guide helps identify which existing docs map to CHANGELOG, DEVLOG, ADR, or PRD
7. Guide includes examples of different starting scenarios
8. Guide includes safety checklist: backup existing files, use version control, test in branch first

### Story 2.2: Create Migration Strategy Guide

**As a** developer migrating existing documentation,
**I want** step-by-step migration strategies for different scenarios,
**so that** I can choose the approach that fits my project's needs.

#### Acceptance Criteria
1. Migration strategy guide created in `/docs/migration-strategies.md`
2. Guide includes "Big Bang" strategy (migrate everything at once) with pros/cons
3. Guide includes "Gradual Adoption" strategy (start with one document type) with pros/cons
4. Guide includes "Hybrid" strategy (keep some existing docs, add new system) with pros/cons
5. Each strategy includes step-by-step implementation plan
6. Each strategy includes rollback plan if migration doesn't work
7. Guide includes decision matrix to help choose the right strategy
8. Guide addresses team coordination during migration
9. Guide emphasizes safety-first approach: never delete existing files until new system is validated, use separate branch for migration, commit frequently during migration

### Story 2.3: Create Content Conversion Guide

**As a** developer converting existing documentation,
**I want** guidance on extracting and reformatting content from various sources,
**so that** I can populate the 5-document system with my existing knowledge.

#### Acceptance Criteria
1. Content conversion guide created in `/docs/content-conversion.md` (or integrated into Migration Guide)
2. Guide explains how to extract CHANGELOG content from: git history, release notes, existing CHANGELOG files
3. Guide explains how to extract DEVLOG content from: meeting notes, decision logs, project wikis, commit messages
4. Guide explains how to create STATE content from: current sprint boards, active task lists, blocker tracking
5. Guide explains how to identify and extract ADR content from: design docs, architecture docs, email threads
6. Guide explains how to create PRD from: existing requirements docs, user stories, product specs
7. Guide includes examples of before/after conversions for each document type
8. Guide includes tips for handling incomplete or missing historical information
9. Guide addresses how to handle conflicting information from multiple sources
10. Guide includes safety protocol: preserve original files in archive folder, never overwrite existing documentation, validate converted content before removing originals

### Story 2.4: Create Incremental Adoption Guide

**As a** developer wanting to try the system without full commitment,
**I want** guidance on adopting one document type at a time,
**so that** I can validate the approach before migrating everything.

#### Acceptance Criteria
1. Incremental adoption guide created in `/docs/incremental-adoption.md` (or integrated into Migration Guide)
2. Guide recommends starting order (e.g., start with CHANGELOG, then DEVLOG, then STATE, then ADRs, then PRD)
3. Guide explains how to use partial system (e.g., CHANGELOG + DEVLOG only, or add STATE for multi-agent coordination)
4. Guide shows how to integrate new documents with existing documentation
5. Guide includes success criteria for each phase (when to proceed to next document type)
6. Guide addresses how to handle cross-references when not all documents exist yet
7. Guide includes timeline estimates for each adoption phase
8. Guide explains how to get team buy-in incrementally
9. Guide emphasizes non-destructive approach: add new files alongside existing docs, validate each phase before proceeding, maintain existing documentation until team confirms new system works
10. Guide addresses common questions: "Can I skip ADRs?", "Do I need a PRD for small projects?", "Is STATE optional?"

### Story 2.5: Create Team Migration Guide

**As a** team lead migrating a team project,
**I want** guidance on coordinating migration across multiple developers,
**so that** the transition is smooth and everyone adopts the new system.

#### Acceptance Criteria
1. Team migration guide created in `/docs/team-migration.md`
2. Guide includes communication plan template for announcing the change
3. Guide includes training plan for getting team members up to speed
4. Guide addresses how to handle ongoing work during migration
5. Guide includes roles and responsibilities during migration (who updates what)
6. Guide addresses merge conflict prevention during transition period
7. Guide includes checklist for team readiness before starting migration
8. Guide includes tips for handling resistance or skepticism from team members
9. Guide explains how to establish new documentation habits and workflows
10. Guide includes safety protocols for team environments: require code review for migration PRs, establish rollback procedures, maintain existing docs until team consensus, use feature branch for migration work, document what was changed and where originals are archived

---

## Epic 3: Augment & Claude Code Platform Support

**Epic Goal:** Deliver production-ready starter packs for Augment and Claude Code with feature parity and equal reliability.

**Note:** Cursor support deferred to post-MVP. Focus on making Augment and Claude Code work reliably.

### Story 3.1: Augment Starter Pack ✅ COMPLETE

**As an** Augment user,
**I want** a complete starter pack with rules, validation, and configuration,
**so that** I can use Log File Genius with Augment immediately.

#### Acceptance Criteria
1. ✅ `.augment/rules/` directory with log-file-maintenance, status-update, update-planning-docs
2. ✅ `.logfile-config.yml` profile configuration
3. ✅ Validation scripts (PowerShell and Bash)
4. ✅ Git hooks for automated validation
5. ✅ README with installation and usage instructions
6. ✅ Profile-aware rules that read `.logfile-config.yml`

**Status:** Complete. Augment starter pack exists in `product/starter-packs/augment/`.

### Story 3.2: Claude Code Starter Pack ✅ COMPLETE

**As a** Claude Code user,
**I want** a complete starter pack with project instructions, rules, and configuration,
**so that** I can use Log File Genius with Claude Code immediately.

#### Acceptance Criteria
1. ✅ `.claude/project_instructions.md` with core principles and commands
2. ✅ `.claude/rules/` directory with log-file-maintenance, status-update, update-planning-docs
3. ✅ `.logfile-config.yml` profile configuration
4. ✅ Validation scripts (PowerShell and Bash)
5. ✅ Git hooks for automated validation
6. ✅ README with installation and usage instructions
7. ✅ Profile-aware rules that read `.logfile-config.yml`

**Status:** Complete. Claude Code starter pack exists in `product/starter-packs/claude-code/`.

### Story 3.3: Platform Comparison Guide ⚠️ INCOMPLETE

**As a** developer choosing between Augment and Claude Code,
**I want** a comparison of how the log file system works on each platform,
**so that** I can understand what features are available in my chosen tool.

#### Acceptance Criteria
1. Platform comparison guide created in `/product/docs/platform-comparison.md`
2. Guide includes comparison table showing feature support for Augment and Claude Code
3. Guide explains any platform-specific limitations or differences
4. Guide provides recommendations for which platform to use based on user needs
5. Guide includes installation difficulty ratings for each platform
6. Root README.md updated to link to platform comparison guide

**Status:** Not started. Need to document Augment vs Claude Code differences.

### Story 3.4: Installer Integration ✅ COMPLETE

**As a** user installing Log File Genius,
**I want** the installer to detect my AI assistant and install the correct starter pack,
**so that** I don't have to manually choose or configure files.

#### Acceptance Criteria
1. ✅ Installer detects Augment (checks for `.augment/` or Augment CLI)
2. ✅ Installer detects Claude Code (checks for `.claude/` or Claude CLI)
3. ✅ Installer prompts user to select if both detected
4. ✅ Installer copies correct starter pack files
5. ✅ Installer works on Windows (PowerShell) and Mac/Linux (Bash)
6. ✅ Installer handles errors gracefully

**Status:** Complete. `install.ps1` and `install.sh` work reliably (after significant debugging).

---

## Epic 4: Documentation & Usage Guides

**Epic Goal:** Provide comprehensive documentation including installation guides, usage examples, and the complete log_file_how_to.md so users understand how to implement and maintain the system across different AI assistants.

### Story 4.1: Create Comprehensive log_file_how_to.md

**As a** developer learning the log file system,
**I want** complete documentation explaining the philosophy, structure, and usage of the 5-document system,
**so that** I understand why and how to use CHANGELOG, DEVLOG, STATE, ADRs, and PRD effectively.

#### Acceptance Criteria
1. `log_file_how_to.md` created in `/docs` folder based on existing content from `/context`
2. Document explains the business problem (AI context window exhaustion, token waste)
3. Document describes all five document types (CHANGELOG, DEVLOG, STATE, ADR, PRD) and their purposes
4. Document includes token efficiency benefits with concrete metrics (93% reduction example)
5. Document explains cross-linking strategy and relative path usage
6. Document includes update frequency guidelines for each document type (STATE: every 30-60 min, CHANGELOG: after commits, DEVLOG: after decisions)
7. Document explains archival process for keeping files token-efficient
8. Document includes Context Layers progressive disclosure strategy (Layer 1: <500 tokens, Layer 2: <2k, Layer 3: <10k, Layer 4: on-demand)
9. Document includes multi-agent coordination guidance
10. Root README.md links to log_file_how_to.md as primary documentation

### Story 4.2: Create Installation Guide for Each Platform

**As a** developer installing the log file system,
**I want** step-by-step installation instructions specific to my AI assistant,
**so that** I can set up the system correctly without confusion.

#### Acceptance Criteria
1. Installation guide created for Augment in `/docs/install-augment.md`
2. Installation guide created for Claude Code in `/docs/install-claude-code.md`
3. Installation guide created for Cursor in `/docs/install-cursor.md`
4. Each guide includes: prerequisites, file copying steps, path customization, AI assistant configuration, verification steps
5. Each guide includes screenshots or examples where helpful
6. Each guide includes troubleshooting section for common issues
7. Root README.md links to all platform-specific installation guides

### Story 4.3: Create Usage Examples and Best Practices

**As a** developer using the log file system,
**I want** real-world examples and best practices,
**so that** I can use the system effectively and avoid common mistakes.

#### Acceptance Criteria
1. Best practices guide created in `/docs/best-practices.md`
2. Guide includes examples of good vs. poor CHANGELOG entries
3. Guide includes examples of good vs. poor DEVLOG entries
4. Guide includes guidance on when to create ADRs vs. DEVLOG entries
5. Guide includes tips for keeping documentation token-efficient
6. Guide includes examples of effective cross-linking
7. Guide includes guidance on balancing detail vs. brevity
8. Guide includes common anti-patterns to avoid

### Story 4.4: Create Maintenance and Archival Guide

**As a** developer maintaining the log file system over time,
**I want** clear guidance on when and how to archive old entries,
**so that** my documentation stays token-efficient as the project grows.

#### Acceptance Criteria
1. Maintenance guide created in `/docs/maintenance-guide.md`
2. Guide explains when to archive (file size thresholds, time-based rules)
3. Guide provides step-by-step archival process for CHANGELOG
4. Guide provides step-by-step archival process for DEVLOG
5. Guide explains how to maintain cross-references after archival
6. Guide includes example archive folder structure
7. Guide explains how to update Current Context sections regularly
8. Guide includes checklist for monthly/quarterly maintenance tasks

### Story 4.5: Create FAQ and Troubleshooting Guide

**As a** developer encountering issues with the log file system,
**I want** a FAQ and troubleshooting guide,
**so that** I can quickly resolve common problems without external help.

#### Acceptance Criteria
1. FAQ created in `/docs/faq.md`
2. FAQ includes questions about: choosing file locations, fixing broken cross-links, handling large projects, multi-repo scenarios
3. FAQ includes questions about AI assistant integration and rule configuration
4. FAQ includes questions about when to use each document type
5. Troubleshooting section includes solutions for: broken links, AI not following rules, token budget still too high, merge conflicts
6. FAQ includes "How do I know if it's working?" section with success indicators
7. Root README.md links to FAQ prominently

---

## Epic 5: AI Assistant Integration & Automation

**Epic Goal:** Deliver ready-to-use configuration files for Augment and Claude Code so users can automate log file maintenance.

**Status:** ✅ COMPLETE - Both Augment and Claude Code starter packs are production-ready.

### Story 5.1: Create Augment Rules Package ✅ COMPLETE

**As an** Augment user,
**I want** ready-to-use Augment rules for log file maintenance,
**so that** I can automate CHANGELOG, DEVLOG, and ADR updates without manual effort.

#### Acceptance Criteria
1. ✅ `update-planning-docs.md` rule created in `.augment/rules/` folder
2. ✅ `status-update.md` rule created in `.augment/rules/` folder
3. ✅ `log-file-maintenance.md` rule created in `.augment/rules/` folder
4. ✅ Each rule includes clear description of when and how to use it
5. ✅ Rules include placeholder paths that users customize for their project
6. ✅ Rules reference the correct template files and documentation
7. ✅ README in starter pack explains how to install and customize rules
8. ✅ Rules tested with Augment to verify functionality

**Status:** Complete. Rules exist in `product/starter-packs/augment/.augment/rules/`.

### Story 5.2: Create Claude Code Instructions Package ✅ COMPLETE

**As a** Claude Code user,
**I want** ready-to-use project instructions and rules for log file maintenance,
**so that** Claude Code automatically maintains my documentation files.

#### Acceptance Criteria
1. ✅ Project instructions created in `.claude/project_instructions.md`
2. ✅ Rules created in `.claude/rules/` (log-file-maintenance, status-update, update-planning-docs)
3. ✅ Instructions include examples showing expected behavior
4. ✅ Instructions include customization guide for different project structures
5. ✅ Installation README includes verification steps to confirm instructions are working
6. ✅ Instructions include guidance on when to manually override automated behavior
7. ✅ Instructions tested with multiple project structures to ensure portability

**Status:** Complete. Instructions exist in `product/starter-packs/claude-code/.claude/`.

### Story 5.4: Create Integration Testing Guide

**As a** developer setting up AI assistant integration,
**I want** a guide for testing that my AI assistant is correctly maintaining log files,
**so that** I can verify the automation is working before relying on it.

#### Acceptance Criteria
1. Integration testing guide created in `/docs/testing-integration.md`
2. Guide includes test scenarios for each rule/instruction (update-planning-docs, status-update, maintenance)
3. Guide includes expected outcomes for each test scenario
4. Guide includes troubleshooting steps if tests fail
5. Guide includes platform-specific testing notes for Augment, Claude Code, and Cursor
6. Guide includes checklist for verifying correct installation
7. Guide explains how to validate that cross-links are working correctly

### Story 5.5: Create Rule Customization Guide

**As a** developer with unique project needs,
**I want** guidance on customizing AI assistant rules for my specific workflow,
**so that** I can adapt the system to my project's structure and conventions.

#### Acceptance Criteria
1. Customization guide created in `/docs/customizing-rules.md`
2. Guide explains how to modify file paths in rules for different project structures
3. Guide explains how to add custom maintenance tasks to existing rules
4. Guide explains how to create new rules based on the provided templates
5. Guide includes examples of common customizations (different folder structures, additional document types, custom archival schedules)
6. Guide includes warnings about what NOT to change (core logic, cross-linking patterns)
7. Guide includes validation checklist after customization

---

## Epic 6: Examples & Community Resources

**Epic Goal:** Provide real-world examples, sample projects, and community contribution guidelines so users can see the system in action and contribute improvements.

### Story 6.1: Create Sample Project with Complete Documentation

**As a** developer learning the log file system,
**I want** a complete sample project showing the system in use,
**so that** I can see real examples of CHANGELOG, DEVLOG, ADRs, and PRD working together.

#### Acceptance Criteria
1. Sample project created in `/examples/sample-project` folder
2. Sample includes populated CHANGELOG.md with realistic entries and archive examples
3. Sample includes populated DEVLOG.md with Current Context, decision entries, and cross-references
4. Sample includes at least 3 ADR files demonstrating different decision types
5. Sample includes a PRD.md or reference to PRD structure
6. Sample demonstrates proper cross-linking between all documents
7. Sample includes README explaining what the sample demonstrates
8. Sample shows both recent entries and archived entries
9. Sample demonstrates token-efficient formatting

### Story 6.2: Create Before/After Comparison Example

**As a** developer evaluating the log file system,
**I want** a before/after comparison showing traditional documentation vs. the 5-document system,
**so that** I can understand the concrete benefits and token savings.

#### Acceptance Criteria
1. Before/after example created in `/examples/before-after` folder
2. "Before" folder shows traditional documentation approach (verbose, scattered context)
3. "After" folder shows same project using the 5-document system (CHANGELOG, DEVLOG, STATE, ADR, PRD)
4. Comparison document includes token count for each approach
5. Comparison document highlights key improvements (findability, token efficiency, AI comprehension)
6. Comparison includes metrics from real usage (e.g., "93% token reduction from ~90-110k to ~7-10k tokens")
7. Comparison explains what changed and why it's better
8. Root README.md links to before/after comparison prominently

### Story 6.3: Create Multi-Repo Example

**As a** developer working with multiple repositories,
**I want** an example showing how to use the log file system across a multi-repo project,
**so that** I can maintain consistent documentation across all my repositories.

#### Acceptance Criteria
1. Multi-repo example created in `/examples/multi-repo` folder
2. Example shows at least 2 related repositories (e.g., frontend + backend)
3. Example demonstrates how to handle cross-repo references
4. Example shows shared vs. repo-specific documentation
5. Example includes guidance on maintaining consistency across repos
6. Example README explains the multi-repo strategy and trade-offs
7. Example demonstrates how AI assistants can work across repos

### Story 6.4: Create Community Contribution Guidelines

**As a** developer wanting to improve the log file system,
**I want** clear contribution guidelines,
**so that** I can submit improvements, bug fixes, or new platform support.

#### Acceptance Criteria
1. CONTRIBUTING.md updated with detailed contribution guidelines
2. Guidelines include: how to report issues, how to submit PRs, coding standards, documentation standards
3. Guidelines explain the process for adding new AI assistant platform support
4. Guidelines include templates for bug reports and feature requests
5. Guidelines explain how to test changes before submitting
6. Guidelines include code of conduct for community interactions
7. Guidelines explain the review and merge process

### Story 6.5: Create Success Stories and Testimonials Section

**As a** developer considering the log file system,
**I want** to see success stories and testimonials from other users,
**so that** I can understand real-world benefits and use cases.

#### Acceptance Criteria
1. Success stories section created in `/docs/success-stories.md`
2. Section includes at least 3 example use cases (different project types, team sizes)
3. Each story includes: project context, problems faced, how the system helped, measurable outcomes
4. Section includes placeholder for community-submitted stories
5. Section includes instructions for submitting your own success story
6. Root README.md includes highlights from success stories
7. Section demonstrates diversity of use cases (solo dev, team, open source, enterprise)

---

## Success Metrics & Validation Strategy

### Deployment Channels

1. **Direct Clone/Fork** - Standard adoption method
   - Users clone: `git clone https://github.com/clark-mackey/log-file-setup.git`
   - Your name in every URL and reference

2. **GitHub Template Repository** ⭐ One-click adoption
   - Enable "Use This Template" button in repo settings
   - Users can create their own repo with structure pre-populated in 30 seconds
   - Reduces friction from "interesting idea" to "actively using"

3. **GitHub Pages** - Professional documentation hosting
   - URL: `clark-mackey.github.io/log-file-setup`
   - Automatically built from `/docs` folder
   - Makes documentation searchable and linkable
   - Shows technical expertise

4. **GitHub Releases** - Professional versioning
   - Tagged versions (v1.0.0, v1.1.0, etc.)
   - Release notes for each version
   - Downloadable archives
   - Shows active maintenance

5. **Starter Packs** - Pre-configured AI assistant rules
   - `/starter-packs/augment/` - Ready-to-use Augment rules
   - `/starter-packs/cursor/` - Ready-to-use Cursor rules
   - `/starter-packs/claude-code/` - Ready-to-use Claude Code rules
   - Copy-paste and go, no configuration needed

### Current State (December 2024)

**Actual Metrics:**
- **8 GitHub stars** (live on GitHub, public repository)
- **0 forks** (early stage)
- **0 issues/discussions** (no community engagement yet)
- **Unknown unique visitors** (GitHub Analytics not yet reviewed)
- **0 blog posts/articles** (no external mentions)
- **0 community PRs** (no external contributions)

**Key Insight:** Repository is live but not yet promoted. Focus needed on reliability before marketing.

### 6-Month Success Targets (From Current State)

**Quantitative Metrics:**
- **500 GitHub stars** (demonstrates market validation) - **Current: 8**
- **150 forks** (3:1 star-to-fork ratio typical) - **Current: 0**
- **50 issues/discussions** (community engagement) - **Current: 0**
- **5,000 unique visitors** (GitHub Analytics) - **Current: Unknown**
- **10 blog posts/articles** mentioning the project - **Current: 0**
- **3 community PRs merged** (community contribution) - **Current: 0**

**Prerequisite for Growth:** Fix reliability issues (Epic 7) before promoting to wider audience.

**Qualitative Metrics:**
- ✅ Featured in **2 AI coding newsletters** (e.g., TLDR AI, AI Breakfast)
- ✅ Mentioned in **1 podcast or YouTube video** about AI coding
- ✅ **5 detailed success stories** posted in Discussions
- ✅ **1 corporate team** (5+ developers) adopts the system

### 1-Year Success Targets

**Quantitative Metrics:**
- **2,000 GitHub stars** (realistic for well-marketed, high-quality tool)
- **50 community contributions** (PRs merged)
- **25 blog posts/articles** mentioning the project
- **500 forks**
- **20,000 unique visitors**
- **100 issues/discussions** created by community

**Qualitative Metrics:**
- ✅ Featured in **official documentation** of at least 1 AI coding assistant
- ✅ **10 corporate teams** using the system
- ✅ **3 derivative projects** built on the methodology
- ✅ Invited to speak at **1 conference or meetup** about the methodology
- ✅ **1 academic paper or industry whitepaper** cites the work

### Adoption Quality Metrics

**Active Usage Tracking:**
- **Active Users:** Number of repos using the system (track via GitHub search for template structure)
- **Retention:** % of users still using it after 3 months
- **Depth of Adoption:** % of users implementing all 4 documents vs. just 1-2
- **Multi-Agent Adoption:** Number of teams using it with Factory Droid, Claude Code subagents, etc.

**How to Track:**
- GitHub search: `"docs/planning/DEVLOG.md" "docs/planning/CHANGELOG.md"`
- Discussions: Ask users to share their repos
- Analytics: Track which documentation pages are most visited

### Ecosystem Integration Metrics

- **Tool Integrations:** Number of official integrations (Cursor extension, Claude Code command, Augment plugin)
- **Starter Pack Downloads:** Number of downloads per starter pack
- **Template Usage:** Number of repos created via "Use This Template" button
- **Derivative Works:** Number of projects that extend or build on the methodology

### Impact Metrics (Most Important)

- **Token Savings Reported:** Aggregate token reduction % from community (target: avg 80%+)
- **Time Savings Reported:** Aggregate time saved per week (target: avg 5+ hours)
- **Error Reduction Reported:** % reduction in AI mistakes (target: avg 40%+)
- **Success Stories:** Number of detailed case studies (target: 10 in year 1)

**How to Track:**
- Discussions: "Share Your Results" thread
- Surveys: Quarterly user survey
- Case Studies: Reach out to active users for detailed write-ups

### Validation & Feedback Mechanisms

**GitHub-Based Feedback:**
1. **GitHub Issues** - Bug reports, feature requests
2. **GitHub Discussions** - Q&A, show-and-tell, community engagement
   - "Success Stories" category for social proof
   - "Ideas" category with upvoting for feature prioritization
3. **GitHub Analytics** - Traffic, clones, popular content tracking
4. **README Badges** - Stars, forks, license, last commit (instant credibility)

**Community Engagement:**
- "Success Stories" Discussion category with template for users
- "Showcase" section in README featuring projects using the system
- Feature request voting system via Discussions
- Active solicitation of case studies from early adopters

**Brand Visibility Strategy:**
- Personal brand tagline: "Token-Efficient Documentation for Multi-Agent AI Development"
- Launch blog post with distribution to Reddit, Hacker News, Twitter, AI newsletters
- Comparison table in README showing positioning vs. competitors
- GitHub Topics: `ai-development`, `documentation`, `developer-tools`, `augment`, `claude-code`, `context-management`, `ai-coding-assistant`, `cursor-ai`, `token-optimization`, `multi-agent`, `devlog`, `adr`, `template`
- Pin repository to GitHub profile
- "Created by Clark Mackey" in all documentation

### Rationale for Metrics

**Why These Numbers Are Achievable:**

1. **Solves a Real, Painful Problem** - Context window management is the #1 complaint about AI coding assistants; 93% token reduction is a massive value proposition

2. **Market Is Growing Rapidly** - GitHub Copilot has 1.8M+ paid subscribers; Cursor, Claude Code, Factory Droid all launched/growing in 2024-2025; timing is perfect

3. **Unique Market Position** - More comprehensive than cursor-agent-tracking (135 stars), more unique than Claude-Code-Workflow (278 stars), addresses multi-agent coordination which is unsolved

4. **Built-In Virality** - Developers who adopt will naturally share (solves pain), multi-agent teams will evangelize (critical for workflow), token efficiency metrics are highly shareable (concrete numbers)

**Competitive Context:**
- awesome-cursorrules: 35,000 stars (different problem: code generation rules)
- context-engineering-intro: 11,200 stars (focused on single-feature implementation)
- Claude-Code-Workflow: 278 stars (workflow orchestration, less comprehensive)
- cursor-agent-tracking: 135 stars (too simple, not comprehensive)

---

## Checklist Results Report

**Date:** October 30, 2025
**Validation Mode:** Comprehensive Analysis
**PRD Version:** 1.0

### Executive Summary

**Overall PRD Completeness:** 75%

**MVP Scope Appropriateness:** ✅ **Just Right**
The scope is appropriately focused on delivering a documentation repository with templates, guides, and AI assistant integration. No feature creep detected. The 6-epic structure provides comprehensive coverage without overbuilding.

**Readiness for Architecture Phase:** ✅ **Ready**
Despite some gaps in success metrics and operational details, the PRD provides sufficient clarity for architecture work. This is a low-complexity project (static documentation repository) where the functional requirements and epic structure are well-defined.

**Most Critical Gaps (Now Addressed):**
- ~~Success metrics and KPIs~~ ✅ **RESOLVED** - Comprehensive metrics added
- ~~Deployment strategy~~ ✅ **RESOLVED** - Multi-channel strategy defined
- ~~User validation approach~~ ✅ **RESOLVED** - Validation plan added
- Stakeholder management - Deferred (solo project, can be addressed during execution)

### Category Analysis Table

| Category                         | Status  | Critical Issues                                                                 |
| -------------------------------- | ------- | ------------------------------------------------------------------------------- |
| 1. Problem Definition & Context  | PARTIAL | Missing competitive analysis and formal user research (acceptable for MVP)      |
| 2. MVP Scope Definition          | PASS    | ✅ Explicit scope boundaries, validation approach, and timeline now defined     |
| 3. User Experience Requirements  | PARTIAL | User flows not documented; acceptable given this is a documentation repository  |
| 4. Functional Requirements       | PASS    | ✅ Excellent - clear, testable requirements with strong acceptance criteria     |
| 5. Non-Functional Requirements   | PASS    | ✅ Strong NFRs appropriate for documentation repository                         |
| 6. Epic & Story Structure        | PASS    | ✅ Excellent - well-structured epics with clear goals and appropriately sized stories |
| 7. Technical Guidance            | PASS    | ✅ Deployment strategy and monitoring approach now defined                      |
| 8. Cross-Functional Requirements | PARTIAL | Integration requirements covered; operational requirements light but acceptable |
| 9. Clarity & Communication       | PASS    | ✅ Good documentation quality; stakeholder management deferred to execution     |

### Top Issues by Priority

#### BLOCKERS
✅ **None** - All blockers have been resolved. Ready to proceed to architecture phase.

#### HIGH Priority (Resolved)
1. ✅ **Define Success Metrics** - RESOLVED: Comprehensive 6-month and 1-year targets added with quantitative and qualitative metrics
2. ✅ **Specify Deployment Strategy** - RESOLVED: 5-channel strategy defined (clone, template, GitHub Pages, releases, starter packs)
3. ✅ **Add MVP Validation Plan** - RESOLVED: GitHub-based feedback mechanisms and community engagement strategy defined

#### MEDIUM Priority (Deferred to Execution)
4. **Document Scope Boundaries** - Can be added during Epic 1 execution
5. **Add Competitive Analysis** - Can be added during Epic 4 (Documentation) execution
6. **Define Timeline** - Rough estimate: 7-10 weeks part-time or 3-5 weeks full-time
7. **Identify Stakeholders** - Solo project; can be addressed as community grows

#### LOW Priority (Optional Enhancements)
8. **Add User Flow Diagrams** - Can be added during Epic 4 execution
9. **Include Monitoring Strategy** - GitHub Analytics defined; can be expanded during execution
10. **Document Technical Debt Approach** - Low complexity project; can be addressed as needed

### MVP Scope Assessment

**✅ Scope is Appropriate**

The 6-epic structure is well-balanced:
- **Epic 1** (Foundation) - Essential ✅
- **Epic 2** (Brownfield) - High value, addresses real user need ✅
- **Epic 3** (Multi-Platform) - Essential for stated goal of tool-agnostic system ✅
- **Epic 4** (Documentation) - Essential for usability ✅
- **Epic 5** (AI Integration) - Core value proposition ✅
- **Epic 6** (Examples) - Essential for learning and adoption ✅

**Features That Could Be Cut (if needed):**
- Story 6.3 (Multi-Repo Example) - Nice to have but not essential for MVP
- Story 6.5 (Success Stories) - Could be added post-launch based on real user feedback
- Story 3.4 (Platform Comparison Guide) - Could be simplified to a table in main README

**Missing Features:** None identified - scope appears complete for stated goals.

**Complexity Assessment:** Low - Primarily documentation and template creation. No code, services, or databases.

**Timeline Estimate:**
- Epic 1: 1-2 weeks
- Epic 2: 1 week
- Epic 3: 1-2 weeks (requires research and testing across platforms)
- Epic 4: 2 weeks
- Epic 5: 1-2 weeks (testing across platforms)
- Epic 6: 1 week
- **Total: 7-10 weeks** part-time or 3-5 weeks full-time

### Technical Readiness

**Clarity of Technical Constraints:** ✅ Excellent
- Markdown-only format: Clear
- Zero dependencies: Clear
- Multi-platform AI assistant support: Clear
- MIT License: Clear
- GitHub repository: Clear

**Identified Technical Risks:** ⚠️ Low Risk Overall
1. Platform Compatibility - AI assistant platforms may change rule/instruction formats
2. Cross-Linking Fragility - Relative paths may break if users reorganize files
3. Template Maintenance - Keeping templates updated as best practices evolve

**Areas Needing Architect Investigation:** Minimal
1. Deployment Strategy - ✅ Resolved: GitHub Pages + Releases + Template
2. Version Management - Semantic versioning for releases recommended
3. Testing Strategy - Manual validation across different project structures

### Final Decision

**✅ READY FOR ARCHITECT**

The PRD and epics are comprehensive, properly structured, and ready for architectural design.

**Rationale:**
- Functional requirements are excellent (95% complete)
- Epic and story structure is exemplary (100% complete)
- Technical constraints are clear
- Scope is appropriate for MVP
- Success metrics and deployment strategy now defined
- Missing elements (competitive analysis, stakeholder management) can be addressed in parallel with development

**Recommended Next Steps:**
1. ✅ Success metrics defined
2. ✅ Deployment strategy clarified
3. ✅ Validation plan established
4. **Next:** Proceed to architecture phase or begin Epic 1 execution
5. Address MEDIUM priority items during Epic 1 execution
6. Iterate based on user feedback after MVP launch

---

## Epic 7: Core Reliability & Bug Fixes 🔴 HIGH PRIORITY

**Epic Goal:** Fix critical reliability issues discovered through real-world usage to make the system dependable for daily use.

**Priority:** HIGHEST - These issues block effective daily usage and user adoption.

**Story Order Rationale:** Fix rule adherence first (7.2), achieve platform parity (7.3), then implement reliability features (7.1, 7.4, 7.5). Advanced automation (7.6-7.7) moved to Epic 11.

### Story 7.2: Improve Rule Adherence (Make AI Agents Follow Rules Consistently)

**As a** developer relying on automated log maintenance,
**I want** AI agents to consistently follow the log file maintenance rules,
**so that** I don't have to manually fix missed updates or incorrect entries.

#### Acceptance Criteria
1. Analyze why Augment Code fails to follow rules (rule complexity? unclear instructions? token budget?)
2. Simplify rule language to be more explicit and actionable
3. Add pre-commit checklist that AI MUST display before committing
4. Add post-commit verification that AI MUST confirm
5. Test rule improvements with both Augment and Claude Code
6. Add "Critical" or "Mandatory" markers to non-negotiable steps
7. Break complex rules into smaller, sequential steps
8. Add examples within rules showing correct behavior
9. Update both Augment and Claude Code rules with improvements
10. Document known limitations and workarounds
11. Define measurable success criteria: "AI follows rules in 95% of commits over 30-day period"
12. Create rollback plan if simplified rules still fail (revert to previous version, add manual validation step)
13. Document AI platform version compatibility matrix (Augment v1.x, Claude Code v2.x, etc.)

#### Technical Notes
- Focus on clarity over brevity in rule instructions
- Use numbered steps, not paragraphs
- Add visual markers (🔴, ✅, ⚠️) for emphasis
- Test with real commits to verify adherence improves
- Track adherence metrics: commits with CHANGELOG updates / total commits
- Consider A/B testing rule variations

### Story 7.3: Achieve Augment/Claude Code Parity

**As a** user of either Augment or Claude Code,
**I want** both platforms to work equally well with Log File Genius,
**so that** I can choose my AI assistant based on preference, not reliability.

#### Acceptance Criteria
1. Audit feature differences between Augment and Claude Code starter packs
2. Ensure both have identical core functionality:
   - CHANGELOG maintenance
   - DEVLOG maintenance
   - Token-based archival
   - Pre-commit checklist
   - Post-commit verification
   - Session start context reading
3. Test both platforms with identical workflows
4. Document any platform-specific limitations
5. Update README to clearly state parity status
6. Create comparison table showing feature support across platforms
7. Ensure validation scripts work identically for both platforms

#### Technical Notes
- Augment uses `.augment/rules/`, Claude Code uses `.claude/rules/`
- Both should reference `.logfile-config.yml` for configuration
- Both should use identical token budgets and archival logic
- Platform-specific features (if any) should be clearly documented as optional

### Story 7.1: Fix Archival Logic (Token-Based, Not Date-Based)

**As a** developer using the log file system daily,
**I want** archival to trigger based on token count and file size (not dates),
**so that** my log files stay within token budgets regardless of how frequently I update them.

#### Acceptance Criteria
1. Remove all date-based archival logic ("older than 2 weeks") from rules
2. Update `log-file-maintenance.md` (Augment) to use token/size-based triggers only
3. Update `.claude/rules/log-file-maintenance.md` (Claude Code) to use token/size-based triggers only
4. Archival triggers when:
   - CHANGELOG exceeds 10,000 tokens (or profile-specific limit)
   - DEVLOG exceeds 15,000 tokens (or profile-specific limit)
   - Combined logs exceed 25,000 tokens (or profile-specific limit)
5. Archive oldest entries first (regardless of date) until under token budget
6. Update validation scripts to check token counts and recommend archival
7. Test with real-world log files to verify token-based archival works
8. Update documentation to explain token-based archival strategy
9. Add examples showing before/after archival with token counts
10. Implement backup mechanism before archival (copy to `.lfg-backup/` directory)
11. Define archive file naming convention: `CHANGELOG-YYYY-MM.md` (month of oldest entry)
12. Create recovery process for accidental archival (restore from backup, validate integrity)

#### Technical Notes
- Use existing token counting logic from validation scripts
- Profile-aware: Read `.logfile-config.yml` for custom token targets
- Archive to `logs/archive/CHANGELOG-YYYY-MM.md` and `logs/archive/DEVLOG-YYYY-MM.md`
- Maintain cross-references after archival
- Backup directory: `.lfg-backup/` (git-ignored)
- Recovery command: `lfg restore --from-backup <timestamp>`

### Story 7.4: Validation Script Improvements

**As a** developer using the validation scripts,
**I want** validation to catch common errors and provide actionable feedback,
**so that** I can fix issues before they cause problems.

#### Acceptance Criteria
1. Validation checks token counts and warns when approaching limits
2. Validation detects missing CHANGELOG entries for recent commits
3. Validation detects broken cross-references between log files
4. Validation checks DEVLOG "Current Context" is up-to-date (updated within last 7 days)
5. Validation provides specific, actionable error messages (not generic warnings)
6. Validation script returns non-zero exit code on errors (for CI/CD integration)
7. Validation respects `.logfile-config.yml` profile settings
8. Add `--fix` flag to auto-fix common issues (e.g., formatting)
9. Add `--verbose` flag for detailed output
10. Test validation scripts on real-world log files with known issues
11. Performance requirement: Validation completes in <5 seconds for files up to 50,000 tokens
12. Configuration for custom token limits via `.logfile-config.yml` (override defaults)
13. Integration with existing workflows: pre-commit hooks, CI/CD pipelines, manual validation

#### Technical Notes
- Enhance existing `validate-log-files.ps1` and `validate-log-files.sh`
- Use token counting from existing scripts
- Profile-aware: Read `.logfile-config.yml` for thresholds
- Exit codes: 0 = pass, 1 = warnings, 2 = errors
- Performance optimization: Cache token counts, parallel file processing
- Workflow integration: Export validation results in JSON format for CI/CD parsing

### Story 7.5: Git Hook Reliability

**As a** developer using git hooks for automated validation,
**I want** hooks to work reliably across platforms (Windows, Mac, Linux),
**so that** validation runs automatically without manual intervention.

#### Acceptance Criteria
1. Test git hooks on Windows (PowerShell, Git Bash)
2. Test git hooks on Mac (bash, zsh)
3. Test git hooks on Linux (bash)
4. Hooks detect and use correct validation script (`.ps1` vs `.sh`)
5. Hooks provide clear error messages if validation fails
6. Hooks allow bypass with `--no-verify` flag (documented)
7. Hooks work with both Augment and Claude Code starter packs
8. Update installation scripts to correctly install hooks on all platforms
9. Document hook installation and troubleshooting
10. Add hook testing to validation suite

#### Technical Notes
- Hooks located in `.git-hooks/pre-commit` (template)
- Installer copies to `.git/hooks/pre-commit`
- Must handle Windows line endings (CRLF vs LF)
- Must be executable on Unix systems (`chmod +x`)

---

## Epic 8: AI Context Optimization 🧠 MISSION CRITICAL

**Epic Goal:** Build features that directly help AI agents not get lost and not waste tokens - smart summarization, token monitoring, AI-optimized formatting.

**Priority:** HIGHEST - This is the core mission. Every feature must answer: "Does this help AI agents navigate better, remember better, or consume fewer tokens?"

**Design Principles:**
- AI agents are the primary user, not human developers
- Every feature must reduce tokens OR improve AI navigation
- Simplicity over complexity - complex systems confuse AI agents
- Measure success by: tokens saved, AI confusion reduced, context quality improved

**Mission Alignment Test:** Before adding any feature, ask:
1. Does this reduce token consumption?
2. Does this help AI agents find information faster?
3. Does this prevent AI agents from getting lost or confused?
4. If none of the above, REJECT the feature.

### Story 8.1: Smart Context Summarization

**As an** AI coding assistant starting a new session,
**I want** an auto-generated concise project summary,
**so that** I can understand the project state instantly without reading full log files.

#### Acceptance Criteria
1. Generate summary from CHANGELOG + DEVLOG + STATE in <500 tokens
2. Summary includes: current version, active work, recent decisions, blockers
3. Summary prioritizes recent over old (last 7 days weighted higher)
4. Summary format optimized for AI comprehension (structured, not prose)
5. Summary updates automatically when log files change
6. Summary stored in `logs/CONTEXT_SUMMARY.md` for instant access
7. AI rules reference summary as first-read document
8. Summary includes "What to do next" section based on STATE.md
9. Token count displayed in summary header
10. Validation warns if summary exceeds 500 tokens

#### Technical Notes
- Use existing log file content, not external APIs
- Structure: Version → Active Work → Recent Decisions → Blockers → Next Steps
- Consider frontmatter with token count and last-updated timestamp
- AI agents should read this FIRST before diving into full logs

### Story 8.2: Token Budget Dashboard

**As an** AI coding assistant,
**I want** real-time visibility into token consumption,
**so that** I know when context is getting bloated and needs archival.

#### Acceptance Criteria
1. Dashboard shows current token count for each log file
2. Dashboard shows percentage of budget used (e.g., "CHANGELOG: 8,500/10,000 (85%)")
3. Dashboard warns at 80% threshold with specific guidance
4. Dashboard recommends archival when over budget
5. Dashboard accessible via simple command or file read
6. Dashboard updates on every log file change
7. Dashboard stored in `logs/TOKEN_STATUS.md` for AI access
8. AI rules include "check token status before adding entries"
9. Dashboard shows trend (growing/stable/shrinking)
10. Dashboard includes "entries to archive" count when over budget

#### Technical Notes
- Reuse token counting from validation scripts
- Simple markdown format for AI readability
- Consider JSON alternative for programmatic access
- Update via git hook or validation script

### Story 8.3: AI-Optimized Document Templates

**As an** AI coding assistant reading log files,
**I want** documents structured for maximum AI comprehension,
**so that** I can extract information quickly without confusion.

#### Acceptance Criteria
1. Templates use consistent heading hierarchy (H1 → H2 → H3)
2. Templates include frontmatter with metadata (token count, last updated, related files)
3. Templates use bullet points over paragraphs (faster parsing)
4. Templates include "Quick Summary" section at top of each file
5. Templates use explicit section markers (## Current Context, ## Daily Log)
6. Templates avoid ambiguous language ("this", "that", "it")
7. Templates include cross-reference links in consistent format
8. Templates validated for AI readability (no orphan sections, no broken links)
9. Templates include token budget in header
10. Documentation explains why each format choice helps AI agents

#### Technical Notes
- Audit existing templates against AI comprehension best practices
- Test with multiple AI assistants to verify comprehension
- Consider "AI readability score" metric
- Frontmatter format: YAML for consistency

### Story 8.4: Intelligent Archival Triggers

**As an** AI coding assistant,
**I want** archival to happen based on what I actually access,
**so that** frequently-referenced content stays available while stale content archives.

#### Acceptance Criteria
1. Track which log entries AI agents reference (via frontmatter or markers)
2. Archive least-accessed entries first, not just oldest
3. Preserve entries referenced in last 30 days regardless of age
4. Archive entries that haven't been referenced in 60+ days
5. Archival preserves cross-references (update links after archival)
6. Archival creates summary of archived content for reference
7. Archived content searchable but not loaded by default
8. AI rules explain archival strategy so agents understand what's available
9. Archival respects token budget as primary trigger
10. Archival logs what was archived and why

#### Technical Notes
- Access tracking via simple marker in frontmatter or comment
- Consider "last accessed" timestamp per entry
- Balance access-based with size-based archival
- Fallback to token-based if access tracking unavailable

### Story 8.5: Context Relevance Scoring

**As an** AI coding assistant working on a specific task,
**I want** to know which log entries are most relevant to my current work,
**so that** I can focus on important context and skip irrelevant history.

#### Acceptance Criteria
1. Each log entry tagged with relevant topics/areas (e.g., "auth", "database", "UI")
2. AI can filter log entries by topic relevance
3. STATE.md "Active Work" links to relevant CHANGELOG/DEVLOG entries
4. Cross-references include relevance hints ("see also", "superseded by", "related to")
5. Recent entries weighted higher than old entries
6. Entries marked as "foundational" never deprioritized (ADRs, major decisions)
7. AI rules explain how to use relevance scoring
8. Validation checks for orphan entries (no tags, no references)
9. Topic tags consistent across all log files
10. Documentation explains tagging conventions

#### Technical Notes
- Simple tagging system (avoid complex taxonomies)
- Tags in frontmatter or inline markers
- Consider auto-tagging based on file paths mentioned
- Keep tagging lightweight - don't add token overhead

### Story 8.6: Session Handoff Protocol

**As an** AI coding assistant ending a session,
**I want** a standard way to write a handoff note for the next session,
**so that** the next agent can pick up exactly where I left off without re-reading full logs.

#### Acceptance Criteria
1. Rule includes "🔚 SESSION END" section mirroring existing "🔄 SESSION START"
2. Agent writes handoff note before session ends containing: what was done, what's in progress, what's next
3. Handoff stored in `## Last Session` section of DEVLOG.md (above Daily Log)
4. Handoff format is compact: 3 bullet points max (Done, In Progress, Next)
5. Handoff overwrites previous handoff (only latest session matters)
6. SESSION START rule updated to read handoff first
7. Handoff includes branch name and last commit hash
8. Token budget: <150 tokens per handoff
9. No external tools required - agent writes directly to markdown
10. Validation warns if handoff section is missing or >150 tokens

#### Technical Notes
- Modify `product/ai-rules/augment/log-file-maintenance.md` and claude-code equivalent
- Add `## Last Session` section template to DEVLOG_template.md
- Implementation: rule change + template change only, no scripts

### Story 8.7: Self-Assessed Token Counting

**As an** AI coding assistant writing log entries,
**I want** a simple heuristic to estimate token usage without running scripts,
**so that** I can self-regulate entry length and stay within budget.

#### Acceptance Criteria
1. Rule includes token estimation heuristic: "~4 characters = 1 token"
2. Rule includes quick-reference table: 1 line ≈ 20 tokens, 1 paragraph ≈ 80 tokens
3. Agent estimates token count before writing entries
4. Agent checks estimated file size against budget thresholds from rule
5. If estimated over budget, agent triggers archival before adding new entry
6. No Python scripts or external tools required for estimation
7. Heuristic accurate within ±20% for English markdown text
8. Rule includes example: "This 80-char line ≈ 20 tokens"
9. Token budgets embedded in rule (CHANGELOG <10k, DEVLOG <15k, Combined <25k)
10. Validation scripts remain available for precise counting but are not required

#### Technical Notes
- Add "📊 TOKEN SELF-ASSESSMENT" section to log-file-maintenance rule
- Heuristic: `token_estimate = character_count / 4`
- Keep budgets in sync with profile definitions
- Implementation: rule change only

### Story 8.8: Entry Verbosity Control

**As an** AI coding assistant writing DEVLOG entries,
**I want** a compact entry format option,
**so that** routine entries don't consume 150-250 tokens when 50-80 would suffice.

#### Acceptance Criteria
1. Rule defines two DEVLOG entry formats: Standard (narrative) and Compact (3-line)
2. Compact format: `What → Why → Files` on 3 lines
3. Standard format reserved for: major decisions, incidents, milestones
4. Compact format used for: routine changes, minor fixes, session summaries
5. Compact entry target: 50-80 tokens (vs 150-250 for standard)
6. DEVLOG template updated with compact format example
7. Rule provides decision guide: "If it needs an ADR, use standard. Otherwise, compact."
8. Both formats maintain human readability
9. Token savings: 50-100 tokens per entry for routine work
10. Validation accepts both formats without warnings

#### Technical Notes
- Update `product/templates/DEVLOG_template.md` with compact format section
- Update log-file-maintenance rule with format selection guidance
- Compact format example:
  ```
  ### 2026-02-06: Fixed auth token refresh
  Token refresh failed silently on expired sessions. Added retry logic with exponential backoff.
  Files: `src/auth.js`, `src/retry.js`
  ```
- Implementation: template change + rule change

### Story 8.9: Cross-File Navigation Hints

**As an** AI coding assistant reading a CHANGELOG entry,
**I want** a pointer to the related DEVLOG entry that explains *why*,
**so that** I can navigate between files without guessing by date.

#### Acceptance Criteria
1. Rule convention: CHANGELOG entries with DEVLOG decisions include `→ DEVLOG {date}`
2. Rule convention: DEVLOG entries referencing specific changes include `→ CHANGELOG {version}`
3. Navigation hints added at end of entry line (inline, not separate line)
4. Token cost: ~8 tokens per hint
5. Hints are optional - only added when cross-reference exists
6. Hints use consistent format across all log files
7. Agent adds hints automatically when writing related entries
8. Validation warns on orphan decisions (DEVLOG decision with no CHANGELOG link)
9. Hints work in both rendered and raw markdown
10. No new files or tools required

#### Technical Notes
- Add "🔗 CROSS-REFERENCES" convention to log-file-maintenance rule
- Format: `→ DEVLOG 2026-02-06` or `→ CHANGELOG v0.3.0`
- Implementation: rule convention only

### Story 8.10: Stale Context Detection

**As an** AI coding assistant starting a session,
**I want** to know if the Current Context section is outdated,
**so that** I don't make decisions based on stale information.

#### Acceptance Criteria
1. Rule clause: "At session start, check `Last Updated` date in Current Context"
2. If Current Context is >7 days old, agent MUST update it before other work
3. Agent compares `Last Updated` to current date (no external tools needed)
4. Update includes: version, phase, objectives, recent changes since last update
5. Staleness check added to SESSION START section of rule
6. Agent reports staleness to user: "Current Context is X days old. Updating."
7. Updated context includes new `Last Updated` date
8. Token budget for context update: <800 tokens (existing budget)
9. No scripts or external dependencies required
10. Validation warns if `Last Updated` is >14 days old

#### Technical Notes
- Add staleness check to "🔄 SESSION START" section of log-file-maintenance rule
- Simple date comparison: agent reads date, compares to today
- Implementation: rule clause only

### Story 8.11: Archival Summary Index

**As an** AI coding assistant looking for an old decision or entry,
**I want** a summary of what each archive file contains,
**so that** I can find the right archive without reading all of them.

#### Acceptance Criteria
1. Rule: when archiving, agent adds summary line to Archive section
2. Summary format: `- [filename](path) - Brief description of contents`
3. Summary includes: key topics, decisions, epics covered in that archive
4. Summary target: ~10 tokens per archive file
5. Archive section in DEVLOG and CHANGELOG templates updated with example
6. Agent can scan summaries to find relevant archive without opening files
7. Summary written at time of archival (not retroactively)
8. Validation warns if archive files exist without summary entries
9. No new files or tools required
10. Summaries maintained in the active log file's Archive section

#### Technical Notes
- Update Archive section guidance in log-file-maintenance rule
- Update DEVLOG_template.md and CHANGELOG_template.md Archive sections
- Example: `- [DEVLOG-2026-01.md](archive/DEVLOG-2026-01.md) - Epic 7 reliability, JWT decision, rate limiting incident`
- Implementation: rule change + template change

---

## Rejected Ideas (Mission Drift)

The following epics were rejected after code-police review identified 60% mission drift. These features serve human developers, not AI agents, and do not reduce tokens or improve AI navigation.

### ~~Epic 9: CLI Tooling & Developer Experience~~ ❌ REJECTED

**Why Rejected:** CLI tools serve human developers, not AI agents. Commands like `lfg context`, `lfg handoff`, `lfg status` are developer convenience features that don't reduce token consumption or help AI agents navigate better.

**Original Goal:** Provide command-line tools for context injection, session handoffs, and status checks.

**Mission Alignment Score:** 3/10 - Severe drift from core mission.

**What Would Be Lost:** `lfg context`, `lfg handoff`, `lfg status`, `lfg log` commands. These are developer conveniences that can be achieved with simple file reading - no special tooling needed.

### ~~Epic 10: Claude Code Subagent Integration~~ ❌ REJECTED

**Why Rejected:** No evidence Claude Code subagents exist as native architecture. Adds massive complexity (coordination protocols, file locking, fallback logic) without proven benefit. Each integration point is a potential failure mode that confuses AI agents.

**Original Goal:** Create dedicated subagents (lfg-maintainer, lfg-archivist, lfg-validator, lfg-context-curator) for autonomous documentation.

**Mission Alignment Score:** 2/10 - Complexity explosion, solves symptom (rule adherence) not root cause (unclear rules).

**Code-Police Findings:**
- Missing technical foundation (no Claude Code subagent API spec)
- Integration conflicts with MCP server (both try to write same files)
- Race conditions from concurrent file modifications
- Debugging nightmare with distributed failures
- Vendor lock-in to unspecified architecture

**What Would Be Lost:** Subagent-based automation. Alternative: Better rule specification and validation (Epic 7) addresses root cause.

### ~~Epic 11: Advanced Automation~~ ❌ REJECTED

**Why Rejected:** Git hook auto-population and CI enforcement serve development process, not AI memory. Zero token reduction, zero AI navigation improvement.

**Original Goal:** Auto-populate CHANGELOG from commit messages, enforce token budgets in CI.

**Mission Alignment Score:** 1/10 - Complete drift from core mission.

**Code-Police Findings:**
- Auto-generated entries lack context that only working AI has
- CI enforcement is developer tooling, not AI benefit
- Premature automation before reliability proven

**What Would Be Lost:** Automatic CHANGELOG entries, CI token budget checks. Alternative: AI writes rich content directly (current approach works), validation scripts already provide budget checks.

---

## Future Considerations (v2.0+)

The following features were identified as high-value but deferred due to complexity or scope. They represent the roadmap for LFG beyond MVP.

### Real-Time State Sync

**Concept:** A lightweight daemon/watcher that auto-updates STATE.md based on git activity.

**Value:** Zero manual maintenance - detects branch switches, commit activity, and updates "Active Work" automatically.

**Complexity:** HIGH - Requires background process, file watching, git integration.

**Trigger for prioritization:** User feedback requesting less manual STATE updates.

### Conflict-Free Concurrent Editing (CRDT)

**Concept:** CRDT-style or append-only log format for DEVLOG/STATE that auto-merges without conflicts.

**Value:** Teams currently fear merge conflicts in log files. This eliminates that friction entirely.

**Complexity:** HIGH - Requires data structure changes, merge tooling, editor integration.

**Trigger for prioritization:** Team adoption exceeds solo developer usage.

### Shared Context Dashboard

**Concept:** Simple web view (GitHub Pages or local server) showing current STATE across team members.

**Value:** Async standup replacement - see who's working on what, blockers, recent decisions at a glance.

**Complexity:** MEDIUM - Web UI, real-time updates, authentication for private repos.

**Trigger for prioritization:** Teams request visibility features.

### AI Session Replay

**Concept:** Record what context was provided to AI and what it produced, enabling "why did the AI do that?" debugging.

**Value:** AI debugging is currently painful. Session replay provides forensic capability.

**Complexity:** HIGH - Logging infrastructure, storage, replay UI, privacy considerations.

**Trigger for prioritization:** Enterprise/team users request audit capabilities.

### Token Usage Analytics Dashboard

**Concept:** Dashboard showing tokens saved over time, context efficiency trends, and ROI proof.

**Value:** Proves value, justifies continued use, provides concrete metrics for advocacy.

**Complexity:** LOW-MEDIUM - Tracking infrastructure, visualization, historical data.

**Trigger for prioritization:** Marketing push or user requests for metrics.

### MCP Server (Programmatic API)

**Concept:** Expose LFG as an MCP (Model Context Protocol) server with tools like `get_context`, `log_update`, and `query_history`.

**Value:**
- AI assistants call tools programmatically instead of following rules
- Budget-aware responses (accept max_tokens parameter)
- Structured queries for project history
- Multi-agent coordination via shared API

**Why Deferred (2026-01 Analysis):**
Dogfooding analysis revealed that LFG's value comes from *rich, contextual entries* that only the AI working on a task can write. MCP tools would need to accept ~500-1000 tokens of content per DEVLOG entry - the token savings are minimal compared to direct file writes. Current rules-based approach with git hook safety nets achieves 95%+ reliability without MCP overhead.

**Complexity:** HIGH - TypeScript, npm package, MCP SDK, client configurations.

**Trigger for prioritization:**
- Multi-agent scenarios where agents need shared context API
- Enterprise deployments requiring programmatic access
- Rules-based approach proves unreliable at scale

**If Implemented:**
- 3 tools: `get_context(scope, max_tokens)`, `log_update(type, content)`, `query_history(question)`
- Budget-aware responses, lazy loading
- ~150 token overhead for tool definitions
- See `context/code-police-analysis-2026-01.md` for full architecture specification

---

## Next Steps

### UX Expert Prompt
*To be generated after PRD approval*

### Architect Prompt - Epic 8: Log Automation & Reliability

*No architect prompt needed. Epic 8 extends existing infrastructure (lfg.py, pre-commit hooks, AI rules). Implementation is straightforward CLI additions. See Epic 8 stories for acceptance criteria.*
