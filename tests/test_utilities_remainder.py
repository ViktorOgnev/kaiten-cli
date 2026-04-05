from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.executor import build_request, execute_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_api_keys_and_removed_items(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "api-keys" in result.output
    assert "removed-cards" in result.output
    assert "removed-boards" in result.output


def test_resolve_utility_remainder_aliases():
    assert resolve_tool("kaiten_list_api_keys").canonical_name == "api-keys.list"
    assert resolve_tool("kaiten_delete_api_key").canonical_name == "api-keys.delete"
    assert resolve_tool("kaiten_list_removed_cards").canonical_name == "removed-cards.list"
    assert resolve_tool("kaiten_list_removed_boards").canonical_name == "removed-boards.list"


def test_build_request_for_create_api_key():
    tool = resolve_tool("api-keys.create")
    payload = merge_inputs(tool, {"name": "local-dev"})

    path, query, body = build_request(tool, payload)

    assert path == "/api-keys"
    assert query is None
    assert body == {"name": "local-dev"}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_removed_cards_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/removed/cards", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1}])
    )

    tool = resolve_tool("removed-cards.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1}]


@respx.mock
def test_cli_removed_boards_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/removed/boards", params={"limit": "50"}).mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "removed-boards", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_removed_boards"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
