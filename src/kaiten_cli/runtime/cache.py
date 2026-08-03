"""Execution-scoped and persistent cache helpers."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from platformdirs import user_cache_path

from kaiten_cli.models import (
    CACHE_MODE_AUTO,
    CACHE_MODE_READWRITE,
    CACHE_MODE_REFRESH,
    CACHE_POLICY_NONE,
    CACHE_POLICY_PERSISTENT_HEAVY,
    DebugReporter,
    PERSISTENT_CACHE_POLICIES,
    ResolvedProfile,
)
from kaiten_cli.runtime.fs_security import ensure_private_file
from kaiten_cli.runtime.sqlite_errors import is_corrupt_database_error
from kaiten_cli.runtime.trace import ExecutionStats, path_family_for

HTTP_CACHE_DB_SCHEMA_VERSION = 4
AUTO_ENTITY_TTL_SECONDS = 30 * 60
AUTO_MEDIUM_TTL_SECONDS = 6 * 60 * 60
AUTO_HEAVY_TTL_SECONDS = 24 * 60 * 60
AUTO_HISTORICAL_TTL_SECONDS = 7 * 24 * 60 * 60
AUTO_HEAVY_ROW_THRESHOLD = 500
AUTO_MEDIUM_ROW_THRESHOLD = 100
AUTO_HEAVY_PAYLOAD_BYTES = 1_000_000
AUTO_MEDIUM_PAYLOAD_BYTES = 100_000
AUTO_DENSE_FAMILY_WINDOW_SECONDS = 30 * 60
AUTO_DENSE_FAMILY_MEDIUM_THRESHOLD = 25
AUTO_DENSE_FAMILY_HEAVY_THRESHOLD = 100


def persistent_cache_path() -> Path:
    return user_cache_path("kaiten-cli") / "http-cache.sqlite3"


def _normalize_params(params: dict[str, Any] | None) -> dict[str, Any]:
    if not params:
        return {}
    return {key: value for key, value in sorted(params.items()) if value is not None}


def _payload_rows_count(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("items", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
    return 1 if payload is not None else 0


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _looks_historical(params_json: str) -> bool:
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        return False
    if not isinstance(params, dict):
        return False
    for key in ("created_before", "updated_before", "to", "window_end", "date_to", "date-to"):
        value = _parse_datetime(params.get(key))
        if value is None:
            continue
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        if value < today_start:
            return True
    return False


@dataclass(frozen=True, slots=True)
class RequestCacheKey:
    scope: str
    method: str
    path: str
    params_json: str
    path_family: str


class PersistentCache:
    """Small sqlite-backed cache for cross-process safe GET reuse."""

    def __init__(self, path: Path, reporter: DebugReporter | None = None):
        self.path = path
        self.reporter = reporter

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _open_connection(self) -> sqlite3.Connection:
        ensure_private_file(self.path)
        return sqlite3.connect(self.path)

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                scope TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                path_family TEXT NOT NULL DEFAULT '',
                params_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                expires_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT 0,
                cache_policy TEXT NOT NULL DEFAULT '',
                ttl_seconds INTEGER NOT NULL DEFAULT 0,
                payload_bytes INTEGER NOT NULL DEFAULT 0,
                rows_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (scope, method, path, params_json)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_responses_family_recent
            ON responses (scope, method, path_family, updated_at)
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
        except (OSError, sqlite3.Error) as exc:
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
        except (OSError, sqlite3.Error) as exc:
            self._close_quietly(conn)
            if isinstance(exc, sqlite3.Error) and is_corrupt_database_error(exc):
                return self._reset_store(type(exc).__name__)
            self._debug(f"cache: local store bypass store=http-cache reason={type(exc).__name__}")
            return None

    def get(self, key: RequestCacheKey) -> tuple[str, Any | None]:
        now = time.time()
        conn = self._connect()
        if conn is None:
            return "miss", None
        with closing(conn), conn:
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

    def set(
        self,
        key: RequestCacheKey,
        payload: Any,
        *,
        ttl_seconds: int,
        cache_policy: str,
        payload_bytes: int,
        rows_count: int,
    ) -> None:
        if payload is None:
            return
        payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        now = time.time()
        expires_at = now + ttl_seconds
        conn = self._connect()
        if conn is None:
            return
        with closing(conn), conn:
            conn.execute(
                """
                INSERT INTO responses (
                    scope, method, path, path_family, params_json, payload_json, expires_at, updated_at,
                    created_at, cache_policy, ttl_seconds, payload_bytes, rows_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scope, method, path, params_json)
                DO UPDATE SET
                    path_family = excluded.path_family,
                    payload_json = excluded.payload_json,
                    expires_at = excluded.expires_at,
                    updated_at = excluded.updated_at,
                    cache_policy = excluded.cache_policy,
                    ttl_seconds = excluded.ttl_seconds,
                    payload_bytes = excluded.payload_bytes,
                    rows_count = excluded.rows_count
                """,
                (
                    key.scope,
                    key.method,
                    key.path,
                    key.path_family,
                    key.params_json,
                    payload_json,
                    expires_at,
                    now,
                    now,
                    cache_policy,
                    ttl_seconds,
                    payload_bytes,
                    rows_count,
                ),
            )
            conn.commit()

    def count_recent_family(
        self, *, scope: str, method: str, path_family: str, since: float
    ) -> int:
        conn = self._connect()
        if conn is None:
            return 0
        with closing(conn), conn:
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM responses
                WHERE scope = ? AND method = ? AND path_family = ? AND updated_at >= ?
                """,
                (scope, method, path_family, since),
            ).fetchone()
        return int(row[0]) if row is not None else 0

    def extend_recent_family(
        self,
        *,
        scope: str,
        method: str,
        path_family: str,
        since: float,
        ttl_seconds: int,
    ) -> int:
        now = time.time()
        expires_at = now + ttl_seconds
        conn = self._connect()
        if conn is None:
            return 0
        with closing(conn), conn:
            cursor = conn.execute(
                """
                UPDATE responses
                SET
                    expires_at = CASE WHEN expires_at < ? THEN ? ELSE expires_at END,
                    ttl_seconds = CASE WHEN ttl_seconds < ? THEN ? ELSE ttl_seconds END
                WHERE scope = ? AND method = ? AND path_family = ? AND updated_at >= ?
                """,
                (
                    expires_at,
                    expires_at,
                    ttl_seconds,
                    ttl_seconds,
                    scope,
                    method,
                    path_family,
                    since,
                ),
            )
            conn.commit()
        return int(cursor.rowcount)

    def clear_scope(self, scope: str) -> None:
        conn = self._connect()
        if conn is None:
            return
        with closing(conn), conn:
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
    _rate_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _last_request_time: float = field(default=0.0, init=False)

    @classmethod
    def for_profile(
        cls, profile: ResolvedProfile, reporter: DebugReporter | None = None
    ) -> ExecutionContext:
        persistent = None
        if profile.cache_mode in {CACHE_MODE_AUTO, CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}:
            persistent = PersistentCache(persistent_cache_path(), reporter=reporter)
        return cls(
            profile=profile,
            reporter=reporter,
            persistent_cache=persistent,
            stats=ExecutionStats(
                cache_mode=profile.cache_mode,
                cache_ttl_seconds=(
                    profile.cache_ttl_seconds
                    if profile.cache_mode in {CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}
                    else None
                ),
            ),
        )

    @property
    def scope(self) -> str:
        credential_fingerprint = hashlib.sha256(self.profile.token.encode("utf-8")).hexdigest()[:16]
        scope_components = json.dumps(
            [
                self.profile.domain,
                self.profile.name or "environment",
                credential_fingerprint,
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return f"scope-{hashlib.sha256(scope_components.encode('utf-8')).hexdigest()}"

    async def wait_for_rate_slot(self, delay_seconds: float) -> None:
        """Share one low-load request budget across all clients in this execution."""

        async with self._rate_lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < delay_seconds:
                await asyncio.sleep(delay_seconds - elapsed)
            self._last_request_time = asyncio.get_running_loop().time()

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _make_key(self, method: str, path: str, params: dict[str, Any] | None) -> RequestCacheKey:
        normalized_params = _normalize_params(params)
        params_json = json.dumps(
            normalized_params, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return RequestCacheKey(
            scope=self.scope,
            method=method.upper(),
            path=path,
            params_json=params_json,
            path_family=path_family_for(path),
        )

    def _persistent_allowed(self, cache_policy: str) -> bool:
        return (
            cache_policy in PERSISTENT_CACHE_POLICIES
            and self.persistent_cache is not None
            and self.profile.cache_mode
            in {CACHE_MODE_AUTO, CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}
        )

    def _read_from_disk(self, key: RequestCacheKey, *, cache_policy: str) -> Any | None:
        if cache_policy == CACHE_POLICY_NONE:
            return None
        if self.persistent_cache is None or cache_policy not in PERSISTENT_CACHE_POLICIES:
            self.stats.record_cache_bypass(
                cache="disk", method=key.method, path_family=key.path_family
            )
            self._debug(f"cache: disk bypass method={key.method} path={key.path}")
            return None
        if self.profile.cache_mode == CACHE_MODE_REFRESH:
            self.stats.record_cache_bypass(
                cache="disk", method=key.method, path_family=key.path_family
            )
            self._debug(f"cache: disk bypass refresh method={key.method} path={key.path}")
            return None
        try:
            status, payload = self.persistent_cache.get(key)
        except (OSError, sqlite3.Error, ValueError, json.JSONDecodeError) as exc:
            self.stats.record_cache_bypass(
                cache="disk", method=key.method, path_family=key.path_family
            )
            self._debug(
                f"cache: disk bypass method={key.method} path={key.path} reason={type(exc).__name__}"
            )
            return None
        if status == "hit":
            self.stats.record_cache_hit(
                cache="disk", method=key.method, path_family=key.path_family
            )
        elif status == "miss":
            self.stats.record_cache_miss(
                cache="disk", method=key.method, path_family=key.path_family
            )
        elif status == "expired":
            self.stats.record_cache_miss(
                cache="disk_expired", method=key.method, path_family=key.path_family
            )
        self._debug(f"cache: disk {status} method={key.method} path={key.path}")
        return payload

    def _write_to_disk(self, key: RequestCacheKey, payload: Any, *, cache_policy: str) -> None:
        if not self._persistent_allowed(cache_policy):
            return
        payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        payload_bytes = len(payload_json.encode("utf-8"))
        rows_count = _payload_rows_count(payload)
        ttl_seconds = self._ttl_seconds_for_payload(
            key,
            payload_bytes=payload_bytes,
            rows_count=rows_count,
            cache_policy=cache_policy,
        )
        try:
            self.persistent_cache.set(
                key,
                payload,
                ttl_seconds=ttl_seconds,
                cache_policy=cache_policy,
                payload_bytes=payload_bytes,
                rows_count=rows_count,
            )
            self._debug(
                "cache: disk write "
                f"method={key.method} path={key.path} ttl_seconds={ttl_seconds} "
                f"rows={rows_count} bytes={payload_bytes} family={key.path_family}"
            )
            self._extend_dense_family(key, ttl_seconds=ttl_seconds)
        except (OSError, TypeError, sqlite3.Error, ValueError) as exc:
            self._debug(
                f"cache: disk bypass method={key.method} path={key.path} reason={type(exc).__name__}"
            )

    def _ttl_seconds_for_payload(
        self,
        key: RequestCacheKey,
        *,
        payload_bytes: int,
        rows_count: int,
        cache_policy: str,
    ) -> int:
        if self.profile.cache_mode != CACHE_MODE_AUTO:
            return self.profile.cache_ttl_seconds
        if _looks_historical(key.params_json):
            return AUTO_HISTORICAL_TTL_SECONDS
        if cache_policy == CACHE_POLICY_PERSISTENT_HEAVY:
            return AUTO_HEAVY_TTL_SECONDS
        if rows_count >= AUTO_HEAVY_ROW_THRESHOLD or payload_bytes >= AUTO_HEAVY_PAYLOAD_BYTES:
            return AUTO_HEAVY_TTL_SECONDS
        if rows_count >= AUTO_MEDIUM_ROW_THRESHOLD or payload_bytes >= AUTO_MEDIUM_PAYLOAD_BYTES:
            return AUTO_MEDIUM_TTL_SECONDS
        recent_family_count = self._recent_family_count(key) + 1
        if recent_family_count >= AUTO_DENSE_FAMILY_HEAVY_THRESHOLD:
            return AUTO_HEAVY_TTL_SECONDS
        if recent_family_count >= AUTO_DENSE_FAMILY_MEDIUM_THRESHOLD:
            return AUTO_MEDIUM_TTL_SECONDS
        return AUTO_ENTITY_TTL_SECONDS

    def _recent_family_count(self, key: RequestCacheKey) -> int:
        if self.persistent_cache is None:
            return 0
        since = time.time() - AUTO_DENSE_FAMILY_WINDOW_SECONDS
        try:
            return self.persistent_cache.count_recent_family(
                scope=key.scope,
                method=key.method,
                path_family=key.path_family,
                since=since,
            )
        except (OSError, sqlite3.Error):
            return 0

    def _extend_dense_family(self, key: RequestCacheKey, *, ttl_seconds: int) -> None:
        if (
            self.persistent_cache is None
            or self.profile.cache_mode != CACHE_MODE_AUTO
            or ttl_seconds < AUTO_MEDIUM_TTL_SECONDS
        ):
            return
        since = time.time() - AUTO_DENSE_FAMILY_WINDOW_SECONDS
        try:
            updated = self.persistent_cache.extend_recent_family(
                scope=key.scope,
                method=key.method,
                path_family=key.path_family,
                since=since,
                ttl_seconds=ttl_seconds,
            )
        except (OSError, sqlite3.Error) as exc:
            self._debug(
                f"cache: dense family extend bypass family={key.path_family} reason={type(exc).__name__}"
            )
            return
        if updated:
            self._debug(
                "cache: dense family extended "
                f"method={key.method} family={key.path_family} ttl_seconds={ttl_seconds} rows={updated}"
            )

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
                self.stats.record_cache_hit(
                    cache="request", method=key.method, path_family=key.path_family
                )
                self._debug(f"cache: request hit method={key.method} path={key.path}")
                return copy.deepcopy(self._request_cache[key])
            task = self._inflight.get(key)
            if task is None:
                self.stats.record_cache_miss(
                    cache="request", method=key.method, path_family=key.path_family
                )
                self._debug(f"cache: request miss method={key.method} path={key.path}")
                task = asyncio.create_task(
                    self._load_or_fetch(key, cache_policy=cache_policy, fetch=fetch)
                )
                self._inflight[key] = task
            else:
                self.stats.record_cache_hit(
                    cache="inflight_dedup", method=key.method, path_family=key.path_family
                )
                self._debug(f"cache: inflight dedup hit method={key.method} path={key.path}")

        try:
            return copy.deepcopy(await task)
        finally:
            if task.done():
                async with self._lock:
                    if self._inflight.get(key) is task:
                        self._inflight.pop(key, None)

    async def clear_cache_scope(self, *, reason: str) -> None:
        async with self._lock:
            self._request_cache.clear()
        if self.persistent_cache is not None:
            try:
                self.persistent_cache.clear_scope(self.scope)
                self._debug(f"cache: profile cleared scope={self.scope} reason={reason}")
            except (OSError, sqlite3.Error) as exc:
                self._debug(
                    f"cache: clear bypass scope={self.scope} reason={reason} error={type(exc).__name__}"
                )

    async def invalidate_after_mutation(self) -> None:
        await self.clear_cache_scope(reason="mutation")
