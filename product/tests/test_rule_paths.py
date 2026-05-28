"""Guard: every `.log-file-genius/<dir>/` path in the installed rules must
reference the actual installed layout (`.log-file-genius/product/<dir>/`).

Pre-cleanup, several rule files inherited paths from before the product/project
split (ADR-008) — e.g. `.log-file-genius/templates/` instead of
`.log-file-genius/product/templates/`. Agents following those got 404s. This
test scans all rule files for any `.log-file-genius/(templates|docs|scripts)/`
reference and verifies it includes the `product/` segment.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Spec 2 canonical-fragments layout: scan product/rules/ for stale paths.
# product/ai-rules/claude-code/project_instructions.md is retained transiently
# until the install-template task; include it in the scan so we catch any stale
# paths it still has.
RULE_DIRS = [
    ROOT / "product/rules",
    ROOT / "product/ai-rules/claude-code",
]
# Any path under .log-file-genius/ that targets a known subdir must go through
# /product/. The repo-root `.log-file-genius/.git` etc. are not targets.
STALE_PATTERN = re.compile(r"\.log-file-genius/(?!product/)(templates|docs|scripts)/")


def test_no_stale_submodule_paths_in_rules():
    offenders = []
    for d in RULE_DIRS:
        for f in d.glob("*.md"):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                m = STALE_PATTERN.search(line)
                if m:
                    offenders.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not offenders, (
        "Stale '.log-file-genius/<dir>/' paths missing the '/product/' segment "
        "(agents will hit 404s):\n  " + "\n  ".join(offenders)
    )


def test_installer_doc_link_points_at_product():
    # The installer prints a 'Documentation: ...' line on success. It must
    # reference the actual installed location of log_file_how_to.md, which is
    # under product/.
    for installer in ("install.sh", "install.ps1"):
        txt = (ROOT / "product/scripts" / installer).read_text(encoding="utf-8")
        assert ".log-file-genius/docs/log_file_how_to.md" not in txt, (
            f"{installer} prints a broken doc link (missing /product/ segment)"
        )
        assert ".log-file-genius/product/docs/log_file_how_to.md" in txt, (
            f"{installer} no longer prints the docs link at all"
        )


# Spec 1 had a test asserting install.sh/.ps1 skip project_instructions.md when
# copying .claude/rules/ contents — that whole copy pattern was replaced in
# Spec 2 (install.sh now walks product/rules/ fragments and routes by frontmatter
# `targets`; project_instructions is rendered from a template, not copied). The
# semantic replacement — "no duplicate project_instructions in .claude/rules/" —
# is asserted end-to-end by T18's cross-platform smoke tests against a real
# install. Test removed to keep the guard meaningful.
