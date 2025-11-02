# Log File Genius

**Stop the context rot. Give your AI a genius-level memory.**

> A token-efficient documentation system that reduces AI context bloat by 93% while maintaining near perfect project memory.

[![GitHub stars](https://img.shields.io/github/stars/clark-mackey/log-file-genius?style=social)](https://github.com/clark-mackey/log-file-genius/stargazers)
[![Use this template](https://img.shields.io/badge/use%20this-template-blue)](https://github.com/clark-mackey/log-file-genius/generate)
[![License: MIT](https://img.shields.io/github/license/clark-mackey/log-file-genius)](LICENSE)

[Quick Start](#-quick-start) • [Migration Guide](docs/MIGRATION_GUIDE.md) • [The Methodology](docs/log_file_how_to.md) • [Examples](examples/) • [Why It's Genius](#-why-its-genius)

---

## 😫 The Problem: Your AI Has a Terrible Memory

Traditional project documentation becomes a bloated mess over time. Your AI coding assistant spends half its context window just trying to remember what happened last week.

**Before Log File Genius:**
- 📊 **90,000-110,000 tokens** of verbose logs.
- 🤖 **45-55% of your AI's context window** wasted on history.
- ❌ **Result:** The AI lacks context, makes uninformed decisions, and repeats past mistakes.

It's like trying to have a conversation with someone who has amnesia. Every. Single. Day.

Or maybe you are new here and vibe coding your first projects. 

**Vibe Coding Before Log File Genius:**
- 📊 **50,000-70,000 tokens** of retrying work-arounds and responding to your questions about how code works.
- 🤖 **45-55% of your AI's context window** wasted on hand holding and ineffective loops through code.
- ❌ **Result:** The AI has the wrong context, makes bad decisions, and hallucinates.

## 💡 The Solution: A Genius-Level Memory

Log File Genius is a five-document system that gives your AI a an improved long-term memory while consuming less than **5%** of its context window.

**After Log File Genius:**
- 📊 **~7,000-10,000 tokens** for complete project history.
- 🤖 **93% reduction** in context bloat. 
- ✅ **Result:** The AI has near-instant access to all decisions, changes, and narratives, leading to smarter, faster, and more accurate coding.

| Document | The Vibe | Purpose | Token Budget |
|---|---|---|---|
| **PRD** | The Dream ✨ | What we're building and why | ~5k tokens |
| **CHANGELOG** | The Facts 📊 | What changed (files, versions, facts) | ~2k tokens |
| **DEVLOG** | The Story ✍️ | *Why* it changed (the narrative, the reasoning) | ~3k tokens |
| **ADRs** | The Rules 🏛️ | How we made significant decisions | On-demand |
| **STATE** | The Current State | What agent on what task? | <500 tokens |

[Dive into the full methodology →](docs/log_file_how_to.md)

---

## 🧠 Why It's Genius

This isn't just another documentation template. It's a complete system designed for AI-first development.

- **93% Token Reduction:** Keep your context window free for what matters: the code you're writing *right now*. Sheds old context like a snake sheds its skin.

- **Near Perfect Project Memory:** The five-document system separates facts from narrative, giving your AI a complete, holistic understanding of the project's history and goals.

- **⚡ Zero-Search Navigation:** With bidirectional frontmatter linking, your AI never wastes tokens searching for files. It instantly knows where to find related documents.

- **🤖 Multi-Agent Ready:** The included `STATE.md` file and handoff protocol provide a lightweight coordination layer, preventing agent collisions and duplicated work in complex, multi-agent environments.

- **Scalable by Design:** The built-in archiving strategy keeps your active logs lean and fast, even on multi-year projects.

- **Tool Agnostic:** Works seamlessly with Claude, Cursor, GitHub Copilot, Augment, and any other AI coding assistant. Your toaster will probably be running it soon.

---

## � Repository Structure

**⚠️ Important:** This repository has a unique structure because it both *teaches* the log file methodology AND *uses* it for its own development (dogfooding).

```
log-file-genius/
├── product/                    # 📦 THE PRODUCT (what we distribute to you)
│   ├── templates/              # Clean templates for your projects
│   ├── docs/                   # How-to guides and documentation
│   ├── examples/               # Sample projects showing the system in action
│   └── starter-packs/          # Pre-configured setups for different AI assistants
│
├── project/                    # 🔧 THE PROJECT (our development process)
│   ├── planning/               # Our CHANGELOG, DEVLOG, STATE
│   ├── adr/                    # Our architectural decision records
│   └── specs/                  # Our PRD and epic files
│
└── .project-identity.yaml      # Explains the meta-problem (read this first!)
```

**When using this repository:**
- **Copy from `product/`** - These are the clean templates and docs for YOUR projects
- **Don't copy from `project/`** - These are OUR development files (examples of the system in use, but specific to building Log File Genius)

See [`.project-identity.yaml`](.project-identity.yaml) for the full explanation of this structure and why it exists.

---

## �🚀 Quick Start

### One-Command Installation (30 Seconds)

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
- ✅ Install templates, validation scripts, and AI assistant rules
- ✅ Configure everything for immediate use

**What gets installed:**
- `.augment/` or `.claude/` - AI assistant rules
- `templates/` - CHANGELOG, DEVLOG, ADR, STATE templates
- `scripts/` - Validation scripts (PowerShell + Bash)
- `.logfile-config.yml` - Profile configuration
- `.git-hooks/` - Optional pre-commit validation

**What stays hidden:**
- `.log-file-genius/` - Source repository (for updates)

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
./.log-file-genius/product/scripts/install.sh --update
```

---

### Migration from Existing Docs

Already have documentation? See the [**Migration Guide**](product/docs/MIGRATION_GUIDE.md) for:
- **Scenario A:** No docs → Start fresh (1-2 hours)
- **Scenario B:** Have CHANGELOG → Expand (3-6 hours)
- **Scenario C:** Verbose docs → Condense (1-2 days)
- **Scenario D:** Partial implementation → Complete (2-4 hours)

## 📦 Starter Packs

Get running even faster with pre-configured starter packs for your favorite tools.

| Tool | Link | Status |
|---|---|---|
| **Claude Code** | `product/starter-packs/claude-code/` | ✅ Available |
| **Cursor** | `product/starter-packs/cursor/` | 🚧 Coming Soon |
| **GitHub Copilot** | `product/starter-packs/github-copilot/` | 🚧 Coming Soon |
| **Augment** | `product/starter-packs/augment/` | ✅ Available |

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
