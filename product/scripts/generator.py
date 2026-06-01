"""Generator: fragments -> AGENTS.md.

Pure functions: parse_fragment(path) returns (frontmatter_dict, body_str).

Rendering has one primitive and two wrappers (Spec 4 §1):
  - render_canonical_body(fragments) -> the canonical AGENTS.md content
    (frontmatter + intro + section index + all fragment bodies), no markers.
  - render_full(fragments) -> alias for render_canonical_body. This is what
    writes the in-repo product/AGENTS.md (fully LFG-owned, no markers).
  - render_block(fragments) -> the canonical body wrapped in LFG:BEGIN/END
    managed-block markers. Used by the install/update merge.

render_agents_md remains as a backward-compatible alias for render_full so
existing callers (lfg.py `generate`) keep producing byte-identical output.
None of these do I/O on AGENTS.md itself — the caller writes.

Output is LF, UTF-8 (no BOM), single trailing newline. Fails loudly on
malformed frontmatter or above-budget output. Same inputs => byte-identical
output (idempotent).
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AGENTS_TOKEN_BUDGET = 4500  # chars/4 heuristic. Re-bumped to 4500 after T11's
# subagent contract block landed AGENTS.md at 3999/4000 — zero headroom would
# break the gate on any subsequent fragment edit. 4500 keeps growth bounded
# (~4.5% of a 100k context) and leaves ~500 tokens of editing slack. If this
# starts climbing toward 4500, that's a real signal to compress, not to raise.
# History: Spec 2 designed 3000 → measured 3772 → bumped to 4000 (T6) →
# T11 contract pushed near 4000 → bumped to 4500 (T13).


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


def render_canonical_body(fragments: List[Tuple[Dict[str, Any], str]]) -> str:
    """Emit the canonical AGENTS.md content (no enclosing markers).

    This is the single source of truth for AGENTS.md content: frontmatter +
    intro + available commands + section index + all fragment bodies. It is
    exactly what product/AGENTS.md contains today.
    """
    # Keep only fragments destined for AGENTS.md; sort by order.
    in_agents = [f for f in fragments if "agents_md" in f[0].get("targets", [])]
    in_agents.sort(key=lambda fb: fb[0]["order"])

    lines: List[str] = []
    # 1. Own frontmatter
    lines += [
        "---",
        "doc: AGENTS",
        "related:",
        "  state: ./logs/STATE.md",
        "  changelog: ./logs/CHANGELOG.md",
        "  devlog: ./logs/DEVLOG.md",
        "---",
        "",
    ]
    # 2. Read this first
    lines += [
        "# Log File Genius — AGENTS guidance",
        "",
        "**Read this first.** This project uses Log File Genius. To orient cold:",
        "",
        "- `logs/STATE.md` — the now (current context + last session)",
        "- `logs/CHANGELOG.md` Unreleased — recent changes",
        "- `logs/DEVLOG.md` Daily Log — why decisions were made",
        "",
    ]
    # 3. Available commands
    lines += [
        "## Available commands",
        "",
        "- `lfg validate` — validate log files (format + token budget)",
        "- `lfg prime [--n N]` — emit a subagent context digest (the lead pastes this into a subagent prompt to establish role + give context)",
        "- `lfg promote <id>` — lead-only; promote a subagent's staged entries to canonical CHANGELOG/DEVLOG",
        "- `lfg status` — quick project status",
        "- `lfg generate` — regenerate AGENTS.md from product/rules/ fragments (LFG contributors)",
        "",
    ]
    # 4. Section index
    lines += ["## Sections", ""]
    for fm, _ in in_agents:
        lines.append(f"- **{fm['fragment']}** — {fm['summary']}")
    lines.append("")
    # 5. Fragments
    for fm, body in in_agents:
        lines.append(f"## {fm['fragment']}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")

    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"

    # Hard budget gate
    tokens = len(out) // 4
    if tokens > AGENTS_TOKEN_BUDGET:
        raise GeneratorError(
            f"AGENTS.md exceeds token budget ({tokens} > {AGENTS_TOKEN_BUDGET}); "
            "compress fragments or raise the budget intentionally"
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
# guarantees byte-identical output (the CI drift gate `lfg generate --check`).
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
) -> str:
    """Wrap the canonical body in LFG:BEGIN/END managed-block markers.

    The BEGIN marker captures the running LFG version (from VERSION.json by
    default). Used by the install/update merge so the block can be located and
    rewritten in place without clobbering surrounding user content.

    Output is LF, UTF-8-safe, single trailing newline.
    """
    if version is None:
        version = read_repo_version()
    body = render_canonical_body(fragments)
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
