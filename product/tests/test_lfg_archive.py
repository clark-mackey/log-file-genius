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


def _seed_oversize_changelog(tmp_path):
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
    (tmp_path / "logs").mkdir()
    body = "## [Unreleased]\n- x\n"
    for i in range(5, 0, -1):
        body += f"\n## [0.{i}.0] - 2026-0{i}-01\n- " + ("x" * 9998) + "\n"
    (tmp_path / "logs" / "CHANGELOG.md").write_text(f"# Changelog\n\n{body}", encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(
        "# Development Log\n\n## Daily Log\n\n### 2026-05-28: x\n- y\n", encoding="utf-8")


def test_archive_dry_run_writes_nothing(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--dry-run"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Move from CHANGELOG.md" in r.stdout
    # No archive file created.
    assert not (tmp_path / "logs" / "archive").exists()


def test_archive_force_skips_prompt_and_applies(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--force"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "logs" / "archive").is_dir()
    # Some CHANGELOG-* file in archive.
    assert any(p.name.startswith("CHANGELOG-v") for p in (tmp_path / "logs" / "archive").iterdir())


def test_archive_state_and_adr_rejected(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--state"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "STATE" in (r.stdout + r.stderr)
    assert "don't archive" in (r.stdout + r.stderr).lower()

    r = _run(["archive", "--adr"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "ADR" in (r.stdout + r.stderr)


def test_archive_no_action_when_under_budget(tmp_path):
    """Empty plan exits 0 with a friendly message."""
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
        token_targets:
          changelog: 10000
        archival:
          keep_fraction: 0.8
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n- tiny\n", encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text("# Development Log\n\n## Daily Log\n", encoding="utf-8")
    r = _run(["archive", "--dry-run"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Nothing to archive" in r.stdout
