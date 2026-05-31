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
from typing import Dict, List, Optional, Tuple, Union


# --- Semver-ish version comparison -----------------------------------------
#
# Used by the validators to decide whether an installed version is ahead of,
# behind, or equal to the latest-known version. Handles:
#   - normal X.Y.Z
#   - pre-release suffix (1.2.3-rc.1) — sorts BEFORE its release (1.2.3)
#   - build metadata (1.2.3+local.abc) — ignored for precedence
# Follows semver.org precedence rules (minus exotic edge cases we don't ship).

_VersionParts = Tuple[Tuple[int, int, int], Tuple[Union[int, str], ...]]


def parse_version(version: str) -> _VersionParts:
    """Parse a version string into ((major, minor, patch), prerelease_ids).

    Build metadata (everything after '+') is stripped and ignored.
    A missing pre-release is represented by an empty tuple, which always
    sorts *after* any non-empty pre-release (per semver precedence).
    A leading 'v' (e.g. "v0.4.0") is tolerated.
    Missing minor/patch components default to 0.
    """
    text = version.strip()
    if text.startswith("v") or text.startswith("V"):
        text = text[1:]

    # Build metadata does not affect precedence — discard it.
    text = text.split("+", 1)[0]

    # Split off the pre-release segment (first '-').
    core, _, prerelease = text.partition("-")

    nums = core.split(".")
    major = int(nums[0]) if len(nums) > 0 and nums[0].isdigit() else 0
    minor = int(nums[1]) if len(nums) > 1 and nums[1].isdigit() else 0
    patch = int(nums[2]) if len(nums) > 2 and nums[2].isdigit() else 0

    pre_ids: Tuple[Union[int, str], ...] = ()
    if prerelease:
        ids: List[Union[int, str]] = []
        for ident in prerelease.split("."):
            ids.append(int(ident) if ident.isdigit() else ident)
        pre_ids = tuple(ids)

    return (major, minor, patch), pre_ids


def _prerelease_key(pre_ids: Tuple[Union[int, str], ...]) -> tuple:
    """Sort key for the pre-release segment honoring semver rules.

    - No pre-release outranks any pre-release: (1,) > (0, ...).
    - Numeric identifiers compare numerically and rank below alphanumerics.
    """
    if not pre_ids:
        # Release version: sorts after any pre-release.
        return (1,)
    key: List[tuple] = []
    for ident in pre_ids:
        if isinstance(ident, int):
            key.append((0, ident, ""))
        else:
            key.append((1, 0, ident))
    return (0, tuple(key))


def compare_versions(a: str, b: str) -> int:
    """Compare two versions. Returns -1 if a < b, 0 if equal, 1 if a > b.

    Build metadata is ignored; pre-release versions sort before their
    associated release.
    """
    core_a, pre_a = parse_version(a)
    core_b, pre_b = parse_version(b)

    if core_a != core_b:
        return -1 if core_a < core_b else 1

    key_a = _prerelease_key(pre_a)
    key_b = _prerelease_key(pre_b)
    if key_a == key_b:
        return 0
    return -1 if key_a < key_b else 1


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
    parser.add_argument('--compare', nargs=2, metavar=('INSTALLED', 'LATEST'),
                        help="Compare two versions. Prints 'ahead', 'behind', or "
                             "'current' and exits 0.")

    args = parser.parse_args()

    # Lightweight version-comparison mode for the validators (no manifest needed).
    if args.compare:
        installed, latest = args.compare
        result = compare_versions(installed, latest)
        print("ahead" if result > 0 else "behind" if result < 0 else "current")
        sys.exit(0)

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

