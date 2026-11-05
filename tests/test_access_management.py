from __future__ import annotations

import json

import httpx
import pytest
import respx

from kaiten_cli.app import cli
from kaiten_cli.discovery import describe_tool, search_tools
from kaiten_cli.errors import ApiError, ConfigError, MutationBlockedError, ValidationError
from kaiten_cli.models import CACHE_POLICY_REQUEST_SCOPE
from kaiten_cli.registry import resolve_tool
from kaiten_cli.registry.access_management import TOOLS
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs

UID = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
ORIGIN = "https://sandbox.kaiten.ru/api/latest"


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


@pytest.mark.parametrize(
    "namespace,target,value,path",
    [
        ("document-users", "document_uid", UID, f"/documents/{UID}/users"),
        ("document-group-users", "group_uid", UID, f"/document-groups/{UID}/users"),
        ("story-map-users", "map_id", 10, "/story-maps/10/users"),
    ],
)
def test_user_assignment_requests(namespace, target, value, path):
    for action, method, attributes, suffix, query, body in (
        (
            "list",
            "GET",
            {"include_inherited_access": False},
            "",
            {"include_inherited_access": False},
            None,
        ),
        (
            "add",
            "POST",
            {"user_id": 7, "role_id": UID, "send_email": False},
            "",
            None,
            {"user_id": 7, "role_id": UID, "send_email": False},
        ),
        ("update", "PATCH", {"user_id": 7, "role_id": OTHER}, "/7", None, {"role_id": OTHER}),
        ("remove", "DELETE", {"user_id": 7}, "/7", None, None),
    ):
        tool = resolve_tool(f"{namespace}.{action}")
        assert tool.operation.method == method
        assert build_request(tool, merge_inputs(tool, {target: value, **attributes})) == (
            path + suffix,
            query,
            body,
        )


@pytest.mark.parametrize("namespace", ["document-users", "document-group-users", "story-map-users"])
def test_add_requires_target_user(namespace):
    target = (
        {"map_id": 10}
        if namespace == "story-map-users"
        else {"group_uid" if namespace == "document-group-users" else "document_uid": UID}
    )
    with pytest.raises(ValidationError, match="user_id or email"):
        merge_inputs(resolve_tool(f"{namespace}.add"), target)


@pytest.mark.parametrize(
    "namespace,base",
    [
        ("space-access-groups", "spaces"),
        ("document-access-groups", "documents"),
        ("document-group-access-groups", "document-groups"),
        ("story-map-access-groups", "story-maps"),
    ],
)
def test_group_reads_use_uuid_and_keep_inheritance(namespace, base):
    tool = resolve_tool(f"{namespace}.list")
    assert build_request(
        tool, merge_inputs(tool, {"entity_uid": UID, "include_inherited_access": True})
    ) == (
        f"/{base}/{UID}/groups",
        {"include_inherited_access": True},
        None,
    )


def test_access_roles_are_not_timesheet_roles():
    assert resolve_tool("roles.list").operation.path_template == "/tree-entity-roles"
    assert resolve_tool("user-roles.list").operation.path_template == "/user-roles"
    tool = resolve_tool("roles.update")
    assert build_request(
        tool,
        merge_inputs(
            tool,
            {
                "role_id": UID,
                "permissions": {"document": {"read": False}},
                "new_permissions_default_value": False,
            },
        ),
    ) == (
        f"/tree-entity-roles/{UID}",
        None,
        {"permissions": {"document": {"read": False}}, "new_permissions_default_value": False},
    )
    delete = resolve_tool("roles.delete")
    assert build_request(
        delete, merge_inputs(delete, {"role_id": UID, "replacing_role_id": OTHER})
    )[2] == {"replacing_role_id": OTHER}
    assert build_request(delete, merge_inputs(delete, {"role_id": UID}))[2] is None


def test_story_maps_null_parent_and_partial_update():
    tool = resolve_tool("story-maps.update")
    assert build_request(tool, merge_inputs(tool, {"map_id": 10, "parent_entity_uid": "null"})) == (
        "/story-maps/10",
        None,
        {"parent_entity_uid": None},
    )
    assert build_request(tool, merge_inputs(tool, {"map_id": 10, "access": "by_invite"}))[2] == {
        "access": "by_invite"
    }
    assert build_request(resolve_tool("story-maps.delete"), {"map_id": 10}) == (
        "/story-maps/10",
        None,
        None,
    )


@pytest.mark.parametrize(
    "name,method,payload,path,body",
    [
        (
            "roles.create",
            "POST",
            {"name": "Custom", "permissions": {"document": {"read": False}}},
            "/tree-entity-roles",
            {"name": "Custom", "permissions": {"document": {"read": False}}},
        ),
        ("story-maps.list", "GET", {"limit": 100, "offset": 100}, "/story-maps", None),
        ("story-maps.get", "GET", {"map_id": 10}, "/story-maps/10", None),
        (
            "story-maps.create",
            "POST",
            {"title": "Roadmap", "access": "by_invite"},
            "/story-maps",
            {"title": "Roadmap", "access": "by_invite"},
        ),
        (
            "story-maps.update",
            "PATCH",
            {"map_id": 10, "title": "Updated"},
            "/story-maps/10",
            {"title": "Updated"},
        ),
        ("story-maps.delete", "DELETE", {"map_id": 10}, "/story-maps/10", None),
    ],
)
def test_role_and_story_map_request_contracts(name, method, payload, path, body, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1730000000)
    if name == "story-maps.create":
        body = {**body, "sort_order": 1730000000}
    tool = resolve_tool(name)
    assert tool.operation.method == method
    actual_path, query, actual_body = build_request(tool, merge_inputs(tool, payload))
    assert actual_path == path
    assert actual_body == body
    assert query == ({"limit": 100, "offset": 100} if name == "story-maps.list" else None)


def test_story_map_create_preserves_explicit_position():
    tool = resolve_tool("story-maps.create")
    assert build_request(tool, merge_inputs(tool, {"title": "Positioned", "sort_order": 1.5}))[
        2
    ] == {"title": "Positioned", "sort_order": 1.5}


@pytest.mark.asyncio
@respx.mock
async def test_assignment_read_preserves_server_effective_and_direct_roles():
    rows = [
        {
            "user_id": 7,
            "own_role_ids": [],
            "role_ids": [UID],
            "groups_role_ids": [OTHER],
            "own_groups_role_ids": None,
            "role_permissions": {"document": {"read": True}},
        }
    ]
    route = respx.get(f"{ORIGIN}/documents/{UID}/users").mock(
        return_value=httpx.Response(200, json=rows)
    )
    tool = resolve_tool("document-users.list")
    assert (
        await execute_tool(
            tool,
            merge_inputs(tool, {"document_uid": UID, "include_inherited_access": True}),
            read_only=True,
        )
        == rows
    )
    assert route.calls[0].request.url.params["include_inherited_access"] == "true"


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    "name", ["company-users.update", "company-groups.create", "company-groups.update"]
)
async def test_company_permission_writes_share_read_only_guard(name):
    with pytest.raises(MutationBlockedError):
        await execute_tool(resolve_tool(name), {}, read_only=True)
    assert not respx.calls


@pytest.mark.parametrize(
    "name,target",
    [
        ("company-users.update", {"user_id": 7}),
        ("company-groups.create", {"name": "Team"}),
        ("company-groups.update", {"group_uid": UID}),
    ],
)
def test_named_permissions_are_partial_and_exclusive(name, target):
    tool = resolve_tool(name)
    body = build_request(
        tool, merge_inputs(tool, {**target, "named_permissions": {"entitiesTree": False}})
    )[2]
    assert body["named_permissions"] == {"entitiesTree": False}
    assert "permissions" not in body
    assert (
        build_request(tool, merge_inputs(tool, {**target, "permissions": 0}))[2]["permissions"] == 0
    )
    with pytest.raises(ValidationError, match="not both"):
        build_request(
            tool,
            merge_inputs(
                tool, {**target, "permissions": 0, "named_permissions": {"members": True}}
            ),
        )
    with pytest.raises(ValidationError):
        build_request(tool, merge_inputs(tool, {**target, "named_permissions": {"members": 1}}))


def test_company_user_payload_cannot_hide_mixed_permission_formats():
    tool = resolve_tool("company-users.update")
    with pytest.raises(ValidationError, match="not both"):
        build_request(
            tool,
            merge_inputs(
                tool,
                {
                    "user_id": 7,
                    "permissions": 0,
                    "payload": {"named_permissions": {"members": False}},
                },
            ),
        )
    with pytest.raises(ValidationError, match="booleans"):
        build_request(
            tool,
            merge_inputs(
                tool, {"user_id": 7, "payload": {"named_permissions": {"members": "false"}}}
            ),
        )


@pytest.mark.asyncio
@respx.mock
async def test_admin_inventory_pages_and_shapes_without_disk_cache():
    route = respx.get(f"{ORIGIN}/admin-tree-entities").mock(
        side_effect=[
            httpx.Response(
                200, json=[{"uid": UID, "title": "Private"}, {"uid": OTHER, "title": "Other"}]
            ),
            httpx.Response(200, json=[]),
        ]
    )
    tool = resolve_tool("admin-tree-entities.list-all")
    result = await execute_tool(
        tool, merge_inputs(tool, {"page_size": 2, "max_pages": 2, "fields": "uid"}), read_only=True
    )
    assert result == [{"uid": UID}, {"uid": OTHER}]
    assert [call.request.url.params["offset"] for call in route.calls] == ["0", "2"]
    assert all(
        call.request.url.params["entity_types"] == "space,document,document_group,story_map"
        for call in route.calls
    )
    assert tool.cache_policy == CACHE_POLICY_REQUEST_SCOPE


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    "pages,match",
    [
        ([[{"uid": UID}], [{"uid": UID}]], "repeated"),
        ([[{"uid": UID}]], "max_pages"),
        ([{"records": []}], "invalid page"),
        ([[{"title": "no uid"}]], "invalid entity"),
        ([[{"uid": []}]], "invalid entity"),
        ([[{"uid": UID}, {"uid": OTHER}]], "invalid page"),
    ],
)
async def test_inventory_refuses_incomplete_results(pages, match):
    respx.get(f"{ORIGIN}/admin-tree-entities").mock(
        side_effect=[httpx.Response(200, json=p) for p in pages]
    )
    tool = resolve_tool("admin-tree-entities.list-all")
    with pytest.raises(ConfigError, match=match):
        await execute_tool(tool, merge_inputs(tool, {"page_size": 1, "max_pages": len(pages)}))


@pytest.mark.asyncio
@respx.mock
async def test_empty_inventory_is_success():
    route = respx.get(f"{ORIGIN}/admin-tree-entities").mock(
        return_value=httpx.Response(200, json=[])
    )
    tool = resolve_tool("admin-tree-entities.list-all")
    assert await execute_tool(tool, merge_inputs(tool, {})) == []
    assert route.call_count == 1


def test_admin_direct_filters_are_literal():
    tool = resolve_tool("admin-tree-entities.list")
    values = {
        "parent_uid": UID,
        "user_id": 7,
        "entity_types": "document",
        "relations": "ancestors",
        "limit": 100,
        "offset": 100,
    }
    assert build_request(tool, merge_inputs(tool, values)) == ("/admin-tree-entities", values, None)


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status", [401, 403, 404, 405])
async def test_denied_extension_does_not_fall_back(status):
    route = respx.post(f"{ORIGIN}/documents/{UID}/users").mock(
        return_value=httpx.Response(status, json={"message": "Denied"})
    )
    tool = resolve_tool("document-users.add")
    with pytest.raises(ApiError):
        await execute_tool(
            tool, merge_inputs(tool, {"document_uid": UID, "user_id": 7, "role_id": OTHER})
        )
    assert route.call_count == 1
    assert len(respx.calls) == 1


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    "tool", [tool for tool in TOOLS if tool.is_mutation], ids=lambda tool: tool.canonical_name
)
async def test_all_new_mutations_are_blocked_before_http(tool):
    # The guard runs before even resolving fields/credentials or building a request.
    with pytest.raises(MutationBlockedError):
        await execute_tool(tool, {}, read_only=True)
    assert not respx.calls


@respx.mock
@pytest.mark.parametrize("source", ["flags", "file", "stdin"])
def test_cli_input_modes_for_nested_permissions(runner, tmp_path, source):
    route = respx.patch(f"{ORIGIN}/tree-entity-roles/{UID}").mock(
        return_value=httpx.Response(200, json={"id": UID})
    )
    payload = {"role_id": UID, "permissions": {"document": {"read": False}}}
    args = ["--locale", "ru", "--json"]
    stdin = None
    if source == "flags":
        args += [
            "roles",
            "update",
            "--role-id",
            UID,
            "--permissions",
            json.dumps(payload["permissions"]),
        ]
    elif source == "file":
        path = tmp_path / "role.json"
        path.write_text(json.dumps(payload))
        args += ["--from-file", str(path), "roles", "update"]
    else:
        args += ["--stdin-json", "roles", "update"]
        stdin = json.dumps(payload)
    result = runner.invoke(cli, args, input=stdin)
    assert result.exit_code == 0, result.output
    assert json.loads(route.calls[0].request.content) == {"permissions": payload["permissions"]}


def test_discovery_is_explicit_about_contract_and_boundary(runner):
    for tool in TOOLS:
        info = describe_tool(tool.canonical_name)
        assert info["live_contract"]["status"] == (
            "live_passed_with_runtime_fix"
            if tool.canonical_name == "story-maps.create"
            else "live_passed"
        )
        assert "Undocumented" in " ".join(info["usage_notes"])
        assert resolve_tool(tool.mcp_alias) is tool
        if not tool.is_mutation:
            assert tool.cache_policy == CACHE_POLICY_REQUEST_SCOPE
    new_names = {tool.canonical_name for tool in TOOLS}
    assert any(item["canonical_name"] in new_names for item in search_tools("папки", limit=20))
    assert "admin-tree-entities.batch-update" not in {tool.canonical_name for tool in TOOLS}
    result = runner.invoke(cli, ["--locale", "ru", "--json", "agent-help"])
    assert result.exit_code == 0, result.output
    assert "access_management" in json.loads(result.output)["data"]["docs"]["skills"]
