"""Validate on-demand rule fragments and render compact shared startup guidance.

render_canonical_body is the rendering primitive. render_full and render_agents_md
retain the public generator interface; render_block adds install/update markers.
Detailed procedures remain in ordinary product/rules and product/docs files.
Output is deterministic LF/UTF-8 with a single trailing newline and a 250-token cap.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AGENTS_TOKEN_BUDGET = 250  # Compact startup; full procedures are read on demand.


class GeneratorError(ValueError):
    pass


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Parse the supported fragment-frontmatter subset.

    Supported:
      key: scalar          # plain string/integer
      key: "quoted string" # single or double quotes
      key: a, b, c         # inline comma-separated list (used for `targets`)
      key: [a, b, c]       # inline bracketed list (also accepted for `targets`)
      # comment            # full-line comments only

    NOT supported (use inline list instead):
      key:
        - a
        - b
    A YAML block list will be silently parsed as an empty string. Fragments
    must use the inline form; `test_fragments.py` enforces frontmatter shape.
    """
    fm: Dict[str, Any] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            raise GeneratorError(f"bad frontmatter line: {s!r}")
        k, _, v = s.partition(":")
        k = k.strip()
        v = v.strip()
        if k == "order":
            try:
                fm[k] = int(v)
            except ValueError as e:
                raise GeneratorError(f"'order' must be an integer, got {v!r}") from e
        elif k == "targets":
            v = v.lstrip("[").rstrip("]")
            fm[k] = [t.strip() for t in v.split(",") if t.strip()]
        else:
            if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                v = v[1:-1]
            fm[k] = v
    return fm


def parse_fragment(path: Path) -> Tuple[Dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise GeneratorError(f"{path.name}: missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise GeneratorError(f"{path.name}: unterminated frontmatter")
    fm = _parse_frontmatter(text[4:end])
    body = text[end + 5:]  # skip past closing '\n---\n'
    return fm, body


def render_canonical_body(fragments, root=None):
    from startup import render
    out = render(root)
    tokens = (len(out) + 3) // 4
    if tokens > AGENTS_TOKEN_BUDGET:
        raise GeneratorError(
            f"AGENTS.md exceeds token budget ({tokens} > {AGENTS_TOKEN_BUDGET}); "
            "shorten configured paths or startup guidance; do not omit constraints"
        )
    return out


def render_full(fragments: List[Tuple[Dict[str, Any], str]]) -> str:
    """Return the canonical body unchanged.

    Used to emit the in-repo product/AGENTS.md, which is fully LFG-owned and
    carries no markers.
    """
    return render_canonical_body(fragments)


# Backward-compatible alias for the original public entry point. lfg.py's
# `generate` command imports this name; keeping it identical to render_full
# guarantees byte-identical output (the CI drift gate `python3 .log-file-genius/product/scripts/lfg.py generate --check`).
render_agents_md = render_full


# --- Managed-block markers (Spec 4 §1) --------------------------------------

# BEGIN line uses an em-dash separator exactly as the spec shows. The strip
# regex below matches the spec's strict BEGIN regex so render_block output is
# round-trippable back to render_full output.
_BLOCK_BEGIN_TEMPLATE = "<!-- LFG:BEGIN v{version} — DO NOT EDIT BETWEEN THESE MARKERS -->"
_BLOCK_END = "<!-- LFG:END -->"

# Mirror of the spec's BEGIN-marker regex:
#   <!--\s*LFG:BEGIN\s+v(\S+)\s*(?:—[^>]*)?-->
_BLOCK_BEGIN_RE = re.compile(r"<!--\s*LFG:BEGIN\s+v(\S+)\s*(?:—[^>]*)?-->")


def read_repo_version() -> str:
    """Read the `version` field from product/VERSION.json.

    Follows the same lookup pattern as check-version.py: VERSION.json lives in
    the product/ directory (the parent of this scripts/ dir).
    """
    version_file = Path(__file__).resolve().parent.parent / "VERSION.json"
    with open(version_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    version = manifest.get("version")
    if not version:
        raise GeneratorError(f"VERSION.json missing 'version' field at {version_file}")
    return str(version)


def render_block(
    fragments: List[Tuple[Dict[str, Any], str]],
    version: Optional[str] = None,
    root: Optional[Path] = None,
) -> str:
    """Wrap the canonical body in LFG:BEGIN/END managed-block markers.

    The BEGIN marker captures the running LFG version (from VERSION.json by
    default). Used by the install/update merge so the block can be located and
    rewritten in place without clobbering surrounding user content.

    Output is LF, UTF-8-safe, single trailing newline.
    """
    if version is None:
        version = read_repo_version()
    body = render_canonical_body(fragments, root=root)
    begin = _BLOCK_BEGIN_TEMPLATE.format(version=version)
    # body already ends in exactly one "\n"; emit BEGIN + body + END + newline.
    return f"{begin}\n{body}{_BLOCK_END}\n"


def strip_block_markers(text: str) -> str:
    """Inverse of render_block: return the canonical body inside the markers.

    Strips the BEGIN line (matching the spec's strict regex) and the literal
    END line, returning the interior byte-for-byte as render_full would emit
    it. Raises GeneratorError if the markers are not found.
    """
    begin_match = _BLOCK_BEGIN_RE.search(text)
    if begin_match is None:
        raise GeneratorError("no LFG:BEGIN marker found")
    end_idx = text.find(_BLOCK_END)
    if end_idx == -1:
        raise GeneratorError("no LFG:END marker found")

    # Interior starts after the BEGIN line's trailing newline.
    body_start = text.find("\n", begin_match.end())
    if body_start == -1:
        raise GeneratorError("malformed block: BEGIN marker has no following newline")
    body_start += 1
    return text[body_start:end_idx]
