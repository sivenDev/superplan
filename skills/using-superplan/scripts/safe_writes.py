"""Locked, preconditioned, atomic text updates for Superplan workspace files."""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised on Windows only
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised on POSIX only
    msvcrt = None


@dataclass(frozen=True)
class TextUpdate:
    path: Path
    original: str | None
    updated: str


def _lock_path(root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "superplan.lock"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        candidate = Path(result.stdout.strip())
        return (candidate if candidate.is_absolute() else root / candidate).resolve()
    digest = hashlib.sha256(str(root.resolve()).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "superplan-locks" / f"{digest}.lock"


@contextmanager
def workspace_lock(root: Path) -> Iterator[None]:
    path = _lock_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        elif msvcrt is not None:  # pragma: no cover - exercised on Windows only
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:  # pragma: no cover - supported Python platforms expose one API
            raise OSError("no supported file-locking API")
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            elif msvcrt is not None:  # pragma: no cover - exercised on Windows only
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _read_text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def _stage_text(path: Path, content: str, mode: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    staged = Path(raw_path)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        staged.chmod(mode)
        return staged
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


def commit_text_updates(updates: list[TextUpdate]) -> list[Path]:
    paths = [update.path for update in updates]
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate path in text update transaction")

    current: dict[Path, str | None] = {}
    changed: list[TextUpdate] = []
    modes: dict[Path, int] = {}
    for update in updates:
        content = _read_text(update.path)
        current[update.path] = content
        if content != update.original:
            raise OSError(f"{update.path}: changed since preflight")
        if content == update.updated:
            continue
        changed.append(update)
        modes[update.path] = (
            stat.S_IMODE(update.path.stat().st_mode) if content is not None else 0o644
        )

    staged_updates: dict[Path, Path] = {}
    rollback_files: dict[Path, Path] = {}
    replaced: list[TextUpdate] = []
    try:
        for update in changed:
            staged_updates[update.path] = _stage_text(
                update.path,
                update.updated,
                modes[update.path],
            )
            if update.original is not None:
                rollback_files[update.path] = _stage_text(
                    update.path,
                    update.original,
                    modes[update.path],
                )

        for update in changed:
            if _read_text(update.path) != current[update.path]:
                raise OSError(f"{update.path}: changed since preflight")

        for update in changed:
            os.replace(staged_updates[update.path], update.path)
            del staged_updates[update.path]
            replaced.append(update)
    except OSError as exc:
        rollback_errors: list[str] = []
        for update in reversed(replaced):
            try:
                if update.original is None:
                    update.path.unlink(missing_ok=True)
                else:
                    os.replace(rollback_files.pop(update.path), update.path)
            except OSError as rollback_exc:
                rollback_errors.append(f"{update.path}: {rollback_exc}")
        detail = f"; rollback failed: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise OSError(f"write transaction failed: {exc}{detail}") from exc
    finally:
        for path in [*staged_updates.values(), *rollback_files.values()]:
            path.unlink(missing_ok=True)

    return [update.path for update in changed]
