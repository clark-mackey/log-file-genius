import textwrap
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive import (
    parse_changelog, parse_devlog, ArchivePlan, ArchiveAction, ArchiveError,
    _estimate_tokens, DEFAULT_KEEP_FRACTION, COMBINED_KEEP_FRACTION_FLOOR,
    _plan_changelog, _plan_devlog, build_plan, apply,
)
from typing import Optional


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


def _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500):
    """Build a CHANGELOG with controlled token counts.

    unreleased_tokens / version_tokens are in tokens; each body becomes a
    single line of 'x' chars whose length is tokens*4 minus 2 (for '- ').
    """
    unreleased_body = "- " + ("x" * (unreleased_tokens * 4 - 2)) + "\n"
    versions = ""
    for i in range(version_count, 0, -1):  # newest first: v0.5 down to v0.1
        body = "- " + ("x" * (version_tokens * 4 - 2)) + "\n"
        versions += f"## [0.{i}.0] - 2026-0{i}-01\n\n{body}\n"
    return f"# Changelog\n\n## [Unreleased]\n\n{unreleased_body}\n{versions}"


def test_plan_changelog_archives_oldest_versions_until_under_budget(tmp_path):
    # Budget 10000; unreleased=200; 5 versions x 2500 tokens.
    text = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert not refusals
    assert len(actions) == 1
    action = actions[0]
    # 0.8 * 10000 = 8000 target. Plan should bring source under 8000.
    assert action.tokens_after <= 8000
    # Archive content contains the oldest version block.
    assert "[0.1.0]" in action.moved_content
    # Archive filename pattern self-documents the range.
    name = action.archive_path.name
    assert name.startswith("CHANGELOG-v0.1.0-to-") and name.endswith(".md")


def test_plan_changelog_refuses_when_unreleased_alone_over_budget(tmp_path):
    # Unreleased alone = 11000 tokens; budget = 10000.
    text = _make_changelog(unreleased_tokens=11_000, version_count=2, version_tokens=500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert actions == []
    assert any("Unreleased" in r for r in refusals)


def test_plan_changelog_no_action_when_already_under_budget(tmp_path):
    text = _make_changelog(unreleased_tokens=100, version_count=2, version_tokens=500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert actions == []
    assert refusals == []


def _make_devlog(entry_token_sizes):
    """Build a DEVLOG; entry_token_sizes[i] in tokens for the i-th entry (newest first)."""
    header = "# Development Log\n\n## Daily Log - Newest First\n\n"
    entries = []
    base_date = 28
    for i, t in enumerate(entry_token_sizes):
        # date counts down from 2026-05-28
        date = f"2026-05-{base_date - i:02d}"
        body = "x" * (t * 4)
        entries.append(f"### {date}: entry {i}\n\n{body}\n\n")
    return header + "".join(entries)


def test_plan_devlog_keeps_newest_entries_fitting_keep_fraction(tmp_path):
    # Budget 15000, keep_fraction 0.8 → target 12000.
    # 5 entries x 3000 tokens each = 15000 total + headers.
    text = _make_devlog([3000] * 5)
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    assert refusals == []
    assert len(actions) == 1
    # Oldest entries archive; the newest (2026-05-28) stays in source.
    assert "2026-05-28" not in actions[0].moved_content
    # The oldest seeded date (2026-05-24, i=4) IS archived.
    assert "2026-05-24" in actions[0].moved_content


def test_plan_devlog_no_action_when_under_budget(tmp_path):
    text = _make_devlog([1000] * 3)  # 3000 tokens total
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    assert actions == [] and refusals == []


def test_plan_devlog_warns_when_single_newest_oversize(tmp_path):
    # Newest entry alone is 13000 tokens (> 0.8 * 15000 = 12000).
    text = _make_devlog([13000, 1000, 1000])
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    # Newest stays in source (never archived).
    if actions:
        assert "2026-05-28" not in actions[0].moved_content
    assert any("newest" in w.lower() and "oversize" in w.lower() for w in warnings)


def _write_minimal_config_and_logs(tmp_path,
                                    changelog_text=None,
                                    devlog_text=None):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 10000
          devlog: 15000
          combined: 25000
        archival:
          keep_fraction: 0.8
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir(exist_ok=True)
    if changelog_text:
        (tmp_path / "logs" / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
    if devlog_text:
        (tmp_path / "logs" / "DEVLOG.md").write_text(devlog_text, encoding="utf-8")


def test_build_plan_reads_config_paths_and_budgets(tmp_path):
    _write_minimal_config_and_logs(
        tmp_path,
        changelog_text=_make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500),
        devlog_text=_make_devlog([1000] * 3),
    )
    plan = build_plan(tmp_path)
    # Only CHANGELOG over budget; DEVLOG fits.
    assert len(plan.actions) == 1
    assert "CHANGELOG" in plan.actions[0].source_path.name


def test_build_plan_devlog_over_individual_budget(tmp_path):
    # DEVLOG alone is over 15000; CHANGELOG fits.
    text_cl = _make_changelog(unreleased_tokens=200, version_count=3, version_tokens=2000)
    text_dl = _make_devlog([4000] * 4)  # 16000 — over 15000
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl, devlog_text=text_dl)
    plan = build_plan(tmp_path)
    devlog_actions = [a for a in plan.actions if "DEVLOG" in a.source_path.name]
    assert len(devlog_actions) == 1


def test_build_plan_no_action_when_all_under_budget(tmp_path):
    _write_minimal_config_and_logs(
        tmp_path,
        changelog_text=_make_changelog(100, 1, 100),
        devlog_text=_make_devlog([100]),
    )
    plan = build_plan(tmp_path)
    assert plan.is_empty()


def test_apply_writes_archive_and_rewrites_source(tmp_path):
    text_cl = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl)

    plan = build_plan(tmp_path, include_devlog=False)
    assert len(plan.actions) == 1
    action = plan.actions[0]

    apply(plan)

    # Archive file exists with the moved content.
    assert action.archive_path.exists()
    archived = action.archive_path.read_text(encoding="utf-8")
    assert "[0.1.0]" in archived  # oldest version was moved

    # Source no longer contains that oldest version.
    new_source = action.source_path.read_text(encoding="utf-8")
    assert "[0.1.0]" not in new_source

    # Source [Unreleased] preserved.
    assert "## [Unreleased]" in new_source

    # Source has a ## Archive section with the summary line.
    assert "## Archive" in new_source
    assert "CHANGELOG-v0.1.0-to-" in new_source


def test_apply_appends_to_existing_archive_section(tmp_path):
    # Pre-existing Archive section should be appended to, not duplicated.
    initial = textwrap.dedent("""\
        # Changelog

        ## [Unreleased]
        - x

        ## [0.3.0] - 2026-03-01
        """) + ("- " + "x" * 9996 + "\n") + textwrap.dedent("""

        ## [0.2.0] - 2026-02-01
        """) + ("- " + "x" * 9996 + "\n") + textwrap.dedent("""

        ## Archive

        - [CHANGELOG-v0.0.1-to-v0.1.0.md](archive/CHANGELOG-v0.0.1-to-v0.1.0.md) — old
        """)
    _write_minimal_config_and_logs(tmp_path, changelog_text=initial)

    plan = build_plan(tmp_path, include_devlog=False)
    apply(plan)

    src_text = (tmp_path / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    # Both archive lines should be present.
    assert "CHANGELOG-v0.0.1-to-v0.1.0.md" in src_text
    # The Archive header should appear exactly once.
    assert src_text.count("## Archive") == 1


def test_apply_creates_archive_dir_if_missing(tmp_path):
    text_cl = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl)
    # Confirm no archive dir initially.
    assert not (tmp_path / "logs" / "archive").exists()

    plan = build_plan(tmp_path, include_devlog=False)
    apply(plan)

    assert (tmp_path / "logs" / "archive").is_dir()
