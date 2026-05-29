import textwrap
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive import (
    parse_changelog, parse_devlog, ArchivePlan, ArchiveAction, ArchiveError,
    _estimate_tokens, DEFAULT_KEEP_FRACTION, COMBINED_KEEP_FRACTION_FLOOR,
)


def test_constants_match_spec():
    assert DEFAULT_KEEP_FRACTION == 0.8
    assert COMBINED_KEEP_FRACTION_FLOOR == 0.3


def test_estimate_tokens_is_chars_div_4():
    assert _estimate_tokens("") == 0
    assert _estimate_tokens("a" * 8) == 2
    assert _estimate_tokens("a" * 100) == 25


def test_parse_changelog_separates_sections():
    text = textwrap.dedent("""\
        ---
        doc: CHANGELOG
        ---

        # Changelog

        ## [Unreleased]

        ### Added
        - In-flight work A.

        ## [0.2.0] - 2026-05-01

        ### Added
        - Spec 2 shipped.

        ## [0.1.0] - 2026-04-01

        ### Added
        - Spec 1 shipped.
    """)
    parsed = parse_changelog(text)
    assert parsed["header"].startswith("---\ndoc: CHANGELOG\n---")
    assert "[Unreleased]" in parsed["unreleased"]
    assert "In-flight work A" in parsed["unreleased"]
    assert len(parsed["versions"]) == 2
    assert parsed["versions"][0]["version"] == "0.2.0"
    assert "Spec 2 shipped" in parsed["versions"][0]["content"]
    assert parsed["versions"][1]["version"] == "0.1.0"
    assert parsed["archive_section"] == ""  # no Archive section yet


def test_parse_changelog_preserves_archive_section():
    text = textwrap.dedent("""\
        # Changelog

        ## [Unreleased]
        - x

        ## [0.1.0] - 2026-04-01
        - old

        ## Archive

        - [CHANGELOG-v0.0.1-to-v0.0.9.md](archive/CHANGELOG-v0.0.1-to-v0.0.9.md) — early versions
    """)
    parsed = parse_changelog(text)
    assert "## Archive" in parsed["archive_section"]
    assert "CHANGELOG-v0.0.1-to-v0.0.9.md" in parsed["archive_section"]


def test_parse_changelog_no_unreleased_raises():
    text = "# Changelog\n\n## [0.1.0] - 2026-04-01\n- old\n"
    with pytest.raises(ValueError, match="missing.*Unreleased"):
        parse_changelog(text)


def test_parse_devlog_separates_entries_in_file_order():
    text = textwrap.dedent("""\
        ---
        doc: DEVLOG
        ---

        # Development Log

        ## Daily Log - Newest First

        ### 2026-05-28: Spec 3 design

        Newest entry content.

        ### 2026-05-27: Spec 2 shipped

        Middle entry.

        ### 2025-12-01: Late-2025 work

        Oldest entry.
    """)
    parsed = parse_devlog(text)
    assert "# Development Log" in parsed["header"]
    assert "## Daily Log" in parsed["daily_log_heading"]
    assert len(parsed["entries"]) == 3
    assert parsed["entries"][0]["date"] == "2026-05-28"
    assert "Newest entry" in parsed["entries"][0]["content"]
    assert parsed["entries"][1]["date"] == "2026-05-27"
    assert parsed["entries"][2]["date"] == "2025-12-01"
    assert parsed["archive_section"] == ""


def test_parse_devlog_preserves_archive_section():
    text = textwrap.dedent("""\
        # Development Log
        ## Daily Log - Newest First

        ### 2026-05-28: x
        a

        ## Archive

        - [DEVLOG-2025-10.md](archive/DEVLOG-2025-10.md) - early
    """)
    parsed = parse_devlog(text)
    assert "DEVLOG-2025-10.md" in parsed["archive_section"]


def test_parse_devlog_no_daily_log_heading_raises():
    text = "# Development Log\n\n### 2026-05-28: orphan entry\n"
    with pytest.raises(ArchiveError, match="missing.*Daily Log"):
        parse_devlog(text)


def test_parse_devlog_no_entries_empty_list():
    text = textwrap.dedent("""\
        # Development Log

        ## Daily Log - Newest First

        (no entries yet)
    """)
    parsed = parse_devlog(text)
    assert parsed["entries"] == []
