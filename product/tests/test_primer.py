import json
import textwrap
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from primer import build_prime, SUBAGENT_MARKER


def write_log(tmp_path, name, text):
    (tmp_path / "logs").mkdir(exist_ok=True)
    p = tmp_path / "logs" / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_prime_starts_with_subagent_marker(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n\n## Current Context\n- Version: v1\n")
    write_log(tmp_path, "CHANGELOG.md", "# Changelog\n## [Unreleased]\n### Added\n- Item A.\n")
    out = build_prime(project_root=tmp_path, n=5, as_json=False)
    assert out.split("\n", 1)[0] == SUBAGENT_MARKER


def test_prime_includes_state_and_changelog_entries(tmp_path):
    write_log(tmp_path, "STATE.md",
              "# Current State\n\n## Current Context\n- Version: v1.2.3\n- Phase: testing\n")
    write_log(tmp_path, "CHANGELOG.md", textwrap.dedent("""
        # Changelog
        ## [Unreleased]
        ### Added
        - Most recent entry.
        - Older entry.
    """))
    out = build_prime(project_root=tmp_path, n=2, as_json=False)
    assert "v1.2.3" in out
    assert "Most recent entry" in out
    assert "Older entry" in out


def test_prime_n_limits_changelog_entries(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n")
    lines = "\n".join(f"- Entry {i}." for i in range(10))
    write_log(tmp_path, "CHANGELOG.md",
              f"# Changelog\n## [Unreleased]\n### Added\n{lines}\n")
    out = build_prime(project_root=tmp_path, n=3, as_json=False)
    assert "Entry 0" in out
    assert "Entry 1" in out
    assert "Entry 2" in out
    assert "Entry 3" not in out


def test_prime_json_shape(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n")
    write_log(tmp_path, "CHANGELOG.md", "# Changelog\n## [Unreleased]\n- E.\n")
    out = build_prime(project_root=tmp_path, n=5, as_json=True)
    data = json.loads(out)
    assert data["role"] == "subagent"
    assert data["marker"] == SUBAGENT_MARKER
    assert "state" in data
    assert "changelog_entries" in data
    assert isinstance(data["changelog_entries"], list)


def test_prime_handles_missing_files(tmp_path):
    # No logs/ dir at all
    out = build_prime(project_root=tmp_path, n=5, as_json=False)
    assert SUBAGENT_MARKER in out
    assert "STATE.md not found" in out or "missing" in out.lower()
