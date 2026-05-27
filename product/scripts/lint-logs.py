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
    python lint-logs.py --self-test        # Run validator self-tests first

Exit codes:
    0 - All validations passed
    1 - Warnings found
    2 - Errors found
    3 - Self-test failed (validator cannot be trusted)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_parser import parse_config, ConfigError


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


class SelfTestResult:
    """Result of validator self-tests"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.failures) == 0

    def add_pass(self, test_name: str):
        self.tests_run += 1
        self.tests_passed += 1

    def add_failure(self, test_name: str, reason: str):
        self.tests_run += 1
        self.failures.append(f"{test_name}: {reason}")


class ValidatorSelfTest:
    """
    Meta-validation: Validators must verify themselves before running.
    Solves the 'who watches the watchers' problem.
    """

    @staticmethod
    def run_all_tests() -> SelfTestResult:
        """Run all self-tests to verify validator integrity"""
        result = SelfTestResult()

        # Test 1: Regex patterns compile correctly
        ValidatorSelfTest._test_regex_patterns(result)

        # Test 2: Token estimation is reasonable
        ValidatorSelfTest._test_token_estimation(result)

        # Test 3: Known-good input produces expected output
        ValidatorSelfTest._test_known_good_changelog(result)

        # Test 4: Known-bad input produces expected errors
        ValidatorSelfTest._test_known_bad_changelog(result)

        # Test 5: ValidationResult tracking works
        ValidatorSelfTest._test_validation_result_tracking(result)

        # Test 6: DEVLOG validation logic works
        ValidatorSelfTest._test_devlog_detection(result)

        return result

    @staticmethod
    def _test_regex_patterns(result: SelfTestResult):
        """Test that all regex patterns compile and match expected inputs"""
        test_name = "regex_patterns_compile"
        try:
            # Test Unreleased section pattern
            pattern = r'^##\s+\[Unreleased\]'
            if not re.match(pattern, '## [Unreleased]'):
                result.add_failure(test_name, "Unreleased pattern failed to match")
                return

            # Test changelog entry pattern
            entry = "- Added feature. Files: `src/main.py`. Commit: `abc1234`"
            if 'Files:' not in entry or 'Commit:' not in entry:
                result.add_failure(test_name, "Entry detection logic broken")
                return

            # Test commit hash extraction
            commit_match = re.search(r'Commit:\s*`([^`]+)`', entry)
            if not commit_match or commit_match.group(1) != 'abc1234':
                result.add_failure(test_name, "Commit hash extraction failed")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))

    @staticmethod
    def _test_token_estimation(result: SelfTestResult):
        """Test that token estimation produces reasonable results"""
        test_name = "token_estimation"
        try:
            # 100 characters should be ~25 tokens (using 4 chars/token estimate)
            test_text = "a" * 100
            estimated = len(test_text) // 4
            if estimated != 25:
                result.add_failure(test_name, f"Expected 25 tokens, got {estimated}")
                return

            # Empty string should be 0 tokens
            if len("") // 4 != 0:
                result.add_failure(test_name, "Empty string should be 0 tokens")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))

    @staticmethod
    def _test_known_good_changelog(result: SelfTestResult):
        """Test that valid CHANGELOG content passes validation"""
        test_name = "known_good_changelog"
        try:
            good_entry = "- Added new feature. Files: `src/app.py`. Commit: `abc1234`"

            # Should have Files: and Commit:
            if 'Files:' not in good_entry:
                result.add_failure(test_name, "Good entry missing Files: detection")
                return
            if 'Commit:' not in good_entry:
                result.add_failure(test_name, "Good entry missing Commit: detection")
                return

            # Should have period before Files:
            if not re.search(r'\.\s+Files:', good_entry):
                result.add_failure(test_name, "Period detection before Files: failed")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))

    @staticmethod
    def _test_known_bad_changelog(result: SelfTestResult):
        """Test that invalid CHANGELOG content produces warnings"""
        test_name = "known_bad_changelog"
        try:
            # Entry missing commit hash
            bad_entry = "- Added feature. Files: `src/app.py`"
            if 'Commit:' in bad_entry:
                result.add_failure(test_name, "Bad entry incorrectly has Commit:")
                return

            # Short commit hash
            short_hash = "abc"
            if len(short_hash) >= 7:
                result.add_failure(test_name, "Short hash detection broken")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))

    @staticmethod
    def _test_validation_result_tracking(result: SelfTestResult):
        """Test that ValidationResult correctly tracks issues"""
        test_name = "validation_result_tracking"
        try:
            vr = ValidationResult(file="test.md")

            # Initial state
            if vr.errors != 0 or vr.warnings != 0:
                result.add_failure(test_name, "Initial counts should be 0")
                return

            # Add error
            vr.add_issue('error', 1, "Test error")
            if vr.errors != 1:
                result.add_failure(test_name, "Error count not incremented")
                return

            # Add warning
            vr.add_issue('warning', 2, "Test warning")
            if vr.warnings != 1:
                result.add_failure(test_name, "Warning count not incremented")
                return

            # Check issues list
            if len(vr.issues) != 2:
                result.add_failure(test_name, f"Expected 2 issues, got {len(vr.issues)}")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))

    @staticmethod
    def _test_devlog_detection(result: SelfTestResult):
        """Test DEVLOG section detection logic"""
        test_name = "devlog_detection"
        try:
            # Should detect Current Context
            test_line = "## Current Context (Source of Truth)"
            if 'Current Context' not in test_line and 'Source of Truth' not in test_line:
                result.add_failure(test_name, "Current Context detection failed")
                return

            # Should detect Daily Log
            test_line2 = "## Daily Log"
            if 'Daily Log' not in test_line2:
                result.add_failure(test_name, "Daily Log detection failed")
                return

            result.add_pass(test_name)
        except Exception as e:
            result.add_failure(test_name, str(e))


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
            return parse_config(config_path)
        except ConfigError as e:
            print(f"ERROR: Invalid .logfile-config.yml: {e}", file=sys.stderr)
            sys.exit(2)

    def _validate_frontmatter_links(self, file_path: str, lines: List[str], result: ValidationResult):
        """Validate frontmatter links point to existing files"""
        in_frontmatter = False

        for i, line in enumerate(lines, 1):
            # Detect frontmatter section
            if '## Related Documents' in line:
                in_frontmatter = True
                continue
            if in_frontmatter and line.startswith('##') and '## Related Documents' not in line:
                break  # End of frontmatter

            # Check markdown links: [text](path)
            if in_frontmatter:
                matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                for link_text, link_path in matches:
                    # Skip external URLs
                    if link_path.startswith('http://') or link_path.startswith('https://'):
                        continue

                    # Resolve relative path from file location
                    file_dir = os.path.dirname(file_path)
                    full_path = os.path.normpath(os.path.join(file_dir, link_path))

                    if not os.path.exists(full_path):
                        result.add_issue('warning', i,
                                       f"Broken frontmatter link: [{link_text}]({link_path})",
                                       f"File not found: {full_path}")
    
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

        # Validate frontmatter links
        self._validate_frontmatter_links(self.changelog_path, lines, result)

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

        # Validate frontmatter links
        self._validate_frontmatter_links(self.devlog_path, lines, result)

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


def print_self_test_results(result: SelfTestResult, json_output: bool = False):
    """Print self-test results"""
    if json_output:
        output = {
            'self_test': {
                'passed': result.passed,
                'tests_run': result.tests_run,
                'tests_passed': result.tests_passed,
                'failures': result.failures
            }
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print("\n" + "="*60)
    print("Log File Genius - Validator Self-Test")
    print("="*60 + "\n")

    if result.passed:
        print(f"[OK] All {result.tests_run} self-tests passed")
        print("     Validator integrity verified - results can be trusted")
    else:
        print(f"[X] SELF-TEST FAILED: {len(result.failures)}/{result.tests_run} tests failed")
        print("    CRITICAL: Validator cannot be trusted!")
        print("\nFailures:")
        for failure in result.failures:
            print(f"  - {failure}")

    print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate Log File Genius log files")
    parser.add_argument('--changelog', action='store_true', help="Validate only CHANGELOG")
    parser.add_argument('--devlog', action='store_true', help="Validate only DEVLOG")
    parser.add_argument('--strict', action='store_true', help="Fail on warnings")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--config', default=".logfile-config.yml", help="Config file path")
    parser.add_argument('--self-test', action='store_true',
                        help="Run validator self-tests (always runs before validation)")
    parser.add_argument('--skip-self-test', action='store_true',
                        help="Skip self-tests (not recommended)")

    args = parser.parse_args()

    # Run self-tests first (unless explicitly skipped)
    if not args.skip_self_test:
        self_test_result = ValidatorSelfTest.run_all_tests()

        if args.self_test:
            # Just running self-tests, show results and exit
            print_self_test_results(self_test_result, json_output=args.json)
            sys.exit(0 if self_test_result.passed else 3)

        if not self_test_result.passed:
            # Self-tests failed - cannot trust validation results
            print_self_test_results(self_test_result, json_output=args.json)
            print("ABORTING: Validator self-tests failed. Results cannot be trusted.")
            print("Fix the validator or use --skip-self-test (not recommended).")
            sys.exit(3)

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

