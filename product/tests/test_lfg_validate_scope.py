"""Regression test: `lfg validate --changelog` / `--devlog` must forward the
flags lint-logs.py actually accepts (--changelog / --devlog), not the
nonexistent --changelog-only / --devlog-only variants.

Before the fix, cmd_validate appended '--changelog-only'/'--devlog-only', so
argparse in lint-logs.py died with "unrecognized arguments". These tests assert
both subcommands exit cleanly and scope validation to the single named file.
"""
import json
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


def _seed_clean_logs(tmp_path):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 100000
          devlog: 100000
          combined: 200000
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "CHANGELOG.md").write_text(
        "# Changelog\n\n"
        "See https://keepachangelog.com/ for format.\n\n"
        "## [Unreleased]\n- nothing yet\n",
        encoding="utf-8",
    )
    (tmp_path / "logs" / "DEVLOG.md").write_text(
        "# Development Log\n\n## Daily Log\n\n### 2026-05-28: x\n- y\n",
        encoding="utf-8",
    )


def test_validate_changelog_only(tmp_path):
    _seed_clean_logs(tmp_path)
    r = _run(["validate", "--changelog", "--json"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    results = json.loads(r.stdout)["results"]
    assert len(results) == 1, results
    assert "CHANGELOG" in results[0]["file"]


def test_validate_devlog_only(tmp_path):
    _seed_clean_logs(tmp_path)
    r = _run(["validate", "--devlog", "--json"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    results = json.loads(r.stdout)["results"]
    assert len(results) == 1, results
    assert "DEVLOG" in results[0]["file"]
