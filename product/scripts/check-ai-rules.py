#!/usr/bin/env python3
"""
Log File Genius - AI Rule Conflict Detector

Detects potential conflicts between AI rules that could cause unpredictable behavior.
Validates rule structure, dependencies, and identifies contradictions.

Usage:
    python check-ai-rules.py                    # Check all AI rules
    python check-ai-rules.py --rules-dir PATH   # Check rules in specific directory
    python check-ai-rules.py --json             # Output as JSON

Exit codes:
    0 - No conflicts detected
    1 - Warnings found (potential conflicts)
    2 - Errors found (definite conflicts)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class RuleMetadata:
    """Metadata extracted from an AI rule file"""
    file_path: str
    name: str
    trigger_type: str  # 'always', 'manual', 'conditional'
    keywords: Set[str] = field(default_factory=set)
    actions: Set[str] = field(default_factory=set)  # 'commit', 'update', 'create', 'delete'
    forbids: Set[str] = field(default_factory=set)  # things this rule forbids
    requires: Set[str] = field(default_factory=set)  # things this rule requires
    directives: Dict[str, str] = field(default_factory=dict)  # topic -> require/forbid/optional


@dataclass
class ConflictReport:
    """Report of detected conflicts"""
    conflicts: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)

    def add_conflict(self, rule1: str, rule2: str, reason: str, severity: str = "error"):
        entry = {"rule1": rule1, "rule2": rule2, "reason": reason, "severity": severity}
        if severity == "error":
            self.conflicts.append(entry)
        else:
            self.warnings.append(entry)


# Topics that rules can make statements about
RULE_TOPICS = [
    "changelog", "devlog", "commit", "push", "merge", "adr",
    "documentation", "secrets", "security", "validation"
]

# Phrases that indicate stop conditions (not actual forbids)
STOP_CONDITION_PHRASES = [
    "do not proceed", "don't proceed", "stop", "wait", "until",
    "before proceeding", "do not run", "do not continue"
]


def extract_rule_metadata(file_path: Path) -> RuleMetadata:
    """Extract metadata from an AI rule file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()

    # Determine trigger type
    if "always active" in content or "non-negotiable" in content:
        trigger_type = "always"
    elif "trigger" in content or "when" in content[:500]:
        trigger_type = "manual"
    else:
        trigger_type = "conditional"

    # Extract keywords
    keywords = set()
    keyword_patterns = [
        r'\b(must|always|never|required|mandatory|forbidden|optional)\b',
        r'\b(before|after|during)\s+(commit|push|merge)',
        r'\b(update|create|delete|modify|read)\b',
    ]
    for pattern in keyword_patterns:
        keywords.update(re.findall(pattern, content))

    # Extract actions
    actions = set()
    if re.search(r'(git\s+)?commit', content):
        actions.add("commit")
    if re.search(r'update\s+(changelog|devlog|file)', content):
        actions.add("update")
    if re.search(r'create\s+(file|entry|adr)', content):
        actions.add("create")

    # Extract topic-specific directives (what the rule says about each topic)
    directives: Dict[str, str] = {}  # topic -> 'require' | 'forbid' | 'optional'

    for topic in RULE_TOPICS:
        if topic not in content:
            continue

        # Find sentences containing this topic
        topic_pattern = rf'[^.]*\b{topic}\b[^.]*\.'
        topic_sentences = re.findall(topic_pattern, content)

        for sentence in topic_sentences:
            # Skip stop conditions (not real forbids)
            if any(phrase in sentence for phrase in STOP_CONDITION_PHRASES):
                continue

            # Check if this is a requirement or forbid
            if re.search(r'\b(must|always|required?|shall)\b', sentence):
                directives[topic] = 'require'
            elif re.search(r'\b(never|forbidden?|don\'t|do not|shall not)\b', sentence):
                directives[topic] = 'forbid'
            elif re.search(r'\b(optional|may|can|if needed)\b', sentence):
                directives[topic] = 'optional'

    # Legacy: still extract forbids/requires for backward compat but filter better
    forbids = set()
    forbid_matches = re.findall(r'(?:never|forbidden?|❌)\s+(\w+(?:\s+\w+){0,3})', content)
    # Filter out stop conditions
    for match in forbid_matches[:10]:
        if not any(phrase in match for phrase in STOP_CONDITION_PHRASES):
            forbids.add(match)

    requires = set()
    require_matches = re.findall(r'(?:must|required?)\s+(\w+(?:\s+\w+){0,3})', content)
    requires.update(require_matches[:10])

    # Get rule name from first heading or filename
    name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    name = name_match.group(1) if name_match else file_path.stem

    return RuleMetadata(
        file_path=str(file_path),
        name=name,
        trigger_type=trigger_type,
        keywords=keywords,
        actions=actions,
        forbids=forbids,
        requires=requires,
        directives=directives
    )


def detect_conflicts(rules: List[RuleMetadata]) -> ConflictReport:
    """Detect conflicts between rules using topic-based analysis"""
    report = ConflictReport()

    for i, rule1 in enumerate(rules):
        for rule2 in rules[i+1:]:
            # PRIMARY CHECK: Topic-based directive conflicts
            # If both rules talk about the same topic with contradicting directives
            common_topics = set(rule1.directives.keys()) & set(rule2.directives.keys())
            for topic in common_topics:
                d1 = rule1.directives[topic]
                d2 = rule2.directives[topic]

                # Direct contradiction: one requires, other forbids
                if (d1 == 'require' and d2 == 'forbid') or (d1 == 'forbid' and d2 == 'require'):
                    report.add_conflict(
                        rule1.name, rule2.name,
                        f"Contradicting directives for '{topic}': {rule1.name} {d1}s it, {rule2.name} {d2}s it",
                        severity="error"
                    )
                # Soft conflict: one requires, other says optional
                elif (d1 == 'require' and d2 == 'optional') or (d1 == 'optional' and d2 == 'require'):
                    report.add_conflict(
                        rule1.name, rule2.name,
                        f"Conflicting optionality for '{topic}': one requires, other says optional",
                        severity="warning"
                    )

            # SECONDARY CHECK: Both always-active rules modifying same thing
            # (only warn if they don't have explicit topic directives)
            if rule1.trigger_type == "always" and rule2.trigger_type == "always":
                shared_actions = rule1.actions & rule2.actions
                # Only flag if no topic-based conflict already found
                if shared_actions and not common_topics:
                    for action in shared_actions:
                        report.add_conflict(
                            rule1.name, rule2.name,
                            f"Both always-active rules affect '{action}' - verify they're compatible",
                            severity="info"  # Downgrade to info since it may be intentional
                        )

    return report


def find_rule_files(rules_dir: Path) -> List[Path]:
    """Find all AI rule markdown files, deduplicated by filename"""
    rule_files = list(rules_dir.glob('**/*.md'))
    rule_files = [f for f in rule_files if f.is_file()]

    # Deduplicate by filename - if the same filename appears in multiple dirs,
    # keep only the first occurrence.
    seen_names: Set[str] = set()
    unique_files = []
    for f in rule_files:
        if f.name not in seen_names:
            seen_names.add(f.name)
            unique_files.append(f)

    return unique_files


def print_results(rules: List[RuleMetadata], report: ConflictReport, json_output: bool = False):
    """Print conflict detection results"""
    if json_output:
        output = {
            "rules_checked": len(rules),
            "conflicts": report.conflicts,
            "warnings": report.warnings,
            "summary": {
                "errors": len(report.conflicts),
                "warnings": len(report.warnings)
            }
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print("\n" + "="*60)
    print("Log File Genius - AI Rule Conflict Detection")
    print("="*60)

    print(f"\nRules analyzed: {len(rules)}")
    for rule in rules:
        print(f"  - {rule.name} ({rule.trigger_type})")

    if report.conflicts:
        print(f"\n[X] CONFLICTS DETECTED ({len(report.conflicts)}):")
        for c in report.conflicts:
            print(f"\n  {c['rule1']} <-> {c['rule2']}")
            print(f"  Reason: {c['reason']}")

    if report.warnings:
        print(f"\n[!] WARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"\n  {w['rule1']} <-> {w['rule2']}")
            print(f"  Reason: {w['reason']}")

    print("\n" + "="*60)
    if not report.conflicts and not report.warnings:
        print("[OK] No conflicts detected")
    else:
        print(f"Summary: {len(report.conflicts)} errors, {len(report.warnings)} warnings")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Detect conflicts between AI rules")
    parser.add_argument('--rules-dir', type=str, help="Directory containing AI rules")
    parser.add_argument('--json', action='store_true', help="Output as JSON")

    args = parser.parse_args()

    # Find rules directory
    if args.rules_dir:
        rules_dir = Path(args.rules_dir)
    else:
        # Default: check product/rules (canonical fragments; ai-rules/ removed in T22)
        script_dir = Path(__file__).parent
        product_dir = script_dir.parent
        rules_dir = product_dir / "rules"

    if not rules_dir.exists():
        print(f"ERROR: Rules directory not found: {rules_dir}", file=sys.stderr)
        sys.exit(1)

    # Find and analyze rules
    rule_files = find_rule_files(rules_dir)
    if not rule_files:
        print(f"No rule files found in {rules_dir}", file=sys.stderr)
        sys.exit(0)

    rules = [extract_rule_metadata(f) for f in rule_files]

    # Detect conflicts
    report = detect_conflicts(rules)

    # Print results
    print_results(rules, report, json_output=args.json)

    # Exit code
    if report.conflicts:
        sys.exit(2)
    elif report.warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
