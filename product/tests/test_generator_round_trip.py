"""Spec 4 §1 round-trip tests for the canonical-body generator primitive.

Proves the managed-block wrapper (render_block) round-trips cleanly back to
the full output (render_full), that the BEGIN marker matches the spec's strict
regex and carries the VERSION.json version, and that render_full still equals
the committed on-disk product/AGENTS.md (the drift gate).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "product" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generator import (  # noqa: E402
    parse_fragment,
    render_block,
    render_full,
    read_repo_version,
    strip_block_markers,
)

# The spec's strict BEGIN-marker regex (anchored to the start of a line).
SPEC_BEGIN_RE = re.compile(r"^<!--\s*LFG:BEGIN\s+v(\S+)\s*(?:—[^>]*)?-->$")
SPEC_END_LITERAL = "<!-- LFG:END -->"


def _load_fragments():
    rules_dir = ROOT / "product" / "rules"
    return [parse_fragment(p) for p in sorted(rules_dir.glob("*.md"))]


def test_strip_block_markers_recovers_render_full_byte_for_byte():
    fragments = _load_fragments()
    block = render_block(fragments)
    assert strip_block_markers(block) == render_full(fragments)


def test_block_begins_with_spec_regex_and_ends_with_end_marker():
    fragments = _load_fragments()
    block = render_block(fragments)
    lines = block.splitlines()
    # First line matches the spec BEGIN regex.
    assert SPEC_BEGIN_RE.match(lines[0]), f"BEGIN line did not match spec: {lines[0]!r}"
    # Last non-empty line is the literal END marker. render_block emits a
    # single trailing newline after END, so the last splitlines() element is
    # the END marker itself.
    assert lines[-1] == SPEC_END_LITERAL
    # And the block text ends with the END marker plus one trailing newline.
    assert block.endswith(SPEC_END_LITERAL + "\n")


def test_begin_marker_version_matches_version_json():
    fragments = _load_fragments()
    block = render_block(fragments)
    begin_line = block.splitlines()[0]
    captured = SPEC_BEGIN_RE.match(begin_line).group(1)

    version_file = ROOT / "product" / "VERSION.json"
    expected = json.loads(version_file.read_text(encoding="utf-8"))["version"]

    assert captured == expected
    # read_repo_version() is the same source render_block uses by default.
    assert captured == read_repo_version()


def test_render_full_matches_on_disk_agents_md():
    """render_full output must equal the committed product/AGENTS.md.

    This is the no-drift proof: the same content `lfg generate` writes. The
    on-disk file is written as LF/UTF-8 with a single trailing newline by the
    generate command, and render_full emits the same, so a plain UTF-8 read
    compares equal with no trailing-newline fixup needed.
    """
    fragments = _load_fragments()
    on_disk = (ROOT / "product" / "AGENTS.md").read_text(encoding="utf-8")
    assert render_full(fragments) == on_disk


def test_explicit_version_is_honored():
    """render_block(version=...) lets callers pin a version without VERSION.json."""
    fragments = _load_fragments()
    block = render_block(fragments, version="9.9.9")
    captured = SPEC_BEGIN_RE.match(block.splitlines()[0]).group(1)
    assert captured == "9.9.9"
    # Interior still round-trips to render_full regardless of the version token.
    assert strip_block_markers(block) == render_full(fragments)
