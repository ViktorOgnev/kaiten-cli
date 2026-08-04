from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_roles_groups_and_subscribers(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "space-users" in result.output
    assert "company-groups" in result.output
    assert "group-users" in result.output
    assert "roles" in result.output
    assert "card-subscribers" in result.output
    assert "column-subscribers" in result.output


def test_resolve_roles_groups_and_subscribers_aliases():
    assert resolve_tool("kaiten_list_space_users").canonical_name == "space-users.list"
    assert resolve_tool("kaiten_list_company_users").canonical_name == "company-users.list"
    assert (
        resolve_tool("kaiten_list_all_company_users").canonical_name
        == "company-users.list-all"
    )
    assert resolve_tool("kaiten_create_company_group").canonical_name == "company-groups.create"
    assert resolve_tool("kaiten_get_role").canonical_name == "roles.get"
    assert resolve_tool("kaiten_add_column_subscriber").canonical_name == "column-subscribers.add"


def test_build_request_for_add_column_subscriber_sets_default_type():
    tool = resolve_tool("column-subscribers.add")
    payload = merge_inputs(tool, {"column_id": 10, "user_id": 7})

    path, query, body = build_request(tool, payload)

    assert path == "/columns/10/subscribers"
    assert query is None
    assert body == {"user_id": 7, "type": 1}


def test_build_request_for_add_space_user_accepts_uuid_role_id():
    tool = resolve_tool("space-users.add")
    payload = merge_inputs(
        tool, {"space_id": 10, "user_id": 7, "role_id": "7ec9167c-4ad4-4a08-a3b9-8768b0c5a431"}
    )

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/10/users"
    assert query is None
    assert body == {"user_id": 7, "role_id": "7ec9167c-4ad4-4a08-a3b9-8768b0c5a431"}


def test_build_request_for_company_users_list_defaults_members_section():
    tool = resolve_tool("company-users.list")
    payload = merge_inputs(
        tool,
        {
            "temporarily_inactive_status": "all_users",
            "sd_access_type": "has_access",
            "compact": True,
            "fields": "id,email,apps_permissions",
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/company/users"
    assert query == {
        "for_members_section": True,
        "limit": 100,
        "offset": 0,
        "sd_access_type": "has_access",
        "temporarily_inactive_status": "all_users",
    }
    assert body is None


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_company_groups_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/groups", params={"limit": "50"}
    ).mock(return_value=Response(200, json=[{"uid": "grp-1", "name": "Engineering"}]))

    tool = resolve_tool("company-groups.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"uid": "grp-1", "name": "Engineering"}]


@pytest.mark.asyncio
@respx.mock
async def test_company_users_list_all_paginates_to_short_page_and_shapes(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/company/users").mock(
        side_effect=[
            Response(
                200,
                json=[
                    {"id": 1, "full_name": "One", "avatar": "data:image/png;base64,a"},
                    {"id": 2, "full_name": "Two", "avatar": "data:image/png;base64,b"},
                ],
            ),
            Response(
                200,
                json=[{"id": 3, "full_name": "Three", "avatar": "data:image/png;base64,c"}],
            ),
        ]
    )
    tool = resolve_tool("company-users.list-all")
    payload = merge_inputs(
        tool,
        {
            "page_size": 2,
            "max_pages": 3,
            "compact": True,
            "fields": "id,full_name",
        },
    )

    result = await execute_tool(tool, payload)

    assert result == [
        {"id": 1, "full_name": "One"},
        {"id": 2, "full_name": "Two"},
        {"id": 3, "full_name": "Three"},
    ]
    assert route.call_count == 2
    assert dict(route.calls[0].request.url.params) == {
        "for_members_section": "true",
        "limit": "2",
        "offset": "0",
    }
    assert dict(route.calls[1].request.url.params)["offset"] == "2"


@pytest.mark.asyncio
@respx.mock
async def test_company_users_list_all_fails_instead_of_truncating_on_cap(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/company/users").mock(
        side_effect=[
            Response(200, json=[{"id": 1}, {"id": 2}]),
            Response(200, json=[{"id": 3}, {"id": 4}]),
        ]
    )
    tool = resolve_tool("company-users.list-all")
    payload = merge_inputs(tool, {"page_size": 2, "max_pages": 2})

    with pytest.raises(ValidationError, match="silently truncated"):
        await execute_tool(tool, payload)

    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_roles_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/tree-entity-roles", params={"limit": "50"}
    ).mock(return_value=Response(200, json=[{"id": "role-1", "name": "Admin"}]))

    tool = resolve_tool("roles.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "role-1", "name": "Admin"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_space_users_compact(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/users").mock(
        return_value=Response(
            200, json=[{"id": 7, "full_name": "Alice", "avatar": "data:image/png;base64,abc"}]
        )
    )

    tool = resolve_tool("space-users.list")
    payload = merge_inputs(tool, {"space_id": 10, "compact": True})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 7, "full_name": "Alice"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_card_subscribers_compact(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/10/subscribers").mock(
        return_value=Response(
            200, json=[{"id": 7, "full_name": "Alice", "avatar": "data:image/png;base64,abc"}]
        )
    )

    tool = resolve_tool("card-subscribers.list")
    payload = merge_inputs(tool, {"card_id": 10, "compact": True})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 7, "full_name": "Alice"}]


@respx.mock
def test_cli_company_groups_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/company/groups", params={"limit": "50"}).mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "company-groups", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_company_groups"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    canonical_payload = json.loads(canonical.output)
    alias_payload = json.loads(alias.output)
    canonical_payload.pop("stats", None)
    alias_payload.pop("stats", None)
    assert canonical_payload == alias_payload
