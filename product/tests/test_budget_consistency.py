"""Guard: the canonical token-budget *defaults* must agree across every loader.

Note on scope:
  - This checks the FALLBACK DEFAULTS that apply when no config / profile override
    is present. Those must be identical everywhere: CHANGELOG 10000, DEVLOG 15000,
    COMBINED 25000 (validators derive warnings at 80%).
  - It deliberately does NOT force `profiles/*.yml` to the canonical numbers.
    Profiles are presets and may differ on purpose (e.g. startup.yml is tighter:
    7500/10000/17500). Forcing them to canon would erase intentional design.
  - The human-facing contradiction guard ("under 10,000 tokens combined" in
    project_instructions.md) lives in test_rule_directives.py, which runs after
    Phase 4 removes that string.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lint_logs_defaults_match_canon():
    txt = (ROOT / "product/scripts/lint-logs.py").read_text(encoding="utf-8")
    assert "'changelog', 10000" in txt
    assert "'devlog', 15000" in txt
    assert "'combined', 25000" in txt


def test_shell_validator_defaults_match_canon():
    sh = (ROOT / "product/scripts/validate-log-files.sh").read_text(encoding="utf-8")
    assert "CHANGELOG_TOKEN_ERROR=10000" in sh
    assert "DEVLOG_TOKEN_ERROR=15000" in sh
    assert "CHANGELOG_TOKEN_WARNING=8000" in sh
    assert "DEVLOG_TOKEN_WARNING=12000" in sh

    ps = (ROOT / "product/scripts/validate-log-files.ps1").read_text(encoding="utf-8")
    assert "CHANGELOG_TOKEN_ERROR = 10000" in ps
    assert "DEVLOG_TOKEN_ERROR = 15000" in ps
