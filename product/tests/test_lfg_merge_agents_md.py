"""Tests for the `lfg merge-agents-md` subcommand (Spec 4 §1 / T5).

Drives the CLI via subprocess (matching test_lfg_archive.py style). Covers:
fresh target creation, idempotent re-run, user-authored prepend (+ --no-wrap),
and the forward-version refusal / --force-downgrade escape hatch.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(LFG)] + args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_fresh_target_creates_file_with_markers(tmp_path):
    target = tmp_path / "AGENTS.md"
    r = _run(["merge-agents-md", "--to", str(target)])
    assert r.returncode == 0, r.stderr
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "<!-- LFG:BEGIN v" in content
    assert "<!-- LFG:END -->" in content
    assert "Updated" in r.stdout


def test_run_twice_is_idempotent(tmp_path):
    target = tmp_path / "AGENTS.md"
    r1 = _run(["merge-agents-md", "--to", str(target)])
    assert r1.returncode == 0, r1.stderr
    first_bytes = target.read_bytes()

    r2 = _run(["merge-agents-md", "--to", str(target)])
    assert r2.returncode == 0, r2.stderr
    assert "already up to date" in r2.stdout
    # File untouched, byte-for-byte.
    assert target.read_bytes() == first_bytes


def test_user_authored_file_prepends_and_preserves(tmp_path):
    target = tmp_path / "AGENTS.md"
    user_content = (
        "# AGENTS.md\n"
        "\n"
        "Hand-authored instructions for coding agents.\n"
        "\n"
        "## Build\n"
        "Run `make build`.\n"
    )
    target.write_text(user_content, encoding="utf-8", newline="\n")

    r = _run(["merge-agents-md", "--to", str(target)])
    assert r.returncode == 0, r.stderr
    content = target.read_text(encoding="utf-8")
    # Block prepended at the top, user content preserved below.
    assert content.startswith("<!-- LFG:BEGIN v")
    assert "Hand-authored instructions for coding agents." in content
    assert "Run `make build`." in content


def test_no_wrap_respected_on_lfg_looking_file(tmp_path):
    target = tmp_path / "AGENTS.md"
    # A pre-marker LFG-looking file (frontmatter doc: AGENTS).
    lfg_like = (
        "---\n"
        "doc: AGENTS\n"
        "---\n"
        "\n"
        "# Old pre-marker LFG body\n"
        "Marker-sentinel-line-to-detect.\n"
    )
    target.write_text(lfg_like, encoding="utf-8", newline="\n")

    r = _run(["merge-agents-md", "--to", str(target), "--no-wrap"])
    assert r.returncode == 0, r.stderr
    content = target.read_text(encoding="utf-8")
    # --no-wrap treats LFG-looking content as user content: block prepended,
    # old content preserved below rather than discarded.
    assert content.startswith("<!-- LFG:BEGIN v")
    assert "Marker-sentinel-line-to-detect." in content


def test_corrupt_begin_without_end_refuses_does_not_prepend(tmp_path):
    # BLOCKER 1: a BEGIN with no END must error (non-zero) and leave the file
    # untouched — never prepend a second BEGIN that a later merge mis-slices.
    target = tmp_path / "AGENTS.md"
    corrupt = (
        "# User notes\n"
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "orphaned body, no end marker\n"
    )
    target.write_text(corrupt, encoding="utf-8", newline="\n")
    before = target.read_bytes()

    r = _run(["merge-agents-md", "--to", str(target)])
    assert r.returncode != 0
    assert "corrupt" in r.stderr.lower()
    # File untouched, byte-for-byte — no second BEGIN injected.
    assert target.read_bytes() == before


def test_corrupt_begin_without_end_refuses_even_with_no_wrap(tmp_path):
    # The corrupt-marker error fires regardless of --no-wrap.
    target = tmp_path / "AGENTS.md"
    corrupt = (
        "<!-- LFG:BEGIN v0.3.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "orphaned body\n"
    )
    target.write_text(corrupt, encoding="utf-8", newline="\n")
    before = target.read_bytes()

    r = _run(["merge-agents-md", "--to", str(target), "--no-wrap"])
    assert r.returncode != 0
    assert "corrupt" in r.stderr.lower()
    assert target.read_bytes() == before


def test_user_authored_prepend_announces_preservation(tmp_path):
    # SHOULD-FIX 4: prepend case prints a specific message about preservation.
    target = tmp_path / "AGENTS.md"
    target.write_text(
        "# AGENTS.md\nHand-authored.\n", encoding="utf-8", newline="\n"
    )
    r = _run(["merge-agents-md", "--to", str(target)])
    assert r.returncode == 0, r.stderr
    assert "preserved" in r.stdout.lower()
    assert "prepended" in r.stdout.lower()


def test_newer_marker_refuses_without_force_succeeds_with(tmp_path):
    target = tmp_path / "AGENTS.md"
    newer = (
        "<!-- LFG:BEGIN v99.0.0 — DO NOT EDIT BETWEEN THESE MARKERS -->\n"
        "future body\n"
        "<!-- LFG:END -->\n"
    )
    target.write_text(newer, encoding="utf-8", newline="\n")

    # Without --force-downgrade: refuse, non-zero, file untouched.
    before = target.read_bytes()
    r1 = _run(["merge-agents-md", "--to", str(target)])
    assert r1.returncode != 0
    assert "force-downgrade" in r1.stderr
    assert target.read_bytes() == before

    # With --force-downgrade: succeeds, future body replaced.
    r2 = _run(["merge-agents-md", "--to", str(target), "--force-downgrade"])
    assert r2.returncode == 0, r2.stderr
    content = target.read_text(encoding="utf-8")
    assert "future body" not in content
    assert "<!-- LFG:BEGIN v" in content


def test_bom_crlf_managed_file_is_renormalized(tmp_path):
    """A managed AGENTS.md re-saved with a UTF-8 BOM + CRLF must NOT be treated
    as up-to-date — the idempotency check compares raw bytes, so it gets a
    normalizing rewrite to clean UTF-8/LF (encoding policy honored)."""
    target = tmp_path / "AGENTS.md"
    # First produce a clean managed file.
    r1 = _run(["merge-agents-md", "--to", str(target)])
    assert r1.returncode == 0, r1.stderr
    clean = target.read_bytes()

    # Re-save it with a UTF-8 BOM and CRLF line endings (Notepad-style).
    target.write_bytes(b"\xef\xbb\xbf" + clean.replace(b"\n", b"\r\n"))
    assert target.read_bytes()[:3] == b"\xef\xbb\xbf"
    assert b"\r\n" in target.read_bytes()

    # Re-run: must rewrite (not "already up to date") and normalize the bytes.
    r2 = _run(["merge-agents-md", "--to", str(target)])
    assert r2.returncode == 0, r2.stderr
    assert "already up to date" not in r2.stdout
    after = target.read_bytes()
    assert after[:3] != b"\xef\xbb\xbf"  # BOM gone
    assert b"\r\n" not in after  # CRLF gone
    assert after == clean  # back to canonical bytes
