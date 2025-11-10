#!/usr/bin/env python3
"""
Log File Genius - Log Linter

Validates CHANGELOG.md and DEVLOG.md files for format compliance,
token budgets, and content quality.

Usage:
    python lint-logs.py                    # Validate all files
    python lint-logs.py --changelog        # Validate only CHANGELOG
    python lint-logs.py --devlog           # Validate only DEVLOG
    python lint-logs.py --strict           # Fail on warnings
    python lint-logs.py --json             # Output as JSON

Exit codes:
    0 - All validations passed
    1 - Warnings found
    2 - Errors found
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import yaml


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # 'error', 'warning', 'info'
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation results for a file"""
    file: str
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(self, severity: str, line: Optional[int], message: str, suggestion: Optional[str] = None):
        """Add a validation issue"""
        self.issues.append(ValidationIssue(severity, self.file, line, message, suggestion))
        if severity == 'error':
            self.errors += 1
        elif severity == 'warning':
            self.warnings += 1
        else:
            self.passed += 1


class LogLinter:
    """Main linter class"""
    
    def __init__(self, config_path: str = ".logfile-config.yml"):
        self.config = self._load_config(config_path)
        self.changelog_path = self.config.get('paths', {}).get('changelog', 'logs/CHANGELOG.md')
        self.devlog_path = self.config.get('paths', {}).get('devlog', 'logs/DEVLOG.md')
        
        # Token targets from profile or defaults
        profile = self.config.get('profile', 'solo-developer')
        self.changelog_target = self.config.get('token_targets', {}).get('changelog', 10000)
        self.devlog_target = self.config.get('token_targets', {}).get('devlog', 15000)
        self.combined_target = self.config.get('token_targets', {}).get('combined', 25000)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from .logfile-config.yml"""
        if not os.path.exists(config_path):
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)
            return {}
    
    def validate_changelog(self) -> ValidationResult:
        """Validate CHANGELOG.md format and content"""
        result = ValidationResult(file=self.changelog_path)
        
        if not os.path.exists(self.changelog_path):
            result.add_issue('error', None, f"CHANGELOG not found at {self.changelog_path}",
                           "Run the installer to create CHANGELOG.md")
            return result
        
        with open(self.changelog_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check for required sections
        has_unreleased = False
        has_keepachangelog_link = False
        
        for i, line in enumerate(lines, 1):
            # Check for ## [Unreleased] section
            if re.match(r'^##\s+\[Unreleased\]', line):
                has_unreleased = True
            
            # Check for Keep a Changelog link
            if 'keepachangelog.com' in line:
                has_keepachangelog_link = True
            
            # Validate entry format: - Description. Files: `path`. Commit: `hash`
            if line.strip().startswith('- ') and 'Files:' in line:
                if not self._validate_changelog_entry(line, i, result):
                    continue
        
        if not has_unreleased:
            result.add_issue('error', None, "Missing ## [Unreleased] section",
                           "Add '## [Unreleased]' section to track upcoming changes")
        
        if not has_keepachangelog_link:
            result.add_issue('warning', None, "Missing Keep a Changelog link",
                           "Add link to https://keepachangelog.com/ in header")
        
        # Token count validation
        token_count = self._estimate_tokens('\n'.join(lines))
        if token_count > self.changelog_target:
            result.add_issue('error', None, 
                           f"CHANGELOG exceeds token target ({token_count} > {self.changelog_target})",
                           "Archive old entries to logs/archive/CHANGELOG-YYYY-MM.md")
        elif token_count > self.changelog_target * 0.8:
            result.add_issue('warning', None,
                           f"CHANGELOG approaching token target ({token_count}/{self.changelog_target})",
                           "Consider archiving entries older than 2 weeks")
        
        return result
    
    def _validate_changelog_entry(self, line: str, line_num: int, result: ValidationResult) -> bool:
        """Validate a single CHANGELOG entry"""
        # Expected format: - Description. Files: `path`. Commit: `hash`
        
        # Check for Files: section
        if 'Files:' not in line:
            result.add_issue('warning', line_num, "Entry missing 'Files:' section",
                           "Add 'Files: `path/to/file`' to entry")
            return False
        
        # Check for Commit: section
        if 'Commit:' not in line:
            result.add_issue('warning', line_num, "Entry missing 'Commit:' section",
                           "Add 'Commit: `hash`' to entry")
            return False
        
        # Extract commit hash
        commit_match = re.search(r'Commit:\s*`([^`]+)`', line)
        if commit_match:
            commit_hash = commit_match.group(1)
            if commit_hash == 'pending':
                result.add_issue('info', line_num, "Entry has pending commit",
                               "Update with actual commit hash after committing")
            elif len(commit_hash) < 7:
                result.add_issue('warning', line_num, f"Commit hash too short: {commit_hash}",
                               "Use at least 7 characters for commit hash")
        
        # Check for proper sentence ending before Files:
        if not re.search(r'\.\s+Files:', line):
            result.add_issue('warning', line_num, "Missing period before 'Files:'",
                           "End description with period: 'Description. Files: ...'")
        
        return True
    
    def validate_devlog(self) -> ValidationResult:
        """Validate DEVLOG.md format and content"""
        result = ValidationResult(file=self.devlog_path)
        
        if not os.path.exists(self.devlog_path):
            result.add_issue('error', None, f"DEVLOG not found at {self.devlog_path}",
                           "Run the installer to create DEVLOG.md")
            return result
        
        with open(self.devlog_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check for Current Context section
        has_current_context = False
        has_daily_log = False
        
        for i, line in enumerate(lines, 1):
            if 'Current Context' in line or 'Source of Truth' in line:
                has_current_context = True
            if 'Daily Log' in line or 'Development Log' in line:
                has_daily_log = True
        
        if not has_current_context:
            result.add_issue('error', None, "Missing 'Current Context' section",
                           "Add '## Current Context (Source of Truth)' section")
        
        if not has_daily_log:
            result.add_issue('warning', None, "Missing 'Daily Log' section",
                           "Add '## Daily Log' section for development entries")
        
        # Token count validation
        token_count = self._estimate_tokens('\n'.join(lines))
        if token_count > self.devlog_target:
            result.add_issue('error', None,
                           f"DEVLOG exceeds token target ({token_count} > {self.devlog_target})",
                           "Archive old entries to logs/archive/DEVLOG-YYYY-MM.md")
        elif token_count > self.devlog_target * 0.8:
            result.add_issue('warning', None,
                           f"DEVLOG approaching token target ({token_count}/{self.devlog_target})",
                           "Consider archiving entries older than 2 weeks")
        
        return result
    
    def validate_combined_tokens(self) -> ValidationResult:
        """Validate combined token count of CHANGELOG + DEVLOG"""
        result = ValidationResult(file="Combined (CHANGELOG + DEVLOG)")
        
        changelog_tokens = 0
        devlog_tokens = 0
        
        if os.path.exists(self.changelog_path):
            with open(self.changelog_path, 'r', encoding='utf-8') as f:
                changelog_tokens = self._estimate_tokens(f.read())
        
        if os.path.exists(self.devlog_path):
            with open(self.devlog_path, 'r', encoding='utf-8') as f:
                devlog_tokens = self._estimate_tokens(f.read())
        
        combined = changelog_tokens + devlog_tokens
        
        if combined > self.combined_target:
            result.add_issue('error', None,
                           f"Combined tokens exceed target ({combined} > {self.combined_target})",
                           "Archive old entries from both files")
        elif combined > self.combined_target * 0.8:
            result.add_issue('warning', None,
                           f"Combined tokens approaching target ({combined}/{self.combined_target})",
                           "Plan to archive old entries soon")
        else:
            result.add_issue('info', None,
                           f"Combined tokens within target ({combined}/{self.combined_target})")
        
        return result
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validations and return results"""
        results = []
        results.append(self.validate_changelog())
        results.append(self.validate_devlog())
        results.append(self.validate_combined_tokens())
        return results


def print_results(results: List[ValidationResult], json_output: bool = False):
    """Print validation results"""
    if json_output:
        output = {
            'results': [
                {
                    'file': r.file,
                    'passed': r.passed,
                    'warnings': r.warnings,
                    'errors': r.errors,
                    'issues': [
                        {
                            'severity': i.severity,
                            'line': i.line,
                            'message': i.message,
                            'suggestion': i.suggestion
                        }
                        for i in r.issues
                    ]
                }
                for r in results
            ]
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    print("\n" + "="*60)
    print("Log File Genius - Validation Results")
    print("="*60 + "\n")

    total_errors = sum(r.errors for r in results)
    total_warnings = sum(r.warnings for r in results)

    for result in results:
        print(f"\n{result.file}:")
        print("-" * 60)

        if not result.issues:
            print("[OK] No issues found")
            continue

        for issue in result.issues:
            icon = {"error": "[X]", "warning": "[!]", "info": "[i]"}[issue.severity]
            line_info = f" (line {issue.line})" if issue.line else ""
            print(f"{icon} {issue.message}{line_info}")
            if issue.suggestion:
                # Use ASCII arrow for Windows compatibility
                print(f"    -> {issue.suggestion}")

    print("\n" + "="*60)
    print(f"Summary: {total_errors} errors, {total_warnings} warnings")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate Log File Genius log files")
    parser.add_argument('--changelog', action='store_true', help="Validate only CHANGELOG")
    parser.add_argument('--devlog', action='store_true', help="Validate only DEVLOG")
    parser.add_argument('--strict', action='store_true', help="Fail on warnings")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--config', default=".logfile-config.yml", help="Config file path")
    
    args = parser.parse_args()
    
    linter = LogLinter(config_path=args.config)
    
    if args.changelog:
        results = [linter.validate_changelog()]
    elif args.devlog:
        results = [linter.validate_devlog()]
    else:
        results = linter.run_all_validations()
    
    print_results(results, json_output=args.json)
    
    # Determine exit code
    total_errors = sum(r.errors for r in results)
    total_warnings = sum(r.warnings for r in results)
    
    if total_errors > 0:
        sys.exit(2)
    elif args.strict and total_warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

