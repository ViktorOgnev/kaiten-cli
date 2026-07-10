"""Classification helpers for safe SQLite recovery."""

from __future__ import annotations

import sqlite3


_RESETTABLE_PRIMARY_CODES = frozenset(
    {
        getattr(sqlite3, "SQLITE_CORRUPT", 11),
        getattr(sqlite3, "SQLITE_NOTADB", 26),
    }
)


def is_corrupt_database_error(error: sqlite3.Error) -> bool:
    """Return whether rebuilding a disposable or derived database is safe."""

    code = getattr(error, "sqlite_errorcode", None)
    if isinstance(code, int):
        return code & 0xFF in _RESETTABLE_PRIMARY_CODES
    message = str(error).strip().lower()
    return "file is not a database" in message or "database disk image is malformed" in message
