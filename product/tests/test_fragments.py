# product/tests/test_fragments.py
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "product/rules"
ALLOWED_TARGETS = {"agents_md", "claude_rules", "augment_rules"}


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: missing opening frontmatter delimiter"
    end = text.find("\n---\n", 4)
    assert end != -1, f"{path.name}: unterminated frontmatter"
    return text[4:end]


def _parse_fm(text):
    fm = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert ":" in line, f"bad frontmatter line: {line!r}"
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


@pytest.mark.parametrize("path", list(RULES.glob("*.md")))
def test_fragment_has_required_frontmatter_keys(path):
    fm = _parse_fm(_frontmatter(path))
    assert "fragment" in fm, f"{path.name}: missing 'fragment'"
    assert "order" in fm, f"{path.name}: missing 'order'"
    assert "targets" in fm, f"{path.name}: missing 'targets'"
    assert "summary" in fm, f"{path.name}: missing 'summary'"
    # order is an integer
    int(fm["order"])
    # targets is a subset of the allowed set
    targets = {t.strip() for t in fm["targets"].lstrip("[").rstrip("]").split(",") if t.strip()}
    assert targets <= ALLOWED_TARGETS, f"{path.name}: unknown targets {targets - ALLOWED_TARGETS}"


def test_no_per_tool_path_literals_in_fragments():
    """Fragments must reference paths via .logfile-config.yml, not literal
    .claude/ or .augment/ strings. Code-block examples (between triple
    backticks) are allowed."""
    offenders = []
    pattern = re.compile(r"\.(claude|augment)/")
    for path in RULES.glob("*.md"):
        in_code = False
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if pattern.search(line):
                offenders.append(f"{path.name}:{i}: {line.strip()}")
    assert not offenders, "per-tool paths in fragments:\n  " + "\n  ".join(offenders)


def test_fragment_orders_unique():
    orders = []
    for path in RULES.glob("*.md"):
        fm = _parse_fm(_frontmatter(path))
        orders.append(int(fm["order"]))
    assert len(orders) == len(set(orders)), f"duplicate order values: {orders}"
