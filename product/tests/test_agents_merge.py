"""Tests for the managed-block AGENTS.md merge engine (Spec 4 §1 / T4).

Covers every spec row: fresh install, markers-present interior replacement,
forward-version refusal, the pre-marker LFG fingerprint bridge (loaded from
`git show v0.3.0:product/AGENTS.md`), user-authored prepend, the --no-wrap
escape hatch, CRLF+BOM normalization, idempotency, and atomicity.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from agents_merge import (  # noqa: E402
    LFG_BEGIN_RE,
    LFG_END_LIT,
    ForwardVersionError,
    atomic_write,
    looks_like_lfg,
    merge_into_existing,
    read_text_normalized,
)

RUNNING = "0.4.0"

# A representative rendered block (BEGIN + body + END), as render_block emits.
BLOCK = (
    "<!-- LFG:BEGIN v0.4.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
    "---\n"
    "doc: AGENTS\n"
    "---\n"
    "\n"
    "# Log File Genius — AGENTS guidance\n"
    "\n"
    "Generated content here.\n"
    "<!-- LFG:END -->\n"
)


# --- Fixtures ----------------------------------------------------------------

def _v030_agents_md() -> str:
    """The only historical LFG AGENTS.md (v0.3.0), loaded via git show."""
    repo_root = Path(__file__).resolve().parents[2]
    out = subprocess.run(
        ["git", "show", "v0.3.0:product/AGENTS.md"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    # Decode explicitly as UTF-8 (the file contains an em-dash); the Windows
    # console default (cp1252) would choke on it.
    return out.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


CODEX_AGENTS_MD = """\
# AGENTS.md

This file gives instructions to coding agents working in this repo.

## Build
Run `make build` to compile.

## Conventions
- Use tabs, not spaces.
- Keep functions short.
"""


# --- looks_like_lfg ----------------------------------------------------------

def test_looks_like_lfg_primary_frontmatter_signal():
    content = "---\ndoc: AGENTS\nrelated:\n  state: ./logs/STATE.md\n---\n\n# Hi\n"
    assert looks_like_lfg(content) is True


def test_looks_like_lfg_tolerates_leading_blank_lines():
    content = "\n\n---\ndoc: AGENTS\n---\n"
    assert looks_like_lfg(content) is True


def test_looks_like_lfg_v030_fixture_is_lfg():
    content = _v030_agents_md()
    assert looks_like_lfg(content) is True


def test_looks_like_lfg_codex_file_is_not_lfg():
    assert looks_like_lfg(CODEX_AGENTS_MD) is False


def test_looks_like_lfg_empty_is_false():
    assert looks_like_lfg("") is False


def test_looks_like_lfg_defensive_fallback_two_signals():
    # No frontmatter, but two distinctive signals: command list + 5-doc paths.
    content = (
        "# Some doc\n"
        "Use lfg validate, lfg prime, lfg generate.\n"
        "See logs/STATE.md, logs/CHANGELOG.md, logs/DEVLOG.md.\n"
    )
    assert looks_like_lfg(content) is True


def test_looks_like_lfg_defensive_fallback_one_signal_is_false():
    # Only the command list signal; one signal is not enough.
    content = "Use lfg validate, lfg prime, lfg generate.\n"
    assert looks_like_lfg(content) is False


def test_looks_like_lfg_doc_other_value_not_lfg():
    content = "---\ndoc: README\n---\n\n# Not us\n"
    assert looks_like_lfg(content) is False


# --- merge_into_existing: case 1 (fresh) -------------------------------------

def test_merge_fresh_none_returns_block():
    assert merge_into_existing(None, BLOCK, RUNNING) == BLOCK


def test_merge_fresh_blank_returns_block():
    assert merge_into_existing("   \n\n  ", BLOCK, RUNNING) == BLOCK


# --- merge_into_existing: case 2 (markers present) ---------------------------

def test_merge_markers_present_replaces_interior_preserves_surroundings():
    existing = (
        "# My personal notes above the block\n"
        "Keep this line.\n"
        "\n"
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "old generated body\n"
        "<!-- LFG:END -->\n"
        "\n"
        "## My notes below the block\n"
        "Keep this too.\n"
    )
    result = merge_into_existing(existing, BLOCK, RUNNING)
    assert "# My personal notes above the block" in result
    assert "Keep this line." in result
    assert "## My notes below the block" in result
    assert "Keep this too." in result
    # Old body gone, new block present.
    assert "old generated body" not in result
    assert "Generated content here." in result
    # The new block sits exactly where the old one was. block ends in a "\n";
    # the merge absorbs one newline that followed END, so the blank line that
    # separated the old block from the notes below is reproduced exactly once.
    expected = (
        "# My personal notes above the block\n"
        "Keep this line.\n"
        "\n"
        + BLOCK
        + "\n"
        "## My notes below the block\n"
        "Keep this too.\n"
    )
    assert result == expected


def test_merge_forward_version_raises():
    existing = (
        "<!-- LFG:BEGIN v99.0.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "future body\n"
        "<!-- LFG:END -->\n"
    )
    with pytest.raises(ForwardVersionError):
        merge_into_existing(existing, BLOCK, RUNNING)


def test_merge_forward_version_force_downgrade_replaces_no_raise():
    existing = (
        "<!-- LFG:BEGIN v99.0.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "future body\n"
        "<!-- LFG:END -->\n"
    )
    # With force_downgrade, the newer-marker check is skipped and the interior
    # is replaced anyway (the lone trailing newline after END is absorbed).
    result = merge_into_existing(existing, BLOCK, RUNNING, force_downgrade=True)
    assert result == BLOCK
    assert "future body" not in result


def test_merge_equal_version_replaces_no_raise():
    existing = (
        "<!-- LFG:BEGIN v0.4.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "same-version body\n"
        "<!-- LFG:END -->\n"
    )
    result = merge_into_existing(existing, BLOCK, RUNNING)
    # The lone trailing newline after END is absorbed into the managed region.
    assert result == BLOCK


# --- merge_into_existing: case 3 (no markers + LFG fingerprint) --------------

def test_merge_v030_no_markers_returns_block():
    existing = _v030_agents_md()
    assert LFG_BEGIN_RE.search(existing) is None  # confirm fixture has no markers
    result = merge_into_existing(existing, BLOCK, RUNNING)
    assert result == BLOCK


# --- merge_into_existing: case 4 (user-authored) -----------------------------

def test_merge_codex_prepends_block_preserves_user_content():
    result = merge_into_existing(CODEX_AGENTS_MD, BLOCK, RUNNING)
    assert result == BLOCK + "\n" + CODEX_AGENTS_MD
    # User content still fully present.
    assert "Run `make build` to compile." in result
    assert "Use tabs, not spaces." in result
    # Block is at the top.
    assert result.startswith(BLOCK)


def test_merge_no_wrap_on_lfg_file_prepends_instead_of_wrapping():
    existing = _v030_agents_md()
    result = merge_into_existing(existing, BLOCK, RUNNING, allow_wrap=False)
    # With wrapping disabled, LFG-looking content is treated as user content:
    # block prepended, old content preserved below.
    assert result == BLOCK + "\n" + existing
    assert existing in result


# --- Idempotency -------------------------------------------------------------

def test_merge_idempotent_markers_present():
    existing = (
        "# Note above\n"
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "old body\n"
        "<!-- LFG:END -->\n"
        "# Note below\n"
    )
    once = merge_into_existing(existing, BLOCK, RUNNING)
    twice = merge_into_existing(once, BLOCK, RUNNING)
    assert once == twice


# --- Encoding / IO -----------------------------------------------------------

def test_read_text_normalized_strips_bom_and_normalizes_crlf(tmp_path):
    path = tmp_path / "AGENTS.md"
    raw = (
        "﻿"  # UTF-8 BOM
        "# Note above\r\n"
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\r\n"
        "old body\r\n"
        "<!-- LFG:END -->\r\n"
    )
    path.write_bytes(raw.encode("utf-8"))

    content = read_text_normalized(path)
    assert "\r" not in content
    assert not content.startswith("﻿")
    # Markers still detected on normalized content.
    assert LFG_BEGIN_RE.search(content) is not None
    assert LFG_END_LIT in content


def test_read_text_normalized_missing_file_returns_empty(tmp_path):
    assert read_text_normalized(tmp_path / "nope.md") == ""


def test_atomic_write_round_trip_is_clean_lf_no_bom(tmp_path):
    path = tmp_path / "AGENTS.md"
    atomic_write(path, BLOCK)
    raw = path.read_bytes()
    assert b"\r" not in raw
    assert not raw.startswith(b"\xef\xbb\xbf")  # no UTF-8 BOM
    assert raw.decode("utf-8") == BLOCK
    # No leftover tmp file.
    assert not (tmp_path / "AGENTS.md.lfg-tmp").exists()


def test_crlf_bom_input_full_round_trip(tmp_path):
    """Notepad-edited file: read normalizes, merge runs, write is clean."""
    path = tmp_path / "AGENTS.md"
    raw = (
        "﻿"
        "# User note\r\n"
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\r\n"
        "old body\r\n"
        "<!-- LFG:END -->\r\n"
    )
    path.write_bytes(raw.encode("utf-8"))

    existing = read_text_normalized(path)
    merged = merge_into_existing(existing, BLOCK, RUNNING)
    atomic_write(path, merged)

    out = path.read_bytes()
    assert b"\r" not in out
    assert not out.startswith(b"\xef\xbb\xbf")
    text = out.decode("utf-8")
    assert "# User note" in text
    assert "Generated content here." in text
    assert "old body" not in text


# --- Atomicity ---------------------------------------------------------------

def test_atomic_write_failure_before_replace_leaves_original(tmp_path, monkeypatch):
    path = tmp_path / "AGENTS.md"
    original = "ORIGINAL CONTENT\n"
    path.write_text(original, encoding="utf-8", newline="\n")
    original_bytes = path.read_bytes()

    def boom(src, dst):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", boom)

    with pytest.raises(OSError):
        atomic_write(path, "NEW CONTENT THAT MUST NOT LAND\n")

    # Original file is byte-for-byte unchanged.
    assert path.read_bytes() == original_bytes
