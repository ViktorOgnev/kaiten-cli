"""Private filesystem helpers for credentials and derived Kaiten data."""

from __future__ import annotations

import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path


PRIVATE_DIRECTORY_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


def _set_mode(descriptor: int, path: Path, mode: int) -> None:
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(descriptor, mode)
    else:  # pragma: no cover - Windows fallback
        path.chmod(mode)


def _mode_needs_repair(descriptor: int, mode: int) -> bool:
    return stat.S_IMODE(os.fstat(descriptor).st_mode) != mode


def secure_directory(
    path: Path,
    *,
    mode: int = PRIVATE_DIRECTORY_MODE,
    repair_existing: bool = True,
) -> None:
    """Create a private directory and optionally repair an existing directory's mode."""

    if path.is_symlink():
        if repair_existing:
            raise OSError(f"Refusing to use symlinked private directory: {path}")
        resolved = path.resolve(strict=True)
        if not resolved.is_dir():
            raise OSError(f"Private directory path is not a directory: {path}")
        if os.name != "nt":
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(resolved, flags)
            os.close(descriptor)
        return
    existed = path.exists()
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    if os.name == "nt":  # pragma: no cover - Windows ACLs remain platform-managed
        if not path.is_dir():
            raise OSError(f"Private directory path is not a directory: {path}")
        if repair_existing or not existed:
            path.chmod(mode)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        if (repair_existing or not existed) and _mode_needs_repair(descriptor, mode):
            _set_mode(descriptor, path, mode)
    finally:
        os.close(descriptor)


def ensure_private_file(
    path: Path,
    *,
    mode: int = PRIVATE_FILE_MODE,
    repair_parent: bool = True,
) -> None:
    """Create an empty private file when absent and repair its POSIX mode."""

    secure_directory(path.parent, repair_existing=repair_parent)
    if os.name == "nt":  # pragma: no cover - Windows ACLs remain platform-managed
        if path.is_symlink():
            raise OSError(f"Refusing to use symlinked private file: {path}")
        path.touch(exist_ok=True)
        if not path.is_file():
            raise OSError(f"Private file path is not a regular file: {path}")
        path.chmod(mode)
        return
    flags = (
        os.O_CREAT
        | os.O_EXCL
        | os.O_RDWR
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    descriptor: int | None = None
    for _ in range(3):
        try:
            descriptor = os.open(path, flags, mode)
            break
        except FileExistsError:
            secure_existing_file(path, mode=mode)
            if path.exists():
                return
    if descriptor is None:
        raise OSError(f"Private file path changed repeatedly while opening: {path}")
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(f"Private file path is not a regular file: {path}")
        if _mode_needs_repair(descriptor, mode):
            _set_mode(descriptor, path, mode)
    finally:
        os.close(descriptor)


def secure_existing_file(path: Path, *, mode: int = PRIVATE_FILE_MODE) -> None:
    """Repair a private file mode without creating the file."""

    if path.is_symlink():
        raise OSError(f"Refusing to use symlinked private file: {path}")
    if not path.exists():
        return
    if os.name == "nt":  # pragma: no cover - Windows ACLs remain platform-managed
        if not path.is_file():
            raise OSError(f"Private file path is not a regular file: {path}")
        path.chmod(mode)
        return
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(f"Private file path is not a regular file: {path}")
        if _mode_needs_repair(descriptor, mode):
            _set_mode(descriptor, path, mode)
    finally:
        os.close(descriptor)


@contextmanager
def open_private_append(
    path: Path,
    *,
    mode: int = PRIVATE_FILE_MODE,
    repair_parent: bool = False,
) -> Iterator[TextIOWrapper]:
    """Open one no-follow descriptor for both private-mode repair and append writes."""

    secure_directory(path.parent, repair_existing=repair_parent)
    if path.is_symlink():
        raise OSError(f"Refusing to use symlinked private file: {path}")
    flags = (
        os.O_CREAT
        | os.O_WRONLY
        | os.O_APPEND
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    descriptor = os.open(path, flags, mode)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(f"Private file path is not a regular file: {path}")
        if _mode_needs_repair(descriptor, mode):
            _set_mode(descriptor, path, mode)
        with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
            descriptor = -1
            yield stream
    finally:
        if descriptor >= 0:
            os.close(descriptor)
