"""Guard: every template carries frontmatter, and its prose Related Documents
links stay in sync with the frontmatter `related:` graph (no divergence)."""
import re
from pathlib import Path

T = Path(__file__).resolve().parents[1] / "templates"
EXPECTED = {
    "CHANGELOG_template.md": {"DEVLOG", "STATE", "ADRs"},
    "DEVLOG_template.md": {"CHANGELOG", "STATE", "ADRs"},
    "STATE_template.md": {"CHANGELOG", "DEVLOG", "ADRs"},
}


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "missing frontmatter"
    return m.group(1)


def test_each_template_has_frontmatter():
    for name in list(EXPECTED) + ["ADR_template.md"]:
        text = (T / name).read_text(encoding="utf-8")
        fm = _frontmatter(text)
        assert "doc:" in fm and "related:" in fm


def test_prose_links_match_frontmatter_targets():
    # Every related: target path (top-level templates use ./X.md) must also
    # appear as a markdown link in the prose body.
    for name in EXPECTED:
        text = (T / name).read_text(encoding="utf-8")
        fm = _frontmatter(text)
        targets = re.findall(r":\s*(\./[^\s]+)", fm)
        assert targets, f"{name}: no ./ targets parsed from frontmatter"
        body = text[text.index("---", 3) + 3:]
        for tgt in targets:
            assert f"({tgt})" in body, f"{name}: {tgt} missing from prose links"
