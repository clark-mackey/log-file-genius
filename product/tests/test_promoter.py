import textwrap
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from promoter import promote, PromoteError


def _seed(tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "CHANGELOG.md").write_text(textwrap.dedent("""
        # Changelog
        ## [Unreleased]
        ### Added
        - Existing entry.
    """).lstrip(), encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(textwrap.dedent("""
        # Development Log

        ## Daily Log - Newest First

        ### 2026-01-01: prior entry
    """).lstrip(), encoding="utf-8")
    return tmp_path


def _stage(root, subagent_id, changelog=None, devlog=None):
    d = root / ".lfg" / "staged" / subagent_id
    d.mkdir(parents=True)
    if changelog is not None:
        (d / "changelog.md").write_text(changelog, encoding="utf-8")
    if devlog is not None:
        (d / "devlog.md").write_text(devlog, encoding="utf-8")
    return d


def test_promote_appends_changelog_and_clears_staged(tmp_path):
    root = _seed(tmp_path)
    staged = _stage(root, "sub42",
                    changelog="- New entry from subagent. Files: `x.py`. Commit: `pending`")
    promote(root, "sub42")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Existing entry" in cl
    assert "New entry from subagent" in cl
    assert not staged.exists()


def test_promote_appends_devlog(tmp_path):
    root = _seed(tmp_path)
    _stage(root, "sub42",
           devlog="### 2026-05-28: subagent did things\n\nDetails.")
    promote(root, "sub42")
    dl = (root / "logs" / "DEVLOG.md").read_text(encoding="utf-8")
    assert "subagent did things" in dl
    assert "prior entry" in dl  # original preserved


def test_promote_missing_staged_dir_is_noop(tmp_path):
    root = _seed(tmp_path)
    promote(root, "nonexistent")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Existing entry" in cl  # unchanged


def test_promote_writes_audit_trail(tmp_path):
    root = _seed(tmp_path)
    _stage(root, "sub42", changelog="- Entry.")
    promote(root, "sub42")
    audit = (root / ".lfg" / "promoted.log").read_text(encoding="utf-8")
    assert "sub42" in audit
    assert datetime.utcnow().strftime("%Y") in audit


def test_promote_routes_entries_to_their_declared_category(tmp_path):
    """Code-owl review finding #1: subagent staged entries that declare
    '### Fixed' must land under the canonical CHANGELOG's '### Fixed'
    subsection, not under whichever '###' is first."""
    root = _seed(tmp_path)
    cl_path = root / "logs" / "CHANGELOG.md"
    cl_path.write_text(
        "# Changelog\n## [Unreleased]\n### Added\n- Existing add.\n\n### Fixed\n- Existing fix.\n",
        encoding="utf-8",
    )
    _stage(root, "sub99", changelog="### Fixed\n- A new fix from subagent.\n")
    promote(root, "sub99")
    cl = cl_path.read_text(encoding="utf-8")
    fixed_block = cl[cl.index("### Fixed"):]
    added_block = cl[cl.index("### Added"):cl.index("### Fixed")]
    assert "A new fix from subagent" in fixed_block
    assert "A new fix from subagent" not in added_block


def test_promote_creates_new_category_when_missing(tmp_path):
    """If the canonical CHANGELOG doesn't have the staged category yet, promote
    adds a new '### <Category>' subsection at the end of [Unreleased]."""
    root = _seed(tmp_path)
    _stage(root, "sub88", changelog="### Security\n- Closed an auth gap.\n")
    promote(root, "sub88")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "### Security" in cl
    assert "Closed an auth gap" in cl


def test_promote_preserves_multiline_devlog_blocks(tmp_path):
    """Code-owl review finding #2: DEVLOG entries often span multiple
    paragraphs separated by blank lines — the promoter must not strip the
    interior blanks."""
    root = _seed(tmp_path)
    entry = (
        "### 2026-05-28: A standard-format entry\n"
        "\n"
        "**Situation:** Setup.\n"
        "\n"
        "**Decision:** Did the thing.\n"
    )
    _stage(root, "subml", devlog=entry)
    promote(root, "subml")
    dl = (root / "logs" / "DEVLOG.md").read_text(encoding="utf-8")
    assert "**Situation:**" in dl
    assert "**Decision:**" in dl
    sit = dl.index("**Situation:**")
    dec = dl.index("**Decision:**")
    assert "\n\n" in dl[sit:dec], "interior blank line between paragraphs was stripped"
