"""Minimal, dependency-free parser for the LFG config subset.

Supported subset (documented contract):
  - UTF-8 text, space indentation only (tabs are an error)
  - top-level `key: value` scalars
  - one level of nesting: a `key:` line followed by 2-space-indented `key: value`
  - `#` comments (full-line or trailing), blank lines ignored
  - values may be optionally single- or double-quoted
  - integer-looking values are coerced to int

Anything outside this subset raises ConfigError (fail loudly, never guess).
"""
from __future__ import annotations
import os
from typing import Dict, Any


class ConfigError(ValueError):
    pass


def _coerce(value: str) -> Any:
    v = value.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    if v.lstrip("-").isdigit():
        return int(v)
    return v


def _strip_comment(line: str) -> str:
    # Remove trailing comments not inside quotes (config subset has no '#' in values).
    out = []
    quote = None
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
            out.append(ch)
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def parse_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        return {}

    result: Dict[str, Any] = {}
    current_parent = None

    # utf-8-sig transparently strips a BOM (common from Windows/Notepad edits) so
    # the first key isn't silently mangled. OS/decode errors become ConfigError so
    # callers get the clean failure path, never a raw traceback.
    try:
        f = open(config_path, "r", encoding="utf-8-sig")
    except OSError as e:
        raise ConfigError(f"Could not open config: {e}")

    with f:
        try:
            lines = list(enumerate(f, 1))
        except (OSError, UnicodeDecodeError) as e:
            raise ConfigError(f"Could not read config: {e}")
        for lineno, raw in lines:
            if "\t" in raw:
                raise ConfigError(f"Tab indentation not allowed (line {lineno})")
            line = _strip_comment(raw)
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()

            if ":" not in stripped:
                raise ConfigError(f"Expected 'key: value' (line {lineno}): {stripped!r}")

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if indent == 0:
                if value == "":
                    result[key] = {}
                    current_parent = key
                else:
                    result[key] = _coerce(value)
                    current_parent = None
            elif indent == 2:
                if current_parent is None or not isinstance(result.get(current_parent), dict):
                    raise ConfigError(f"Nested key without parent block (line {lineno})")
                result[current_parent][key] = _coerce(value)
            else:
                raise ConfigError(f"Unexpected indentation {indent} (line {lineno})")

    return result
