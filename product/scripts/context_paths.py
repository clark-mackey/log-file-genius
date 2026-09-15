"""Shared repository/config resolution; no dependency on the caller's directory."""
from pathlib import Path
from config_parser import parse_config

DEFAULTS = dict(state="logs/STATE.md", changelog="logs/CHANGELOG.md",
                devlog="logs/DEVLOG.md", adr_dir="logs/adr", incidents_dir="logs/incidents")


def project_root(start):
    start = Path(start).resolve()
    for path in (start, *start.parents):
        if (path / ".logfile-config.yml").is_file():
            return path
        if (path / ".git").exists():
            return path
    return start


def context_paths(root):
    root = Path(root).resolve()
    cfg = parse_config(str(root / ".logfile-config.yml")).get("paths", {})
    # Older configurations used 'adr'.
    cfg = dict(cfg)
    if "adr_dir" not in cfg and "adr" in cfg:
        cfg["adr_dir"] = cfg["adr"]
    result = {}
    for key, default in DEFAULTS.items():
        path = (root / cfg.get(key, default)).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Configured {key} escapes repository: {path}")
        result[key] = path
    return result


def tokens(text):
    return (len(text) + 3) // 4
