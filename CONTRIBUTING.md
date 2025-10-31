# Contributing to Log File Genius

Thank you for your interest in contributing to Log File Genius! This project aims to help developers maintain token-efficient documentation for AI coding assistants, and your contributions help make that mission better.

## 🎯 Ways to Contribute

### 1. Report Bugs 🐛

Found a bug? Help us fix it!

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce the problem
   - Expected vs. actual behavior
   - Your environment (OS, AI assistant, project type)
   - Screenshots or error messages if applicable

### 2. Suggest Features 💡

Have an idea for improvement?

1. **Check existing discussions** to see if it's been proposed
2. **Open a discussion** in the Ideas category
3. **Describe:**
   - The problem you're trying to solve
   - Your proposed solution
   - Why it would benefit other users
   - Any alternatives you've considered

### 3. Improve Documentation 📚

Documentation improvements are always welcome!

- Fix typos or unclear explanations
- Add examples or use cases
- Improve installation guides
- Translate documentation (future)
- Add platform-specific tips

### 4. Add Platform Support 🔌

Help expand support for more AI coding assistants!

**Currently supported:**
- Augment
- Claude Code

**Wanted:**
- Cursor
- GitHub Copilot
- Continue
- Cody
- Other AI assistants

**To add a new platform:**
1. Create a starter pack in `starter-packs/[platform-name]/`
2. Include setup instructions, rules/instructions, and examples
3. Test thoroughly with the platform
4. Update the main README.md with the new platform
5. Submit a PR with your changes

### 5. Share Success Stories 🎉

Using Log File Genius successfully? Share your story!

1. **Post in Discussions** under "Show and Tell"
2. **Include:**
   - Your project type and size
   - Token reduction achieved
   - Challenges you faced
   - Tips for other users
   - Before/after metrics if available

## 🚀 Getting Started

### Prerequisites

- Git installed
- A GitHub account
- Familiarity with Markdown
- (Optional) Experience with AI coding assistants

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/log-file-genius.git
   cd log-file-genius
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**
   - Edit documentation files
   - Add new templates or examples
   - Update starter packs

4. **Test your changes**
   - Verify all links work
   - Check Markdown formatting
   - Test with actual AI assistants if applicable
   - Ensure examples are accurate

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## 📝 Contribution Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy toward other contributors

### Commit Message Format

Use clear, descriptive commit messages:

```
Add: New feature or file
Update: Changes to existing content
Fix: Bug fixes
Remove: Deleted files or features
Docs: Documentation-only changes
```

Examples:
- `Add: Cursor starter pack with installation guide`
- `Fix: Broken links in migration guide`
- `Update: README with new token reduction metrics`
- `Docs: Clarify ADR creation process`

### Documentation Standards

- **Use Markdown** for all documentation
- **Keep it concise** - respect token budgets
- **Include examples** where helpful
- **Link, don't duplicate** - reference existing docs
- **Test all links** before submitting
- **Use relative paths** for internal links

### File Naming Conventions

- **Templates:** `UPPERCASE_template.md` (e.g., `CHANGELOG_template.md`)
- **Documentation:** `lowercase-with-hyphens.md` (e.g., `migration-guide.md`)
- **ADRs:** `NNN-short-title.md` (e.g., `001-github-pages-deployment.md`)
- **Examples:** Descriptive names matching content

### Token Efficiency

Remember: This project is about token efficiency!

- Keep documentation concise
- Use bullet points over paragraphs
- Link to external resources instead of copying
- Avoid redundant explanations
- Test token counts for major additions

## 🔍 Review Process

### What to Expect

1. **Initial Review:** A maintainer will review within 3-5 days
2. **Feedback:** You may receive requests for changes
3. **Iteration:** Make requested changes and push updates
4. **Approval:** Once approved, your PR will be merged
5. **Recognition:** You'll be added to contributors list!

### Review Criteria

- **Accuracy:** Information is correct and tested
- **Clarity:** Easy to understand for target audience
- **Completeness:** Includes all necessary information
- **Consistency:** Matches existing style and structure
- **Value:** Provides clear benefit to users

## 🎁 Recognition

All contributors will be:
- Listed in the project's contributors
- Mentioned in release notes (for significant contributions)
- Thanked in the community discussions

## 📋 Starter Pack Contribution Checklist

If you're adding a new AI assistant starter pack:

- [ ] Created `starter-packs/[platform-name]/` directory
- [ ] Included README.md with setup instructions
- [ ] Added platform-specific rules/instructions
- [ ] Provided working examples
- [ ] Tested with the actual platform
- [ ] Updated main README.md with platform status
- [ ] Documented any platform-specific quirks
- [ ] Included troubleshooting section
- [ ] Added links to official platform documentation

## 🆘 Need Help?

- **Questions?** Open a discussion in Q&A
- **Stuck?** Ask in the discussion thread for your PR
- **Not sure?** Reach out to maintainers via issues

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Log File Genius better for everyone!** 🙏

Every contribution, no matter how small, helps developers worldwide maintain better documentation for their AI coding assistants.

