"""Frozen workplan oracles: deterministic behavior, not model or human evidence."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import archive
import metadata
import routing
import safe_write
import startup
from context_paths import project_root, context_paths, tokens
from freshness import assess
from primer import build_prime

PRODUCT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((Path(__file__).parent / 'context-fixtures.json').read_text())


def seed(root):
    (root / 'logs/adr').mkdir(parents=True)
    (root / '.logfile-config.yml').write_text('paths:\n  state: logs/STATE.md\n')
    (root / 'logs/STATE.md').write_text('## Current Context\n**Next action:** Inspect code\n\n## Last Session\nNo evidence\n')
    (root / 'logs/CHANGELOG.md').write_text('# Changelog\n## [Unreleased]\n- behavior\n')
    return root


def adr(root, number, applies='project-wide', status='Accepted', replacement=None):
    path = context_paths(root)['adr_dir'] / f'{number:03}.md'
    text = (f'# ADR-{number:03}: Rule {number}\n\n**Status:** {status}\n\n'
            '## Routing\n**Read when:** Change this component\n'
            f'**Applies to:** {applies}\n**Constraint:** Preserve invariant {number}.\n\n## Decision\nEvidence and rationale.\n')
    if replacement:
        text += f'\n**Superseded by:** [replacement]({replacement})\n'
    path.write_text(text)
    return path


def test_cross_component_global_union_supersession_and_unknown(tmp_path):
    root = seed(tmp_path)
    adr(root, 1)
    adr(root, 2, 'api/*')
    adr(root, 3, 'ui/*')
    adr(root, 4, 'old/*', 'Superseded', '002.md')
    records, errors = routing.collect(root)
    assert not errors
    assert [r.id for r in routing.select(records, ['api/x', 'ui/y'], ['ADR-004'])] == ['ADR-001', 'ADR-002', 'ADR-003']
    assert routing.run(root, ids=['ADR-999'])[0] == 2
    assert 'bounded' in routing.run(root)[1]


def test_cycle_placeholder_and_missing_replacement_refuse(tmp_path):
    root = seed(tmp_path)
    a = adr(root, 1, status='Superseded', replacement='002.md')
    assert routing.run(root, write=True)[0] == 2
    adr(root, 2, status='Superseded', replacement='001.md')
    assert 'cycle' in routing.run(root)[1]
    a.write_text(a.read_text().replace('Preserve invariant 1.', '[Constraint]'))
    assert 'placeholder' in routing.run(root)[1]
    assert not (root / 'logs/adr/README.md').exists()


def test_partition_manifest_stale_views_curated_prose_and_overflow(tmp_path):
    root = seed(tmp_path)
    for n in range(1, 8):
        adr(root, n, f'component{n}/*')
    index = root / 'logs/adr/README.md'
    index.write_text('# Decisions\n\nKEEP CURATED NOTES\n')
    assert routing.run(root, write=True, budget=200)[0] == 0
    text = index.read_text()
    assert 'KEEP CURATED NOTES' in text
    for n in range(1, 8):
        assert f'ADR-{n:03}' in text
        assert (root / f'logs/adr/routes/adr-{n:03}.md').exists()
    assert routing.run(root, check=True, budget=200)[0] == 0
    path = root / 'logs/adr/001.md'
    path.write_text(path.read_text() + '\nNew rationale\n')
    assert routing.run(root, check=True, budget=200)[0] == 1
    code, text = routing.run(root, paths=[f'component{n}/x' for n in range(1,8)], budget=1)
    assert code == 2 and 'INCOMPLETE' in text
    assert all(f'{n:03}.md' in text for n in range(1,8))


def test_custom_paths_and_nested_start(tmp_path):
    root = seed(tmp_path)
    (root / '.logfile-config.yml').write_text('paths:\n  state: "knowledge space/STATE.md"\n  adr: "knowledge space/decisions"\n')
    nested = root / 'src/deep'; nested.mkdir(parents=True)
    assert project_root(nested) == root
    text = startup.render(root)
    assert 'knowledge space/STATE.md' in text and 'knowledge space/decisions/README.md' in text
    assert context_paths(root)['adr_dir'] == root / 'knowledge space/decisions'
    (root / '.logfile-config.yml').write_text('paths:\n  state: ../outside.md\n')
    with pytest.raises(ValueError, match='escapes'):
        context_paths(root)


@pytest.mark.parametrize('frontmatter', [True, False])
def test_crlf_metadata_preserves_body_and_restore(tmp_path, frontmatter):
    root = seed(tmp_path)
    path = root / 'logs/windows.md'
    body = b'# Windows document\r\n\r\nKeep original bytes.\r\n'
    original = (b'---\r\ndoc: CUSTOM\r\n---\r\n' if frontmatter else b'') + body
    path.write_bytes(original)
    code, message = metadata.run(root, write=True)
    assert code == 0, message
    migrated = path.read_bytes()
    assert migrated.endswith(body) and b'type: "Project Reference"\r\n' in migrated
    assert metadata.run(root, write=True)[0] == 0
    assert path.read_bytes() == migrated
    assert metadata.run(root, restore=True)[0] == 0
    assert path.read_bytes() == original


def test_crlf_routes_remain_current_after_generation(tmp_path):
    root = seed(tmp_path)
    path = adr(root, 1)
    original = path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    path.write_bytes(original)
    assert routing.run(root, write=True)[0] == 0
    assert routing.run(root, check=True)[0] == 0
    assert path.read_bytes() == original


def test_cli_redirected_output_uses_utf8(tmp_path):
    root = seed(tmp_path)
    (root / 'logs/STATE.md').write_bytes('## Current Context\nPreserve café ✓\n'.encode())
    env = dict(os.environ, PYTHONIOENCODING='cp1252')
    result = subprocess.run([sys.executable, str(PRODUCT / 'scripts/lfg.py'), 'prime'],
                            cwd=root, env=env, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert 'café ✓' in result.stdout.decode('utf-8')


@pytest.mark.parametrize('failure', ['validate', 'backup', 'temp', 'temp-write', 'replace', 'concurrent'])
def test_safe_write_failures_preserve_original(tmp_path, monkeypatch, failure):
    path = tmp_path / 'record.md'; original = b'original\r\n'; path.write_bytes(original)
    def fail(*args, **kwargs):
        raise OSError('injected')
    validate = (lambda data: fail()) if failure == 'validate' else (lambda data: None)
    if failure == 'backup':
        real_open = Path.open
        def backup_failure(path, mode='r', *args, **kwargs):
            if mode == 'xb':
                fail()
            return real_open(path, mode, *args, **kwargs)
        monkeypatch.setattr(Path, 'open', backup_failure)
    if failure == 'temp':
        monkeypatch.setattr(safe_write.tempfile, 'mkstemp', fail)
    if failure == 'replace':
        monkeypatch.setattr(safe_write.os, 'replace', fail)
    if failure == 'temp-write':
        real_fdopen = safe_write.os.fdopen
        class BrokenWriter:
            def __init__(self, fd, *args, **kwargs):
                self.stream = real_fdopen(fd, *args, **kwargs)
            def __enter__(self):
                return self
            def write(self, data):
                fail()
            def __exit__(self, *args):
                self.stream.close()
        monkeypatch.setattr(safe_write.os, 'fdopen', BrokenWriter)
    if failure == 'concurrent':
        real = safe_write.tempfile.mkstemp
        def change(*args, **kwargs):
            path.write_bytes(b'concurrent edit')
            return real(*args, **kwargs)
        monkeypatch.setattr(safe_write.tempfile, 'mkstemp', change)
    with pytest.raises((ValueError, OSError)):
        safe_write.replace(path, b'candidate', original, validate)
    monkeypatch.undo()
    assert path.read_bytes() == (b'concurrent edit' if failure == 'concurrent' else original)


def test_metadata_additive_idempotent_full_yaml_and_restore(tmp_path):
    root = seed(tmp_path)
    adr(root, 1)
    custom = root / 'logs/custom.md'
    original = b'---\ndoc: CUSTOM\ncustom_key: "Keep: this"\nrelated:\n  state: ./STATE.md\n---\n\n# Title: "quote"\nBody unchanged.\n'
    custom.write_bytes(original)
    assert metadata.run(root, index=True)[0] == 0
    assert custom.read_bytes() == original
    assert metadata.run(root, write=True, index=True)[0] == 0
    import yaml
    for path in (root / 'logs').rglob('*.md'):
        if path.name not in ('index.md', 'log.md'):
            fm = path.read_text().split('---', 2)[1]
            assert isinstance(yaml.safe_load(fm)['type'], str)
    assert custom.read_bytes().endswith(original.split(b'---\n', 2)[2])
    assert 'custom_key: "Keep: this"' in custom.read_text()
    assert 'verified:' not in custom.read_text()
    before = custom.read_bytes()
    assert metadata.run(root, write=True, index=True)[0] == 0
    assert custom.read_bytes() == before
    assert metadata.run(root, restore=True)[0] == 0
    assert custom.read_bytes() == original
    assert not (root / 'logs/index.md').exists()


def test_metadata_unsupported_and_interfile_failure_resume(tmp_path, monkeypatch):
    root = seed(tmp_path)
    invalid = root / 'logs/bad.md'; invalid.write_text('---\ncustom: [a, b]\n---\nbody\n')
    assert metadata.run(root, write=True)[0] == 2
    assert not (root / '.lfg').exists()
    invalid.unlink()
    real = metadata.replace
    calls = []
    def interrupted(path, *args, **kwargs):
        if Path(path).suffix == '.md':
            calls.append(path)
            if len(calls) == 2:
                raise OSError('interfile interruption')
        return real(path, *args, **kwargs)
    monkeypatch.setattr(metadata, 'replace', interrupted)
    with pytest.raises(OSError):
        metadata.run(root, write=True, index=True)
    assert json.loads((root / '.lfg/metadata-migration.json').read_text())['status'] == 'in-progress'
    assert not (root / 'logs/index.md').exists()
    monkeypatch.undo()
    assert metadata.run(root, write=True, index=True)[0] == 0
    assert (root / 'logs/index.md').exists()


def test_selected_packet_roles_sections_missing_dedup_overflow(tmp_path):
    root = seed(tmp_path); adr(root, 1)
    args = dict(project_root=root, selected=['logs/adr/001.md#Decision'] * 2 + ['missing.md'], objective='Work')
    text = build_prime(**args, role='reader')
    assert 'LFG_SUBAGENT_PRIME' not in text
    assert text.count('# Source: logs/adr/001.md#Decision') == 1
    assert 'MISSING: missing.md' in text
    assert 'LFG_SUBAGENT_PRIME' in build_prime(**args)
    with pytest.raises(ValueError, match='INCOMPLETE'):
        build_prime(**args, budget=10)
    with pytest.raises(ValueError, match='escapes'):
        build_prime(root, selected=['../secret'])


def test_branch_freshness_never_verifies_unknown(tmp_path):
    root = seed(tmp_path)
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    result = assess(root)
    assert result['status'] == 'unknown'
    assert any('baseline branch' in s for s in result['issues'])
    assert result['external_status'].startswith('unknown')


def test_empty_index_and_mixed_template_ownership(tmp_path):
    root = seed(tmp_path)
    (root/'logs/index.md').write_bytes(b'')
    # Reserved structure is reported before writes; user placeholder is preserved.
    assert metadata.run(root, write=True, index=True)[0] == 2
    assert (root/'logs/index.md').read_bytes() == b''
    import update_template_hashes as hashes
    templates = root/'templates'; templates.mkdir()
    shutil.copyfile(PRODUCT/'templates/ADR_template.md', templates/'known.md')
    (templates/'user.md').write_text('KEEP USER')
    assert hashes.match_dir(templates, require_all=True) == 1
    assert hashes.match_dir(templates) == 0


def test_failed_routing_does_not_publish_native_pointers(tmp_path):
    root = seed(tmp_path)
    (root/'logs/adr/broken.md').write_text('# ADR-001: Missing routing\n**Status:** Accepted\n')
    readme = root/'README.md'; readme.write_text('KEEP USER')
    with pytest.raises(ValueError, match='UNRESOLVED'):
        startup.install(root)
    assert readme.read_text() == 'KEEP USER'
    assert not (root/'CLAUDE.md').exists()


def test_generic_setup_creates_claude_import(tmp_path):
    root = seed(tmp_path)
    (root / 'AGENTS.md').write_text('KEEP AGENTS\n')

    startup.install(root)

    text = (root / 'CLAUDE.md').read_text()
    assert text.count('@AGENTS.md') == 1


def test_setup_prefers_nested_claude_file_and_is_idempotent(tmp_path):
    root = seed(tmp_path)
    (root / 'AGENTS.md').write_text('KEEP AGENTS\n')
    nested = root / '.claude/CLAUDE.md'
    nested.parent.mkdir()
    nested.write_text('KEEP CLAUDE\n')

    startup.install(root)
    first = nested.read_bytes()
    startup.install(root)

    assert not (root / 'CLAUDE.md').exists()
    assert nested.read_bytes() == first
    assert 'KEEP CLAUDE' in nested.read_text()
    assert nested.read_text().count('@../AGENTS.md') == 1


def test_existing_claude_import_is_not_duplicated(tmp_path):
    root = seed(tmp_path)
    (root / 'AGENTS.md').write_text('KEEP AGENTS\n')
    claude = root / 'CLAUDE.md'
    claude.write_text('KEEP CLAUDE\n\n@AGENTS.md\n')
    original = claude.read_bytes()

    startup.install(root)
    startup.install(root)

    assert claude.read_bytes() == original
    assert claude.read_text().count('@AGENTS.md') == 1


@pytest.mark.parametrize('example', ['```text\n@AGENTS.md\n```',
                                     '~~~\n@AGENTS.md\n~~~',
                                     '<!--\n@AGENTS.md\n-->', '`@AGENTS.md`',
                                     '    @AGENTS.md', '\t@AGENTS.md'])
def test_claude_import_example_does_not_replace_real_import(tmp_path, example):
    root = seed(tmp_path)
    claude = root / 'CLAUDE.md'
    claude.write_text(example + '\n')
    startup.install(root)
    assert example in claude.read_text()
    assert '<!-- LFG:POINTER:BEGIN -->\n@AGENTS.md\n' in claude.read_text()


def test_context_setup_preserves_agent_skills_and_claude_settings(tmp_path):
    root = seed(tmp_path)
    owned = {}
    for relative in ('.agents/skills/custom/SKILL.md', '.claude/skills/custom/SKILL.md',
                     '.claude/settings.json', '.claude/agents/reviewer.md'):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'USER OWNED\r\n')
        owned[path] = path.read_bytes()
    startup.install(root)
    startup.install(root)
    assert all(path.read_bytes() == content for path, content in owned.items())


@pytest.mark.skipif(sys.platform == 'win32', reason='symlinks require Windows Developer Mode')
@pytest.mark.parametrize('relative', ['CLAUDE.md', '.claude/CLAUDE.md', 'WARP.md', '.hermes.md'])
def test_native_symlink_to_canonical_agents_needs_no_pointer(tmp_path, relative):
    root = seed(tmp_path)
    agents = root / 'AGENTS.md'; agents.write_text('CANONICAL INSTRUCTIONS\n')
    native = root / relative; native.parent.mkdir(parents=True, exist_ok=True)
    native.symlink_to(agents)
    startup.install(root)
    startup.install(root)
    assert native.is_symlink()
    assert agents.read_text() == 'CANONICAL INSTRUCTIONS\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='symlinks require Windows Developer Mode')
def test_existing_symlink_import_is_refused_without_writing_target(tmp_path):
    root = seed(tmp_path / 'repo')
    outside = tmp_path / 'outside.md'
    outside.write_text('@AGENTS.md\n')
    (root / 'CLAUDE.md').symlink_to(outside)
    with pytest.raises(ValueError, match='escapes repository|Symlink'):
        startup.install(root)
    assert outside.read_text() == '@AGENTS.md\n'
    assert (root / 'CLAUDE.md').is_symlink()


@pytest.mark.skipif(sys.platform == 'win32', reason='symlinks require Windows Developer Mode')
@pytest.mark.parametrize('directory, filename', [('.claude', 'CLAUDE.md'), ('.hermes', 'AGENTS.md')])
def test_context_setup_refuses_external_parent_symlink(tmp_path, directory, filename):
    root = seed(tmp_path / 'repo')
    outside = tmp_path / 'outside'; outside.mkdir()
    target = outside / filename; target.write_text('PRIVATE INSTRUCTIONS\n')
    (root / directory).symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='escapes repository'):
        startup.install(root)
    assert target.read_text() == 'PRIVATE INSTRUCTIONS\n'


@pytest.mark.parametrize('directory, expected', [('.agents', 'generic'), ('.claude', 'Claude Code')])
def test_installer_prefers_current_agent_conventions_over_augment(tmp_path, directory, expected):
    root = tmp_path / 'consumer'; root.mkdir()
    (root / directory).mkdir()
    (root / '.augment').mkdir()
    product = root / '.log-file-genius/product'
    shutil.copytree(PRODUCT, product, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(product / 'scripts/install.ps1'), '-Force', '-Profile', 'solo-developer']
    else:
        command = ['bash', str(product / 'scripts/install.sh'), '--force', '--profile', 'solo-developer']
    result = subprocess.run(command, cwd=root, input='', capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Detected ' + expected in result.stdout
    assert (root / 'CLAUDE.md').exists()


def test_existing_hermes_priority_and_warp_files_are_preserved(tmp_path):
    root = seed(tmp_path)
    (root / 'AGENTS.md').write_text('KEEP AGENTS\n')
    (root / '.hermes').mkdir()
    expected = {
        root / '.hermes.md': 'AGENTS.md',
        root / 'HERMES.md': 'AGENTS.md',
        root / 'AGENTS.override.md': 'AGENTS.md',
        root / '.hermes/AGENTS.md': '../AGENTS.md',
        root / '.hermes/AGENTS.override.md': '../AGENTS.md',
        root / 'WARP.md': 'AGENTS.md',
    }
    for path in expected:
        path.write_text(f'KEEP {path.name}\n')

    startup.install(root)
    startup.install(root)

    for path, target in expected.items():
        text = path.read_text()
        assert f'KEEP {path.name}' in text
        assert text.count(f'[{target}]({target})') == 1


def test_archive_ignores_alternate_fence_inside_code(tmp_path):
    path = tmp_path/'archive/x.md'
    archive._write_archive_file(path, '```text\n~~~\n```\n[Guide](docs/g.md "Guide")\n', 'DEVLOG.md')
    assert '[Guide](../docs/g.md "Guide")' in path.read_text()


def test_restore_retains_edit_racing_with_retirement(tmp_path, monkeypatch):
    path = tmp_path/'index.md'; path.write_bytes(b'generated')
    real = Path.rename
    def change_then_move(source, target):
        source.write_bytes(b'concurrent user edit')
        return real(source, target)
    monkeypatch.setattr(Path, 'rename', change_then_move)
    with pytest.raises(ValueError, match='Concurrent edit preserved'):
        safe_write.retire(path, b'generated')
    assert path.read_bytes() == b'concurrent user edit'


def test_archive_collisions_stale_plans_custom_names_and_durable_links(tmp_path):
    root = seed(tmp_path); decision = adr(root, 1)
    (root/'.logfile-config.yml').write_text('paths:\n  devlog: logs/journal.md\ntoken_targets:\n  devlog: 150\n')
    source = root/'logs/journal.md'
    original = ('## Daily Log\n### 2026-09-12: New\nRecent\n\n### 2025-01-01: Old\n'
                '[decision](adr/001.md "Decision")\n' + 'x' * 1000 + '\n')
    source.write_text(original)
    plan = archive.build_plan(root, include_changelog=False)
    assert plan.actions
    target = plan.actions[0].archive_path
    target.parent.mkdir(parents=True); target.write_text('KEEP ARCHIVE')
    with pytest.raises(archive.ArchiveError, match='collision'):
        archive.apply(plan)
    assert target.read_text() == 'KEEP ARCHIVE' and source.read_text() == original
    target.unlink()
    source.write_text(original + '\nConcurrent edit\n')
    with pytest.raises(archive.ArchiveError, match='changed since preview'):
        archive.apply(plan)
    source.write_text(original)
    archive.apply(plan)
    assert '[decision](../adr/001.md "Decision")' in target.read_text()
    assert decision.exists() and 'Recent' in source.read_text()
    assert routing.run(root, write=True)[0] == 0
    assert 'ADR-001' in (root/'logs/adr/README.md').read_text()


def test_archive_legacy_mixed_oversize_refuses_without_byte_changes(tmp_path):
    root = seed(tmp_path)
    path = root / 'logs/DEVLOG.md'
    for prefix in ('## 2024-01-01: legacy', '### 2026-09-12: valid\nnew\n## 2024-01-01: legacy', 'no entries'):
        original = ('# Development Log\n## Daily Log\n' + prefix + '\n' + 'x' * 64000).encode()
        path.write_bytes(original)
        plan = archive.build_plan(root, include_changelog=False)
        assert plan.refusal_reasons and 'within budget' not in plan.to_human()
        with pytest.raises(archive.ArchiveError):
            archive.apply(plan)
        assert path.read_bytes() == original
        assert not (root / 'logs/archive').exists()


@pytest.mark.parametrize('assistant', ['claude-code', 'augment', 'codex', 'pi', 'warp', 'orca',
                                       'hermes', 'grok-build', 'generic', 'aider'])
def test_fresh_install_brownfield_override_repeat_and_cli_cleanliness(tmp_path, assistant):
    root = tmp_path / 'repo with spaces'; root.mkdir()
    product = root / '.log-file-genius/product'
    shutil.copytree(PRODUCT, product, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
    # A real local source remote exercises update without network access.
    source = product.parent
    subprocess.run(['git', 'init', '-q', '-b', 'main', str(source)], check=True)
    subprocess.run(['git', '-C', str(source), 'add', 'product'], check=True)
    subprocess.run(['git', '-C', str(source), '-c', 'user.name=LFG fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'fixture'], check=True)
    remote = tmp_path/'upstream.git'
    # Use Git transport to avoid platform-specific local hardlink/copy failures.
    subprocess.run(['git', 'clone', '--bare', '--no-local', '-q', str(source), str(remote)], check=True)
    subprocess.run(['git', '-C', str(source), 'remote', 'add', 'origin', str(remote)], check=True)
    (root / '.claude').mkdir()
    (root / 'AGENTS.md').write_text('# My instructions\nKEEP USER\n')
    (root / 'AGENTS.override.md').write_text('KEEP OVERRIDE\n')
    (root / 'CLAUDE.md').write_text('KEEP CLAUDE\n')
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(product/'scripts/install.ps1'), '-Force', '-Profile', 'solo-developer', '-AiAssistant', assistant]
    else:
        command = ['bash', str(product/'scripts/install.sh'), '--force', '--profile', 'solo-developer', '--ai-assistant', assistant]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'KEEP USER' in (root/'AGENTS.md').read_text()
    assert '@AGENTS.md' in (root/'CLAUDE.md').read_text()
    assert 'KEEP OVERRIDE' in (root/'AGENTS.override.md').read_text()
    assert (root/'logs/adr/README.md').exists()
    # Fresh installs are an OKF bundle without a separate metadata command.
    import yaml
    for path in (root/'logs').rglob('*.md'):
        frontmatter = path.read_text().split('---', 2)[1]
        fields = yaml.safe_load(frontmatter)
        if path.name == 'index.md':
            assert fields['okf_version'] == '0.2'
        else:
            assert isinstance(fields['type'], str) and fields['type'].strip()
    index = root/'logs/index.md'
    assert 'STATE.md' in index.read_text()
    index_bytes = index.read_bytes()
    assert tokens(startup.render()) <= MANIFEST['limits']['startup_tokens']
    custom = root/'logs/incidents/README.md'; custom.write_text('KEEP INCIDENT INDEX\n')
    state = root/'logs/STATE.md'; state.write_text('KEEP STATE\n')
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert custom.read_text() == 'KEEP INCIDENT INDEX\n' and state.read_text() == 'KEEP STATE\n'
    assert index.read_bytes() == index_bytes
    env = dict(os.environ); env.pop('PYTHONDONTWRITEBYTECODE', None)
    for args in (['status'], ['prime'], ['routes', '--check']):
        result = subprocess.run([sys.executable, str(product/'scripts/lfg.py'), *args], cwd=root, env=env, capture_output=True)
        assert result.returncode == 0, result.stderr
    assert not list(product.rglob('*.pyc'))
    # Full lifecycle: discover → plan packet → handoff/resume → archive → update.
    state.write_text((PRODUCT/'templates/STATE_template.md').read_text())
    adr(root, 1)
    cli = [sys.executable, str(product/'scripts/lfg.py')]
    def run(*args):
        return subprocess.run(cli + list(args), cwd=root, env=env, capture_output=True, text=True)
    assert run('routes', '--write').returncode == 0
    packet = run('prime', '--role', 'reader', '--include', 'logs/adr/001.md', '--objective', 'Resume work')
    assert packet.returncode == 0 and 'ADR-001' in packet.stdout
    assert run('freshness').returncode == 1  # unknown baseline is an honest resume result
    config = root/'.logfile-config.yml'
    config.write_text(config.read_text().replace('devlog: 15000', 'devlog: 200'))
    (root/'logs/DEVLOG.md').write_text('## Daily Log\n### 2026-09-12: Now\nRecent\n### 2025-01-01: Old\n[Rule](adr/001.md)\n' + 'x' * 1000 + '\n')
    assert run('archive', '--devlog', '--dry-run').returncode == 0
    assert run('archive', '--devlog', '--force').returncode == 0
    assert run('routes', '--check').returncode == 0
    templates = root/'templates'; templates.mkdir()
    shutil.copyfile(PRODUCT/'templates/ADR_template.md', templates/'known.md')
    (templates/'user.md').write_text('KEEP CUSTOM TEMPLATE')
    update = (['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(product/'scripts/update.ps1'), '-Force']
              if sys.platform == 'win32' else ['bash', str(product/'scripts/update.sh')])
    result = subprocess.run(update, cwd=root, input='n\n'*10, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (templates/'user.md').read_text() == 'KEEP CUSTOM TEMPLATE'
    assert 'KEEP USER' in (root/'AGENTS.md').read_text()
    assert run('routes', '--check').returncode == 0


@pytest.mark.parametrize('existing', ['logs', 'config', 'metadata-failure'])
def test_install_okf_preservation_and_failure(tmp_path, existing):
    root = tmp_path / 'project'; root.mkdir()
    product = root / '.log-file-genius/product'
    shutil.copytree(PRODUCT, product, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
    if existing == 'logs':
        (root/'logs').mkdir()
        (root/'logs/notes.md').write_text('# User notes\nUnmodified body.\n')
    elif existing == 'config':
        (root/'.logfile-config.yml').write_text('profile: solo-developer\n')
    else:
        # A producer refusal must reach the installer caller, never claim success.
        template = product/'templates/DEVLOG_template.md'
        template.write_text('---\ntype: [unsupported, sequence]\n---\n# Development Log\n')
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(product/'scripts/install.ps1'), '-Force', '-Profile', 'solo-developer', '-AiAssistant', 'generic']
    else:
        command = ['bash', str(product/'scripts/install.sh'), '--force', '--profile', 'solo-developer', '--ai-assistant', 'generic']
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    if existing == 'metadata-failure':
        assert result.returncode == 2, result.stdout + result.stderr
        assert 'OKF initialization incomplete' in result.stdout
        assert 'Installation Complete!' not in result.stdout
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'Preview OKF adoption' in result.stdout
        if existing == 'logs':
            assert (root/'logs/notes.md').read_text() == '# User notes\nUnmodified body.\n'
        else:
            assert (root/'.logfile-config.yml').read_text() == 'profile: solo-developer\n'
    assert not (root/'logs/index.md').exists()
    assert not (root/'.lfg/metadata-migration.json').exists()


@pytest.mark.skipif(sys.platform == 'win32', reason='Bash PATH isolation')
def test_fresh_install_requires_python_before_writes(tmp_path):
    root = tmp_path/'project'; root.mkdir()
    commands = tmp_path/'bin'; commands.mkdir()
    (commands/'dirname').symlink_to(shutil.which('dirname'))
    env = dict(os.environ, PATH=str(commands))
    result = subprocess.run([shutil.which('bash'), str(PRODUCT/'scripts/install.sh'),
                             '--force', '--profile', 'solo-developer', '--ai-assistant', 'generic'],
                            cwd=root, env=env, capture_output=True, text=True)
    assert result.returncode == 2, result.stdout + result.stderr
    assert 'Python 3.10+ is required' in result.stdout
    assert not list(root.iterdir())
