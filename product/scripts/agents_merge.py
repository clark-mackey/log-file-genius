"""Managed-block AGENTS.md merge engine (Spec 4 §1).

The P0 data-safety core: lets LFG co-exist with a user-owned AGENTS.md instead
of clobbering it. The generated content lives between HTML-comment markers:

    <!-- LFG:BEGIN v0.4.0 — DO NOT EDIT BETWEEN THESE MARKERS -->
    <generated body>
    <!-- LFG:END -->

`merge_into_existing` decides, given the current file contents and a freshly
rendered block, what the new file should be — preserving user content above and
below the markers, refusing to downgrade a newer-managed block, and recognizing
a pre-marker LFG AGENTS.md (the v0.3.0 bridge) by fingerprint.

Pure string logic + a pair of encoding-safe IO helpers (mirroring archive.py's
patterns). No argparse, no side effects at import — the CLI wiring is T5.

Encoding & atomicity policy (Spec 4 §1):
  - Read with utf-8-sig (strips BOM), normalize CRLF/CR -> LF.
  - Write LF, UTF-8, no BOM, atomically (tmp file + fsync + os.replace).
"""
from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path
from typing import Optional

# --- Markers (mirror generator.py / the spec's strict regex) ----------------

LFG_BEGIN_RE = re.compile(r"<!--\s*LFG:BEGIN\s+v(?P<ver>\S+)\s*(?:—[^>]*)?-->")
LFG_END_LIT = "<!-- LFG:END -->"


class ForwardVersionError(Exception):
    """Raised when the existing managed block was written by a newer LFG.

    Refuses to silently overwrite a future block schema. The CLI offers
    --force-downgrade as the escape hatch (a separate path that does not call
    this with the refusal in place).
    """


# --- Version comparator (reuse check-version.py; do not reinvent semver) -----
#
# check-version.py has a hyphen in its name and is not importable by `import`,
# so load it once via importlib from its file path (same approach the existing
# test_check_version.py uses).

def _load_compare_versions():
    scripts_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "_lfg_check_version", scripts_dir / "check-version.py"
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError("could not load check-version.py for version comparison")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compare_versions


_compare_versions = _load_compare_versions()


# --- Fingerprint -------------------------------------------------------------

def _parse_leading_frontmatter(content: str) -> Optional[dict[str, str]]:
    """Parse a leading `---`-delimited YAML frontmatter block into a flat dict.

    Only the top-level `key: value` lines are captured (enough for the doc:
    AGENTS check). Returns None when the file does not open with a frontmatter
    block. Leading whitespace/blank lines before the first `---` are tolerated.
    """
    lines = content.splitlines()
    # Skip leading blank lines.
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx >= len(lines) or lines[idx].strip() != "---":
        return None

    fm: dict[str, str] = {}
    for line in lines[idx + 1:]:
        if line.strip() == "---":
            return fm
        if ":" not in line:
            continue
        # Only capture top-level (non-indented) keys.
        if line[:1] in (" ", "\t"):
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    # No closing delimiter found -> not a well-formed frontmatter block.
    return None


def looks_like_lfg(content: str) -> bool:
    """Fingerprint an unmarked AGENTS.md as LFG-generated (pre-marker bridge).

    PRIMARY signal (sufficient alone): YAML frontmatter with a `doc: AGENTS`
    line. Present in v0.3.0 and HEAD; absent from hand-authored / Codex /
    Aider AGENTS.md files.

    DEFENSIVE fallback (only when frontmatter is absent/stripped) — TRUE if
    >=2 of:
      - 'Log File Genius' in the first 200 chars
      - all of 'lfg validate', 'lfg prime', 'lfg generate'
      - all of 'logs/STATE.md', 'logs/CHANGELOG.md', 'logs/DEVLOG.md'
    """
    if not content:
        return False

    # Primary: frontmatter doc: AGENTS.
    fm = _parse_leading_frontmatter(content)
    if fm is not None and fm.get("doc") == "AGENTS":
        return True

    # Defensive fallback.
    head = content[:200]
    signals = 0
    if "Log File Genius" in head:
        signals += 1
    if all(cmd in content for cmd in ("lfg validate", "lfg prime", "lfg generate")):
        signals += 1
    if all(
        path in content
        for path in ("logs/STATE.md", "logs/CHANGELOG.md", "logs/DEVLOG.md")
    ):
        signals += 1
    return signals >= 2


# --- Merge -------------------------------------------------------------------

def merge_into_existing(
    existing: Optional[str],
    block: str,
    running_version: str,
    allow_wrap: bool = True,
) -> str:
    """Return the new AGENTS.md content.

    1. existing is None or blank -> return block (fresh install).
    2. existing has BEGIN + END markers:
         - captured version > running_version -> raise ForwardVersionError.
         - else replace everything from BEGIN through END (inclusive) with
           block; content before BEGIN and after END is preserved verbatim.
    3. existing has no markers + looks_like_lfg + allow_wrap -> return block.
    4. existing has no markers + (not LFG or allow_wrap False) -> prepend
       block + blank line at the top, keep all user content below.
    """
    if existing is None or existing.strip() == "":
        return block

    begin_match = LFG_BEGIN_RE.search(existing)
    end_idx = existing.find(LFG_END_LIT)

    # Case 2: a complete managed block is present.
    if begin_match is not None and end_idx != -1 and end_idx > begin_match.start():
        captured = begin_match.group("ver")
        if _compare_versions(captured, running_version) > 0:
            raise ForwardVersionError(
                f"AGENTS.md was managed by a newer LFG (v{captured} > "
                f"v{running_version}). Upgrade the submodule or pass "
                f"--force-downgrade."
            )
        before = existing[: begin_match.start()]
        after = existing[end_idx + len(LFG_END_LIT):]
        # block ends in exactly one "\n". Absorb a single newline that follows
        # the END literal into the managed region so the block/after boundary is
        # not double-counted — this keeps the merge idempotent when user content
        # sits below the block (re-running the merge reproduces the same `after`).
        if after.startswith("\n"):
            after = after[1:]
        return before + block + after

    # Case 3: pre-marker LFG content (e.g. a v0.3.0 install) + wrap allowed.
    #
    # The spec describes this as "wrap the entire existing content in markers,
    # then replace the interior with block." Wrapping freshly and then replacing
    # the interior with `block` discards the old body entirely, so the net
    # result is simply `block`. That is intended: the old unmarked body is stale
    # LFG content being regenerated — no user content is lost because there is
    # none outside the (notional) markers. Returning `block` is the correct,
    # simplest implementation of that equivalence.
    if begin_match is None and allow_wrap and looks_like_lfg(existing):
        return block

    # Case 4: user-authored content (or wrapping disabled). Prepend the block,
    # keep all user content below, untouched.
    return block + "\n" + existing


# --- Encoding / IO helpers (mirror archive.py style) -------------------------

def read_text_normalized(path: str | os.PathLike[str]) -> str:
    """Read a file as text: strip a UTF-8 BOM, normalize line endings to LF.

    Returns "" if the file does not exist. Marker regexes operate on the
    normalized content only (Spec 4 §1).
    """
    p = Path(path)
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def atomic_write(path: str | os.PathLike[str], content: str) -> None:
    """Write content atomically as UTF-8, LF, no BOM.

    Writes to <path>.lfg-tmp, flushes + fsyncs, then os.replace() onto the
    target. A crash mid-write leaves the original file intact.
    """
    p = Path(path)
    tmp = p.with_name(p.name + ".lfg-tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)
