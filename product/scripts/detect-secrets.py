#!/usr/bin/env python3
"""
Log File Genius - Context-Aware Secret Detection

Detects potential secrets in log files while distinguishing real secrets
from documentation examples. Uses multiple detection strategies:
- Entropy detection (high-randomness strings)
- Pattern matching (known secret formats)
- Context awareness (distinguishes examples from real secrets)
- Allowlist support (user-defined exceptions)

Exit codes:
  0 - No secrets found
  1 - Warnings only (low confidence findings)
  2 - Errors (high confidence secrets detected)
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Known secret patterns with confidence levels
SECRET_PATTERNS = [
    # (pattern, name, confidence: high/medium/low)
    (r'password\s*[:=]\s*["\']?([^\s"\']{8,})["\']?', 'password', 'high'),
    (r'api[_-]?key\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?', 'api_key', 'high'),
    (r'secret[_-]?key\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?', 'secret_key', 'high'),
    (r'token\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{20,})["\']?', 'token', 'high'),
    (r'bearer\s+([A-Za-z0-9\-._~+/]+=*)', 'bearer_token', 'high'),
    (r'aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*["\']?([A-Z0-9]{20})["\']?', 'aws_access_key', 'high'),
    (r'aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?', 'aws_secret_key', 'high'),
    (r'ghp_[A-Za-z0-9]{36}', 'github_pat', 'high'),
    (r'sk-[A-Za-z0-9]{48}', 'openai_key', 'high'),
    (r'mongodb(\+srv)?://[^:]+:([^@]+)@', 'mongodb_password', 'high'),
    (r'postgres(ql)?://[^:]+:([^@]+)@', 'postgres_password', 'high'),
    (r'mysql://[^:]+:([^@]+)@', 'mysql_password', 'high'),
    # Medium confidence - might be examples
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'email', 'medium'),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'ip_address', 'low'),
]

# Context indicators that suggest documentation/examples (not real secrets)
EXAMPLE_INDICATORS = [
    r'example', r'sample', r'demo', r'test', r'dummy', r'fake', r'placeholder',
    r'your[_-]?', r'<.*>', r'\[.*\]', r'xxx+', r'123+', r'abc+',
    r'replace\s+with', r'set\s+your', r'enter\s+your', r'insert\s+your',
]

# File extensions that are documentation (higher tolerance for examples)
DOC_EXTENSIONS = {'.md', '.txt', '.rst', '.adoc', '.html'}


@dataclass
class Finding:
    """A potential secret finding"""
    file_path: str
    line_number: int
    line_content: str
    secret_type: str
    matched_value: str
    confidence: str  # high, medium, low
    is_example: bool = False
    reason: str = ""


@dataclass
class ScanResult:
    """Results from scanning files"""
    findings: List[Finding] = field(default_factory=list)
    files_scanned: int = 0

    def add(self, finding: Finding):
        self.findings.append(finding)

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.confidence == 'high' and not f.is_example]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.confidence != 'high' or f.is_example]


def calculate_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string (higher = more random)"""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(s)
        entropy -= p * math.log2(p)
    return entropy


def is_example_context(line: str, value: str) -> Tuple[bool, str]:
    """Check if the matched value appears to be an example/placeholder"""
    line_lower = line.lower()
    value_lower = value.lower()

    # Check for example indicators in the line
    for indicator in EXAMPLE_INDICATORS:
        if re.search(indicator, line_lower):
            return True, f"Contains example indicator: {indicator}"
        if re.search(indicator, value_lower):
            return True, f"Value contains example indicator: {indicator}"

    # Check for placeholder patterns in value
    if re.match(r'^[x]+$', value_lower) or re.match(r'^[0]+$', value):
        return True, "Value is placeholder pattern (xxx, 000)"

    # Check for sequential patterns
    if value_lower in ['abcdef', 'abc123', '123456', 'password', 'secret']:
        return True, "Value is common placeholder"

    # Check for markdown code fence context (likely documentation)
    if '```' in line or line.strip().startswith('#'):
        return True, "In code fence or comment context"

    return False, ""


def scan_line(line: str, line_num: int, file_path: str) -> List[Finding]:
    """Scan a single line for secrets"""
    findings = []

    for pattern, secret_type, confidence in SECRET_PATTERNS:
        for match in re.finditer(pattern, line, re.IGNORECASE):
            # Get the captured group (the actual secret value) or full match
            value = match.group(1) if match.lastindex else match.group(0)

            # Check if this looks like an example
            is_example, reason = is_example_context(line, value)

            # For documentation files, be more lenient
            if Path(file_path).suffix in DOC_EXTENSIONS:
                # Entropy check - real secrets tend to have high entropy
                entropy = calculate_entropy(value)
                if entropy < 3.0:  # Low entropy = likely placeholder
                    is_example = True
                    reason = f"Low entropy ({entropy:.2f}) suggests placeholder"

            findings.append(Finding(
                file_path=file_path,
                line_number=line_num,
                line_content=line.strip()[:100],
                secret_type=secret_type,
                matched_value=value[:20] + '...' if len(value) > 20 else value,
                confidence=confidence,
                is_example=is_example,
                reason=reason
            ))

    return findings


def load_allowlist(allowlist_path: Optional[Path]) -> Set[str]:
    """Load patterns to ignore from allowlist file"""
    if not allowlist_path or not allowlist_path.exists():
        return set()

    patterns = set()
    with open(allowlist_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.add(line)
    return patterns


def scan_file(file_path: Path, allowlist: Set[str]) -> List[Finding]:
    """Scan a file for secrets"""
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip allowlisted lines
                if any(pattern in line for pattern in allowlist):
                    continue

                line_findings = scan_line(line, line_num, str(file_path))
                findings.extend(line_findings)
    except Exception as e:
        print(f"Warning: Could not scan {file_path}: {e}", file=sys.stderr)

    return findings


def scan_files(paths: List[Path], allowlist: Set[str]) -> ScanResult:
    """Scan multiple files for secrets"""
    result = ScanResult()

    for path in paths:
        if path.is_file():
            findings = scan_file(path, allowlist)
            result.findings.extend(findings)
            result.files_scanned += 1
        elif path.is_dir():
            # Scan markdown files in directory
            for md_file in path.glob('**/*.md'):
                findings = scan_file(md_file, allowlist)
                result.findings.extend(findings)
                result.files_scanned += 1

    return result


def print_results(result: ScanResult, json_output: bool = False):
    """Print scan results"""
    if json_output:
        output = {
            "files_scanned": result.files_scanned,
            "findings": [
                {
                    "file": f.file_path,
                    "line": f.line_number,
                    "type": f.secret_type,
                    "confidence": f.confidence,
                    "is_example": f.is_example,
                    "reason": f.reason
                }
                for f in result.findings
            ],
            "summary": {
                "errors": len(result.errors),
                "warnings": len(result.warnings)
            }
        }
        print(json.dumps(output, indent=2))
        return

    print("\n" + "="*60)
    print("Log File Genius - Secret Detection")
    print("="*60)
    print(f"\nFiles scanned: {result.files_scanned}")

    if result.errors:
        print(f"\n[X] SECRETS DETECTED ({len(result.errors)}):")
        for f in result.errors:
            print(f"\n  {f.file_path}:{f.line_number}")
            print(f"  Type: {f.secret_type} (confidence: {f.confidence})")
            print(f"  Line: {f.line_content}")
            print(f"  Fix: Replace with placeholder or use vault reference")

    if result.warnings:
        print(f"\n[!] POSSIBLE SECRETS ({len(result.warnings)}):")
        for f in result.warnings:
            reason = f" ({f.reason})" if f.reason else ""
            status = "EXAMPLE" if f.is_example else "LOW CONFIDENCE"
            print(f"\n  [{status}] {f.file_path}:{f.line_number}{reason}")
            print(f"  Type: {f.secret_type}")

    print("\n" + "="*60)
    if not result.errors and not result.warnings:
        print("[OK] No secrets detected")
    elif result.errors:
        print(f"[X] {len(result.errors)} secrets found - commit blocked")
    else:
        print(f"[!] {len(result.warnings)} warnings - review recommended")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Detect secrets in log files")
    parser.add_argument('paths', nargs='*', default=['logs/'], help="Files or directories to scan")
    parser.add_argument('--allowlist', type=str, help="Path to allowlist file")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--strict', action='store_true', help="Treat warnings as errors")

    args = parser.parse_args()

    # Convert paths
    paths = [Path(p) for p in args.paths]

    # Load allowlist
    allowlist_path = Path(args.allowlist) if args.allowlist else None
    allowlist = load_allowlist(allowlist_path)

    # Scan files
    result = scan_files(paths, allowlist)

    # Print results
    print_results(result, json_output=args.json)

    # Exit code
    if result.errors:
        sys.exit(2)
    elif result.warnings and args.strict:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
