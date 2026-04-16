"""Execution-scoped and persistent cache helpers."""

from __future__ import annotations

import asyncio
import copy
import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from platformdirs import user_cache_path

from kaiten_cli.models import (
    CACHE_MODE_OFF,
    CACHE_MODE_READWRITE,
    CACHE_MODE_REFRESH,
    CACHE_POLICY_NONE,
    CACHE_POLICY_PERSISTENT_OPT_IN,
    DebugReporter,
    ResolvedProfile,
)
from kaiten_cli.runtime.trace import ExecutionStats

HTTP_CACHE_DB_SCHEMA_VERSION = 1


def persistent_cache_path() -> Path:
    return user_cache_path("kaiten-cli") / "http-cache.sqlite3"


def _normalize_params(params: dict[str, Any] | None) -> dict[str, Any]:
    if not params:
        return {}
    return {key: value for key, value in sorted(params.items()) if value is not None}


@dataclass(frozen=True, slots=True)
class RequestCacheKey:
    scope: str
    method: str
    path: str
    params_json: str


class PersistentCache:
    """Small sqlite-backed cache for opt-in cross-process GET reuse."""

    def __init__(self, path: Path, reporter: DebugReporter | None = None):
        self.path = path
        self.reporter = reporter

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _open_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                scope TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                params_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                expires_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                PRIMARY KEY (scope, method, path, params_json)
            )
            """
        )
        conn.execute(f"PRAGMA user_version = {HTTP_CACHE_DB_SCHEMA_VERSION}")
        conn.commit()

    def _close_quietly(self, conn: sqlite3.Connection | None) -> None:
        if conn is None:
            return
        try:
            conn.close()
        except sqlite3.Error:
            return

    def _reset_store(self, reason: str) -> sqlite3.Connection | None:
        self._debug(f"cache: local store dropped store=http-cache reason={reason}")
        try:
            self.path.unlink(missing_ok=True)
        except OSError as exc:
            self._debug(f"cache: reset bypass store=http-cache reason={type(exc).__name__}")
            return None
        conn: sqlite3.Connection | None = None
        try:
            conn = self._open_connection()
            self._initialize_schema(conn)
            self._debug("cache: local store recreated store=http-cache")
            return conn
        except sqlite3.Error as exc:
            self._close_quietly(conn)
            self._debug(f"cache: reset bypass store=http-cache reason={type(exc).__name__}")
            return None

    def _connect(self) -> sqlite3.Connection | None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.path.exists()
        conn: sqlite3.Connection | None = None
        try:
            conn = self._open_connection()
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if existing and version != HTTP_CACHE_DB_SCHEMA_VERSION:
                self._close_quietly(conn)
                return self._reset_store(f"incompatible-schema:{version}")
            self._initialize_schema(conn)
            return conn
        except sqlite3.Error as exc:
            self._close_quietly(conn)
            return self._reset_store(type(exc).__name__)

    def get(self, key: RequestCacheKey) -> tuple[str, Any | None]:
        now = time.time()
        conn = self._connect()
        if conn is None:
            return "miss", None
        with conn:
            row = conn.execute(
                """
                SELECT payload_json, expires_at
                FROM responses
                WHERE scope = ? AND method = ? AND path = ? AND params_json = ?
                """,
                (key.scope, key.method, key.path, key.params_json),
            ).fetchone()
            if row is None:
                return "miss", None
            payload_json, expires_at = row
            if expires_at <= now:
                conn.execute(
                    """
                    DELETE FROM responses
                    WHERE scope = ? AND method = ? AND path = ? AND params_json = ?
                    """,
                    (key.scope, key.method, key.path, key.params_json),
                )
                conn.commit()
                return "expired", None
            return "hit", json.loads(payload_json)

    def set(self, key: RequestCacheKey, payload: Any, *, ttl_seconds: int) -> None:
        if payload is None:
            return
        payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        now = time.time()
        expires_at = now + ttl_seconds
        conn = self._connect()
        if conn is None:
            return
        with conn:
            conn.execute(
                """
                INSERT INTO responses (scope, method, path, params_json, payload_json, expires_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scope, method, path, params_json)
                DO UPDATE SET
                    payload_json = excluded.payload_json,
                    expires_at = excluded.expires_at,
                    updated_at = excluded.updated_at
                """,
                (key.scope, key.method, key.path, key.params_json, payload_json, expires_at, now),
            )
            conn.commit()

    def clear_scope(self, scope: str) -> None:
        conn = self._connect()
        if conn is None:
            return
        with conn:
            conn.execute("DELETE FROM responses WHERE scope = ?", (scope,))


@dataclass(slots=True)
class ExecutionContext:
    profile: ResolvedProfile
    reporter: DebugReporter | None = None
    persistent_cache: PersistentCache | None = None
    stats: ExecutionStats = field(default_factory=ExecutionStats)
    _request_cache: dict[RequestCacheKey, Any] = field(default_factory=dict, init=False)
    _inflight: dict[RequestCacheKey, asyncio.Task[Any]] = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @classmethod
    def for_profile(cls, profile: ResolvedProfile, reporter: DebugReporter | None = None) -> ExecutionContext:
        persistent = None
        if profile.cache_mode in {CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}:
            persistent = PersistentCache(persistent_cache_path(), reporter=reporter)
        return cls(profile=profile, reporter=reporter, persistent_cache=persistent)

    @property
    def scope(self) -> str:
        return f"{self.profile.domain}:{self.profile.name or 'environment'}"

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _make_key(self, method: str, path: str, params: dict[str, Any] | None) -> RequestCacheKey:
        normalized_params = _normalize_params(params)
        params_json = json.dumps(normalized_params, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return RequestCacheKey(
            scope=self.scope,
            method=method.upper(),
            path=path,
            params_json=params_json,
        )

    def _persistent_allowed(self, cache_policy: str) -> bool:
        return (
            cache_policy == CACHE_POLICY_PERSISTENT_OPT_IN
            and self.persistent_cache is not None
            and self.profile.cache_mode in {CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}
        )

    def _read_from_disk(self, key: RequestCacheKey, *, cache_policy: str) -> Any | None:
        if cache_policy == CACHE_POLICY_NONE:
            return None
        if self.persistent_cache is None or cache_policy != CACHE_POLICY_PERSISTENT_OPT_IN:
            self.stats.disk_cache_bypasses += 1
            self._debug(f"cache: disk bypass method={key.method} path={key.path}")
            return None
        if self.profile.cache_mode == CACHE_MODE_REFRESH:
            self.stats.disk_cache_bypasses += 1
            self._debug(f"cache: disk bypass refresh method={key.method} path={key.path}")
            return None
        try:
            status, payload = self.persistent_cache.get(key)
        except (OSError, sqlite3.Error, ValueError, json.JSONDecodeError) as exc:
            self.stats.disk_cache_bypasses += 1
            self._debug(f"cache: disk bypass method={key.method} path={key.path} reason={type(exc).__name__}")
            return None
        if status == "hit":
            self.stats.disk_cache_hits += 1
        elif status == "miss":
            self.stats.disk_cache_misses += 1
        elif status == "expired":
            self.stats.disk_cache_expired += 1
        self._debug(f"cache: disk {status} method={key.method} path={key.path}")
        return payload

    def _write_to_disk(self, key: RequestCacheKey, payload: Any, *, cache_policy: str) -> None:
        if not self._persistent_allowed(cache_policy):
            return
        try:
            self.persistent_cache.set(key, payload, ttl_seconds=self.profile.cache_ttl_seconds)
        except (OSError, TypeError, sqlite3.Error, ValueError) as exc:
            self._debug(f"cache: disk bypass method={key.method} path={key.path} reason={type(exc).__name__}")

    async def _load_or_fetch(
        self,
        key: RequestCacheKey,
        *,
        cache_policy: str,
        fetch,
    ) -> Any:
        cached = self._read_from_disk(key, cache_policy=cache_policy)
        if cached is not None:
            async with self._lock:
                self._request_cache[key] = copy.deepcopy(cached)
            return copy.deepcopy(cached)

        payload = await fetch()
        if payload is not None:
            async with self._lock:
                self._request_cache[key] = copy.deepcopy(payload)
            self._write_to_disk(key, payload, cache_policy=cache_policy)
        return copy.deepcopy(payload)

    async def get_json(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        cache_policy: str,
        fetch,
    ) -> Any:
        if method.upper() != "GET" or cache_policy == CACHE_POLICY_NONE:
            return await fetch()

        key = self._make_key(method, path, params)
        async with self._lock:
            if key in self._request_cache:
                self.stats.request_cache_hits += 1
                self._debug(f"cache: request hit method={key.method} path={key.path}")
                return copy.deepcopy(self._request_cache[key])
            task = self._inflight.get(key)
            if task is None:
                self.stats.request_cache_misses += 1
                self._debug(f"cache: request miss method={key.method} path={key.path}")
                task = asyncio.create_task(
                    self._load_or_fetch(key, cache_policy=cache_policy, fetch=fetch)
                )
                self._inflight[key] = task
            else:
                self.stats.inflight_dedup_hits += 1
                self._debug(f"cache: inflight dedup hit method={key.method} path={key.path}")

        try:
            return copy.deepcopy(await task)
        finally:
            if task.done():
                async with self._lock:
                    if self._inflight.get(key) is task:
                        self._inflight.pop(key, None)

    async def invalidate_after_mutation(self) -> None:
        async with self._lock:
            self._request_cache.clear()
        if self.persistent_cache is not None:
            try:
                self.persistent_cache.clear_scope(self.scope)
                self._debug(f"cache: profile invalidated after mutation scope={self.scope}")
            except (OSError, sqlite3.Error) as exc:
                self._debug(f"cache: invalidation bypass scope={self.scope} reason={type(exc).__name__}")
