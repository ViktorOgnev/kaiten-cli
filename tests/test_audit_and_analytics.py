from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.runtime.client import HEAVY_TIMEOUT
from kaiten_cli.runtime.executor import build_request, execute_tool, timeout_for_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_audit_activity_and_saved_filters(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "audit-logs" in result.output
    assert "card-activity" in result.output
    assert "space-activity" in result.output
    assert "company-activity" in result.output
    assert "card-location-history" in result.output
    assert "space-activity-all" in result.output
    assert "saved-filters" in result.output


def test_resolve_audit_aliases():
    assert resolve_tool("kaiten_list_audit_logs").canonical_name == "audit-logs.list"
    assert resolve_tool("kaiten_get_space_activity").canonical_name == "space-activity.get"
    assert resolve_tool("kaiten_get_all_space_activity").canonical_name == "space-activity-all.get"
    assert resolve_tool("kaiten_batch_get_card_location_history").canonical_name == "card-location-history.batch-get"
    assert resolve_tool("kaiten_create_saved_filter").canonical_name == "saved-filters.create"


def test_build_request_for_create_saved_filter_maps_name_to_title():
    tool = resolve_tool("saved-filters.create")
    payload = merge_inputs(tool, {"name": "Backlog", "filter": {"board_id": 1}, "shared": True})

    path, query, body = build_request(tool, payload)

    assert path == "/saved-filters"
    assert query is None
    assert body == {"title": "Backlog", "filter": {"board_id": 1}, "shared": True}


def test_build_request_for_space_activity():
    tool = resolve_tool("space-activity.get")
    payload = merge_inputs(tool, {"space_id": 1, "actions": "card_move", "limit": 10, "offset": 5, "compact": True})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/1/activity"
    assert query == {"actions": "card_move", "limit": 10, "offset": 5}
    assert body is None


def test_timeout_policy_for_bulk_space_activity():
    tool = resolve_tool("space-activity-all.get")
    assert timeout_for_tool(tool) == HEAVY_TIMEOUT


@pytest.mark.asyncio
@respx.mock
async def test_execute_audit_logs_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/audit-logs", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "action": "create"}])
    )

    tool = resolve_tool("audit-logs.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "action": "create"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_space_activity_all_paginates_and_compacts_by_default(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get(
        "https://sandbox.kaiten.ru/api/latest/spaces/1/activity",
        params={"limit": "2", "offset": "0"},
    ).mock(return_value=Response(200, json=[{"id": 1, "actor": {"id": 10}}, {"id": 2, "actor": {"id": 11}}]))
    second = respx.get(
        "https://sandbox.kaiten.ru/api/latest/spaces/1/activity",
        params={"limit": "2", "offset": "2"},
    ).mock(return_value=Response(200, json=[{"id": 3, "actor": {"id": 12}}]))

    tool = resolve_tool("space-activity-all.get")
    payload = merge_inputs(tool, {"space_id": 1, "page_size": 2, "max_pages": 5, "fields": "id"})
    result = await execute_tool(tool, payload)

    assert first.called
    assert second.called
    assert result == [{"id": 1}, {"id": 2}, {"id": 3}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_card_location_history_batch_get_returns_items_errors_and_meta(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-04-15T10:00:00Z", "column_id": 10, "subcolumn_id": 11}])
    )
    second = respx.get("https://sandbox.kaiten.ru/api/latest/cards/2/location-history").mock(
        return_value=Response(404, json={"message": "missing"})
    )
    third = respx.get("https://sandbox.kaiten.ru/api/latest/cards/3/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-04-15T11:00:00Z", "column_id": 20, "subcolumn_id": 21}])
    )

    tool = resolve_tool("card-location-history.batch-get")
    payload = merge_inputs(tool, {"card_ids": "[1,2,3]", "workers": 2, "fields": "changed,column_id"})
    result = await execute_tool(tool, payload)

    assert first.called
    assert second.called
    assert third.called
    assert result["meta"] == {
        "requested": 3,
        "requested_count": 3,
        "unique_count": 3,
        "succeeded": 2,
        "failed": 1,
        "workers": 2,
    }
    assert result["items"] == [
        {"card_id": 1, "history": [{"changed": "2026-04-15T10:00:00Z", "column_id": 10}]},
        {"card_id": 3, "history": [{"changed": "2026-04-15T11:00:00Z", "column_id": 20}]},
    ]
    assert result["errors"] == [
        {"card_id": 2, "error_type": "api_error", "message": "missing", "status_code": 404}
    ]


@pytest.mark.asyncio
@respx.mock
async def test_execute_card_location_history_batch_get_deduplicates_repeated_card_ids(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-04-15T10:00:00Z", "column_id": 10}])
    )

    tool = resolve_tool("card-location-history.batch-get")
    payload = merge_inputs(tool, {"card_ids": "[1,1,1]", "workers": 2, "fields": "changed,column_id"})
    result = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert result["meta"]["requested_count"] == 3
    assert result["meta"]["unique_count"] == 1
    assert result["items"] == [
        {"card_id": 1, "history": [{"changed": "2026-04-15T10:00:00Z", "column_id": 10}]}
    ]


@respx.mock
def test_cli_saved_filters_alias_and_canonical_match(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/saved-filters", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Backlog"}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "saved-filters", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_saved_filters"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called
