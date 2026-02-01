# Add CHANGELOG Entry

Add a factual entry to the CHANGELOG following Log File Genius conventions.

## Instructions

1. Identify the files changed and version (if applicable)
2. Read the last entry in `logs/CHANGELOG.md` for format consistency
3. Create a new entry with this structure:

```markdown
## [VERSION or DATE] - [Brief Description]

### Changed
- `path/to/file.ext` - [what changed]

### Added
- `path/to/new-file.ext` - [purpose]

### Removed
- `path/to/deleted-file.ext` - [reason]

### Fixed
- `path/to/file.ext` - [bug fixed]
```

## Token Budget
- Keep entry under 300 tokens
- Facts only - no narrative or reasoning
- File paths and concrete changes

## Quality Checklist
- [ ] Only facts, no opinions or reasoning
- [ ] File paths are accurate
- [ ] Categories used correctly (Changed/Added/Removed/Fixed)
- [ ] Token budget respected

$ARGUMENTS contains the changes to document.
