"""Generator: fragments -> AGENTS.md.

Pure functions: parse_fragment(path) returns (frontmatter_dict, body_str);
render_agents_md(fragments) returns the rendered AGENTS.md string. Neither
function does I/O on AGENTS.md itself — the caller writes.

Output is LF, UTF-8 (no BOM), single trailing newline. Fails loudly on
malformed frontmatter or above-budget output. Same inputs => byte-identical
output (idempotent).
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

AGENTS_TOKEN_BUDGET = 4000  # chars/4 heuristic. Measured 3772 tokens for the
# current 4-fragment set (post-Spec-1 + headers/index). Spec 2's original 3000
# target was set during design without measuring the actual concat. Trimming
# fragments would weaken their primary purpose (always-active rules), so the
# budget is raised to 4000 — still bounded (under 5% of a 100k context), still
# fails-loudly on unbounded growth, with headroom for the subagent contract
# block T11 adds.


class GeneratorError(ValueError):
    pass


def _parse_frontmatter(text: str) -> Dict[str, Any]:
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


def render_agents_md(fragments: List[Tuple[Dict[str, Any], str]]) -> str:
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
