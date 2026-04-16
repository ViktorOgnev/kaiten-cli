from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli, main
from kaiten_cli.errors import BatchExecutionError, ConfigError, ValidationError
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
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


def test_merge_inputs_rejects_cards_list_all_selection_with_archived():
    tool = resolve_tool("cards.list-all")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"board_id": 10, "selection": "active_only", "archived": True})


def test_build_request_applies_runtime_request_shaper():
    tool = resolve_tool("boards.delete")
    payload = merge_inputs(tool, {"space_id": 3, "board_id": 7, "force": True})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/3/boards/7"
    assert query == {"force": True}
    assert body == {"force": True}


@pytest.mark.asyncio
async def test_execute_mutation_rejects_non_sandbox(config_env, monkeypatch):
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


@respx.mock
def test_cli_verbose_writes_diagnostics_to_stderr_only(capsys):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards", params={"board_id": "10", "limit": "5"}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Task", "state": 2}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    with pytest.MonkeyPatch.context() as monkeypatch:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        exit_code = main(["--json", "--verbose", "cards", "list", "--board-id", "10", "--limit", "5"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert route.called
    assert json.loads(captured.out)["success"] is True
    assert "[verbose] profile:" in captured.err
    assert "[verbose] request: method=GET path=/cards" in captured.err


@pytest.mark.asyncio
@respx.mock
async def test_execute_history_batch_all_failed_raises_structured_error(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(404, json={"message": "not found"})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/2/location-history").mock(
        return_value=Response(404, json={"message": "not found"})
    )

    tool = resolve_tool("card-location-history.batch-get")
    payload = merge_inputs(tool, {"card_ids": "[1,2]"})

    with pytest.raises(BatchExecutionError) as exc_info:
        await execute_tool(tool, payload)

    error = exc_info.value
    assert error.data["meta"] == {
        "requested": 2,
        "requested_count": 2,
        "unique_count": 2,
        "succeeded": 0,
        "failed": 2,
        "workers": 2,
    }
    assert [item["card_id"] for item in error.data["errors"]] == [1, 2]
