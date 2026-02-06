# Log File Genius

**Make your AI agents rip. Not guess, not loop, not forget — rip.**

> Five markdown files + AI rules that give any agent (or subagent) instant, complete project context in under 5% of its context window.

[![GitHub stars](https://img.shields.io/github/stars/clark-mackey/log-file-genius?style=social)](https://github.com/clark-mackey/log-file-genius/stargazers)
[![Use this template](https://img.shields.io/badge/use%20this-template-blue)](https://github.com/clark-mackey/log-file-genius/generate)
[![License: MIT](https://img.shields.io/github/license/clark-mackey/log-file-genius)](LICENSE)

[Quick Start](#-quick-start) • [Installation Guide](INSTALL.md) • [Migration Guide](product/docs/MIGRATION_GUIDE.md) • [The Methodology](product/docs/log_file_how_to.md) • [Examples](product/examples) • [Why It's Genius](#-why-its-genius)

---

## 😫 The Problem: Your AI Agent Is Working Blind

Your agent doesn't know what happened yesterday. It doesn't know why you chose Postgres over Mongo. It doesn't know its teammate just refactored the auth module. So it guesses, goes in circles, and makes decisions you already made — badly.

**Without Log File Genius:**
- 🔄 **Agents repeat past mistakes** because there's no structured record of what failed and why
- 🧠 **Context lost between sessions** — every new chat starts from scratch
- 🤖 **Subagents start from zero** — they have no idea what the lead agent decided
- 📊 **90,000+ tokens** of bloated docs eating your context window, and the AI *still* doesn't know what's going on

It's like hiring a brilliant contractor who shows up every morning with amnesia. Every. Single. Day.

Or maybe you're vibe coding your first projects and wondering why the AI keeps going in circles.

**Vibe Coding Without Log File Genius:**
- 🔄 **Endless loops** — the AI retries the same broken approach because it has no memory of what already failed
- 🤖 **Half your context window** wasted on hand-holding and ineffective back-and-forth
- ❌ **Result:** The AI hallucinates, makes bad decisions, and you spend more time fixing its work than writing code

## 💡 The Solution: A Shared Brain for Every Agent

Log File Genius is five markdown files and a set of AI rules. Any agent — lead, subagent, teammate, or a fresh session — reads them and instantly knows: what are we building, what changed, why we decided that, what's happening right now, and what rules we follow.

The AI maintains the files itself. You don't write documentation — the agent does, as part of its workflow.

**After Log File Genius:**
- ⚡ **Agents make informed decisions** from the first message — no ramp-up, no guessing
- 🔄 **Session continuity** — handoff protocol means zero context lost between sessions
- 🤖 **Subagents spin up dangerous** — full project context in under 500ms
- 📊 **Up to 93% token reduction** — complete project history in ~7,000-10,000 tokens instead of 90,000+

| Document | The Vibe | Purpose | Token Budget |
|---|---|---|---|
| **PRD** | The Dream ✨ | What we're building and why | ~5k tokens |
| **CHANGELOG** | The Facts 📊 | What changed (files, versions, facts) | <10k tokens |
| **DEVLOG** | The Story ✍️ | *Why* it changed (the narrative, the reasoning) | <15k tokens |
| **ADRs** | The Rules 🏛️ | How we made significant decisions | On-demand |
| **STATE** | The Now 📍 | What agent is on what task, right now? | <500 tokens |

[Dive into the full methodology →](product/docs/log_file_how_to.md)

---

## 🧠 Why It's Genius

This isn't just documentation. It's an operating system for AI agent performance.

- **🚀 Agents That Actually Perform:** Your agent reads 5 files and knows everything — what we're building, what changed, why, what's happening now, and what rules to follow. No ramp-up. No guessing. Just execution.

- **🔄 Zero Context Loss Between Sessions:** The handoff protocol means a new session picks up exactly where the last one left off. No more "let me re-read the codebase to understand what's going on."

- **🤖 Multi-Agent & Subagent Ready:** Spin up a subagent and it has full project context in seconds. `STATE.md` prevents collisions. The handoff protocol prevents duplicated work. Agent teams that actually coordinate.

- **🧠 Self-Regulating:** Agents manage their own token budgets, estimate entry sizes, and archive proactively. No babysitting. No external tools. The AI maintains the files as part of its workflow — you don't write documentation, the agent does.

- **🚨 Learns From Failures:** The `🚨 INCIDENT` format in DEVLOG means agents document what broke, why, and how to prevent it. Next time a similar problem comes up, the agent already knows the answer.

- **⚡ Zero-Search Navigation:** Bidirectional frontmatter linking means your AI never wastes tokens searching for files. Every document points to its related documents. One hop to anything.

- **📊 Up to 93% Token Reduction:** Sheds old context like a snake sheds its skin. Complete project history in <5% of the context window, leaving the rest for what matters: the code you're writing *right now*.

- **🔒 Safety Built In:** Secret detection, log validation, and pre-commit hooks catch problems before they hit the repo. Your agent won't accidentally leak API keys into a DEVLOG entry.

- **🔧 Tool Agnostic:** Works with Claude, Cursor, GitHub Copilot, Augment, and any other AI coding assistant. Your toaster will probably be running it soon.

---

## 📁 Repository Structure

This repository uses a two-branch strategy: `main` contains only the `product/` directory for distribution, while `development` contains both `product/` and `project/` directories for development work.

---

## 🚀 Quick Start

### One-Command Installation (30 Seconds)

**For detailed installation instructions, troubleshooting, and next steps, see [INSTALL.md](INSTALL.md).**

Install Log File Genius in your existing project with a single command:

**Bash/Mac/Linux:**
```bash
git submodule add -b main \
  https://github.com/clark-mackey/log-file-genius.git \
  .log-file-genius && \
  ./.log-file-genius/product/scripts/install.sh
```

**PowerShell/Windows:**
```powershell
git submodule add -b main `
  https://github.com/clark-mackey/log-file-genius.git `
  .log-file-genius; `
  .\.log-file-genius\product\scripts\install.ps1
```

The installer will:
- ✅ Detect your AI assistant (Augment, Claude Code, etc.)
- ✅ Prompt for your profile (solo-developer, team, open-source, startup)
- ✅ Create standard `/logs/` folder structure
- ✅ Install log file templates and AI assistant rules
- ✅ Configure everything for immediate use

**What gets installed:**
- `logs/` - All your log files (CHANGELOG, DEVLOG, STATE, ADRs)
- `.augment/` or `.claude/` - AI assistant rules
- `.logfile-config.yml` - Profile configuration

**What stays hidden:**
- `.log-file-genius/` - Source repository (templates, scripts, docs - for updates)

### ✅ Post-Installation Verification

After installation, your project root should contain **ONLY** these files/folders:

**Visible:**
- `logs/` folder (contains CHANGELOG.md, DEVLOG.md, STATE.md, adr/)
- `.logfile-config.yml` file (your profile configuration)

**Hidden (may not show in file explorer by default):**
- `.log-file-genius/` folder (git submodule - the source repository)
- `.augment/` or `.claude/` folder (AI assistant rules)
- `.git/` folder (your project's git repository)

**❌ If you see a visible `log-file-genius/` folder (without the dot), something went wrong.** This means a full clone was created instead of a submodule. Delete it and re-run the installation command.

**Total visible items added to your project root: 2** (logs/ folder + .logfile-config.yml file)

---

### Alternative: GitHub Template (For New Projects)

Starting a brand new project? Use the GitHub template:

1.  **Click the Button:**

    [![Use this template](https://img.shields.io/badge/use%20this-template-blue?style=for-the-badge)](https://github.com/clark-mackey/log-file-genius/generate)

2.  **Create Your New Repository:**
    Give it a name. You now have the complete structure.

3.  **Read the Guide:**
    Follow the [**`log_file_how_to.md`**](product/docs/log_file_how_to.md) guide to start using the system.

---

### Updating Log File Genius

Already installed? Update to the latest version:

```bash
# Update source
cd .log-file-genius && git pull && cd ..

# Re-run installer (smart merge, preserves customizations)
./.log-file-genius/product/scripts/install.sh --force
```

---

### Migration from Existing Docs

Already have documentation? The installer creates a clean `/logs/` structure. You can:
- **Start fresh:** Let the installer create new templates, then manually migrate your existing content
- **Brownfield:** Keep your existing docs where they are and use Log File Genius alongside them
- **Full migration:** Copy your existing CHANGELOG/DEVLOG content into the new `/logs/` files

For detailed migration strategies, see [**Migration Guide**](product/docs/MIGRATION_GUIDE.md).

---

## 💬 Join the Community

This project is for you. Your feedback, ideas, and contributions make it better.

- 🐛 **[Report a bug](https://github.com/clark-mackey/log-file-genius/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/clark-mackey/log-file-genius/issues/new?template=feature_request.md)**
- 💬 **[Join the discussions](https://github.com/clark-mackey/log-file-genius/discussions)** to ask questions or share your success stories.
- ⭐ **Star this repo** if it saved you from context window hell!

## Contributing

Contributions are welcome! Whether it's improving the documentation, adding a new starter pack, or suggesting a new feature, please feel free to open an issue or pull request. Check out the [**`CONTRIBUTING.md`**](CONTRIBUTING.md) file for more details.

---

**Built with ❤️ by [Clark Mackey](https://github.com/clark-mackey)**

*Inspired by the endless struggle against context window limits and weak sauce AI recommendations.*
