"""Preservation-checked per-file replacement, shared by metadata and index writers."""
import hashlib
import os
from pathlib import Path
import tempfile


def retire(path, expected):
    """Remove from active use by atomic rename, retaining actual bytes for recovery."""
    import uuid
    path = Path(path)
    if path.is_symlink() or path.read_bytes() != expected:
        raise ValueError(f'Concurrent change or symlink: {path}')
    saved = path.with_name(path.name + '.lfg-retired-' + uuid.uuid4().hex)
    path.rename(saved)
    if saved.read_bytes() != expected:
        try:
            os.link(saved, path)  # exclusive restoration; preserve any newer path
        except FileExistsError:
            pass
        raise ValueError(f'Concurrent edit preserved at {saved}; reconcile before recovery')
    return saved


def replace(path, content, expected, validate=lambda data: None):
    """Validate before mutation; backup exact bytes; refuse changed targets.

    Atomic per file, not across a collection. Callers journal collection progress.
    A final read detects intervening edits; no claim of cross-process locking.
    """
    path = Path(path)
    data = content.encode("utf-8") if isinstance(content, str) else content
    validate(data)
    def current():
        return path.read_bytes() if path.exists() else None
    if path.is_symlink() or current() != expected:
        raise ValueError(f"Concurrent change or symlink: {path}")
    if data == expected:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if expected is not None:
        digest = hashlib.sha256(expected).hexdigest()[:16]
        backup = path.with_name(path.name + f".lfg-backup-{digest}")
        if backup.exists():
            if backup.read_bytes() != expected:
                raise ValueError(f"Backup collision: {backup}")
        else:
            with backup.open("xb") as stream:
                stream.write(expected)
                stream.flush()
                os.fsync(stream.fileno())
    name = None
    try:
        fd, name = tempfile.mkstemp(prefix=".lfg-", dir=path.parent)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if expected is not None:
            os.chmod(name, path.stat().st_mode)
        if current() != expected:
            raise ValueError(f"Concurrent change: {path}")
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)
    return True
