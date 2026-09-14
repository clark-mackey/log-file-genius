"""Canonical STATE handoff field names are a contract, and must fail loudly.

`freshness.assess` reads the handoff by exact label (`**Baseline commit:**`).
A relabeled field is therefore unreadable: the recorded evidence becomes
indistinguishable from evidence that was never recorded, and nothing told the
writer. These tests pin both halves of the fix - the rename is reported as a
rename at read time, and `lfg validate` rejects it at write time - while
keeping the existing missing/duplicate verdicts intact. A variant label is
never accepted as the baseline value.
"""
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from freshness import assess
from startup import render as render_agent_instructions
from state_contract import CANONICAL_FIELDS

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / 'product/scripts/lfg.py'

CONFIG = textwrap.dedent("""
    paths:
      changelog: logs/CHANGELOG.md
      devlog: logs/DEVLOG.md
      state: logs/STATE.md
    token_targets:
      changelog: 10000
      devlog: 15000
      combined: 25000
      state: 500
""")


def _git(root, *args, check=True):
    return subprocess.run(['git', '-C', str(root), *args], check=check,
                          capture_output=True, text=True)


@pytest.fixture
def handoff(tmp_path):
    """A committed checkout plus a writer for its STATE handoff block."""
    root = tmp_path
    _git(root, 'init', '-q', '-b', 'work', '.')
    _git(root, 'config', 'user.email', 'fixture@example.invalid')
    _git(root, 'config', 'user.name', 'LFG fixture')
    (root / '.logfile-config.yml').write_text(CONFIG, encoding='utf-8')
    (root / 'logs').mkdir()
    (root / 'app.py').write_text("value = int('1')\n", encoding='utf-8')
    (root / 'logs/CHANGELOG.md').write_text(
        '# Changelog\n\nhttps://keepachangelog.com/\n\n## [Unreleased]\n'
        '- Added thing. Files: `app.py`. Commit: `abc1234`\n', encoding='utf-8')
    (root / 'logs/DEVLOG.md').write_text(
        '# Development Log\n\n## Daily Log\n\n### 2026-09-12: x\n- y\n', encoding='utf-8')
    _git(root, 'add', '-A')
    _git(root, 'commit', '-qm', 'baseline')
    baseline = _git(root, 'rev-parse', 'HEAD').stdout.strip()

    def write(commit_block):
        """`commit_block` supplies the baseline-commit line(s) verbatim."""
        (root / 'logs/STATE.md').write_text(
            '# Current State\n\n## Current Context\n\n'
            '**Baseline branch:** work\n'
            + commit_block.format(baseline=baseline) +
            '**Next action:** Fix the integer parsing defect.\n'
            '**Tests:** Not run; evidence unknown.\n'
            '**Blockers:** Local commit refused; reported as unavailable.\n\n'
            '## Last Session\n\nDocs-only handoff commit recorded.\n', encoding='utf-8')
        return root

    write.root = root
    write.baseline = baseline
    return write


def _validate_state(root):
    return subprocess.run([sys.executable, str(LFG), 'validate', '--state-only'],
                          cwd=str(root), capture_output=True, text=True, encoding='utf-8')


def test_canonical_handoff_is_readable(handoff):
    """Control: the canonical label parses, validates and raises no issue."""
    root = handoff('**Baseline commit:** {baseline}\n')
    result = assess(root)
    assert result['issues'] == []
    assert result['handoff']['Baseline commit'] == handoff.baseline
    assert _validate_state(root).returncode == 0


def test_renamed_baseline_field_is_reported_as_a_rename(handoff):
    """The exact evaluation failure: `Baseline commit` written as `Baseline code commit`.

    Pre-fix this was reported with the same words as a baseline that was never
    recorded, so the reader could not tell the evidence existed at all.
    """
    renamed = assess(handoff('**Baseline code commit:** {baseline}\n'))
    absent = assess(handoff(''))

    assert renamed['status'] == 'unknown'
    # The recorded value is never substituted for the canonical field.
    assert renamed['handoff']['Baseline commit'] is None
    # ...but the rename is named, and is distinguishable from plain absence.
    assert renamed['issues'] != absent['issues']
    assert any('Baseline code commit' in issue and 'Baseline commit' in issue
               for issue in renamed['issues']), renamed['issues']
    assert not any('Baseline code commit' in issue for issue in absent['issues'])
    assert renamed['renamed_fields'] == {'Baseline commit': ['Baseline code commit']}
    assert absent['renamed_fields'] == {}


def test_validate_rejects_a_renamed_baseline_field(handoff):
    """The write-time gate: `lfg validate` must fail before the handoff is committed."""
    root = handoff('**Baseline code commit:** {baseline}\n')
    result = _validate_state(root)
    assert result.returncode == 2, result.stdout + result.stderr
    assert 'Baseline commit' in result.stdout
    assert 'Baseline code commit' in result.stdout

    # The canonical spelling is accepted by the same gate.
    assert _validate_state(handoff('**Baseline commit:** {baseline}\n')).returncode == 0


def test_bare_canonical_label_beside_a_variant_is_still_a_rename(handoff):
    """The canonical label present but empty must not vouch for the variant below it.

    This is the rename shape that hides best: the writer keeps the canonical
    line, leaves it blank, and records the value one line down under their own
    spelling. A reader that let the empty label count as recorded would call the
    whole thing ordinary content and say nothing.
    """
    root = handoff('**Baseline commit:**\n'
                   '**Baseline code commit:** {baseline}\n')
    result = assess(root)

    assert result['handoff']['Baseline commit'] is None
    assert result['renamed_fields'] == {'Baseline commit': ['Baseline code commit']}
    assert any('Baseline code commit' in issue for issue in result['issues']), result['issues']
    assert _validate_state(root).returncode == 2


def test_a_bare_label_does_not_absorb_the_following_field(handoff):
    """An empty field reads as missing, not as whatever the next line says."""
    root = handoff('**Baseline commit:** {baseline}\n')
    state = root / 'logs/STATE.md'
    state.write_text(state.read_text(encoding='utf-8').replace(
        '**Next action:** Fix the integer parsing defect.', '**Next action:**'),
        encoding='utf-8')

    result = assess(root)
    assert result['handoff']['Next action'] is None
    assert 'Missing handoff evidence: Next action.' in result['issues']
    # The next line is still read as its own field, not consumed as the value.
    assert result['handoff']['Tests'] == 'Not run; evidence unknown.'


def test_case_and_insertion_variants_are_caught(handoff):
    """Near misses a writer actually produces: recased, prefixed, suffixed."""
    for label in ('Baseline Commit', 'Last baseline commit', 'Baseline commit hash'):
        result = assess(handoff('**' + label + ':** {baseline}\n'))
        assert result['renamed_fields'] == {'Baseline commit': [label]}, label
        assert result['handoff']['Baseline commit'] is None, label


def test_missing_and_duplicate_baselines_still_fail(handoff):
    """Detection must not weaken presence/uniqueness/validity checks."""
    absent = assess(handoff(''))
    assert absent['status'] == 'unknown'
    assert absent['handoff']['Baseline commit'] is None
    assert any('baseline commit' in issue.lower() for issue in absent['issues'])

    duplicated = assess(handoff('**Baseline commit:** {baseline}\n'
                                '**Baseline commit:** {baseline}\n'))
    assert duplicated['status'] == 'unknown'
    assert duplicated['handoff']['Baseline commit'] is None
    assert any('baseline commit' in issue.lower() for issue in duplicated['issues'])
    # A duplicated canonical label is not reported as a rename of itself.
    assert duplicated['renamed_fields'] == {}

    invalid = assess(handoff('**Baseline commit:** not-a-commit\n'))
    assert invalid['handoff']['Baseline commit'] == 'not-a-commit'
    assert any('invalid baseline commit' in issue.lower() for issue in invalid['issues'])


def test_supplementary_field_beside_the_canonical_one_is_not_flagged(handoff):
    """A present canonical field makes an extra related field ordinary prose."""
    result = assess(handoff('**Baseline commit:** {baseline}\n'
                            '**Baseline commit checked by:** the previous session\n'))
    assert result['renamed_fields'] == {}
    assert result['handoff']['Baseline commit'] == handoff.baseline
    assert result['issues'] == []


def test_agent_instructions_name_the_canonical_baseline_labels():
    """The instruction a writer reads must name the label the reader matches.

    The rename this file exists for came from instructions that only ever
    paraphrased the baseline as a "code commit": a paraphrase is what a writer
    relabels. The generated AGENTS.md and the maintenance rule behind it must
    carry the literal labels, and the generated file must still match its
    generator - a hand-edited copy would drift back to a paraphrase unnoticed.
    """
    generated = (ROOT / 'product/AGENTS.md').read_text(encoding='utf-8')
    rule = (ROOT / 'product/rules/log-file-maintenance.md').read_text(encoding='utf-8')
    assert generated == render_agent_instructions(), (
        'product/AGENTS.md is stale; regenerate with `lfg.py generate`')
    for field in ('Baseline branch', 'Baseline commit'):
        assert field in CANONICAL_FIELDS, field
        label = '**' + field + ':**'
        assert label in generated, 'AGENTS.md does not name ' + label
        assert label in rule, 'log-file-maintenance.md does not name ' + label
