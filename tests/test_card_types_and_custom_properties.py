from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_card_types_and_custom_properties(runner):
    result = runner.invoke(cli, ["--help"])
    nested = runner.invoke(cli, ["custom-properties", "select-values", "--help"])

    assert result.exit_code == 0
    assert nested.exit_code == 0
    assert "card-types" in result.output
    assert "custom-properties" in result.output
    assert "list" in nested.output
    assert "create" in nested.output
    assert "delete" in nested.output


def test_resolve_card_type_and_custom_property_aliases():
    assert resolve_tool("kaiten_list_card_types").canonical_name == "card-types.list"
    assert resolve_tool("kaiten_create_custom_property").canonical_name == "custom-properties.create"
    assert resolve_tool("kaiten_delete_select_value").canonical_name == "custom-properties.select-values.delete"


def test_build_request_for_delete_card_type_includes_replacement_body():
    tool = resolve_tool("card-types.delete")
    payload = merge_inputs(tool, {"type_id": 10, "replace_type_id": 3, "has_to_replace_in_workflow": False})

    path, query, body = build_request(tool, payload)

    assert path == "/card-types/10"
    assert query is None
    assert body == {"replace_type_id": 3, "has_to_replace_in_workflow": False}


def test_build_request_for_create_custom_property_includes_optional_body():
    tool = resolve_tool("custom-properties.create")
    payload = merge_inputs(
        tool,
        {
            "name": "Status",
            "type": "select",
            "show_on_facade": True,
            "multi_select": True,
            "data": {"min": 0, "max": 100},
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/company/custom-properties"
    assert query is None
    assert body == {
        "name": "Status",
        "type": "select",
        "show_on_facade": True,
        "multi_select": True,
        "data": {"min": 0, "max": 100},
    }


def test_build_request_for_delete_select_value_uses_soft_delete_patch():
    tool = resolve_tool("custom-properties.select-values.delete")
    payload = merge_inputs(tool, {"property_id": 3, "value_id": 10})

    path, query, body = build_request(tool, payload)

    assert path == "/company/custom-properties/3/select-values/10"
    assert query is None
    assert body == {"deleted": True}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_card_types_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/card-types", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "name": "Bug"}])
    )

    tool = resolve_tool("card-types.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "name": "Bug"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_select_values_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/custom-properties/3/select-values",
        params={"limit": "50"},
    ).mock(return_value=Response(200, json=[{"id": 10, "value": "High"}]))

    tool = resolve_tool("custom-properties.select-values.list")
    payload = merge_inputs(tool, {"property_id": 3})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 10, "value": "High"}]


@respx.mock
def test_cli_select_values_alias_and_nested_canonical_match(runner):
    respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/custom-properties/3/select-values",
        params={"limit": "50"},
    ).mock(return_value=Response(200, json=[]))
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(
        cli,
        ["--json", "custom-properties", "select-values", "list", "--property-id", "3"],
        env=env,
    )
    alias = runner.invoke(cli, ["--json", "kaiten_list_select_values", "--property-id", "3"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
