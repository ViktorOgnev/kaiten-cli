from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ConfigError
from kaiten_cli.executor import build_request, execute_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import resolve_tool


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_cards_compact_and_fields(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards").mock(
        return_value=Response(
            200,
            json=[{"id": 1, "title": "Task", "description": "hidden", "owner": {"id": 7, "full_name": "Alice"}}],
        )
    )

    tool = resolve_tool("cards.list")
    payload = merge_inputs(tool, {"board_id": 10, "limit": 5, "compact": True, "fields": "id,title"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "title": "Task"}]


def test_build_request_for_update_card_keeps_nullable_fields():
    tool = resolve_tool("cards.update")
    payload = merge_inputs(tool, {"card_id": "PROJ-1", "description": "null", "title": "Renamed"})
    path, query, body = build_request(tool, payload)

    assert path == "/cards/PROJ-1"
    assert query is None
    assert body["description"] is None
    assert body["title"] == "Renamed"


def test_build_request_injects_default_limit_for_list_tools():
    tool = resolve_tool("cards.list")
    payload = merge_inputs(tool, {"board_id": 10})

    path, query, body = build_request(tool, payload)

    assert path == "/cards"
    assert body is None
    assert query is not None
    assert query["board_id"] == 10
    assert query["limit"] == 50


@pytest.mark.asyncio
async def test_execute_mutation_rejects_non_sandbox(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "prod-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("cards.create")
    payload = merge_inputs(tool, {"title": "Task", "board_id": 1})

    with pytest.raises(ConfigError):
        await execute_tool(tool, payload)


@respx.mock
def test_cli_cards_list_alias_and_canonical_use_numeric_options(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards").mock(
        return_value=Response(200, json=[{"id": 1, "title": "Task", "state": 2}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(
        cli,
        ["--json", "cards", "list", "--board-id", "10", "--limit", "5", "--compact", "--fields", "id,title,state"],
        env=env,
    )
    alias = runner.invoke(
        cli,
        ["--json", "kaiten_list_cards", "--board-id", "10", "--limit", "5", "--compact", "--fields", "id,title,state"],
        env=env,
    )

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert canonical.output == alias.output
    assert route.called
