"""Guards for the Phase 4 rule edits:
  - no directive dropped during the token diet (completeness gate),
  - SESSION START/END now reference STATE (not DEVLOG Current Context),
  - no hardcoded docs/planning/ paths,
  - the budget contradiction string is gone (deferred here from the budget test).
Snapshot of required directives: docs/superpowers/specs/2026-05-27-rule-directives.md
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = [
    ROOT / "product/ai-rules/claude-code/log-file-maintenance.md",
    ROOT / "product/ai-rules/augment/log-file-maintenance.md",
]
RULE_DIRS = [ROOT / "product/ai-rules/claude-code", ROOT / "product/ai-rules/augment"]

REQUIRED_HEADINGS = [
    "MANDATORY RULE",
    "BEFORE EVERY COMMIT",
    "AFTER EVERY COMMIT",
    "FAILURE DETECTION",
    "SESSION START",
    "SESSION END",
    "TOKEN SELF-ASSESSMENT",
    "ENTRY VERBOSITY",
    "CROSS-REFERENCES",
    "ARCHIVAL",
    "TEMPLATES",
    "SUCCESS CRITERIA",
]


def test_no_directive_dropped_during_compression():
    for rule in RULES:
        txt = rule.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            assert heading in txt, f"{rule.name} missing '{heading}'"


def test_three_entry_formats_preserved():
    # The incident format must survive (not collapsed back to two formats).
    for rule in RULES:
        txt = rule.read_text(encoding="utf-8")
        assert "INCIDENT" in txt, f"{rule.name} lost the incident format"


def test_session_start_reads_state_not_devlog_current_context():
    for rule in RULES:
        txt = rule.read_text(encoding="utf-8")
        section = txt[txt.index("SESSION START"):txt.index("SESSION END")]
        assert "STATE" in section
        assert "DEVLOG Current Context" not in section


def test_no_hardcoded_docs_planning_paths():
    for d in RULE_DIRS:
        for f in d.glob("*.md"):
            assert "docs/planning/" not in f.read_text(encoding="utf-8"), str(f)


def test_no_contradictory_combined_budget_string():
    # The old "<10k combined" contradiction must be gone from all rule files.
    for d in RULE_DIRS:
        for f in d.glob("*.md"):
            assert "10,000 tokens combined" not in f.read_text(encoding="utf-8"), str(f)
