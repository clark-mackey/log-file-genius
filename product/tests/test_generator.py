import textwrap
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generator import (
    parse_fragment, render_agents_md, GeneratorError, AGENTS_TOKEN_BUDGET,
)


def write(tmp_path, name, frontmatter, body):
    p = tmp_path / name
    p.write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}\n", encoding="utf-8")
    return p


def test_parse_fragment_extracts_frontmatter_and_body(tmp_path):
    p = write(tmp_path, "x.md",
              "fragment: x\norder: 1\ntargets: agents_md\nsummary: A short summary.",
              "# Body\n\nHello.")
    fm, body = parse_fragment(p)
    assert fm["fragment"] == "x"
    assert fm["order"] == 1
    assert fm["targets"] == ["agents_md"]
    assert fm["summary"] == "A short summary."
    assert body.strip() == "# Body\n\nHello."


def test_parse_fragment_targets_multi(tmp_path):
    p = write(tmp_path, "x.md",
              "fragment: x\norder: 1\ntargets: agents_md, claude_rules, augment_rules\nsummary: s",
              "body")
    fm, _ = parse_fragment(p)
    assert fm["targets"] == ["agents_md", "claude_rules", "augment_rules"]


def test_parse_fragment_missing_frontmatter_raises(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("no frontmatter here\n", encoding="utf-8")
    with pytest.raises(GeneratorError):
        parse_fragment(p)


def test_startup_keeps_procedures_on_demand(tmp_path):
    fragment = write(tmp_path, "a.md",
                     "fragment: a\norder: 10\ntargets: agents_md\nsummary: Detail.",
                     "ON_DEMAND_SENTINEL " * 1000)
    out = render_agents_md([parse_fragment(fragment)])
    assert "ON_DEMAND_SENTINEL" not in out
    assert "logs/STATE.md" in out and "logs/adr/README.md" in out
    assert "context-guide.md" in out and "lfg.py" in out
    assert len(out) <= 1000
    assert "baseline branch/commit" in out


def test_render_uses_lf_no_bom_trailing_newline(tmp_path):
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 10\ntargets: agents_md\nsummary: s",
              "body")
    out = render_agents_md([parse_fragment(a)])
    assert "\r\n" not in out, "CRLF leaked into output"
    assert not out.startswith("﻿"), "BOM leaked into output"
    assert out.endswith("\n"), "missing trailing newline"
    assert not out.endswith("\n\n"), "double trailing newline"


def test_render_fails_above_budget(tmp_path, monkeypatch):
    # Force a tiny budget so a small fragment trips the gate.
    monkeypatch.setattr("generator.AGENTS_TOKEN_BUDGET", 50)
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 10\ntargets: agents_md\nsummary: s",
              "x" * 1000)  # ~250 tokens at chars/4
    with pytest.raises(GeneratorError, match="exceeds token budget"):
        render_agents_md([parse_fragment(a)])
