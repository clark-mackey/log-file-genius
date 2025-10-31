# Log File Genius

**Stop the context rot. Give your AI a genius-level memory.**

> A token-efficient documentation system that reduces AI context bloat by 93% while maintaining perfect project memory.

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

Log File Genius is a five-document system that gives your AI a perfect, long-term memory while consuming less than **5%** of its context window.

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

- **Perfect Project Memory:** The four-document system separates facts from narrative, giving your AI a complete, holistic understanding of the project's history and goals.

- **⚡ Zero-Search Navigation:** With bidirectional frontmatter linking, your AI never wastes tokens searching for files. It instantly knows where to find related documents.

- **🤖 Multi-Agent Ready:** The included `STATE.md` file and handoff protocol provide a lightweight coordination layer, preventing agent collisions and duplicated work in complex, multi-agent environments.

- **Scalable by Design:** The built-in archiving strategy keeps your active logs lean and fast, even on multi-year projects.

- **Tool Agnostic:** Works seamlessly with Claude, Cursor, GitHub Copilot, Augment, and any other AI coding assistant. Your toaster will probably be running it soon.

---

## 🚀 Quick Start

### For New Projects (30 Seconds)

1.  **Click the Button:**

    [![Use this template](https://img.shields.io/badge/use%20this-template-blue?style=for-the-badge)](https://github.com/clark-mackey/log-file-genius/generate)

2.  **Create Your New Repository:**
    Give it a name. You're done. You now have the complete `log-file-genius` structure.

3.  **Read the Guide:**
    Follow the [**`log_file_how_to.md`**](docs/log_file_how_to.md) guide to start populating your new, genius-level documentation.

### For Existing Projects (1-6 Hours)

Already have a project with some documentation? No problem!

1.  **Quick Assessment:**
    - Do you have a CHANGELOG? DEVLOG? PRD?
    - How many tokens are your docs consuming?
    - Want full adoption or gradual migration?

2.  **Follow the Migration Guide:**
    Read the [**Migration Guide**](docs/MIGRATION_GUIDE.md) for step-by-step instructions tailored to your situation.

3.  **Choose Your Path:**
    - **Scenario A:** No docs → Start fresh (1-2 hours)
    - **Scenario B:** Have CHANGELOG → Expand (3-6 hours)
    - **Scenario C:** Verbose docs → Condense (1-2 days)
    - **Scenario D:** Partial implementation → Complete (2-4 hours)

## 📦 Starter Packs

Get running even faster with pre-configured starter packs for your favorite tools.

| Tool | Link | Status |
|---|---|---|
| **Claude Code** | `starter-packs/claude-code/` | ✅ Available |
| **Cursor** | `starter-packs/cursor/` | 🚧 Coming Soon |
| **GitHub Copilot** | `starter-packs/github-copilot/` | 🚧 Coming Soon |
| **Augment** | `starter-packs/augment/` | ✅ Available |

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
