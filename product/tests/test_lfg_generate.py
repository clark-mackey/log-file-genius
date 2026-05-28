import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"


def run(args, cwd=ROOT):
    return subprocess.run([sys.executable, str(LFG)] + args, cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


def test_generate_writes_agents_md(tmp_path):
    # Use --out so we don't clobber the committed product/AGENTS.md.
    out = tmp_path / "AGENTS.md"
    r = run(["generate", "--out", str(out)])
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "doc: AGENTS" in text
    assert "## log-file-maintenance" in text


def test_generate_idempotent(tmp_path):
    out1 = tmp_path / "1.md"
    out2 = tmp_path / "2.md"
    assert run(["generate", "--out", str(out1)]).returncode == 0
    assert run(["generate", "--out", str(out2)]).returncode == 0
    assert out1.read_bytes() == out2.read_bytes()


def test_generate_check_passes_when_committed_matches():
    # After Step 4 writes product/AGENTS.md, --check is zero-diff.
    r = run(["generate"])
    assert r.returncode == 0, r.stderr
    r = run(["generate", "--check"])
    assert r.returncode == 0, f"check failed:\n{r.stdout}\n{r.stderr}"


def test_generate_check_fails_on_drift():
    target = ROOT / "product/AGENTS.md"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\nINJECTED DRIFT\n")
        r = run(["generate", "--check"])
        assert r.returncode != 0
        combined = (r.stdout + r.stderr).lower()
        assert "drift" in combined or "diff" in combined
    finally:
        # Always restore to keep the repo clean.
        target.write_bytes(original)
