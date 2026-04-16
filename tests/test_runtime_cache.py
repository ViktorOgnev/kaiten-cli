from __future__ import annotations

import asyncio

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.models import ResolvedProfile
from kaiten_cli.runtime.cache import ExecutionContext
from kaiten_cli.runtime.client import KaitenClient
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


@pytest.mark.asyncio
@respx.mock
async def test_request_scope_cache_reuses_identical_gets_within_one_execution():
    profile = ResolvedProfile(name=None, domain="sandbox", token="test-token", sandbox=True)
    context = ExecutionContext.for_profile(profile)
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(200, json={"id": 1, "title": "Task"})
    )
    client = KaitenClient(
        domain="sandbox",
        token="test-token",
        execution_context=context,
        cache_policy="request_scope",
    )

    try:
        first = await client.get("/cards/1")
        second = await client.get("/cards/1")
    finally:
        await client.close()

    assert route.call_count == 1
    assert first == second == {"id": 1, "title": "Task"}


@pytest.mark.asyncio
@respx.mock
async def test_inflight_dedup_shares_one_get_across_clients():
    profile = ResolvedProfile(name=None, domain="sandbox", token="test-token", sandbox=True)
    context = ExecutionContext.for_profile(profile)

    async def delayed_response(request):
        await asyncio.sleep(0.01)
        return Response(200, json={"id": 1, "title": "Task"})

    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(side_effect=delayed_response)
    client1 = KaitenClient(
        domain="sandbox",
        token="test-token",
        execution_context=context,
        cache_policy="request_scope",
    )
    client2 = KaitenClient(
        domain="sandbox",
        token="test-token",
        execution_context=context,
        cache_policy="request_scope",
    )

    try:
        first, second = await asyncio.gather(client1.get("/cards/1"), client2.get("/cards/1"))
    finally:
        await client1.close()
        await client2.close()

    assert route.call_count == 1
    assert first == second == {"id": 1, "title": "Task"}


@pytest.mark.asyncio
@respx.mock
async def test_persistent_cache_hits_across_separate_execute_calls(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: tmp_path / "cache.sqlite3")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    first = await execute_tool(tool, payload, cache_mode="readwrite")
    second = await execute_tool(tool, payload, cache_mode="readwrite")

    assert route.call_count == 1
    assert first == second == {"id": 123, "title": "Task"}


@pytest.mark.asyncio
@respx.mock
async def test_cache_mode_refresh_bypasses_disk_read_and_rewrites(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: tmp_path / "cache.sqlite3")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    await execute_tool(tool, payload, cache_mode="readwrite")
    await execute_tool(tool, payload, cache_mode="readwrite")
    await execute_tool(tool, payload, cache_mode="refresh")
    await execute_tool(tool, payload, cache_mode="readwrite")

    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_successful_mutation_invalidates_persistent_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: tmp_path / "cache.sqlite3")
    get_route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )
    patch_route = respx.patch("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Renamed"})
    )

    get_tool = resolve_tool("cards.get")
    get_payload = merge_inputs(get_tool, {"card_id": 123})
    update_tool = resolve_tool("cards.update")
    update_payload = merge_inputs(update_tool, {"card_id": 123, "title": "Renamed"})

    await execute_tool(get_tool, get_payload, cache_mode="readwrite")
    await execute_tool(get_tool, get_payload, cache_mode="readwrite")
    await execute_tool(update_tool, update_payload, cache_mode="readwrite")
    await execute_tool(get_tool, get_payload, cache_mode="readwrite")

    assert patch_route.call_count == 1
    assert get_route.call_count == 2


@respx.mock
def test_cli_cache_mode_flag_enables_persistent_cache(runner, monkeypatch, tmp_path):
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: tmp_path / "cache.sqlite3")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    first = runner.invoke(
        cli,
        ["--json", "--cache-mode", "readwrite", "cards", "get", "--card-id", "123"],
        env=env,
    )
    second = runner.invoke(
        cli,
        ["--json", "--cache-mode", "readwrite", "cards", "get", "--card-id", "123"],
        env=env,
    )

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert route.call_count == 1
