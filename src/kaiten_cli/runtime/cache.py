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

    def __init__(self, path: Path):
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
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
        return conn

    def get(self, key: RequestCacheKey) -> tuple[str, Any | None]:
        now = time.time()
        with self._connect() as conn:
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
        with self._connect() as conn:
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
        with self._connect() as conn:
            conn.execute("DELETE FROM responses WHERE scope = ?", (scope,))
            conn.commit()


@dataclass(slots=True)
class ExecutionContext:
    profile: ResolvedProfile
    reporter: DebugReporter | None = None
    persistent_cache: PersistentCache | None = None
    _request_cache: dict[RequestCacheKey, Any] = field(default_factory=dict, init=False)
    _inflight: dict[RequestCacheKey, asyncio.Task[Any]] = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @classmethod
    def for_profile(cls, profile: ResolvedProfile, reporter: DebugReporter | None = None) -> ExecutionContext:
        persistent = None
        if profile.cache_mode in {CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}:
            persistent = PersistentCache(persistent_cache_path())
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
            self._debug(f"cache: disk bypass method={key.method} path={key.path}")
            return None
        if self.profile.cache_mode == CACHE_MODE_REFRESH:
            self._debug(f"cache: disk bypass refresh method={key.method} path={key.path}")
            return None
        try:
            status, payload = self.persistent_cache.get(key)
        except (OSError, sqlite3.Error, ValueError, json.JSONDecodeError) as exc:
            self._debug(f"cache: disk bypass method={key.method} path={key.path} reason={type(exc).__name__}")
            return None
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
                self._debug(f"cache: request hit method={key.method} path={key.path}")
                return copy.deepcopy(self._request_cache[key])
            task = self._inflight.get(key)
            if task is None:
                self._debug(f"cache: request miss method={key.method} path={key.path}")
                task = asyncio.create_task(
                    self._load_or_fetch(key, cache_policy=cache_policy, fetch=fetch)
                )
                self._inflight[key] = task
            else:
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
