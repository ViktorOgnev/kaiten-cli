from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.executor import build_request, execute_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_service_desk_groups(runner):
    result = runner.invoke(cli, ["--help"])
    nested = runner.invoke(cli, ["service-desk", "services", "--help"])

    assert result.exit_code == 0
    assert nested.exit_code == 0
    assert "service-desk" in result.output
    assert "list" in nested.output
    assert "create" in nested.output
    assert "delete" in nested.output


def test_resolve_service_desk_aliases():
    assert resolve_tool("kaiten_list_sd_requests").canonical_name == "service-desk.requests.list"
    assert resolve_tool("kaiten_create_sd_service").canonical_name == "service-desk.services.create"
    assert resolve_tool("kaiten_update_sd_settings").canonical_name == "service-desk.settings.update"
    assert resolve_tool("kaiten_attach_card_sla").canonical_name == "card-slas.attach"


def test_build_request_for_delete_sd_service_uses_patch_archive():
    tool = resolve_tool("service-desk.services.delete")
    payload = merge_inputs(tool, {"service_id": 5})

    path, query, body = build_request(tool, payload)

    assert path == "/service-desk/services/5"
    assert query is None
    assert body == {"archived": True}


def test_build_request_for_sd_stats_maps_date_keys():
    tool = resolve_tool("service-desk.stats.get")
    payload = merge_inputs(tool, {"date_from": "2026-01-01", "date_to": "2026-01-31", "report": True})

    path, query, body = build_request(tool, payload)

    assert path == "/service-desk/stats"
    assert body is None
    assert query == {"date-from": "2026-01-01", "date-to": "2026-01-31", "report": True}


def test_service_create_schema_requires_lng():
    tool = resolve_tool("service-desk.services.create")

    assert set(tool.input_schema["required"]) == {"name", "board_id", "position", "lng"}


def test_build_request_for_batch_add_sd_org_users():
    tool = resolve_tool("service-desk.organization-users.batch-add")
    payload = merge_inputs(tool, {"organization_id": 10, "user_ids": [1, 2]})

    path, query, body = build_request(tool, payload)

    assert path == "/service-desk/organizations/10/users"
    assert query is None
    assert body == {"user_ids": [1, 2]}


def test_build_request_for_attach_card_sla():
    tool = resolve_tool("card-slas.attach")
    payload = merge_inputs(tool, {"card_id": 100, "sla_id": "sla-1"})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/100/slas"
    assert query is None
    assert body == {"sla_id": "sla-1"}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_sd_services_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/service-desk/services", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "name": "Support"}])
    )

    tool = resolve_tool("service-desk.services.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "name": "Support"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_sd_users_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/service-desk/users", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "full_name": "Alice"}])
    )

    tool = resolve_tool("service-desk.users.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "full_name": "Alice"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_sd_template_answers(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/service-desk/template-answers").mock(
        return_value=Response(200, json=[{"id": "ta-1", "name": "Hello"}])
    )

    tool = resolve_tool("service-desk.template-answers.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "ta-1", "name": "Hello"}]


@respx.mock
def test_cli_sd_services_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/service-desk/services", params={"limit": "50"}).mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "service-desk", "services", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_sd_services"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
