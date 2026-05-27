import textwrap
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from config_parser import parse_config, ConfigError


def write(tmp_path, text):
    p = tmp_path / ".logfile-config.yml"
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return str(p)


def test_flat_and_nested_keys(tmp_path):
    cfg = parse_config(write(tmp_path, """
        profile: solo-developer
        ai_assistant: claude-code
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 10000
          combined: 25000
    """))
    assert cfg["profile"] == "solo-developer"
    assert cfg["paths"]["changelog"] == "logs/CHANGELOG.md"
    assert cfg["token_targets"]["changelog"] == 10000
    assert cfg["token_targets"]["combined"] == 25000


def test_quotes_and_inline_comments(tmp_path):
    cfg = parse_config(write(tmp_path, """
        log_file_genius_version: "0.2.0"   # version
        profile: 'team'
    """))
    assert cfg["log_file_genius_version"] == "0.2.0"
    assert cfg["profile"] == "team"


def test_missing_file_returns_empty(tmp_path):
    assert parse_config(str(tmp_path / "nope.yml")) == {}


def test_tabs_fail_loudly(tmp_path):
    p = tmp_path / ".logfile-config.yml"
    p.write_text("paths:\n\tchangelog: x\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        parse_config(str(p))


def test_real_profiles_parse(tmp_path):
    # The preset profile files are documentation, but must at least not crash
    # the parser on their top-level scalar keys we rely on.
    profiles = Path(__file__).resolve().parents[1] / "profiles"
    for f in profiles.glob("*.yml"):
        # Should not raise on the top-level scalar keys we rely on.
        parse_config(str(f))
