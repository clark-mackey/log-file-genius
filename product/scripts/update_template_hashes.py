#!/usr/bin/env python3
"""Build / verify the SHA-256 manifest of LFG-shipped templates.

Spec 4 §3. The manifest (`known_template_hashes.json`) is the source of
truth `update.{sh,ps1}` will use (in a LATER task, T7) to tell a user's
LFG-installed root `templates/` files apart from their own hand-authored
ones, so cleanup only ever moves files LFG actually shipped.

Shape of the JSON — a top-level object keyed by LFG version, each value a
map of forward-slash relative filename to lowercase SHA-256 hex digest::

    {
      "0.3.0": {
        "ADR_template.md": "<sha256hex>",
        "CHANGELOG_template.md": "<sha256hex>",
        ...
      },
      "0.4.0": { ... }
    }

The manifest accumulates entries across versions: regenerating for a new
version MERGES the new entry in and preserves all prior-version entries.

Usage:
    python update_template_hashes.py            # write/update for current version
    python update_template_hashes.py --check    # CI gate: exit non-zero on drift
    python update_template_hashes.py --match-dir <dir>  # report LFG-shipped files in <dir>

Stdlib only; Python 3.11+.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# product/scripts/update_template_hashes.py -> product/
_PRODUCT_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATES_DIR = _PRODUCT_ROOT / "templates"
_VERSION_FILE = _PRODUCT_ROOT / "VERSION.json"
_MANIFEST_FILE = _PRODUCT_ROOT / "scripts" / "known_template_hashes.json"

_CHUNK = 65536


def read_current_version(version_file: Path = _VERSION_FILE) -> str:
    """Return the top-level ``version`` string from VERSION.json."""
    try:
        data = json.loads(version_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"VERSION.json not found at {version_file}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"VERSION.json is not valid JSON: {exc}") from exc

    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"VERSION.json has no usable 'version' string: {version!r}")
    return version.strip()


def sha256_of_file(path: Path) -> str:
    """Return the lowercase hex SHA-256 of a file's raw bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_templates(templates_dir: Path = _TEMPLATES_DIR) -> dict[str, str]:
    """Hash every file under ``templates_dir``.

    Keys are POSIX-style (forward-slash) paths relative to the templates
    directory, so the manifest is byte-identical on Windows and Linux.
    """
    if not templates_dir.is_dir():
        raise FileNotFoundError(f"templates directory not found: {templates_dir}")

    hashes: dict[str, str] = {}
    for path in sorted(templates_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(templates_dir).as_posix()
        hashes[rel] = sha256_of_file(path)

    if not hashes:
        raise FileNotFoundError(f"no template files found under {templates_dir}")
    return hashes


def load_manifest(manifest_file: Path = _MANIFEST_FILE) -> dict[str, dict[str, str]]:
    """Load the existing manifest, or return an empty mapping if absent."""
    if not manifest_file.exists():
        return {}
    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest top-level value must be an object keyed by version")
    return data


def write_manifest(
    manifest: dict[str, dict[str, str]], manifest_file: Path = _MANIFEST_FILE
) -> None:
    """Write the manifest as sorted, newline-terminated UTF-8 JSON (LF)."""
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    with manifest_file.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def update_manifest() -> tuple[str, int]:
    """Merge the current version's template hashes into the manifest.

    Preserves all prior-version entries. Returns ``(version, file_count)``.
    """
    version = read_current_version()
    current = hash_templates()
    manifest = load_manifest()
    manifest[version] = current
    write_manifest(manifest)
    return version, len(current)


def check_manifest() -> int:
    """CI gate: verify the on-disk templates match the current-version entry.

    Returns 0 on match, 1 on any drift (missing entry, missing/extra files,
    or changed hashes). Prints a human-readable diff to stderr on failure.
    """
    version = read_current_version()
    on_disk = hash_templates()
    manifest = load_manifest()

    recorded = manifest.get(version)
    if recorded is None:
        print(
            f"manifest has no entry for current version {version!r}; "
            f"run: python {Path(__file__).name}",
            file=sys.stderr,
        )
        return 1

    if recorded == on_disk:
        return 0

    on_disk_keys = set(on_disk)
    recorded_keys = set(recorded)
    for missing in sorted(recorded_keys - on_disk_keys):
        print(f"  in manifest but missing on disk: {missing}", file=sys.stderr)
    for extra in sorted(on_disk_keys - recorded_keys):
        print(f"  on disk but missing from manifest: {extra}", file=sys.stderr)
    for name in sorted(on_disk_keys & recorded_keys):
        if on_disk[name] != recorded[name]:
            print(f"  hash mismatch: {name}", file=sys.stderr)

    print(
        f"template hashes for {version!r} are out of date; "
        f"regenerate with: python {Path(__file__).name}",
        file=sys.stderr,
    )
    return 1


def known_hashes(manifest: dict[str, dict[str, str]]) -> set[str]:
    """Flatten the manifest into the set of every hash any version shipped.

    A file in a project's root ``templates/`` counts as LFG-installed if its
    SHA-256 matches a template LFG shipped in ANY version — so we union all
    per-version digests rather than keying on filename or version.
    """
    digests: set[str] = set()
    for version_entry in manifest.values():
        if isinstance(version_entry, dict):
            digests.update(version_entry.values())
    return digests


def match_dir(target_dir: Path, manifest_file: Path = _MANIFEST_FILE) -> int:
    """Report which files under ``target_dir`` match any LFG-shipped hash.

    Hashes every file under ``target_dir`` (recursively) and compares each
    digest against the union of all hashes in the manifest. Prints one line
    per matching file (``MATCH <relpath>``) to stdout, then a summary line
    (``matched N of M file(s)``).

    Exit codes (so a shell caller can branch without parsing text):
      0 — at least one file matched (the dir holds LFG-installed templates).
      1 — the directory has files but NONE matched (user-authored).
      2 — error (dir missing / not a dir / manifest unreadable / dir empty).
    """
    if not target_dir.is_dir():
        print(f"not a directory: {target_dir}", file=sys.stderr)
        return 2

    try:
        manifest = load_manifest(manifest_file)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    shipped = known_hashes(manifest)

    files = sorted(p for p in target_dir.rglob("*") if p.is_file())
    if not files:
        print(f"no files under {target_dir}", file=sys.stderr)
        return 2

    matched = 0
    for path in files:
        rel = path.relative_to(target_dir).as_posix()
        if sha256_of_file(path) in shipped:
            print(f"MATCH {rel}")
            matched += 1

    print(f"matched {matched} of {len(files)} file(s)")
    return 0 if matched > 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the manifest matches on-disk templates; exit non-zero on drift",
    )
    parser.add_argument(
        "--match-dir",
        metavar="DIR",
        help="report which files in DIR match any LFG-shipped template hash",
    )
    args = parser.parse_args(argv)

    if args.match_dir:
        return match_dir(Path(args.match_dir))

    if args.check:
        return check_manifest()

    version, count = update_manifest()
    print(f"wrote {count} template hash(es) for version {version} to {_MANIFEST_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
