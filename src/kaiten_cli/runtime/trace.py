"""Command trace helpers for CLI-level observability."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.fs_security import open_private_append

REDACTED_ARG_VALUE = "[REDACTED]"
_SENSITIVE_FLAGS = {"--token"}
_NUMERIC_PATH_SEGMENT_RE = re.compile(r"/\d+(?=/|$)")
_UUID_PATH_SEGMENT_RE = re.compile(
    r"/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?=/|$)"
)
_SAFE_CANONICAL_NAME_RE = re.compile(r"^[a-z0-9_.-]+$")
_TRACE_SUMMARY_LIMIT = 20
_POPULATION_COMMANDS = frozenset(
    {
        "cards.list",
        "cards.list-all",
        "space-topology.get",
        "space-activity-all.get",
    }
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
    cache_mode: str = "not_applicable"
    cache_policy: str = "none"
    cache_ttl_seconds: int | None = None
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
            "cache": {
                "mode": self.cache_mode,
                "policy": self.cache_policy,
                "ttl_seconds": self.cache_ttl_seconds,
            },
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


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _counter_payload(counter: Counter[str], *, key: str) -> list[dict[str, Any]]:
    return [
        {key: value, "count": count}
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[
            :_TRACE_SUMMARY_LIMIT
        ]
    ]


def summarize_trace(path: str | Path) -> dict[str, Any]:
    """Stream a trace file into a bounded, payload-free workflow summary."""

    trace_path = Path(path)
    command_counts: Counter[str] = Counter()
    command_modes: dict[str, str] = {}
    path_counts: Counter[str] = Counter()
    working_set_signatures: Counter[tuple[str, str]] = Counter()
    cache_hits: Counter[str] = Counter()
    cache_misses: Counter[str] = Counter()
    cache_bypasses: Counter[str] = Counter()
    lines = 0
    entries = 0
    invalid_lines = 0
    failures = 0
    duration_ms = 0.0
    http_request_count = 0
    api_wait_ms = 0.0
    retry_count = 0
    refresh_count = 0

    try:
        handle = trace_path.open("r", encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValidationError(f"Unable to read trace file: {type(exc).__name__}.") from exc

    with handle:
        for line in handle:
            lines += 1
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue
            if not isinstance(entry, dict):
                invalid_lines += 1
                continue

            canonical_name = entry.get("canonical_name")
            if not isinstance(canonical_name, str) or not _SAFE_CANONICAL_NAME_RE.fullmatch(
                canonical_name
            ):
                canonical_name = "unknown"
            entries += 1
            command_counts[canonical_name] += 1
            command_modes[canonical_name] = str(entry.get("execution_mode") or "unknown")
            if _safe_int(entry.get("exit_code")) != 0:
                failures += 1
            duration_ms += _safe_float(entry.get("duration_ms"))

            stats = entry.get("stats")
            stats = stats if isinstance(stats, dict) else {}
            http_request_count += _safe_int(
                stats.get("http_request_count", entry.get("http_request_count"))
            )
            api_wait_ms += _safe_float(stats.get("api_wait_ms"))
            retry_count += _safe_int(stats.get("retry_count", entry.get("retry_count")))

            cache = stats.get("cache")
            cache = cache if isinstance(cache, dict) else entry.get("cache")
            if isinstance(cache, dict) and cache.get("mode") == "refresh":
                refresh_count += 1

            for source, target in (
                (stats.get("cache_hits", entry.get("cache_hits")), cache_hits),
                (stats.get("cache_misses", entry.get("cache_misses")), cache_misses),
                (stats.get("cache_bypasses", entry.get("cache_bypasses")), cache_bypasses),
            ):
                if isinstance(source, dict):
                    for cache_name, count in source.items():
                        if isinstance(cache_name, str):
                            target[cache_name] += _safe_int(count)

            groups = stats.get("groups")
            if isinstance(groups, list):
                for group in groups:
                    if not isinstance(group, dict):
                        continue
                    family = group.get("path_family")
                    if isinstance(family, str) and family.startswith("/"):
                        path_counts[family] += _safe_int(group.get("http_request_count"))

            argv = entry.get("argv")
            if canonical_name in _POPULATION_COMMANDS and isinstance(argv, list):
                signature = json.dumps(argv, ensure_ascii=False, separators=(",", ":"))
                working_set_signatures[(canonical_name, signature)] += 1

    n_plus_one_commands = sorted(
        command
        for command, count in command_counts.items()
        if count >= 5
        and command_modes.get(command) not in {"local", "meta"}
        and not command.startswith(("query.", "snapshot."))
    )
    n_plus_one_paths = sorted(family for family, count in path_counts.items() if count >= 10)
    repeated_populations = sorted(
        {command for (command, _), count in working_set_signatures.items() if count >= 2}
    )
    recommendations: list[dict[str, Any]] = []
    if n_plus_one_commands or n_plus_one_paths:
        recommendations.append(
            {
                "code": "prefer_batch",
                "commands": n_plus_one_commands,
                "path_families": n_plus_one_paths,
            }
        )
    if repeated_populations:
        recommendations.append(
            {
                "code": "prefer_snapshot",
                "commands": repeated_populations,
            }
        )
    if refresh_count > 1:
        recommendations.append(
            {
                "code": "prefer_auto",
                "refresh_commands": refresh_count,
            }
        )

    return {
        "lines": lines,
        "entries": entries,
        "invalid_lines": invalid_lines,
        "failures": failures,
        "duration_ms": round(duration_ms, 2),
        "http_request_count": http_request_count,
        "api_wait_ms": round(api_wait_ms, 2),
        "retry_count": retry_count,
        "cache_hits": dict(sorted(cache_hits.items())),
        "cache_misses": dict(sorted(cache_misses.items())),
        "cache_bypasses": dict(sorted(cache_bypasses.items())),
        "commands": _counter_payload(command_counts, key="canonical_name"),
        "path_families": _counter_payload(path_counts, key="path_family"),
        "truncated": (
            len(command_counts) > _TRACE_SUMMARY_LIMIT or len(path_counts) > _TRACE_SUMMARY_LIMIT
        ),
        "recommendations": recommendations,
    }


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
            "cache": {
                "mode": "not_applicable",
                "policy": "none",
                "ttl_seconds": None,
            },
        }
        stats_payload = (stats or ExecutionStats()).to_payload(command_duration_ms=duration_ms)
        payload["stats"] = stats_payload
        payload["cache"] = stats_payload["cache"]
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
