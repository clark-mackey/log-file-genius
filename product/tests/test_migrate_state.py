"""Tests for migrate_state.py — brownfield STATE.md migration (Spec 4 §2).

Mirrors test_archive.py's structure: parser tests, plan-builder tests, then
apply() behavior including the two idempotency guards and atomic two-file write.
"""
import importlib.util
import os
import textwrap
from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from migrate_state import (
    parse_state, split_preamble, build_plan, apply,
    MigratePlan, Section, MigrateError,
    CANONICAL_SECTIONS, SNAPSHOT_HEADING_RE, SNAPSHOT_TITLE,
    _estimate_tokens, DEFAULT_STATE_TARGET,
)

TODAY = "2026-06-01"


# --- helpers ----------------------------------------------------------------

def _config(state_target: int = 500) -> dict:
    return {"token_targets": {"state": state_target}}


# A non-compliant STATE.md: missing `## Current Context` would be the structural
# error, but here we keep Current Context and add a non-canonical section so the
# plan has work to do; non-compliance for Guard 1 is driven by token budget in
# some tests and by missing Current Context in others.
NONCANONICAL_STATE = textwrap.dedent("""\
    ---
    doc: STATE
    ---

    # Current State

    ## Current Context

    - **Project:** Demo
    - **Version:** v0.2.0

    ## Last Session

    - **Done:** shipped a thing

    ## Old Sprint Notes

    - We decided to use Postgres because of RLS.
    - Migrated the billing table on 2026-04-02.

    ## Empty Placeholder

    - *None*
    """)


def _devlog(extra: str = "") -> str:
    return textwrap.dedent("""\
        ---
        doc: DEVLOG
        ---

        # Development Log

        ## Daily Log - Newest First

        ### 2026-05-30: Today's work

        Implemented the migrate verb.

        ### 2026-05-01: Earlier work

        Set up the repo.
        """) + extra


def _write_project(tmp_path, state_text, devlog_text, state_target=500):
    (tmp_path / ".logfile-config.yml").write_text(
        "paths:\n  state: logs/STATE.md\n  devlog: logs/DEVLOG.md\n"
        f"token_targets:\n  state: {state_target}\n",
        encoding="utf-8",
    )
    (tmp_path / "logs").mkdir(exist_ok=True)
    (tmp_path / "logs" / "STATE.md").write_text(state_text, encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(devlog_text, encoding="utf-8")
    return tmp_path / "logs" / "STATE.md", tmp_path / "logs" / "DEVLOG.md"


# --- parse_state ------------------------------------------------------------

def test_estimate_tokens_is_chars_div_4():
    assert _estimate_tokens("") == 0
    assert _estimate_tokens("a" * 100) == 25


def test_parse_state_splits_sections_and_counts_tokens():
    sections = parse_state(NONCANONICAL_STATE)
    headings = [s.heading for s in sections]
    assert headings == [
        "Current Context", "Last Session", "Old Sprint Notes", "Empty Placeholder",
    ]
    for s in sections:
        assert s.tokens == _estimate_tokens(s.raw)
        assert s.tokens > 0


def test_split_preamble_separates_frontmatter():
    preamble, sections = split_preamble(NONCANONICAL_STATE)
    assert "doc: STATE" in preamble
    assert "# Current State" in preamble
    assert sections[0].heading == "Current Context"


def test_parse_state_no_headings_returns_empty():
    assert parse_state("just frontmatter\nno headings\n") == []


def test_section_matches_canonical_with_suffix():
    s = Section(heading="Current Context (Source of Truth)", raw="", tokens=0)
    assert s.matches_canonical() == "Current Context"


# --- build_plan -------------------------------------------------------------

def test_build_plan_keeps_canonical_archives_user_drops_empty():
    plan = build_plan(NONCANONICAL_STATE, _config())
    keep_headings = [s.heading for s in plan.keep]
    assert "Current Context" in keep_headings
    assert "Last Session" in keep_headings

    archived = [s.heading for s in plan.archive_to_devlog]
    assert "Old Sprint Notes" in archived  # real content

    dropped = [s.heading for s in plan.drop]
    assert "Empty Placeholder" in dropped  # *None* placeholder


def test_build_plan_target_from_config():
    plan = build_plan(NONCANONICAL_STATE, _config(state_target=750))
    assert plan.target_tokens == 750
    plan_default = build_plan(NONCANONICAL_STATE, {})
    assert plan_default.target_tokens == DEFAULT_STATE_TARGET


def test_build_plan_keeps_canonical_order():
    # Even though "Last Session" appears before "Current Context" in the source,
    # keep order follows CANONICAL_SECTIONS.
    text = textwrap.dedent("""\
        # State
        ## Last Session
        - done

        ## Current Context
        - **Project:** X
        """)
    plan = build_plan(text, _config())
    headings = [s.heading for s in plan.keep]
    assert headings.index("Current Context") < headings.index("Last Session")


def test_build_plan_truncates_over_budget_kept_section():
    # A Current Context section far over the 500-token budget must be truncated
    # and flagged, keeping the most-recent (trailing) lines.
    big_lines = "\n".join(f"- old line {i}" for i in range(400))
    recent = "- NEWEST: this must survive truncation"
    text = f"# State\n## Current Context\n{big_lines}\n{recent}\n"
    plan = build_plan(text, _config(state_target=100))
    kept = next(s for s in plan.keep if s.heading == "Current Context")
    assert kept.tokens <= 100
    assert "NEWEST" in kept.raw           # most-recent content survives
    assert "truncated" in kept.raw.lower()
    assert plan.truncations               # truncation recorded
    assert any("Current Context" in note for note in plan.truncations)


def test_build_plan_structural_section_kept():
    text = textwrap.dedent("""\
        # State
        ## Related Documents
        [CHANGELOG](./CHANGELOG.md)

        ## Current Context
        - **Project:** X
        """)
    plan = build_plan(text, _config())
    assert "Related Documents" in [s.heading for s in plan.keep]
    assert not plan.archive_to_devlog


# --- apply: success path ----------------------------------------------------

def test_apply_writes_state_and_appends_snapshot_at_end_of_daily_log(tmp_path):
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    plan = build_plan(NONCANONICAL_STATE, _config())

    apply(plan, state_path, devlog_path, today=TODAY,
          config_path=tmp_path / ".logfile-config.yml")

    new_state = state_path.read_text(encoding="utf-8")
    # Canonical kept; non-canonical archived out of STATE; placeholder dropped.
    assert "## Current Context" in new_state
    assert "## Last Session" in new_state
    assert "Old Sprint Notes" not in new_state
    assert "Empty Placeholder" not in new_state

    new_devlog = read_devlog = devlog_path.read_text(encoding="utf-8")
    # Snapshot heading present, exact form.
    assert SNAPSHOT_HEADING_RE.search(new_devlog)
    assert f"### {TODAY}: {SNAPSHOT_TITLE}" in new_devlog
    # Archived section content moved into the snapshot.
    assert "Old Sprint Notes" in new_devlog
    assert "Postgres because of RLS" in new_devlog

    # Position: snapshot is at the END of Daily Log — after the oldest existing
    # entry (2026-05-01) and before any later `## ` section. Assert it comes
    # AFTER the oldest dated entry's body, not at the top.
    idx_snapshot = new_devlog.index(SNAPSHOT_TITLE)
    idx_oldest = new_devlog.index("2026-05-01")
    idx_newest = new_devlog.index("2026-05-30")
    assert idx_newest < idx_oldest < idx_snapshot


def test_apply_snapshot_before_archive_section(tmp_path):
    devlog = _devlog(extra="\n## Archive\n\n- [old.md](archive/old.md) — older\n")
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, devlog)
    plan = build_plan(NONCANONICAL_STATE, _config())
    apply(plan, state_path, devlog_path, today=TODAY,
          config_path=tmp_path / ".logfile-config.yml")
    out = devlog_path.read_text(encoding="utf-8")
    # Snapshot sits inside Daily Log, i.e. before the `## Archive` heading.
    assert out.index(SNAPSHOT_TITLE) < out.index("## Archive")


def test_apply_state_only_when_nothing_to_archive(tmp_path):
    # No non-canonical content -> only truncation/drop work; DEVLOG untouched.
    text = textwrap.dedent("""\
        # State
        ## Current Context
        - **Project:** X
        ## Empty
        - *None*
        """)
    state_path, devlog_path = _write_project(tmp_path, text, _devlog())
    devlog_before = devlog_path.read_text(encoding="utf-8")
    plan = build_plan(text, _config())
    assert not plan.archive_to_devlog
    apply(plan, state_path, devlog_path, today=TODAY,
          config_path=tmp_path / ".logfile-config.yml")
    assert "## Empty" not in state_path.read_text(encoding="utf-8")
    # DEVLOG unchanged (no snapshot needed).
    assert devlog_path.read_text(encoding="utf-8") == devlog_before


# --- apply: guards ----------------------------------------------------------

def test_guard1_compliant_state_refuses(tmp_path):
    compliant = textwrap.dedent("""\
        ---
        doc: STATE
        ---
        # Current State
        ## Current Context
        - **Project:** X
        ## Last Session
        - **Done:** y
        """)
    state_path, devlog_path = _write_project(tmp_path, compliant, _devlog())
    plan = build_plan(compliant, _config())
    with pytest.raises(MigrateError, match="already passes"):
        apply(plan, state_path, devlog_path, today=TODAY,
              config_path=tmp_path / ".logfile-config.yml")


def test_guard2_existing_snapshot_refuses(tmp_path):
    devlog = _devlog(
        extra=f"\n### {TODAY}: {SNAPSHOT_TITLE}\n\nalready migrated once\n"
    )
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, devlog)
    plan = build_plan(NONCANONICAL_STATE, _config())
    with pytest.raises(MigrateError, match="already contains"):
        apply(plan, state_path, devlog_path, today=TODAY,
              config_path=tmp_path / ".logfile-config.yml")


def test_idempotency_second_apply_refuses(tmp_path):
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    cfg = tmp_path / ".logfile-config.yml"
    plan = build_plan(NONCANONICAL_STATE, _config())
    apply(plan, state_path, devlog_path, today=TODAY, config_path=cfg)

    # Second run: STATE is now compliant (Guard 1) AND DEVLOG has the snapshot
    # (Guard 2). Either alone refuses; here both should.
    plan2 = build_plan(state_path.read_text(encoding="utf-8"), _config())
    with pytest.raises(MigrateError):
        apply(plan2, state_path, devlog_path, today=TODAY, config_path=cfg)


def test_idempotency_guard2_after_state_edited_back(tmp_path):
    # Migrate, then edit STATE back into non-compliance; Guard 2 still refuses.
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    cfg = tmp_path / ".logfile-config.yml"
    apply(build_plan(NONCANONICAL_STATE, _config()), state_path, devlog_path,
          today=TODAY, config_path=cfg)
    # User re-breaks STATE (removes Current Context -> structural error).
    state_path.write_text("# State\n## Random\n- stuff\n", encoding="utf-8")
    plan2 = build_plan(state_path.read_text(encoding="utf-8"), _config())
    with pytest.raises(MigrateError, match="already contains"):
        apply(plan2, state_path, devlog_path, today=TODAY, config_path=cfg)


# --- DEVLOG validator round-trip --------------------------------------------

def test_snapshot_devlog_round_trips_through_validator(tmp_path):
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    cfg = tmp_path / ".logfile-config.yml"
    apply(build_plan(NONCANONICAL_STATE, _config()), state_path, devlog_path,
          today=TODAY, config_path=cfg)

    # Load lint-logs and validate the migrated DEVLOG — no new errors.
    spec = importlib.util.spec_from_file_location(
        "lint_logs", Path(__file__).resolve().parents[1] / "scripts" / "lint-logs.py"
    )
    lint_logs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint_logs)
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        linter = lint_logs.LogLinter(config_path=str(cfg))
        result = linter.validate_devlog()
    finally:
        os.chdir(cwd)
    assert result.errors == 0


# --- atomicity --------------------------------------------------------------

def test_atomicity_devlog_write_failure_leaves_state_unmigrated(tmp_path, monkeypatch):
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    cfg = tmp_path / ".logfile-config.yml"
    state_before = state_path.read_text(encoding="utf-8")
    devlog_before = devlog_path.read_text(encoding="utf-8")

    plan = build_plan(NONCANONICAL_STATE, _config())

    import migrate_state
    real_replace = os.replace

    def failing_replace(src, dst):
        # Fail the DEVLOG commit (first os.replace). STATE must not land.
        if str(dst) == str(devlog_path):
            raise OSError("simulated DEVLOG replace failure")
        return real_replace(src, dst)

    monkeypatch.setattr(migrate_state.os, "replace", failing_replace)

    with pytest.raises(OSError, match="simulated DEVLOG"):
        apply(plan, state_path, devlog_path, today=TODAY, config_path=cfg)

    # Neither file changed; no stray tmp files.
    assert state_path.read_text(encoding="utf-8") == state_before
    assert devlog_path.read_text(encoding="utf-8") == devlog_before
    assert not (state_path.with_name(state_path.name + ".lfg-tmp")).exists()
    assert not (devlog_path.with_name(devlog_path.name + ".lfg-tmp")).exists()


def test_atomicity_state_write_failure_after_devlog_keeps_snapshot(tmp_path, monkeypatch):
    # If the STATE replace fails AFTER DEVLOG committed, the snapshot is kept
    # (lossless) and STATE retains its original content; Guard 2 blocks re-run.
    state_path, devlog_path = _write_project(tmp_path, NONCANONICAL_STATE, _devlog())
    cfg = tmp_path / ".logfile-config.yml"
    state_before = state_path.read_text(encoding="utf-8")
    plan = build_plan(NONCANONICAL_STATE, _config())

    import migrate_state
    real_replace = os.replace

    def failing_replace(src, dst):
        if str(dst) == str(state_path):
            raise OSError("simulated STATE replace failure")
        return real_replace(src, dst)

    monkeypatch.setattr(migrate_state.os, "replace", failing_replace)
    with pytest.raises(OSError, match="simulated STATE"):
        apply(plan, state_path, devlog_path, today=TODAY, config_path=cfg)

    # STATE unchanged; DEVLOG has the snapshot (lossless).
    assert state_path.read_text(encoding="utf-8") == state_before
    assert SNAPSHOT_HEADING_RE.search(devlog_path.read_text(encoding="utf-8"))
    # No stray STATE tmp.
    assert not (state_path.with_name(state_path.name + ".lfg-tmp")).exists()
