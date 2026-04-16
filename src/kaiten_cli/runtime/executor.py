"""Request planning and tool execution."""

from __future__ import annotations

import asyncio
from typing import Any

from kaiten_cli.errors import ConfigError
from kaiten_cli.models import DebugReporter, ResolvedProfile, ToolSpec
from kaiten_cli.profiles import resolve_profile
from kaiten_cli.runtime.cache import ExecutionContext
from kaiten_cli.runtime.client import DEFAULT_TIMEOUT, HEAVY_TIMEOUT, KaitenClient
from kaiten_cli.runtime.trace import ExecutionStats
from kaiten_cli.runtime.transforms import compact_response, select_fields, strip_base64


def build_request(tool: ToolSpec, payload: dict[str, Any]) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    path_values = {name: str(payload[name]) for name in tool.operation.path_fields}
    path = tool.operation.path_template.format(**path_values)
    query = {
        field: payload[field]
        for field in tool.operation.query_fields
        if field in payload and payload[field] is not None
    } or None
    body = {
        field: payload[field]
        for field in tool.operation.body_fields
        if field in payload
    } or None
    if "limit" in tool.operation.query_fields and tool.response_policy.default_limit is not None:
        query = dict(query or {})
        query.setdefault("limit", tool.response_policy.default_limit)
    if tool.runtime_behavior.request_shaper is not None:
        path, query, body = tool.runtime_behavior.request_shaper(tool, payload, path, query, body)
    return path, query, body


def timeout_for_tool(tool: ToolSpec) -> float:
    return HEAVY_TIMEOUT if tool.response_policy.heavy else DEFAULT_TIMEOUT


def enforce_mutation_safety(tool: ToolSpec, profile: ResolvedProfile) -> None:
    if not tool.is_mutation:
        return
    if profile.sandbox or profile.domain == "sandbox":
        return
    raise ConfigError(
        "Mutation commands are blocked unless the selected profile is marked sandbox or uses the sandbox domain."
    )


def _emit_debug(reporter: DebugReporter | None, message: str) -> None:
    if reporter is not None:
        reporter(message)


async def execute_tool(
    tool: ToolSpec,
    payload: dict[str, Any],
    *,
    profile_name: str | None = None,
    cache_mode: str | None = None,
    cache_ttl_seconds: int | None = None,
    reporter: DebugReporter | None = None,
) -> Any:
    result, _ = await execute_tool_with_diagnostics(
        tool,
        payload,
        profile_name=profile_name,
        cache_mode=cache_mode,
        cache_ttl_seconds=cache_ttl_seconds,
        reporter=reporter,
    )
    return result


async def execute_tool_with_diagnostics(
    tool: ToolSpec,
    payload: dict[str, Any],
    *,
    profile_name: str | None = None,
    cache_mode: str | None = None,
    cache_ttl_seconds: int | None = None,
    reporter: DebugReporter | None = None,
) -> tuple[Any, ExecutionStats]:
    profile = resolve_profile(
        profile_name,
        cache_mode_override=cache_mode,
        cache_ttl_seconds_override=cache_ttl_seconds,
    )
    enforce_mutation_safety(tool, profile)
    _emit_debug(
        reporter,
        "profile: "
        f"source={profile.source} name={profile.name or '-'} domain={profile.domain} "
        f"sandbox={profile.sandbox} cache_mode={profile.cache_mode} cache_ttl_seconds={profile.cache_ttl_seconds}",
    )
    context = ExecutionContext.for_profile(profile, reporter=reporter)
    client = KaitenClient(
        domain=profile.domain,
        token=profile.token,
        reporter=reporter,
        execution_context=context,
        cache_policy=tool.cache_policy,
    )
    path, query, body = build_request(tool, payload)
    timeout = timeout_for_tool(tool)
    _emit_debug(
        reporter,
        "request: "
        f"method={tool.operation.method.upper()} path={path} timeout={timeout:.1f}s "
        f"execution_mode={tool.execution_mode} cache_policy={tool.cache_policy}",
    )
    if tool.runtime_behavior.request_shaper is not None:
        _emit_debug(reporter, f"request-shaper: {tool.runtime_behavior.request_shaper.__name__}")
    result: Any
    try:
        method = tool.operation.method.upper()
        if tool.runtime_behavior.custom_executor is not None:
            _emit_debug(reporter, f"custom-executor: {tool.runtime_behavior.custom_executor.__name__}")
            result = await tool.runtime_behavior.custom_executor(
                client, tool, payload, path, query, body, timeout, reporter
            )
        elif method == "GET":
            result = await client.get(path, params=query, timeout=timeout)
        elif method == "POST":
            result = await client.post(path, json=body, timeout=timeout)
        elif method == "PATCH":
            result = await client.patch(path, json=body, timeout=timeout)
        elif method == "DELETE":
            result = await client.delete(path, json=body, timeout=timeout)
        else:  # pragma: no cover - impossible with current registry
            raise ConfigError(f"Unsupported method: {method}")
    except Exception as exc:
        setattr(exc, "_kaiten_trace_stats", context.stats)
        raise
    finally:
        await client.close()

    compact_enabled = bool(payload.get("compact", False))
    if tool.runtime_behavior.compact_default is not None and "compact" not in payload:
        compact_enabled = tool.runtime_behavior.compact_default
    if tool.response_policy.compact_supported:
        result = compact_response(result, compact_enabled)
    if tool.response_policy.fields_supported:
        result = select_fields(result, payload.get("fields"))
    result, _ = strip_base64(result)
    return result, context.stats


def execute_tool_sync(
    tool: ToolSpec,
    payload: dict[str, Any],
    *,
    profile_name: str | None = None,
    cache_mode: str | None = None,
    cache_ttl_seconds: int | None = None,
    reporter: DebugReporter | None = None,
) -> Any:
    result, _ = execute_tool_sync_with_diagnostics(
        tool,
        payload,
        profile_name=profile_name,
        cache_mode=cache_mode,
        cache_ttl_seconds=cache_ttl_seconds,
        reporter=reporter,
    )
    return result


def execute_tool_sync_with_diagnostics(
    tool: ToolSpec,
    payload: dict[str, Any],
    *,
    profile_name: str | None = None,
    cache_mode: str | None = None,
    cache_ttl_seconds: int | None = None,
    reporter: DebugReporter | None = None,
) -> tuple[Any, ExecutionStats]:
    return asyncio.run(
        execute_tool_with_diagnostics(
            tool,
            payload,
            profile_name=profile_name,
            cache_mode=cache_mode,
            cache_ttl_seconds=cache_ttl_seconds,
            reporter=reporter,
        )
    )
