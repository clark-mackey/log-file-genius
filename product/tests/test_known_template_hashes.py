"""Tests for the SHA-256 template manifest (Spec 4 §3).

Pins three things so the manifest can't silently rot:
  1. The committed manifest has an entry for the current VERSION.json version.
  2. Every file under product/templates/ at HEAD matches its recorded hash
     (i.e. `update_template_hashes.py --check` passes).
  3. A deliberately-wrong hash makes the check fail — proving the gate works.

update_template_hashes.py is loaded via importlib from its file path
(the .py name is fine, but match the codebase pattern for script modules).
"""

import importlib.util
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
_MANIFEST = _SCRIPTS / "known_template_hashes.json"

_SPEC = importlib.util.spec_from_file_location(
    "update_template_hashes", _SCRIPTS / "update_template_hashes.py"
)
uth = importlib.util.module_from_spec(_SPEC)
sys.modules["update_template_hashes"] = uth
_SPEC.loader.exec_module(uth)


def _current_version() -> str:
    return uth.read_current_version()


def test_manifest_file_exists():
    assert _MANIFEST.exists(), "known_template_hashes.json must be committed"


def test_manifest_has_entry_for_current_version():
    manifest = uth.load_manifest()
    version = _current_version()
    assert version in manifest, f"manifest missing entry for version {version!r}"
    assert manifest[version], "current-version entry must not be empty"


def test_every_template_file_has_matching_hash():
    """Every file under product/templates/ at HEAD matches the manifest."""
    on_disk = uth.hash_templates()
    recorded = uth.load_manifest()[_current_version()]

    assert set(on_disk) == set(recorded), (
        "template files on disk differ from the manifest's recorded set"
    )
    for name, digest in on_disk.items():
        assert recorded[name] == digest, f"hash mismatch for {name}"


def test_check_mode_passes_at_head():
    """`--check` returns 0 when the manifest matches the working tree."""
    assert uth.check_manifest() == 0


def test_check_mode_fails_on_wrong_hash(monkeypatch):
    """A deliberately-corrupted manifest makes the check fail (gate works)."""
    version = _current_version()
    good = uth.load_manifest()
    tampered = {version: dict(good[version])}
    # Flip one recorded hash to a clearly-wrong value.
    first_key = next(iter(tampered[version]))
    tampered[version][first_key] = "0" * 64

    monkeypatch.setattr(uth, "load_manifest", lambda *a, **k: tampered)
    assert uth.check_manifest() == 1


def test_check_mode_fails_when_version_absent(monkeypatch):
    """No entry for the current version is also a failure."""
    monkeypatch.setattr(uth, "load_manifest", lambda *a, **k: {})
    assert uth.check_manifest() == 1


def test_hashes_are_lowercase_sha256_hex():
    """Recorded digests are 64-char lowercase hex (defends the format)."""
    recorded = uth.load_manifest()[_current_version()]
    for name, digest in recorded.items():
        assert len(digest) == 64, f"{name}: not a 64-char digest"
        int(digest, 16)  # raises ValueError if not hex
        assert digest == digest.lower(), f"{name}: digest must be lowercase"


def test_manifest_keys_use_forward_slashes():
    """Keys are POSIX-style so the manifest is identical cross-platform."""
    recorded = uth.load_manifest()[_current_version()]
    for name in recorded:
        assert "\\" not in name, f"{name}: backslash in manifest key"
