# Installer Testing Guide

## Manual Testing Checklist

Before releasing a new version, test both installers on all supported platforms.

### Prerequisites

- Windows machine with PowerShell 5.1+
- Mac/Linux machine with Bash 4.0+
- Git installed on both
- Test projects (greenfield and brownfield)

---

## Test Scenarios

### 1. Greenfield Installation (New Project)

**Windows (PowerShell):**
```powershell
# Create test project
mkdir test-project-win
cd test-project-win
git init

# Add Log File Genius as submodule
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius

# Run installer
.\.log-file-genius\product\scripts\install.ps1
```

**Mac/Linux (Bash):**
```bash
# Create test project
mkdir test-project-unix
cd test-project-unix
git init

# Add Log File Genius as submodule
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius

# Run installer
./.log-file-genius/product/scripts/install.sh
```

**Expected Results:**
- ✅ Installer detects AI assistant (or prompts for selection)
- ✅ Installer prompts for profile selection
- ✅ Creates `logs/`, `logs/adr/`, `logs/incidents/`
- ✅ Copies templates: `CHANGELOG.md`, `DEVLOG.md`, `STATE.md`, `adr/TEMPLATE.md`
- ✅ Installs AI rules to `.augment/rules/` or `.claude/rules/`
- ✅ Creates `.logfile-config.yml`
- ✅ Validation passes
- ✅ Success message displays with AI prompt

---

### 2. Brownfield Installation (Existing Project)

**Setup:**
```bash
# Create project with existing files
mkdir test-brownfield
cd test-brownfield
git init
echo "# My Project" > README.md
mkdir src
echo "console.log('hello')" > src/index.js
git add .
git commit -m "Initial commit"

# Add Log File Genius
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
```

**Run installer and verify:**
- ✅ Installer doesn't overwrite existing files
- ✅ Installer creates log files alongside existing structure
- ✅ Git status shows only new log files (no modifications to existing files)

---

### 3. Force Flag Test

```powershell
# Windows
.\.log-file-genius\product\scripts\install.ps1 -Force

# Mac/Linux
./.log-file-genius/product/scripts/install.sh --force
```

**Expected Results:**
- ✅ Skips confirmation prompts
- ✅ Validation still runs
- ✅ Installation completes without user input

---

### 4. Profile Selection Test

Test each profile:

```powershell
# Windows
.\.log-file-genius\product\scripts\install.ps1 -Profile "solo-developer"
.\.log-file-genius\product\scripts\install.ps1 -Profile "team"
.\.log-file-genius\product\scripts\install.ps1 -Profile "open-source"
.\.log-file-genius\product\scripts\install.ps1 -Profile "startup"

# Mac/Linux
./.log-file-genius/product/scripts/install.sh --profile solo-developer
./.log-file-genius/product/scripts/install.sh --profile team
./.log-file-genius/product/scripts/install.sh --profile open-source
./.log-file-genius/product/scripts/install.sh --profile startup
```

**Expected Results:**
- ✅ `.logfile-config.yml` contains correct profile
- ✅ No prompts for profile selection

---

### 5. AI Assistant Selection Test

```powershell
# Windows
.\.log-file-genius\product\scripts\install.ps1 -AiAssistant "augment"
.\.log-file-genius\product\scripts\install.ps1 -AiAssistant "claude-code"

# Mac/Linux
./.log-file-genius/product/scripts/install.sh --ai-assistant augment
./.log-file-genius/product/scripts/install.sh --ai-assistant claude-code
```

**Expected Results:**
- ✅ Augment: Rules installed to `.augment/rules/`
- ✅ Claude Code: Rules installed to `.claude/rules/` + `project_instructions.md` to `.claude/`
- ✅ `.logfile-config.yml` contains correct AI assistant

---

### 6. Rollback Test (Failure Scenarios)

**Test missing templates:**
```bash
# Temporarily rename a template
cd .log-file-genius/product/templates
mv CHANGELOG_template.md CHANGELOG_template.md.bak

# Run installer (should fail and rollback)
cd ../../..
./.log-file-genius/product/scripts/install.sh

# Verify rollback
ls logs/  # Should not exist or be empty

# Restore template
cd .log-file-genius/product/templates
mv CHANGELOG_template.md.bak CHANGELOG_template.md
```

**Expected Results:**
- ✅ Installer fails with clear error message
- ✅ Rollback removes created files
- ✅ Project is in clean state (no partial installation)

---

### 7. Recursive AI Rules Test

**Setup:**
```bash
# Create subdirectory in AI rules
mkdir .log-file-genius/product/ai-rules/augment/advanced
echo "# Advanced Rule" > .log-file-genius/product/ai-rules/augment/advanced/test.md

# Run installer
./.log-file-genius/product/scripts/install.sh --ai-assistant augment
```

**Expected Results:**
- ✅ `.augment/rules/advanced/test.md` exists
- ✅ Directory structure preserved

---

### 8. Validation Test

**Test validation passes:**
```bash
# Run installer
./.log-file-genius/product/scripts/install.sh

# Verify validation output
# Should show:
# - CHANGELOG.md exists
# - DEVLOG.md exists
# - AI rules installed
# - Config file created
```

**Test validation fails:**
```bash
# Run installer
./.log-file-genius/product/scripts/install.sh

# Delete a required file
rm logs/CHANGELOG.md

# Re-run validation manually (if available)
./.log-file-genius/product/scripts/validate-log-files.sh
```

**Expected Results:**
- ✅ Validation detects missing file
- ✅ Clear error message displayed

---

## Automated Testing (Future)

### Docker-based Testing

Create `product/tests/docker-test.sh`:

```bash
#!/bin/bash
# Run installer tests in Docker containers

# Test on Ubuntu
docker run -v $(pwd):/workspace ubuntu:latest bash -c "
  cd /workspace
  git init
  ./product/scripts/install.sh --profile solo-developer --ai-assistant augment --force
  ls -la logs/
"

# Test on Alpine
docker run -v $(pwd):/workspace alpine:latest sh -c "
  apk add bash git
  cd /workspace
  git init
  ./product/scripts/install.sh --profile solo-developer --ai-assistant augment --force
  ls -la logs/
"
```

### PowerShell Pester Tests

Create `product/tests/install.Tests.ps1`:

```powershell
Describe "Log File Genius Installer" {
    BeforeEach {
        # Create temp test directory
        $testDir = New-Item -ItemType Directory -Path "TestDrive:\test-project"
        Push-Location $testDir
        git init
    }
    
    AfterEach {
        Pop-Location
    }
    
    It "Creates logs directory" {
        & "$PSScriptRoot/../scripts/install.ps1" -Force -Profile "solo-developer" -AiAssistant "augment"
        Test-Path "logs" | Should -Be $true
    }
    
    It "Copies templates" {
        & "$PSScriptRoot/../scripts/install.ps1" -Force -Profile "solo-developer" -AiAssistant "augment"
        Test-Path "logs/CHANGELOG.md" | Should -Be $true
        Test-Path "logs/DEVLOG.md" | Should -Be $true
        Test-Path "logs/STATE.md" | Should -Be $true
    }
    
    It "Installs AI rules" {
        & "$PSScriptRoot/../scripts/install.ps1" -Force -Profile "solo-developer" -AiAssistant "augment"
        Test-Path ".augment/rules" | Should -Be $true
    }
    
    It "Creates config file" {
        & "$PSScriptRoot/../scripts/install.ps1" -Force -Profile "solo-developer" -AiAssistant "augment"
        Test-Path ".logfile-config.yml" | Should -Be $true
    }
}
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/test-installers.yml`:

```yaml
name: Test Installers

on: [push, pull_request]

jobs:
  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test PowerShell Installer
        run: |
          mkdir test-project
          cd test-project
          git init
          git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
          .\.log-file-genius\product\scripts\install.ps1 -Force -Profile "solo-developer" -AiAssistant "augment"
          
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Bash Installer
        run: |
          mkdir test-project
          cd test-project
          git init
          git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
          ./.log-file-genius/product/scripts/install.sh --force --profile solo-developer --ai-assistant augment
          
  test-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Bash Installer
        run: |
          mkdir test-project
          cd test-project
          git init
          git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
          ./.log-file-genius/product/scripts/install.sh --force --profile solo-developer --ai-assistant augment
```

---

## Regression Testing

Before each release, run through ALL test scenarios above on:
- ✅ Windows 10/11 (PowerShell 5.1 and 7+)
- ✅ macOS (latest)
- ✅ Ubuntu Linux (latest LTS)

Document results in release notes.

