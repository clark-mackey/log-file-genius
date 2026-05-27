import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "lint_logs", Path(__file__).resolve().parents[1] / "scripts" / "lint-logs.py")
lint_logs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_logs)


def test_loglinter_reads_token_targets_from_config(tmp_path):
    cfg = tmp_path / ".logfile-config.yml"
    cfg.write_text(
        "paths:\n  changelog: logs/CHANGELOG.md\n"
        "token_targets:\n  changelog: 9999\n  devlog: 12345\n  combined: 22222\n",
        encoding="utf-8")
    linter = lint_logs.LogLinter(config_path=str(cfg))
    assert linter.changelog_target == 9999
    assert linter.devlog_target == 12345
    assert linter.combined_target == 22222
    assert linter.changelog_path == "logs/CHANGELOG.md"


def test_loglinter_defaults_without_config(tmp_path):
    linter = lint_logs.LogLinter(config_path=str(tmp_path / "absent.yml"))
    assert linter.changelog_target == 10000
    assert linter.devlog_target == 15000
    assert linter.combined_target == 25000


def test_devlog_no_longer_requires_current_context(tmp_path):
    cfg = tmp_path / ".logfile-config.yml"
    cfg.write_text("paths:\n  devlog: D.md\n  state: S.md\n", encoding="utf-8")
    (tmp_path / "D.md").write_text("# Development Log\n## Daily Log\n### 2026-01-01: x\n", encoding="utf-8")
    import os
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        linter = lint_logs.LogLinter(config_path=str(cfg))
        result = linter.validate_devlog()
    finally:
        os.chdir(cwd)
    assert all("Current Context" not in i.message for i in result.issues)


def test_validate_state_present(tmp_path):
    cfg = tmp_path / ".logfile-config.yml"
    cfg.write_text("paths:\n  state: S.md\ntoken_targets:\n  state: 500\n", encoding="utf-8")
    (tmp_path / "S.md").write_text("# Current State\n## Current Context\n- Version: v1\n", encoding="utf-8")
    import os
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        linter = lint_logs.LogLinter(config_path=str(cfg))
        result = linter.validate_state()
    finally:
        os.chdir(cwd)
    # A small present STATE file has no errors.
    assert result.errors == 0
