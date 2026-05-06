from __future__ import annotations

import asyncio
import sqlite3

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.models import ResolvedProfile
from kaiten_cli.runtime.cache import ExecutionContext, HTTP_CACHE_DB_SCHEMA_VERSION
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
async def test_auto_cache_mode_persists_cacheable_gets_by_default(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    first = await execute_tool(tool, payload)
    second = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert first == second == {"id": 123, "title": "Task"}


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
async def test_auto_heavy_batch_cache_reuses_overlapping_card_ids(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    route_1 = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-01-01T00:00:00Z", "column_id": 10}])
    )
    route_2 = respx.get("https://sandbox.kaiten.ru/api/latest/cards/2/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-01-02T00:00:00Z", "column_id": 20}])
    )
    route_3 = respx.get("https://sandbox.kaiten.ru/api/latest/cards/3/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-01-03T00:00:00Z", "column_id": 30}])
    )

    tool = resolve_tool("card-location-history.batch-get")
    await execute_tool(tool, merge_inputs(tool, {"card_ids": [1, 2]}))
    await execute_tool(tool, merge_inputs(tool, {"card_ids": [2, 3]}))

    assert route_1.call_count == 1
    assert route_2.call_count == 1
    assert route_3.call_count == 1
    with sqlite3.connect(cache_path) as conn:
        row = conn.execute(
            """
            SELECT cache_policy, ttl_seconds, rows_count
            FROM responses
            WHERE path = '/cards/2/location-history'
            """
        ).fetchone()
    assert row == ("persistent_heavy", 86400, 1)


@pytest.mark.asyncio
@respx.mock
async def test_auto_dense_entity_family_extends_recent_ttl(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    monkeypatch.setattr("kaiten_cli.runtime.cache.AUTO_DENSE_FAMILY_MEDIUM_THRESHOLD", 3)
    monkeypatch.setattr("kaiten_cli.runtime.cache.AUTO_DENSE_FAMILY_HEAVY_THRESHOLD", 6)
    routes = [
        respx.get(f"https://sandbox.kaiten.ru/api/latest/cards/{card_id}").mock(
            return_value=Response(200, json={"id": card_id, "title": f"Task {card_id}"})
        )
        for card_id in (1, 2, 3)
    ]

    tool = resolve_tool("cards.get")
    for card_id in (1, 2, 3):
        await execute_tool(tool, merge_inputs(tool, {"card_id": card_id}))

    assert [route.call_count for route in routes] == [1, 1, 1]
    with sqlite3.connect(cache_path) as conn:
        rows = conn.execute(
            """
            SELECT path_family, ttl_seconds
            FROM responses
            WHERE path LIKE '/cards/%'
            ORDER BY path
            """
        ).fetchall()
    assert rows == [
        ("/cards/:id", 21600),
        ("/cards/:id", 21600),
        ("/cards/:id", 21600),
    ]


@pytest.mark.asyncio
@respx.mock
async def test_cache_mode_off_bypasses_auto_persistent_cache(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    await execute_tool(tool, payload, cache_mode="off")
    await execute_tool(tool, payload, cache_mode="off")

    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_persistent_cache_resets_incompatible_store(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    with sqlite3.connect(cache_path) as conn:
        conn.execute("CREATE TABLE legacy_cache (id INTEGER PRIMARY KEY)")
        conn.execute("PRAGMA user_version = 99")
        conn.commit()

    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    first = await execute_tool(tool, payload, cache_mode="readwrite")
    second = await execute_tool(tool, payload, cache_mode="readwrite")

    with sqlite3.connect(cache_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]

    assert route.call_count == 1
    assert first == second == {"id": 123, "title": "Task"}
    assert version == HTTP_CACHE_DB_SCHEMA_VERSION


@pytest.mark.asyncio
@respx.mock
async def test_persistent_cache_resets_corrupt_store(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    cache_path.write_text("not-a-sqlite-db", encoding="utf-8")

    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    await execute_tool(tool, payload, cache_mode="readwrite")
    await execute_tool(tool, payload, cache_mode="readwrite")

    with sqlite3.connect(cache_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]

    assert route.call_count == 1
    assert version == HTTP_CACHE_DB_SCHEMA_VERSION


@pytest.mark.asyncio
@respx.mock
async def test_persistent_cache_reset_failure_falls_back_to_bypass(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    with sqlite3.connect(cache_path) as conn:
        conn.execute("CREATE TABLE legacy_cache (id INTEGER PRIMARY KEY)")
        conn.execute("PRAGMA user_version = 99")
        conn.commit()

    def fail_reset(self, reason: str):
        return None

    monkeypatch.setattr("kaiten_cli.runtime.cache.PersistentCache._reset_store", fail_reset)
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123})

    first = await execute_tool(tool, payload, cache_mode="readwrite")
    second = await execute_tool(tool, payload, cache_mode="readwrite")

    assert route.call_count == 2
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
def test_cli_verbose_reports_cache_reset(capsys, monkeypatch, tmp_path):
    cache_path = tmp_path / "cache.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.cache.persistent_cache_path", lambda: cache_path)
    with sqlite3.connect(cache_path) as conn:
        conn.execute("CREATE TABLE legacy_cache (id INTEGER PRIMARY KEY)")
        conn.execute("PRAGMA user_version = 99")
        conn.commit()

    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(200, json={"id": 123, "title": "Task"})
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    with pytest.MonkeyPatch.context() as patch_env:
        for key, value in env.items():
            patch_env.setenv(key, value)
        from kaiten_cli.app import main

        exit_code = main(["--json", "--verbose", "--cache-mode", "readwrite", "cards", "get", "--card-id", "123"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert route.call_count == 1
    assert "cache: local store dropped store=http-cache reason=incompatible-schema:99" in captured.err
    assert "cache: local store recreated store=http-cache" in captured.err


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
