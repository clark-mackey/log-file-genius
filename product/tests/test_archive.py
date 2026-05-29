import textwrap
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive import (
    parse_changelog, ArchivePlan, ArchiveAction, _estimate_tokens,
    DEFAULT_KEEP_FRACTION, COMBINED_KEEP_FRACTION_FLOOR,
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
