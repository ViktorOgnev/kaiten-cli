"""Command trace helpers for CLI-level observability."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kaiten_cli.runtime.fs_security import open_private_append

REDACTED_ARG_VALUE = "[REDACTED]"
_SENSITIVE_FLAGS = {"--token"}
_NUMERIC_PATH_SEGMENT_RE = re.compile(r"/\d+(?=/|$)")
_UUID_PATH_SEGMENT_RE = re.compile(
    r"/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?=/|$)"
)


def path_family_for(path: str) -> str:
    family = _UUID_PATH_SEGMENT_RE.sub("/:id", path)
    return _NUMERIC_PATH_SEGMENT_RE.sub("/:id", family)


@dataclass(slots=True)
class ExecutionGroupStats:
    source: str
    method: str
    path_family: str
    http_request_count: int = 0
    http_response_count: int = 0
    http_error_count: int = 0
    api_wait_ms: float = 0.0
    http_wait_ms: float = 0.0
    request_cache_hits: int = 0
    request_cache_misses: int = 0
    inflight_dedup_hits: int = 0
    disk_cache_hits: int = 0
    disk_cache_misses: int = 0
    disk_cache_expired: int = 0
    disk_cache_bypasses: int = 0

    def cache_hits(self) -> dict[str, int]:
        return {
            "request": self.request_cache_hits,
            "inflight_dedup": self.inflight_dedup_hits,
            "disk": self.disk_cache_hits,
        }

    def cache_misses(self) -> dict[str, int]:
        return {
            "request": self.request_cache_misses,
            "disk": self.disk_cache_misses + self.disk_cache_expired,
        }

    def cache_bypasses(self) -> dict[str, int]:
        return {"disk": self.disk_cache_bypasses}

    def to_payload(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "method": self.method,
            "path_family": self.path_family,
            "http_request_count": self.http_request_count,
            "http_response_count": self.http_response_count,
            "http_error_count": self.http_error_count,
            "api_wait_ms": round(self.api_wait_ms, 2),
            "http_wait_ms": round(self.http_wait_ms, 2),
            "cache_hits": self.cache_hits(),
            "cache_misses": self.cache_misses(),
            "cache_bypasses": self.cache_bypasses(),
        }


@dataclass(slots=True)
class ExecutionStats:
    http_request_count: int = 0
    http_response_count: int = 0
    http_error_count: int = 0
    api_wait_ms: float = 0.0
    http_wait_ms: float = 0.0
    retry_count: int = 0
    request_cache_hits: int = 0
    request_cache_misses: int = 0
    inflight_dedup_hits: int = 0
    disk_cache_hits: int = 0
    disk_cache_misses: int = 0
    disk_cache_expired: int = 0
    disk_cache_bypasses: int = 0
    _groups: dict[tuple[str, str, str], ExecutionGroupStats] = field(
        default_factory=dict, init=False
    )

    def _group(self, *, source: str, method: str, path_family: str) -> ExecutionGroupStats:
        key = (source, method.upper(), path_family)
        group = self._groups.get(key)
        if group is None:
            group = ExecutionGroupStats(
                source=source, method=method.upper(), path_family=path_family
            )
            self._groups[key] = group
        return group

    def record_http_attempt(
        self,
        *,
        source: str,
        method: str,
        path: str,
        wait_ms: float,
        status_code: int | None = None,
        error: bool = False,
    ) -> None:
        path_family = path_family_for(path)
        self.http_request_count += 1
        self.http_wait_ms += wait_ms
        if source == "kaiten_api":
            self.api_wait_ms += wait_ms
        if status_code is not None:
            self.http_response_count += 1
        if error or (status_code is not None and status_code >= 400):
            self.http_error_count += 1
        group = self._group(source=source, method=method, path_family=path_family)
        group.http_request_count += 1
        group.http_wait_ms += wait_ms
        if source == "kaiten_api":
            group.api_wait_ms += wait_ms
        if status_code is not None:
            group.http_response_count += 1
        if error or (status_code is not None and status_code >= 400):
            group.http_error_count += 1

    def record_cache_hit(self, *, cache: str, method: str, path_family: str) -> None:
        group = self._group(source="kaiten_api", method=method, path_family=path_family)
        if cache == "request":
            self.request_cache_hits += 1
            group.request_cache_hits += 1
        elif cache == "inflight_dedup":
            self.inflight_dedup_hits += 1
            group.inflight_dedup_hits += 1
        elif cache == "disk":
            self.disk_cache_hits += 1
            group.disk_cache_hits += 1

    def record_cache_miss(self, *, cache: str, method: str, path_family: str) -> None:
        group = self._group(source="kaiten_api", method=method, path_family=path_family)
        if cache == "request":
            self.request_cache_misses += 1
            group.request_cache_misses += 1
        elif cache == "disk":
            self.disk_cache_misses += 1
            group.disk_cache_misses += 1
        elif cache == "disk_expired":
            self.disk_cache_expired += 1
            group.disk_cache_expired += 1

    def record_cache_bypass(self, *, cache: str, method: str, path_family: str) -> None:
        group = self._group(source="kaiten_api", method=method, path_family=path_family)
        if cache == "disk":
            self.disk_cache_bypasses += 1
            group.disk_cache_bypasses += 1

    def cache_hits(self) -> dict[str, int]:
        return {
            "request": self.request_cache_hits,
            "inflight_dedup": self.inflight_dedup_hits,
            "disk": self.disk_cache_hits,
        }

    def cache_misses(self) -> dict[str, int]:
        return {
            "request": self.request_cache_misses,
            "disk": self.disk_cache_misses + self.disk_cache_expired,
        }

    def cache_bypasses(self) -> dict[str, int]:
        return {"disk": self.disk_cache_bypasses}

    def groups_payload(self) -> list[dict[str, Any]]:
        return [
            group.to_payload()
            for group in sorted(
                self._groups.values(),
                key=lambda item: (item.source, item.method, item.path_family),
            )
        ]

    def to_payload(self, *, command_duration_ms: float | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "http_request_count": self.http_request_count,
            "http_response_count": self.http_response_count,
            "http_error_count": self.http_error_count,
            "retry_count": self.retry_count,
            "api_wait_ms": round(self.api_wait_ms, 2),
            "http_wait_ms": round(self.http_wait_ms, 2),
            "cache_hits": self.cache_hits(),
            "cache_misses": self.cache_misses(),
            "cache_bypasses": self.cache_bypasses(),
            "groups": self.groups_payload(),
        }
        if command_duration_ms is not None:
            payload["command_duration_ms"] = round(command_duration_ms, 2)
        return payload


def redact_argv(argv: list[str]) -> list[str]:
    redacted: list[str] = []
    skip_next = False
    for value in argv:
        if skip_next:
            redacted.append(REDACTED_ARG_VALUE)
            skip_next = False
            continue
        if value in _SENSITIVE_FLAGS:
            redacted.append(value)
            skip_next = True
            continue
        for flag in _SENSITIVE_FLAGS:
            prefix = f"{flag}="
            if value.startswith(prefix):
                redacted.append(f"{prefix}{REDACTED_ARG_VALUE}")
                break
        else:
            redacted.append(value)
    return redacted


def bulk_trace_meta(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    meta = data.get("meta")
    if not isinstance(meta, dict):
        return {}
    payload: dict[str, Any] = {}
    for key in ("requested_count", "unique_count", "workers", "succeeded", "failed"):
        if key in meta:
            payload[key] = meta[key]
    if "trace" in meta:
        payload["stage_trace"] = meta["trace"]
    return payload


class TraceRecorder:
    """Append compact JSONL command traces."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def write(
        self,
        *,
        canonical_name: str,
        execution_mode: str,
        argv: list[str],
        exit_code: int,
        duration_ms: float,
        stats: ExecutionStats | None = None,
        bulk_meta: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "canonical_name": canonical_name,
            "argv": redact_argv(argv),
            "execution_mode": execution_mode,
            "exit_code": exit_code,
            "duration_ms": round(duration_ms, 2),
            "http_request_count": 0,
            "retry_count": 0,
            "cache_hits": {"request": 0, "inflight_dedup": 0, "disk": 0},
            "cache_misses": {"request": 0, "disk": 0},
            "cache_bypasses": {"disk": 0},
        }
        stats_payload = (stats or ExecutionStats()).to_payload(command_duration_ms=duration_ms)
        payload["stats"] = stats_payload
        if stats is not None:
            payload["http_request_count"] = stats.http_request_count
            payload["retry_count"] = stats.retry_count
            payload["cache_hits"] = stats.cache_hits()
            payload["cache_misses"] = stats.cache_misses()
            payload["cache_bypasses"] = stats.cache_bypasses()
        if bulk_meta:
            payload.update(bulk_meta)
        with open_private_append(self.path, repair_parent=False) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
