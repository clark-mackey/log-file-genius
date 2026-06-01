"""Tests for `lfg validate --state-only` (Spec 4, T8).

The state-only mode lets callers (e.g. update.{sh,ps1}) detect a
STATE-specific validation failure without false-positiving on unrelated
CHANGELOG/DEVLOG issues. It exits non-zero (2) iff STATE.md has ERRORS;
budget warnings stay exit 0 (matching lint-logs' errors-only convention).
"""
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"

# A STATE.md is "clean" when it has the v0.3.0 `## Current Context` section
# and is within budget.
CLEAN_STATE = "# Current State\n\n## Current Context\n\n- Version: v1\n"
# Missing `## Current Context` is the STATE validation ERROR.
BROKEN_STATE = "# Current State\n\n## Some Other Heading\n\n- nothing useful\n"


def _run(args, cwd, stdin=""):
    return subprocess.run(
        [sys.executable, str(LFG)] + args,
        cwd=str(cwd), input=stdin, capture_output=True, text=True, encoding="utf-8",
    )


def _write_config(tmp_path):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
          state: logs/STATE.md
        token_targets:
          changelog: 10000
          devlog: 15000
          combined: 25000
          state: 500
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir()


def _write_clean_changelog_devlog(tmp_path):
    (tmp_path / "logs" / "CHANGELOG.md").write_text(
        "# Changelog\n\nhttps://keepachangelog.com/\n\n## [Unreleased]\n"
        "- Added thing. Files: `src/a.py`. Commit: `abc1234`\n",
        encoding="utf-8",
    )
    (tmp_path / "logs" / "DEVLOG.md").write_text(
        "# Development Log\n\n## Daily Log\n\n### 2026-05-28: x\n- y\n", encoding="utf-8")


def test_state_only_broken_state_exits_nonzero(tmp_path):
    """STATE.md with a known error (no Current Context) -> exit 2."""
    _write_config(tmp_path)
    _write_clean_changelog_devlog(tmp_path)
    (tmp_path / "logs" / "STATE.md").write_text(BROKEN_STATE, encoding="utf-8")
    r = _run(["validate", "--state-only"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "Current Context" in r.stdout


def test_state_only_clean_state_exits_zero(tmp_path):
    """A clean STATE.md -> exit 0."""
    _write_config(tmp_path)
    _write_clean_changelog_devlog(tmp_path)
    (tmp_path / "logs" / "STATE.md").write_text(CLEAN_STATE, encoding="utf-8")
    r = _run(["validate", "--state-only"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_state_only_ignores_broken_changelog(tmp_path):
    """Broken CHANGELOG + clean STATE -> state-only still exits 0.

    This is the whole point: the advisory must not fire on unrelated
    CHANGELOG/DEVLOG problems.
    """
    _write_config(tmp_path)
    # Broken CHANGELOG: missing the required ## [Unreleased] section (an ERROR
    # in full validation). Empty DEVLOG (missing Daily Log -> warning).
    (tmp_path / "logs" / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [0.1.0] - 2026-01-01\n- no unreleased section\n", encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text("# Development Log\n", encoding="utf-8")
    (tmp_path / "logs" / "STATE.md").write_text(CLEAN_STATE, encoding="utf-8")

    # Sanity: the full run DOES fail (proves the CHANGELOG is genuinely broken).
    full = _run(["validate"], cwd=tmp_path)
    assert full.returncode == 2, full.stdout + full.stderr

    # State-only ignores the CHANGELOG error.
    r = _run(["validate", "--state-only"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_full_validate_unchanged_when_state_broken(tmp_path):
    """The existing full `lfg validate` still surfaces a broken STATE as an error."""
    _write_config(tmp_path)
    _write_clean_changelog_devlog(tmp_path)
    (tmp_path / "logs" / "STATE.md").write_text(BROKEN_STATE, encoding="utf-8")
    r = _run(["validate"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "Current Context" in r.stdout
