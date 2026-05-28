"""Cold-read: simulate what a fresh agent does when handed AGENTS.md.

Reads AGENTS.md's frontmatter `related:` map and verifies each target file
exists and is non-empty. This is not an LLM test — it's an assertion that
the artifact's stated navigation graph actually leads somewhere.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[2]

# Common Git Bash location on Windows; ignored on POSIX (bash is on PATH there).
_GIT_BASH = Path("C:/Program Files/Git/usr/bin/bash.exe")


def _bash_exe() -> str:
    """Return the bash executable to use.

    On Windows, Python's PATH may resolve to WSL bash first
    (C:\\Windows\\System32\\bash.exe), which does not understand Windows-style
    paths.  Prefer Git Bash when it's present.
    """
    if sys.platform == "win32" and _GIT_BASH.exists():
        return str(_GIT_BASH)
    return "bash"


def _install_into(tmp: Path) -> None:
    (tmp / ".claude").mkdir()
    submodule = tmp / ".log-file-genius" / "product"
    submodule.mkdir(parents=True)
    # Cross-platform copy (don't shell out to `cp`, which is Unix-only).
    for item in (REPO / "product").iterdir():
        target = submodule / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    # Use as_posix() so Git Bash receives a forward-slash path (C:/...) that
    # it translates correctly.  Wrapping in `bash -c` is required on Windows
    # because MSYS2 only auto-translates Windows paths inside shell strings,
    # not when passed as separate argv elements.
    script = (REPO / "product/scripts/install.sh").as_posix()
    bash = _bash_exe()
    subprocess.check_call(
        [bash, "-c",
         f"bash {script} --profile solo-developer --ai-assistant claude-code --force"],
        cwd=tmp,
        stdout=subprocess.DEVNULL,
    )


def test_agents_md_related_map_resolves():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _install_into(tmp)
        agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
        # Pull the related: block (lines indented under 'related:').
        m = re.search(r"(?ms)^related:\n((?:  .+\n)+)", agents)
        assert m, "AGENTS.md missing 'related:' frontmatter block"
        targets = []
        for line in m.group(1).splitlines():
            mm = re.match(r"^\s+\w+:\s*(\S+)", line)
            if mm:
                targets.append(mm.group(1))
        assert targets, "no related: entries parsed"
        for rel in targets:
            target = (tmp / rel).resolve()
            assert target.exists(), f"AGENTS.md points at {rel} but it does not exist after install"
            assert target.stat().st_size > 0, f"{rel} is empty"
