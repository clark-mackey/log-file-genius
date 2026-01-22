#!/usr/bin/env python3
"""
Log File Genius - Version Manifest Checker

Validates that all components are version-synchronized and checksums match.
Detects version drift between scripts, validators, AI rules, and templates.

Usage:
    python check-version.py              # Check version sync
    python check-version.py --update     # Update checksums in VERSION.json
    python check-version.py --json       # Output as JSON

Exit codes:
    0 - All versions synchronized
    1 - Version mismatch detected
    2 - Checksum mismatch detected
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_script_dir() -> Path:
    """Get the directory containing this script"""
    return Path(__file__).parent.resolve()


def get_product_dir() -> Path:
    """Get the product directory (parent of scripts)"""
    return get_script_dir().parent


def load_version_manifest() -> Dict:
    """Load VERSION.json from product directory"""
    version_file = get_product_dir() / "VERSION.json"
    if not version_file.exists():
        print(f"ERROR: VERSION.json not found at {version_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(version_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_version_manifest(manifest: Dict):
    """Save VERSION.json to product directory"""
    version_file = get_product_dir() / "VERSION.json"
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')


def compute_file_checksum(file_path: Path) -> Optional[str]:
    """Compute SHA256 checksum of a file"""
    if not file_path.exists():
        return None
    
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # First 16 chars for brevity


def check_version_sync(manifest: Dict) -> List[str]:
    """Check that all component versions match the main version"""
    issues = []
    main_version = manifest.get('version', 'unknown')
    components = manifest.get('components', {})
    
    for component, version in components.items():
        if version != main_version:
            issues.append(f"Version drift: {component} is {version}, expected {main_version}")
    
    return issues


def check_checksums(manifest: Dict, update: bool = False) -> Tuple[List[str], bool]:
    """Check file checksums match manifest, optionally update them"""
    issues = []
    updated = False
    scripts_dir = get_script_dir()
    checksums = manifest.get('checksums', {})
    
    for filename, expected_checksum in checksums.items():
        file_path = scripts_dir / filename
        actual_checksum = compute_file_checksum(file_path)
        
        if actual_checksum is None:
            issues.append(f"Missing file: {filename}")
        elif expected_checksum is None:
            if update:
                checksums[filename] = actual_checksum
                updated = True
            else:
                issues.append(f"No checksum recorded for: {filename}")
        elif actual_checksum != expected_checksum:
            if update:
                checksums[filename] = actual_checksum
                updated = True
            else:
                issues.append(f"Checksum mismatch: {filename} (file changed without version bump?)")
    
    return issues, updated


def print_results(manifest: Dict, version_issues: List[str], checksum_issues: List[str], 
                  json_output: bool = False):
    """Print version check results"""
    if json_output:
        output = {
            'version': manifest.get('version'),
            'components': manifest.get('components'),
            'version_sync': len(version_issues) == 0,
            'checksum_valid': len(checksum_issues) == 0,
            'version_issues': version_issues,
            'checksum_issues': checksum_issues
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print("\n" + "="*60)
    print("Log File Genius - Version Manifest Check")
    print("="*60)
    print(f"\nMain Version: {manifest.get('version')}")
    print(f"Release Date: {manifest.get('release_date')}")
    
    print("\nComponents:")
    for component, version in manifest.get('components', {}).items():
        status = "[OK]" if version == manifest.get('version') else "[X]"
        print(f"  {status} {component}: {version}")
    
    if version_issues:
        print("\nVersion Issues:")
        for issue in version_issues:
            print(f"  [X] {issue}")
    
    if checksum_issues:
        print("\nChecksum Issues:")
        for issue in checksum_issues:
            print(f"  [!] {issue}")
    
    print("\n" + "="*60)
    if not version_issues and not checksum_issues:
        print("[OK] All versions synchronized, checksums valid")
    else:
        total = len(version_issues) + len(checksum_issues)
        print(f"[X] {total} issue(s) found")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Check Log File Genius version synchronization")
    parser.add_argument('--update', action='store_true', help="Update checksums in VERSION.json")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    
    args = parser.parse_args()
    
    manifest = load_version_manifest()
    
    # Check version synchronization
    version_issues = check_version_sync(manifest)
    
    # Check checksums
    checksum_issues, updated = check_checksums(manifest, update=args.update)
    
    if updated:
        save_version_manifest(manifest)
        if not args.json:
            print("Updated checksums in VERSION.json")
    
    print_results(manifest, version_issues, checksum_issues, json_output=args.json)
    
    # Exit codes
    if version_issues:
        sys.exit(1)
    elif checksum_issues and not args.update:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

