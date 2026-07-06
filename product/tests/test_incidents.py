"""Tests for incident-report parsing + index rendering (Spec 5 §2 / T2).

Covers the validated-against-real-data contract: filename-authoritative dates,
human-format header-date fallback, undated-sorts-last, title prefix-stripping +
slug fallback, free-text severity/status, status truncation, the five real
`schema writer 2` header shapes, README/TEMPLATE skipping, empty-dir
placeholder, idempotency, BOM/hard-break tolerance, and the em-dash-only-in-file
invariant.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from incidents import (  # noqa: E402
    EMDASH,
    GENERATED_MARKER,
    IncidentMeta,
    build_index,
    parse_incident,
)


def _write(d: Path, name: str, content: str) -> Path:
    p = d / name
    p.write_text(content, encoding="utf-8")
    return p


# --- Date handling -----------------------------------------------------------

def test_filename_date_is_authoritative(tmp_path):
    """Filename ISO date wins even when the header says something else."""
    p = _write(
        tmp_path,
        "2025-11-19-railway-misconfig.md",
        "# Incident Report: Railway misconfig\n\n**Date:** January 1, 2000\n",
    )
    meta = parse_incident(p)
    assert meta.iso_date == "2025-11-19"
    assert meta.raw_date == "2025-11-19"


def test_header_human_date_parsed_to_iso(tmp_path):
    """No filename prefix -> parse the header human date to ISO."""
    p = _write(
        tmp_path,
        "railway-misconfig.md",
        "# Incident Report: Railway misconfig\n\n**Date:** November 19, 2025\n",
    )
    meta = parse_incident(p)
    assert meta.iso_date == "2025-11-19"
    assert meta.raw_date == "2025-11-19"


def test_header_date_discovered_label(tmp_path):
    """`**Date Discovered:**` is accepted as a date field."""
    p = _write(
        tmp_path,
        "some-incident.md",
        "# Incident Report: X\n\n**Date Discovered:** 19 November 2025\n",
    )
    meta = parse_incident(p)
    assert meta.iso_date == "2025-11-19"


def test_unparseable_header_date_is_undated_raw_shown(tmp_path):
    p = _write(
        tmp_path,
        "weird-date.md",
        "# Incident Report: X\n\n**Date:** sometime last winter\n",
    )
    meta = parse_incident(p)
    assert meta.iso_date is None
    assert meta.raw_date == "sometime last winter"


def test_no_date_field_at_all(tmp_path):
    p = _write(tmp_path, "no-date.md", "# Incident Report: X\n\nbody\n")
    meta = parse_incident(p)
    assert meta.iso_date is None
    assert meta.raw_date == EMDASH


# --- Title handling ----------------------------------------------------------

def test_title_strips_incident_report_label(tmp_path):
    p = _write(tmp_path, "2025-01-01-a.md", "# Incident Report: The Big One\n")
    assert parse_incident(p).title == "The Big One"


def test_title_strips_incident_label(tmp_path):
    p = _write(tmp_path, "2025-01-01-a.md", "# Incident: Smaller One\n")
    assert parse_incident(p).title == "Smaller One"


def test_title_plain_heading_unchanged(tmp_path):
    p = _write(tmp_path, "2025-01-01-a.md", "# Database meltdown\n")
    assert parse_incident(p).title == "Database meltdown"


def test_title_falls_back_to_filename_slug(tmp_path):
    """No `# ` heading -> slug title from filename (date prefix stripped)."""
    p = _write(tmp_path, "2025-11-19-railway-account_misconfig.md", "no heading here\n")
    meta = parse_incident(p)
    assert meta.title == "Railway Account Misconfig"


# --- Severity / status -------------------------------------------------------

def test_free_text_severity_and_status(tmp_path):
    p = _write(
        tmp_path,
        "2025-01-01-a.md",
        "# Incident Report: X\n\n**Severity:** High\n**Status:** Resolved\n",
    )
    meta = parse_incident(p)
    assert meta.severity == "High"
    assert meta.status == "Resolved"


def test_missing_fields_become_emdash(tmp_path):
    p = _write(tmp_path, "2025-01-01-a.md", "# Incident Report: X\n\nbody only\n")
    meta = parse_incident(p)
    assert meta.severity == EMDASH
    assert meta.status == EMDASH


def test_status_kept_full_in_dataclass(tmp_path):
    long_status = "Open — origin narrowed to the worker ; fix not yet implemented"
    p = _write(
        tmp_path,
        "2025-01-01-a.md",
        f"# Incident Report: X\n\n**Status:** {long_status}\n",
    )
    assert parse_incident(p).status == long_status


# --- Non-incident / never-raises ---------------------------------------------

def test_non_incident_md_best_effort(tmp_path):
    """A `.md` that isn't really an incident still yields a best-effort meta."""
    p = _write(tmp_path, "random-notes.md", "just some text, no fields\n")
    meta = parse_incident(p)
    assert isinstance(meta, IncidentMeta)
    assert meta.title == "Random Notes"
    assert meta.severity == EMDASH
    assert meta.status == EMDASH
    assert meta.iso_date is None


# --- Status truncation (at render) -------------------------------------------

def test_status_truncation_emdash_clause(tmp_path):
    p = _write(
        tmp_path,
        "2025-01-01-a.md",
        "# Incident Report: X\n"
        "**Status:** Open — origin narrowed to worker ; fix not yet implemented\n",
    )
    out = build_index(tmp_path)
    # Truncated to the first clause (before the em-dash).
    assert "| Open |" in out
    assert "origin narrowed" not in out


def test_status_truncation_caps_long_first_clause(tmp_path):
    long_clause = "A" * 200
    p = _write(
        tmp_path,
        "2025-01-01-a.md",
        f"# Incident Report: X\n**Status:** {long_clause}\n",
    )
    out = build_index(tmp_path)
    # The ellipsis char marks truncation; the full 200-char run is not present.
    assert "…" in out
    assert long_clause not in out


# --- build_index: five real-schema fixtures ----------------------------------

def _seed_real_fixtures(d: Path) -> None:
    """Recreate representative headers mirroring the 5 schema-writer-2 reports."""
    _write(
        d,
        "2025-11-19-railway-account-misconfiguration.md",
        "---\ndoc: INCIDENT\n---\n\n"
        "# Incident Report: Railway Account Misconfiguration\n\n"
        "**Incident ID:** INC-2025-001\n"
        "**Date:** November 19, 2025\n"
        "**Severity:** Medium\n"
        "**Status:** Resolved\n"
        "**Reporter:** AI agent\n",
    )
    _write(
        d,
        "2026-01-15-silent-write-failure.md",
        "# Incident Report: Silent Write Failure\n\n"
        "**Date Discovered:** January 15, 2026\n"
        "**Severity:** High\n"
        "**Status:** Open — awaiting resolution\n"
        "**Duration of Silent Failure:** 3 days\n",
    )
    _write(
        d,
        "2026-03-02-schema-drift.md",
        "# Incident Report: Schema Drift Between Environments\n\n"
        "**Date:** March 2, 2026\n"
        "**Severity:** Medium\n"
        "**Status:** Open — origin narrowed to migration runner ; "
        "fix not yet implemented\n"
        "**Affected Page:** /admin/schema\n",
    )
    _write(
        d,
        "2026-04-10-auth-token-leak.md",
        "# Incident Report: Auth Token Leak\n\n"
        "**Date:** April 10, 2026\n"
        "**Severity:** High\n"
        "**Status:** Resolved\n"
        "**Responder:** AI agent\n",
    )
    _write(
        d,
        "2026-05-21-cache-stampede.md",
        "# Incident Report: Cache Stampede\n\n"
        "**Date:** May 21, 2026\n"
        "**Severity:** Medium\n"
        "**Status:** Mitigated (rate limiter added)\n",
    )


def test_build_index_five_rows_newest_first(tmp_path):
    _seed_real_fixtures(tmp_path)
    out = build_index(tmp_path)
    lines = [ln for ln in out.splitlines() if ln.startswith("| ") and "---" not in ln]
    # 1 header row + 5 data rows.
    data_rows = lines[1:]
    assert len(data_rows) == 5

    # Newest-first by ISO date (from filenames).
    dates_in_order = [row.split("|")[1].strip() for row in data_rows]
    assert dates_in_order == [
        "2026-05-21",
        "2026-04-10",
        "2026-03-02",
        "2026-01-15",
        "2025-11-19",
    ]

    # Clean, label-stripped titles in the links.
    assert "[Railway Account Misconfiguration]" in out
    assert "[Cache Stampede]" in out
    assert "Incident Report:" not in out  # label stripped from every title

    # Truncated statuses: long em-dash/parenthetical clauses cut to first clause.
    assert "| Open |" in out                 # both "Open — ..." statuses
    assert "| Mitigated |" in out            # "Mitigated (rate limiter added)"
    assert "rate limiter" not in out
    assert "awaiting resolution" not in out
    assert "origin narrowed" not in out


def test_build_index_links_point_to_files(tmp_path):
    _seed_real_fixtures(tmp_path)
    out = build_index(tmp_path)
    assert "(./2025-11-19-railway-account-misconfiguration.md)" in out


# --- build_index: skipping, empty, idempotency -------------------------------

def test_build_index_skips_readme_and_template(tmp_path):
    _write(tmp_path, "2025-01-01-real.md", "# Incident Report: Real\n")
    _write(tmp_path, "README.md", "# hand-written index\n")
    _write(tmp_path, "TEMPLATE.md", "# Incident Report: [Short title]\n")
    out = build_index(tmp_path)
    data_rows = [
        ln for ln in out.splitlines()
        if ln.startswith("| ") and "---" not in ln
    ][1:]
    assert len(data_rows) == 1
    assert "[Real]" in out


def test_build_index_skips_readme_case_insensitive(tmp_path):
    _write(tmp_path, "2025-01-01-real.md", "# Incident Report: Real\n")
    _write(tmp_path, "Readme.md", "# weird casing\n")
    _write(tmp_path, "Template.md", "# template\n")
    out = build_index(tmp_path)
    data_rows = [
        ln for ln in out.splitlines()
        if ln.startswith("| ") and "---" not in ln
    ][1:]
    assert len(data_rows) == 1


def test_empty_dir_placeholder_no_table(tmp_path):
    out = build_index(tmp_path)
    assert "_No incidents recorded yet._" in out
    assert "| Date |" not in out
    assert GENERATED_MARKER in out
    assert "doc: INCIDENTS-INDEX" in out


def test_dir_with_only_skipped_files_is_empty(tmp_path):
    _write(tmp_path, "README.md", "# hand-written\n")
    _write(tmp_path, "TEMPLATE.md", "# template\n")
    out = build_index(tmp_path)
    assert "_No incidents recorded yet._" in out


def test_idempotency_byte_identical(tmp_path):
    _seed_real_fixtures(tmp_path)
    first = build_index(tmp_path)
    second = build_index(tmp_path)
    assert first == second


def test_single_trailing_newline(tmp_path):
    _seed_real_fixtures(tmp_path)
    out = build_index(tmp_path)
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


# --- Undated sorts last ------------------------------------------------------

def test_undated_sorts_last(tmp_path):
    _write(tmp_path, "2026-01-01-dated.md", "# Incident Report: Dated\n")
    # No filename date, unparseable header date -> undated.
    _write(
        tmp_path,
        "undated-incident.md",
        "# Incident Report: Undated\n**Date:** whenever\n",
    )
    out = build_index(tmp_path)
    data_rows = [
        ln for ln in out.splitlines()
        if ln.startswith("| ") and "---" not in ln
    ][1:]
    assert "[Dated]" in data_rows[0]
    assert "[Undated]" in data_rows[1]
    # Undated shows its raw date string.
    assert "whenever" in data_rows[1]


def test_duplicate_dates_stable_by_filename(tmp_path):
    _write(tmp_path, "2026-01-01-bravo.md", "# Incident Report: Bravo\n")
    _write(tmp_path, "2026-01-01-alpha.md", "# Incident Report: Alpha\n")
    out = build_index(tmp_path)
    data_rows = [
        ln for ln in out.splitlines()
        if ln.startswith("| ") and "---" not in ln
    ][1:]
    # Same date -> filename ascending: alpha before bravo.
    assert "[Alpha]" in data_rows[0]
    assert "[Bravo]" in data_rows[1]


# --- BOM + trailing hard-break tolerance -------------------------------------

def test_bom_and_trailing_hard_break_spaces(tmp_path):
    """BOM-prefixed file with trailing hard-break spaces still parses cleanly."""
    p = tmp_path / "2025-11-19-bom.md"
    body = (
        "# Incident Report: BOM Test  \n"   # trailing 2-space hard break
        "**Severity:** High  \n"
        "**Status:** Resolved  \n"
    )
    p.write_text(body, encoding="utf-8-sig")  # writes a BOM
    meta = parse_incident(p)
    assert meta.title == "BOM Test"
    assert meta.severity == "High"
    assert meta.status == "Resolved"


# --- em-dash only in the file, never stdout; module never prints --------------

def test_emdash_appears_in_returned_string(tmp_path):
    """The — em-dash for empty fields lands in the returned (file) content."""
    _write(tmp_path, "2025-01-01-a.md", "# Incident Report: X\n")  # no sev/status
    out = build_index(tmp_path)
    assert EMDASH in out


def test_module_never_prints(tmp_path, capsys):
    _seed_real_fixtures(tmp_path)
    for p in tmp_path.glob("*.md"):
        parse_incident(p)
    build_index(tmp_path)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
