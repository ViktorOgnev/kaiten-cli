from __future__ import annotations

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import describe, resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs


ALL_CUTOVER_LISTS = (
    ("spaces.list", {}, 50),
    ("automations.list", {"space_id": 1}, 50),
    ("space-users.list", {"space_id": 1}, 50),
    ("group-users.list", {"group_uid": "group-1"}, 50),
    ("card-allowed-users.list", {"card_id": 1}, 50),
    ("comments.list", {"card_id": 1}, 50),
    ("card-children.list", {"card_id": 1}, 50),
    ("card-parents.list", {"card_id": 1}, 50),
    ("time-logs.list", {"card_id": 1}, 50),
    ("custom-properties.list", {}, 50),
    ("custom-properties.select-values.list", {"property_id": 1}, 50),
    ("custom-properties.catalog-values.list", {"property_id": 1}, 50),
    ("documents.list", {}, 50),
    ("document-groups.list", {}, 50),
    ("company-users.list", {}, 100),
)

PAGINATED_AGGREGATES = (
    ("comments.batch-list", {"card_ids": [1]}),
    ("card-children.batch-list", {"card_ids": [1]}),
    ("time-logs.batch-list", {"card_ids": [1]}),
    ("cards.list-all", {}),
)


@pytest.mark.parametrize(("name", "required", "default_limit"), ALL_CUTOVER_LISTS)
def test_cutover_pagination_defaults_to_safe_single_page(name, required, default_limit):
    tool = resolve_tool(name)

    _, query, _ = build_request(tool, merge_inputs(tool, required))

    assert query is not None
    assert query["limit"] == default_limit
    assert query.get("offset", 0) == 0


@pytest.mark.parametrize(("name", "required", "default_limit"), ALL_CUTOVER_LISTS)
def test_cutover_pagination_forwards_explicit_limit_and_offset(
    name, required, default_limit
):
    tool = resolve_tool(name)

    _, query, _ = build_request(
        tool, merge_inputs(tool, {**required, "limit": 100, "offset": 200})
    )

    assert query is not None
    assert query["limit"] == 100
    assert query["offset"] == 200


@pytest.mark.parametrize(("name", "required", "default_limit"), ALL_CUTOVER_LISTS)
def test_cutover_list_schemas_expose_server_pagination_bounds(name, required, default_limit):
    arguments = {item["name"]: item for item in describe(name)["arguments"]}

    assert arguments["limit"]["minimum"] == 1
    assert arguments["limit"]["maximum"] == 100
    assert arguments["offset"]["minimum"] == 0


@pytest.mark.parametrize(("name", "required", "default_limit"), ALL_CUTOVER_LISTS)
@pytest.mark.parametrize("invalid", ({"limit": 0}, {"limit": 101}, {"offset": -1}))
def test_cutover_pagination_rejects_out_of_range_values(
    name, required, default_limit, invalid
):
    tool = resolve_tool(name)

    with pytest.raises(ValidationError):
        merge_inputs(tool, {**required, **invalid})


@pytest.mark.parametrize(("name", "required"), PAGINATED_AGGREGATES)
def test_paginated_aggregate_schemas_expose_safety_bounds(name, required):
    tool = resolve_tool(name)
    arguments = {item["name"]: item for item in describe(name)["arguments"]}

    assert arguments["page_size"]["minimum"] == 1
    assert arguments["page_size"]["maximum"] == 100
    assert arguments["max_pages"]["minimum"] == 1
    assert arguments["max_pages"]["maximum"] == 1000

    for invalid in ({"page_size": 0}, {"page_size": 101}, {"max_pages": 0}, {"max_pages": 1001}):
        with pytest.raises(ValidationError):
            merge_inputs(tool, {**required, **invalid})


def test_custom_properties_include_values_true_has_migration_error():
    tool = resolve_tool("custom-properties.list")

    with pytest.raises(ValidationError, match="select-values list"):
        merge_inputs(tool, {"include_values": True})


def test_custom_properties_include_values_false_is_accepted_but_never_sent():
    tool = resolve_tool("custom-properties.list")

    _, query, _ = build_request(tool, merge_inputs(tool, {"include_values": False}))

    assert query == {"limit": 50}


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("space_id", [None, 7])
async def test_boards_get_accepts_cutover_response_without_cards(monkeypatch, space_id):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    path = "/boards/10" if space_id is None else "/spaces/7/boards/10"
    route = respx.get(f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"id": 10, "columns": [], "lanes": []})
    )
    tool = resolve_tool("boards.get")
    payload = {"board_id": 10}
    if space_id is not None:
        payload["space_id"] = space_id

    result = await execute_tool(tool, merge_inputs(tool, payload))

    assert route.called
    assert result == {"id": 10, "columns": [], "lanes": []}
    assert any("cards.list-all" in note for note in tool.usage_notes)
