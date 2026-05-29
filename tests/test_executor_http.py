from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli, main
from kaiten_cli.errors import BatchExecutionError, ValidationError
from kaiten_cli.models import OperationSpec, ToolSpec
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


def test_build_request_for_place_existing_board_defaults_position():
    tool = resolve_tool("boards.place-existing")
    payload = merge_inputs(tool, {"space_id": 3, "board_id": 7})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/3/boards/7"
    assert query is None
    assert body == {"top": 0, "left": 0}
    assert "move_from_space_id" not in body


def test_build_request_for_place_existing_board_keeps_explicit_position():
    tool = resolve_tool("boards.place-existing")
    payload = merge_inputs(
        tool,
        {"space_id": 3, "board_id": 7, "top": 16, "left": 560, "sort_order": 2.5},
    )

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/3/boards/7"
    assert query is None
    assert body == {"top": 16, "left": 560, "sort_order": 2.5}
    assert "move_from_space_id" not in body


@pytest.mark.asyncio
@respx.mock
async def test_execute_mutation_allows_normal_profiles(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "prod-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.post("https://prod-tenant.kaiten.ru/api/latest/cards").mock(
        return_value=Response(201, json={"id": 1, "title": "Task"})
    )
    tool = resolve_tool("cards.create")
    payload = merge_inputs(tool, {"title": "Task", "board_id": 1})

    result = await execute_tool(tool, payload)

    assert route.called
    assert result["id"] == 1


@pytest.mark.asyncio
@respx.mock
async def test_execute_direct_put_tool(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.put("https://sandbox.kaiten.ru/api/latest/things/7").mock(
        return_value=Response(200, json={"id": 7, "name": "renamed"})
    )
    tool = ToolSpec(
        canonical_name="things.put",
        mcp_alias="kaiten_put_thing",
        namespace="things",
        action="put",
        description="Synthetic PUT tool.",
        input_schema={
            "type": "object",
            "properties": {
                "thing_id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["thing_id", "name"],
        },
        operation=OperationSpec(
            method="PUT",
            path_template="/things/{thing_id}",
            path_fields=("thing_id",),
            body_fields=("name",),
        ),
    )

    payload = merge_inputs(tool, {"thing_id": 7, "name": "renamed"})
    result = await execute_tool(tool, payload)

    assert tool.is_mutation is True
    assert route.called
    assert route.calls[0].request.headers["content-type"] == "application/json"
    assert json.loads(route.calls[0].request.content) == {"name": "renamed"}
    assert result == {"id": 7, "name": "renamed"}


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
    canonical_payload = json.loads(canonical.output)
    alias_payload = json.loads(alias.output)
    canonical_payload.pop("stats", None)
    alias_payload.pop("stats", None)
    assert canonical_payload == alias_payload
    assert route.called


@respx.mock
def test_cli_boards_place_existing_alias_and_canonical_match(runner):
    route = respx.patch("https://sandbox.kaiten.ru/api/latest/spaces/3/boards/7").mock(
        return_value=Response(200, json={"id": 7, "top": 0, "left": 0, "primary_path": False})
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(
        cli,
        ["--json", "boards", "place-existing", "--space-id", "3", "--board-id", "7"],
        env=env,
    )
    alias = runner.invoke(
        cli,
        ["--json", "kaiten_place_existing_board", "--space-id", "3", "--board-id", "7"],
        env=env,
    )

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    canonical_payload = json.loads(canonical.output)
    alias_payload = json.loads(alias.output)
    canonical_payload.pop("stats", None)
    alias_payload.pop("stats", None)
    assert canonical_payload == alias_payload
    assert route.call_count == 2
    assert [json.loads(call.request.content) for call in route.calls] == [
        {"top": 0, "left": 0},
        {"top": 0, "left": 0},
    ]


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
    assert "[verbose] stats:" in captured.err


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
