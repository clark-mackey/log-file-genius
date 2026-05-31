"""Tests for the version comparator in check-version.py.

Pins the direction of the validators' "update available" message so the
backwards-comparison bug (Spec 4 §4 / issue #2) can't regress.

check-version.py is not importable by name (hyphen), so load it via
importlib from its file path.
"""

import importlib.util
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location(
    "check_version", _SCRIPTS / "check-version.py"
)
check_version = importlib.util.module_from_spec(_SPEC)
sys.modules["check_version"] = check_version
_SPEC.loader.exec_module(check_version)

compare_versions = check_version.compare_versions
parse_version = check_version.parse_version


# --- Direction pinning ------------------------------------------------------
# Convention used by the validators: compare_versions(installed, latest).
#   > 0  → installed is AHEAD of latest (NOT "update available")
#   < 0  → installed is BEHIND latest  ("update available")
#   == 0 → current / up to date


def message_for(installed: str, latest: str) -> str:
    """Mirror the validator's branching to assert on user-facing wording."""
    result = compare_versions(installed, latest)
    if result < 0:
        return f"update available: v{latest} (you have v{installed})"
    if result > 0:
        return f"you are on v{installed}, newer than the latest-known v{latest}"
    return "current"


def test_ahead_is_not_update_available():
    # The original bug: installed 0.3.0, latest-known 0.2.0.
    assert compare_versions("0.3.0", "0.2.0") > 0
    msg = message_for("0.3.0", "0.2.0")
    assert "update available" not in msg
    assert "newer" in msg


def test_behind_is_update_available():
    assert compare_versions("0.2.0", "0.3.0") < 0
    msg = message_for("0.2.0", "0.3.0")
    assert msg == "update available: v0.3.0 (you have v0.2.0)"


def test_equal_is_current():
    assert compare_versions("0.3.0", "0.3.0") == 0
    assert message_for("0.3.0", "0.3.0") == "current"


def test_minor_and_patch_precedence():
    assert compare_versions("0.4.0", "0.3.9") > 0
    assert compare_versions("1.0.0", "0.99.99") > 0
    assert compare_versions("1.2.3", "1.2.4") < 0
    assert compare_versions("1.3.0", "1.2.9") > 0


# --- Pre-release suffix -----------------------------------------------------
# Per semver: a pre-release sorts BEFORE its associated release.


def test_prerelease_sorts_before_release():
    assert compare_versions("1.2.3-rc.1", "1.2.3") < 0
    assert compare_versions("1.2.3", "1.2.3-rc.1") > 0


def test_prerelease_ordering():
    # alpha < beta < rc (lexical), and rc.1 < rc.2 (numeric identifier).
    assert compare_versions("1.0.0-alpha", "1.0.0-beta") < 0
    assert compare_versions("1.0.0-rc.1", "1.0.0-rc.2") < 0
    assert compare_versions("1.0.0-rc.2", "1.0.0-rc.10") < 0  # numeric, not lexical
    # numeric identifiers have lower precedence than alphanumeric
    assert compare_versions("1.0.0-1", "1.0.0-alpha") < 0


def test_prerelease_against_lower_release_still_loses_to_higher_core():
    # 1.2.3-rc.1 is still less than 1.2.4 (core wins).
    assert compare_versions("1.2.3-rc.1", "1.2.4") < 0
    # but greater than 1.2.2.
    assert compare_versions("1.2.3-rc.1", "1.2.2") > 0


# --- Build metadata ---------------------------------------------------------
# Per semver: build metadata is ignored for precedence.


def test_build_metadata_ignored():
    assert compare_versions("1.2.3+local", "1.2.3") == 0
    assert compare_versions("1.2.3+local.abc123", "1.2.3+other.def") == 0
    assert compare_versions("1.2.3", "1.2.3+build.99") == 0


def test_build_metadata_does_not_change_direction():
    assert compare_versions("0.4.0+local", "0.3.0") > 0
    assert compare_versions("0.2.0+ci.5", "0.3.0") < 0


def test_prerelease_with_build_metadata():
    # build metadata stripped, pre-release still applies.
    assert compare_versions("1.2.3-rc.1+local.abc123", "1.2.3") < 0
    assert compare_versions("1.2.3-rc.1+a", "1.2.3-rc.1+b") == 0


# --- Tolerant parsing --------------------------------------------------------


def test_leading_v_tolerated():
    assert compare_versions("v0.4.0", "0.4.0") == 0
    assert compare_versions("v0.4.0", "v0.3.0") > 0


def test_missing_components_default_to_zero():
    assert compare_versions("1", "1.0.0") == 0
    assert compare_versions("1.2", "1.2.0") == 0
    assert compare_versions("1.2", "1.2.1") < 0


def test_parse_version_shape():
    core, pre = parse_version("1.2.3-rc.1+local")
    assert core == (1, 2, 3)
    assert pre == ("rc", 1)
    core2, pre2 = parse_version("0.3.0")
    assert core2 == (0, 3, 0)
    assert pre2 == ()
