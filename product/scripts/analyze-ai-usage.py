#!/usr/bin/env python3
"""
AI Usage Log Analyzer

Analyzes logs/ai-usage-log.md to determine which log files AI assistants
actually use and find useful, to optimize token efficiency.

Usage:
    python product/scripts/analyze-ai-usage.py
    python product/scripts/analyze-ai-usage.py --json
    python product/scripts/analyze-ai-usage.py --detailed
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json


def parse_usage_log(log_path):
    """Parse the AI usage log file and extract session data."""
    
    if not log_path.exists():
        print(f"Error: Usage log not found at {log_path}")
        sys.exit(1)
    
    content = log_path.read_text(encoding='utf-8')
    
    # Pattern: YYYY-MM-DD | Task: ... | Read: ... | Useful: ... | Notes: ...
    pattern = r'(\d{4}-\d{2}-\d{2})\s*\|\s*Task:\s*([^|]+)\|\s*Read:\s*([^|]+)\|\s*Useful:\s*([^|]+)(?:\|\s*Notes:\s*(.+))?'
    
    sessions = []
    for match in re.finditer(pattern, content):
        date, task, read, useful, notes = match.groups()
        
        sessions.append({
            'date': date.strip(),
            'task': task.strip(),
            'read': [x.strip() for x in read.split(',') if x.strip()],
            'useful': [x.strip() for x in useful.split(',') if x.strip()],
            'notes': notes.strip() if notes else ''
        })
    
    return sessions


def analyze_sessions(sessions):
    """Analyze session data and calculate metrics."""
    
    total_sessions = len(sessions)
    
    if total_sessions == 0:
        return {
            'error': 'No sessions found in usage log',
            'total_sessions': 0
        }
    
    # Count reads and usefulness
    read_counts = defaultdict(int)
    useful_counts = defaultdict(int)
    
    for session in sessions:
        for item in session['read']:
            if item != 'N':
                read_counts[item] += 1
        
        for item in session['useful']:
            if item != 'N':
                useful_counts[item] += 1
    
    # Calculate metrics
    changelog_read = sum(1 for s in sessions if any('C' in r for r in s['read']))
    devlog_read = sum(1 for s in sessions if any('D' in r for r in s['read']))
    adr_read = sum(1 for s in sessions if any('A' in r for r in s['read']))
    none_read = sum(1 for s in sessions if 'N' in s['read'])
    
    changelog_useful = sum(1 for s in sessions if any('C' in u for u in s['useful']))
    devlog_useful = sum(1 for s in sessions if any('D' in u for u in s['useful']))
    adr_useful = sum(1 for s in sessions if any('A' in u for u in s['useful']))
    
    # Calculate usefulness ratios
    changelog_ratio = (changelog_useful / changelog_read * 100) if changelog_read > 0 else 0
    devlog_ratio = (devlog_useful / devlog_read * 100) if devlog_read > 0 else 0
    adr_ratio = (adr_useful / adr_read * 100) if adr_read > 0 else 0
    
    # Token efficiency (tokens per useful session)
    changelog_tokens = 8000
    devlog_tokens = 21000
    adr_tokens = 2000  # Average per ADR
    
    changelog_efficiency = changelog_tokens / changelog_useful if changelog_useful > 0 else float('inf')
    devlog_efficiency = devlog_tokens / devlog_useful if devlog_useful > 0 else float('inf')
    adr_efficiency = adr_tokens / adr_useful if adr_useful > 0 else float('inf')
    
    return {
        'total_sessions': total_sessions,
        'usage_frequency': {
            'changelog': {'count': changelog_read, 'percent': changelog_read / total_sessions * 100},
            'devlog': {'count': devlog_read, 'percent': devlog_read / total_sessions * 100},
            'adr': {'count': adr_read, 'percent': adr_read / total_sessions * 100},
            'none': {'count': none_read, 'percent': none_read / total_sessions * 100}
        },
        'usefulness_ratio': {
            'changelog': {'useful': changelog_useful, 'read': changelog_read, 'ratio': changelog_ratio},
            'devlog': {'useful': devlog_useful, 'read': devlog_read, 'ratio': devlog_ratio},
            'adr': {'useful': adr_useful, 'read': adr_read, 'ratio': adr_ratio}
        },
        'token_efficiency': {
            'changelog': {'tokens': changelog_tokens, 'useful_sessions': changelog_useful, 'tokens_per_useful': changelog_efficiency},
            'devlog': {'tokens': devlog_tokens, 'useful_sessions': devlog_useful, 'tokens_per_useful': devlog_efficiency},
            'adr': {'tokens': adr_tokens, 'useful_sessions': adr_useful, 'tokens_per_useful': adr_efficiency}
        },
        'sessions': sessions
    }


def print_report(analysis, detailed=False):
    """Print human-readable analysis report."""
    
    if 'error' in analysis:
        print(f"\n[!] {analysis['error']}")
        return
    
    total = analysis['total_sessions']
    
    print("\n" + "="*70)
    print("AI USAGE LOG ANALYSIS")
    print("="*70)
    
    print(f"\nTotal Sessions Analyzed: {total}")
    
    print("\n" + "-"*70)
    print("USAGE FREQUENCY")
    print("-"*70)
    
    for file_type, data in analysis['usage_frequency'].items():
        count = data['count']
        percent = data['percent']
        bar = "█" * int(percent / 2)
        print(f"{file_type.upper():12} {count:3}/{total:3} ({percent:5.1f}%) {bar}")
    
    print("\n" + "-"*70)
    print("USEFULNESS RATIO (When Read, How Often Useful?)")
    print("-"*70)
    
    for file_type, data in analysis['usefulness_ratio'].items():
        useful = data['useful']
        read = data['read']
        ratio = data['ratio']
        
        if read > 0:
            bar = "█" * int(ratio / 2)
            print(f"{file_type.upper():12} {useful:3}/{read:3} useful ({ratio:5.1f}%) {bar}")
        else:
            print(f"{file_type.upper():12} Not read in any session")
    
    print("\n" + "-"*70)
    print("TOKEN EFFICIENCY (Tokens per Useful Session)")
    print("-"*70)
    
    for file_type, data in analysis['token_efficiency'].items():
        tokens = data['tokens']
        useful = data['useful_sessions']
        efficiency = data['tokens_per_useful']
        
        if useful > 0:
            print(f"{file_type.upper():12} {tokens:6,} tokens / {useful:2} useful = {efficiency:8,.0f} tokens/session")
        else:
            print(f"{file_type.upper():12} {tokens:6,} tokens / {useful:2} useful = N/A (never useful)")
    
    print("\n" + "-"*70)
    print("RECOMMENDATIONS")
    print("-"*70)
    
    # Generate recommendations
    changelog_freq = analysis['usage_frequency']['changelog']['percent']
    changelog_ratio = analysis['usefulness_ratio']['changelog']['ratio']
    devlog_freq = analysis['usage_frequency']['devlog']['percent']
    devlog_ratio = analysis['usefulness_ratio']['devlog']['ratio']
    
    if changelog_freq < 20:
        print("• CHANGELOG read in <20% of sessions -> Consider aggressive archival")
    
    if changelog_ratio < 50 and analysis['usefulness_ratio']['changelog']['read'] > 0:
        print("• CHANGELOG useful <50% when read -> Consider minimizing format")
    
    if devlog_freq > 80:
        print("• DEVLOG read in >80% of sessions -> High value, maintain current format")
    
    if devlog_ratio > 80:
        print("• DEVLOG useful >80% when read -> Excellent signal-to-noise ratio")
    
    changelog_eff = analysis['token_efficiency']['changelog']['tokens_per_useful']
    devlog_eff = analysis['token_efficiency']['devlog']['tokens_per_useful']
    
    if changelog_eff > devlog_eff * 2:
        print(f"• CHANGELOG is {changelog_eff/devlog_eff:.1f}x less efficient than DEVLOG -> Reduce CHANGELOG tokens")
    
    if detailed:
        print("\n" + "-"*70)
        print("SESSION DETAILS")
        print("-"*70)
        
        for i, session in enumerate(analysis['sessions'], 1):
            print(f"\n{i}. {session['date']} - {session['task']}")
            print(f"   Read: {', '.join(session['read'])}")
            print(f"   Useful: {', '.join(session['useful'])}")
            if session['notes']:
                print(f"   Notes: {session['notes']}")
    
    print("\n" + "="*70)


def main():
    """Main entry point."""
    
    # Parse command line args
    output_json = '--json' in sys.argv
    detailed = '--detailed' in sys.argv
    
    # Find usage log
    log_path = Path('logs/ai-usage-log.md')
    
    # Parse and analyze
    sessions = parse_usage_log(log_path)
    analysis = analyze_sessions(sessions)
    
    # Output results
    if output_json:
        print(json.dumps(analysis, indent=2))
    else:
        print_report(analysis, detailed=detailed)


if __name__ == '__main__':
    main()

