"""CLI-level tests for `lfg migrate-state` (Spec 4 §2, T10).

Mirrors test_lfg_archive.py: drive the real lfg.py via subprocess against
temp STATE/DEVLOG fixtures. The pure plan/apply logic lives in
test_migrate_state.py; here we pin the CLI surface:
  - --dry-run prints a plan and writes NOTHING.
  - --force applies without a prompt (STATE rewritten, DEVLOG snapshot appended).
  - already-compliant + empty-plan STATE -> nothing-to-do, exit 0, files unchanged.
  - already-migrated (DEVLOG has snapshot) -> already-migrated, exit 0, unchanged.
"""
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"


def _run(args, cwd, stdin=""):
    return subprocess.run(
        [sys.executable, str(LFG)] + args,
        cwd=str(cwd), input=stdin, capture_output=True, text=True, encoding="utf-8",
    )


def _seed_config(tmp_path):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
          state: logs/STATE.md
        token_targets:
          state: 500
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir(exist_ok=True)


# A v0.2-style STATE: canonical Current Context (so it passes the structural
# validator) PLUS non-canonical sections carrying real content + an empty
# placeholder. The non-canonical real content makes build_plan non-empty.
_BROWNFIELD_STATE = textwrap.dedent("""\
    # Current State

    ## Current Context

    Working on the brownfield migration helper.

    ## Last Session

    Wired the CLI subcommand.

    ## Open Questions

    - Should we archive the old roadmap notes?
    - How do we handle multi-repo state?

    ## Legacy Roadmap

    Phase 1: ship the parser. Phase 2: ship apply. Phase 3: dogfood.

    ## Empty Placeholder

    *None*
""")

_DEVLOG = textwrap.dedent("""\
    # Development Log

    ## Daily Log

    ### 2026-05-30: Initial work
    - Started the migration module.
""")


def _seed_brownfield(tmp_path):
    _seed_config(tmp_path)
    (tmp_path / "logs" / "STATE.md").write_text(_BROWNFIELD_STATE, encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(_DEVLOG, encoding="utf-8")


def test_migrate_state_dry_run_writes_nothing(tmp_path):
    _seed_brownfield(tmp_path)
    state = tmp_path / "logs" / "STATE.md"
    devlog = tmp_path / "logs" / "DEVLOG.md"
    state_before = state.read_bytes()
    devlog_before = devlog.read_bytes()

    r = _run(["migrate-state", "--dry-run"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "STATE migration plan" in r.stdout
    # Non-canonical real content shows up in the plan.
    assert "ARCHIVE TO DEVLOG" in r.stdout

    # Byte-identical: dry-run wrote nothing.
    assert state.read_bytes() == state_before
    assert devlog.read_bytes() == devlog_before


def test_migrate_state_force_applies_without_prompt(tmp_path):
    _seed_brownfield(tmp_path)
    state = tmp_path / "logs" / "STATE.md"
    devlog = tmp_path / "logs" / "DEVLOG.md"
    state_before = state.read_text(encoding="utf-8")
    devlog_before = devlog.read_text(encoding="utf-8")

    r = _run(["migrate-state", "--force"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Applied STATE migration" in r.stdout

    state_after = state.read_text(encoding="utf-8")
    devlog_after = devlog.read_text(encoding="utf-8")

    # STATE rewritten: non-canonical sections removed; canonical kept.
    assert state_after != state_before
    assert "## Current Context" in state_after
    assert "## Legacy Roadmap" not in state_after
    assert "## Open Questions" not in state_after

    # DEVLOG got the one-shot snapshot entry with the archived content.
    assert devlog_after != devlog_before
    assert "STATE snapshot pre-v0.4.0 migration" in devlog_after
    assert "Legacy Roadmap" in devlog_after


def test_migrate_state_compliant_empty_plan_is_noop(tmp_path):
    """STATE already conforms (only canonical sections) -> nothing to do, exit 0."""
    _seed_config(tmp_path)
    compliant = textwrap.dedent("""\
        # Current State

        ## Current Context

        All good here.

        ## Last Session

        Nothing pending.
    """)
    state = tmp_path / "logs" / "STATE.md"
    state.write_text(compliant, encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(_DEVLOG, encoding="utf-8")

    state_before = state.read_bytes()
    devlog_before = (tmp_path / "logs" / "DEVLOG.md").read_bytes()

    r = _run(["migrate-state", "--force"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "nothing to migrate" in r.stdout.lower()

    assert state.read_bytes() == state_before
    assert (tmp_path / "logs" / "DEVLOG.md").read_bytes() == devlog_before


def test_migrate_state_already_migrated_is_noop(tmp_path):
    """DEVLOG already carries the snapshot entry -> guard 2 trips, exit 0, unchanged."""
    _seed_config(tmp_path)
    state = tmp_path / "logs" / "STATE.md"
    state.write_text(_BROWNFIELD_STATE, encoding="utf-8")
    devlog = tmp_path / "logs" / "DEVLOG.md"
    devlog.write_text(textwrap.dedent("""\
        # Development Log

        ## Daily Log

        ### 2026-05-31: Recent work
        - Did stuff.

        ### 2026-05-30: STATE snapshot pre-v0.4.0 migration

        (previously migrated)
    """), encoding="utf-8")

    state_before = state.read_bytes()
    devlog_before = devlog.read_bytes()

    r = _run(["migrate-state", "--force"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "already" in r.stdout.lower()

    assert state.read_bytes() == state_before
    assert devlog.read_bytes() == devlog_before
