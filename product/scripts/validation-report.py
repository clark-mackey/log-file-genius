#!/usr/bin/env python3
"""
Log File Genius - Validation Report Generator

Generates comprehensive validation reports with health scores,
token budget status, and trends over time.

Usage:
    python validation-report.py                # Generate report
    python validation-report.py --html         # Generate HTML report
    python validation-report.py --json         # Output as JSON
    python validation-report.py --history      # Include historical trends

Exit codes:
    0 - Report generated successfully
    1 - Warnings in validation
    2 - Errors in validation
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class ValidationReporter:
    """Generate validation reports with health scores and trends"""
    
    def __init__(self, config_path: str = ".logfile-config.yml"):
        self.config_path = config_path
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'health_score': 0,
            'token_status': {},
            'validation_results': {},
            'trends': {},
            'recommendations': []
        }
    
    def run_validation(self) -> Dict:
        """Run lint-logs.py and capture results"""
        try:
            result = subprocess.run(
                [sys.executable, 'product/scripts/lint-logs.py', '--json'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return {'results': []}
        except Exception as e:
            print(f"Error running validation: {e}", file=sys.stderr)
            return {'results': []}
    
    def calculate_health_score(self, validation_results: Dict) -> int:
        """Calculate overall health score (0-100)"""
        total_errors = sum(r['errors'] for r in validation_results.get('results', []))
        total_warnings = sum(r['warnings'] for r in validation_results.get('results', []))
        
        # Start at 100, deduct points for issues
        score = 100
        score -= total_errors * 20  # Each error costs 20 points
        score -= total_warnings * 5  # Each warning costs 5 points
        
        return max(0, min(100, score))  # Clamp to 0-100
    
    def get_token_status(self, validation_results: Dict) -> Dict:
        """Extract token budget status from validation results"""
        status = {
            'changelog': {'current': 0, 'target': 10000, 'percentage': 0},
            'devlog': {'current': 0, 'target': 15000, 'percentage': 0},
            'combined': {'current': 0, 'target': 25000, 'percentage': 0}
        }
        
        for result in validation_results.get('results', []):
            for issue in result.get('issues', []):
                msg = issue.get('message', '')
                
                # Parse token count messages
                if 'CHANGELOG' in result['file'] and 'token' in msg.lower():
                    if '(' in msg and '/' in msg:
                        parts = msg.split('(')[1].split(')')[0].split('/')
                        if len(parts) == 2:
                            current = int(parts[0].strip().replace(',', ''))
                            target = int(parts[1].strip().replace(',', ''))
                            status['changelog'] = {
                                'current': current,
                                'target': target,
                                'percentage': round((current / target) * 100, 1)
                            }
                
                elif 'DEVLOG' in result['file'] and 'token' in msg.lower():
                    if '(' in msg and '/' in msg:
                        parts = msg.split('(')[1].split(')')[0].split('/')
                        if len(parts) == 2:
                            current = int(parts[0].strip().replace(',', ''))
                            target = int(parts[1].strip().replace(',', ''))
                            status['devlog'] = {
                                'current': current,
                                'target': target,
                                'percentage': round((current / target) * 100, 1)
                            }
                
                elif 'Combined' in result['file'] and 'token' in msg.lower():
                    if '(' in msg and '/' in msg:
                        parts = msg.split('(')[1].split(')')[0].split('/')
                        if len(parts) == 2:
                            current = int(parts[0].strip().replace(',', ''))
                            target = int(parts[1].strip().replace(',', ''))
                            status['combined'] = {
                                'current': current,
                                'target': target,
                                'percentage': round((current / target) * 100, 1)
                            }
        
        return status
    
    def generate_recommendations(self, validation_results: Dict, token_status: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for errors
        total_errors = sum(r['errors'] for r in validation_results.get('results', []))
        if total_errors > 0:
            recommendations.append(f"🔴 Fix {total_errors} validation error(s) immediately")
        
        # Check token budgets
        if token_status['combined']['percentage'] > 80:
            recommendations.append("📦 Archive old log entries - approaching token limit")
        
        if token_status['changelog']['percentage'] > 80:
            recommendations.append("📝 Archive CHANGELOG entries older than 2 weeks")
        
        if token_status['devlog']['percentage'] > 80:
            recommendations.append("📖 Archive DEVLOG entries older than 2 weeks")
        
        # Check for warnings
        total_warnings = sum(r['warnings'] for r in validation_results.get('results', []))
        if total_warnings > 5:
            recommendations.append(f"⚠️ Address {total_warnings} validation warnings")
        
        # Check for missing files
        for result in validation_results.get('results', []):
            for issue in result.get('issues', []):
                if 'not found' in issue.get('message', ''):
                    recommendations.append("📁 Run installer to create missing log files")
                    break
        
        if not recommendations:
            recommendations.append("✅ All systems healthy - keep up the good work!")
        
        return recommendations
    
    def generate_report(self, include_history: bool = False) -> Dict:
        """Generate complete validation report"""
        # Run validation
        validation_results = self.run_validation()
        
        # Calculate metrics
        health_score = self.calculate_health_score(validation_results)
        token_status = self.get_token_status(validation_results)
        recommendations = self.generate_recommendations(validation_results, token_status)
        
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'token_status': token_status,
            'validation_results': validation_results,
            'recommendations': recommendations
        }
        
        return self.report_data
    
    def format_markdown(self, report: Dict) -> str:
        """Format report as Markdown"""
        lines = []
        
        # Header
        lines.append("# Log File Genius - Validation Report")
        lines.append(f"\n**Generated:** {datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Health Score:** {report['health_score']}/100")
        
        # Health indicator
        if report['health_score'] >= 90:
            lines.append("🟢 Excellent")
        elif report['health_score'] >= 70:
            lines.append("🟡 Good")
        elif report['health_score'] >= 50:
            lines.append("🟠 Needs Attention")
        else:
            lines.append("🔴 Critical")
        
        # Token Status
        lines.append("\n## Token Budget Status\n")
        for name, status in report['token_status'].items():
            percentage = status['percentage']
            bar = self._create_progress_bar(percentage)
            lines.append(f"**{name.upper()}:** {status['current']:,} / {status['target']:,} tokens ({percentage}%)")
            lines.append(f"{bar}\n")
        
        # Recommendations
        lines.append("\n## Recommendations\n")
        for rec in report['recommendations']:
            lines.append(f"- {rec}")
        
        # Validation Details
        lines.append("\n## Validation Details\n")
        for result in report['validation_results'].get('results', []):
            lines.append(f"\n### {result['file']}\n")
            if not result['issues']:
                lines.append("✅ No issues\n")
            else:
                for issue in result['issues']:
                    icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[issue['severity']]
                    line_info = f" (line {issue['line']})" if issue['line'] else ''
                    lines.append(f"{icon} {issue['message']}{line_info}")
                    if issue['suggestion']:
                        lines.append(f"   → {issue['suggestion']}")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Create a text-based progress bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage >= 90:
            color = '🔴'
        elif percentage >= 80:
            color = '🟠'
        elif percentage >= 60:
            color = '🟡'
        else:
            color = '🟢'
        
        return f"{color} [{'█' * filled}{'░' * empty}]"
    
    def format_html(self, report: Dict) -> str:
        """Format report as HTML"""
        # Convert markdown to basic HTML
        md = self.format_markdown(report)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Log File Genius - Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .health-score {{ font-size: 48px; font-weight: bold; }}
        .excellent {{ color: #27ae60; }}
        .good {{ color: #f39c12; }}
        .needs-attention {{ color: #e67e22; }}
        .critical {{ color: #e74c3c; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <pre>{md}</pre>
</body>
</html>"""
        return html


def main():
    parser = argparse.ArgumentParser(description="Generate Log File Genius validation report")
    parser.add_argument('--html', action='store_true', help="Generate HTML report")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--history', action='store_true', help="Include historical trends")
    parser.add_argument('--output', help="Output file path")
    
    args = parser.parse_args()
    
    reporter = ValidationReporter()
    report = reporter.generate_report(include_history=args.history)
    
    # Format output
    if args.json:
        output = json.dumps(report, indent=2)
    elif args.html:
        output = reporter.format_html(report)
    else:
        output = reporter.format_markdown(report)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)
    
    # Exit code based on health score
    if report['health_score'] < 50:
        sys.exit(2)
    elif report['health_score'] < 90:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

