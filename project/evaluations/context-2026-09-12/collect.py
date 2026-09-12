#!/usr/bin/env python3
"""Extract auditable evidence. Deliberately never infer a semantic pass from keywords."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import shlex

def read_inventory(calls, cwd):
    """Conservative lower bound; never execute or evaluate model-produced shell text."""
    reads, opaque = [], []
    for number, call in enumerate(calls):
        arguments = call.get('input', {})
        if call['name'] == 'Read':
            reads.append({'tool': number, 'path': arguments.get('file_path'), 'method': 'Read'})
            continue
        if call['name'] not in ('exec_command', 'Bash'):
            if call['name'] == 'Grep':
                opaque.append(number)
            continue
        command = arguments.get('cmd', arguments.get('command', '')) if isinstance(arguments, dict) else str(arguments)
        directory = Path(arguments.get('workdir', cwd)) if isinstance(arguments, dict) else Path(cwd)
        if re.search(r'\b(rg|grep)\b', command) and '--files' not in command:
            opaque.append(number)
        if not re.search(r'\b(cat|sed|nl|head|tail)\b', command):
            if re.search(r'\b(python3?|lfg)\b', command) and re.search(r'\b(routes|prime|read_text|read_bytes)\b', command):
                opaque.append(number)
            continue
        try:
            lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|<>')
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            opaque.append(number)
            continue
        segments, segment = [], []
        for token in tokens + [';']:
            if token in (';', '&&', '||', '|', '&'):
                if segment:
                    segments.append(segment)
                segment = []
            else:
                segment.append(token)
        for segment in segments:
            if segment[0] == 'cd' and len(segment) == 2 and '$' not in segment[1]:
                directory = (directory / segment[1]).resolve()
                continue
            if Path(segment[0]).name not in ('cat', 'sed', 'nl', 'head', 'tail'):
                if any(token in ('for', 'while', 'eval', 'do') for token in segment):
                    opaque.append(number)
                continue
            for token in segment[1:]:
                if token in ('>', '>>', '<', '<<', '>&', '<&'):
                    break  # Never count redirection targets as input-file operands.
                if '$' in token or '`' in token:
                    opaque.append(number)
                    continue
                if not re.search(r'\.(md|py|json|ya?ml|txt)$', token, re.I):
                    continue
                path = Path(token)
                if not path.is_absolute():
                    path = directory / path
                if any(c in token for c in '*?['):
                    # Globs are intentionally not expanded against the post-run tree.
                    opaque.append(number)
                else:
                    reads.append({'tool': number, 'path': str(path.resolve()), 'method': 'shell-explicit-operand'})
    return reads, sorted(set(opaque))

def lines(path):
    if not path.exists():
        return []
    result = []
    for line in path.read_text().splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return result

def estimate(text):
    return math.ceil(len(text) / 4)

def collect(base, out):
    result = json.loads((out / 'result.json').read_text())
    invocation = json.loads((out / 'invocation.json').read_text())
    root = Path(invocation['cwd'])
    if result['fixture'] == 'nested':
        root = root.parent.parent
    events = lines(out / 'events.jsonl')
    tools, messages, models, usage, native = [], [], set(), None, None
    version, host_context, injections, host_calls, context_usage = None, [], [], [], None
    context_usage = next((event['context_usage'] for event in events if event.get('context_usage')), None)
    calls_by_id = {}
    if result['host'] == 'codex':
        for path in Path(invocation['host_config']).glob('sessions/**/*.jsonl'):
            for event in lines(path):
                payload = event.get('payload', {})
                if event['type'] == 'response_item' and payload.get('type') == 'function_call':
                    try:
                        arguments = json.loads(payload.get('arguments', '{}'))
                    except json.JSONDecodeError:
                        arguments = payload.get('arguments')
                    call = {'name': payload.get('name'), 'input': arguments, 'output': ''}
                    calls_by_id[payload['call_id']] = call
                    host_calls.append(call)
                if event['type'] == 'response_item' and payload.get('type') == 'function_call_output':
                    if payload.get('call_id') in calls_by_id:
                        output = payload.get('output', '')
                        calls_by_id[payload['call_id']]['output'] = output if isinstance(output, str) else json.dumps(output)
                if event['type'] == 'session_meta':
                    version = payload.get('cli_version')
                if event['type'] == 'turn_context':
                    models.add(payload['model'])
                if event['type'] == 'world_state':
                    instruction = payload.get('state', {}).get('agents_md')
                    if payload.get('full') and payload.get('state', {}).get('agents_md') == {}:
                        native = ''  # Host explicitly recorded an empty instruction chain.
                    if instruction:
                        native = instruction.get('text', '')
                        host_context.append(instruction)
                if event['type'] == 'response_item' and payload.get('role') == 'user':
                    for content in payload.get('content', []):
                        text = content.get('text', '')
                        for match in re.finditer(r'# AGENTS\.md instructions[^\n]*\n\n<INSTRUCTIONS>.*?</INSTRUCTIONS>', text, re.S):
                            injections.append(match.group())
        for event in events:
            item = event.get('item', {})
            if event['type'] == 'item.completed' and item.get('type') == 'command_execution':
                tools.append({'name': 'shell', 'input': item['command'], 'output': item.get('aggregated_output', ''), 'exit_code': item.get('exit_code')})
            elif event['type'] == 'item.completed' and item.get('type') == 'file_change':
                tools.append({'name': 'file_change', 'input': item.get('changes'), 'output': ''})
            elif event['type'] == 'item.completed' and item.get('type') == 'agent_message':
                messages.append(item['text'])
            if event['type'] == 'turn.completed':
                usage = event.get('usage')
    else:
        pending = {}
        for event in events:
            if event['type'] == 'system' and event.get('subtype') == 'init':
                version = event.get('claude_code_version')
                host_context.append({'init_model': event.get('model'), 'memory_paths': event.get('memory_paths')})
            if event['type'] == 'assistant':
                model = event.get('message', {}).get('model')
                if model and model != '<synthetic>':
                    models.add(model)
                for content in event.get('message', {}).get('content', []):
                    if content['type'] == 'text':
                        messages.append(content['text'])
                    elif content['type'] == 'tool_use' and content['id'] not in pending:
                        tool = {'name': content['name'], 'input': content['input'], 'output': ''}
                        pending[content['id']] = tool
                        tools.append(tool)
            elif event['type'] == 'user':
                for content in event.get('message', {}).get('content', []):
                    if isinstance(content, dict) and content.get('type') == 'tool_result':
                        if content['tool_use_id'] in pending:
                            output = content.get('content', '')
                            pending[content['tool_use_id']]['output'] = output if isinstance(output, str) else json.dumps(output)
                            pending[content['tool_use_id']]['is_error'] = content.get('is_error', False)
            elif event['type'] == 'result':
                usage = event.get('usage')
    sources = json.loads((base / 'oracles' / result['condition'] / f"{result['fixture']}.json").read_text())
    all_output = '\n'.join(t['output'] for t in tools)
    # Remove the common Read/nl line-number envelope only for source matching.
    normalized = re.sub(r'(?m)^[ \t]*\d+[ \t]*(?:→|\t)[ ]?', '', all_output)
    source_hits = {}
    for relative in sources['required_files']:
        path = base / 'seeds' / result['condition'] / result['fixture'] / relative
        if not path.exists():
            source_hits[relative] = {'complete_body_visible': False}
            continue
        text = path.read_text()
        source_hits[relative] = {'complete_body_visible': text.strip() in normalized,
                                 'source_sha256': hashlib.sha256(text.encode()).hexdigest()}
    read_calls = sum(t['name'] == 'Read' for t in tools)
    writes = sum(t['name'] in ('Write', 'Edit', 'file_change') for t in tools)
    shell_writes = [i for i,t in enumerate(tools) if t['name'] in ('Bash', 'shell') and re.search(r'\b(tee|touch|mkdir|cp|mv|rm)\b|(?<![2>])>{1,2}(?!&)', str(t['input']))]
    actual_outputs = host_calls if result['host'] == 'codex' else tools
    source_reads, opaque_reads = read_inventory(actual_outputs, invocation['cwd'])
    try:
        module = ast.parse((root / 'api/receipt.py').read_text())
        function = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'display_amount')
        unchanged_amount = (len(function.body) == 1 and isinstance(function.body[0], ast.Return) and
                            isinstance(function.body[0].value, ast.Name) and function.body[0].value.id == 'amount_minor')
    except (OSError, SyntaxError, StopIteration):
        unchanged_amount = None
    estimates = sum(estimate(t['output']) for t in actual_outputs)
    if native is not None:
        estimates += sum(map(estimate, injections)) if injections else estimate(native)
    other_consumers = set()
    for other in (base / 'results').glob('*/invocation.json'):
        other_cwd = json.loads(other.read_text())['cwd']
        if other_cwd != str(root) and other_cwd != invocation['cwd']:
            if other_cwd.endswith('/src/component'):
                other_cwd = other_cwd.removesuffix('/src/component')
            if other_cwd != str(root):
                other_consumers.add(other_cwd)
    trace = json.dumps(tools + host_calls)
    contamination = [p for p in (str(base), str(Path(__file__).resolve().parent), 'ORACLE.md', *sorted(other_consumers)) if p in trace]
    for path in sorted(other_consumers):
        name = Path(path).name
        if name.startswith('receipt-consumer-') and name in trace and path not in contamination:
            contamination.append(path)
        parent_name = Path(path).parent.name
        if parent_name.startswith('receipt-isolation-') and parent_name in trace and path not in contamination:
            contamination.append(path)
    ambiguous_role = (result['kind'] == 'behavior' and result['fixture'] == 'delegated' and
                      'new subagent implementer' not in (out / 'prompt.txt').read_text())
    owner_control_missing = (result['condition'] == 'ordinary' and
                             result['fixture'] in ('brownfield', 'override') and
                             not (base / 'seeds' / 'ordinary' / result['fixture'] /
                                  ('AGENTS.md' if result['fixture'] == 'brownfield' else 'AGENTS.override.md')).exists())
    evidence = {**result, 'resolved_models': sorted(models), 'host_version': version,
                'native_instruction_text': native,
                'native_injection_status': 'host_world_state_observed' if native is not None else 'unknown',
                'native_instruction_estimated_tokens': estimate(native) if native is not None else None,
                'native_injection_events': injections,
                'native_wrapped_instruction_estimated_tokens': sum(map(estimate, injections)) if injections else None,
                'candidate_entry_visible': bool(native and '# LFG context' in native),
                'host_context': host_context, 'provider_usage': usage,
                'native_context_usage': context_usage,
                'model_identity_source': 'Codex turn_context selection; backend checkpoint not exposed' if result['host'] == 'codex' else 'Claude assistant message model',
                'native_body_utf8_bytes': len(native.encode('utf-8')) if native is not None else None,
                'native_wrapped_utf8_bytes': sum(len(s.encode('utf-8')) for s in injections) if injections else None,
                'final_code_simple_identity_return': unchanged_amount,
                'source_hits': source_hits, 'tools': tools, 'host_calls': host_calls, 'messages': messages,
                'tool_output_estimated_tokens': sum(estimate(t['output']) for t in actual_outputs),
                'discovery_estimated_tokens': estimates if native is not None else None,
                'read_tool_calls_lower_bound': read_calls,
                'source_read_count': None,
                'source_read_lower_bound': len(source_reads), 'source_read_events': source_reads,
                'opaque_read_tools': opaque_reads,
                'read_cap_demonstrably_exceeded': len(source_reads) > 8,
                'direct_write_tool_actions_lower_bound': writes, 'shell_write_candidates': shell_writes,
                'contamination_hits': contamination,
                'role_ambiguous': ambiguous_role,
                'ordinary_owner_instruction_missing': owner_control_missing,
                'trial_validity': 'invalid-cross-trial-or-evaluator-exposure' if contamination else ('invalid-delegation-role-ambiguity' if ambiguous_role else 'trace-audit-no-known-evaluator-path'),
                'narration_estimated_tokens': sum(estimate(m) for m in messages),
                'semantic_adjudication': 'pending', 'gate_result': 'invalid' if contamination or ambiguous_role else 'not_passed',
                'limitations': ['Source-read count and semantic correctness require trace adjudication.',
                    'Discovery total includes all tool output, including failed searches; provider usage is separate.',
                    'Maintenance commits are only measured when the host actually permits local Git writes.']}
    write_path = out / 'evidence.json'
    write_path.write_text(json.dumps(evidence, indent=2)+'\n')
    return {k:v for k,v in evidence.items() if k not in ('native_instruction_text','native_injection_events','host_context','tools','host_calls','messages','final_diff')}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, required=True)
    args = parser.parse_args()
    rows = [collect(args.base, p.parent) for p in sorted((args.base / 'results').glob('*/result.json'))]
    for path in sorted((args.base / 'results').glob('*/attempt-error.json')):
        if not (path.parent / 'result.json').exists():
            rows.append({**json.loads(path.read_text()), 'returncode': None, 'gate_result': 'not_started_or_harness_error'})
    (args.base / 'summary.json').write_text(json.dumps(rows, indent=2)+'\n')
    print(json.dumps({'collected': len(rows), 'process_failures': sum(r['returncode'] != 0 for r in rows),
                      'gate_passes': 0, 'note': 'No semantic or read-count gate inferred from process success.'}))
