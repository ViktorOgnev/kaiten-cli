"""Command trace helpers for CLI-level observability."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REDACTED_ARG_VALUE = "[REDACTED]"
_SENSITIVE_FLAGS = {"--token"}


@dataclass(slots=True)
class ExecutionStats:
    http_request_count: int = 0
    retry_count: int = 0
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
        if stats is not None:
            payload["http_request_count"] = stats.http_request_count
            payload["retry_count"] = stats.retry_count
            payload["cache_hits"] = stats.cache_hits()
            payload["cache_misses"] = stats.cache_misses()
            payload["cache_bypasses"] = stats.cache_bypasses()
        if bulk_meta:
            payload.update(bulk_meta)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
