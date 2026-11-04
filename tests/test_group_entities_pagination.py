from __future__ import annotations

import json

import httpx
import pytest
import respx

from kaiten_cli.app import cli
from kaiten_cli.discovery import describe_tool
from kaiten_cli.errors import ApiError, ConfigError, MutationBlockedError, ValidationError
from kaiten_cli.models import CACHE_POLICY_REQUEST_SCOPE
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs

ORIGIN = "https://sandbox.kaiten.ru/api/latest"
PATH = "/company/groups/group-1/entities"


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def test_single_page_request_preserves_omitted_pagination():
    tool = resolve_tool("group-entities.list")
    assert build_request(tool, merge_inputs(tool, {"group_uid": "group-1"})) == (PATH, None, None)
    payload = merge_inputs(
        tool,
        {"group_uid": "group-1", "limit": 2, "offset": 0, "fields": "uid", "compact": True},
    )
    assert build_request(tool, payload) == (PATH, {"limit": 2, "offset": 0}, None)
    assert describe_tool(tool.canonical_name)["bulk_alternative"] == "group-entities.list-all"


@pytest.mark.parametrize(
    "name,attributes",
    [
        ("list", {"limit": 0}),
        ("list", {"limit": 101}),
        ("list", {"offset": -1}),
        ("list-all", {"page_size": 0}),
        ("list-all", {"page_size": 101}),
        ("list-all", {"max_pages": 0}),
        ("list-all", {"max_pages": 1001}),
    ],
)
def test_invalid_bounds(name, attributes):
    tool = resolve_tool(f"group-entities.{name}")
    with pytest.raises(ValidationError):
        merge_inputs(tool, {"group_uid": "group-1", **attributes})


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("page_size", [1, 2, 100])
async def test_complete_result_is_independent_of_page_size(page_size):
    rows = [
        {"uid": f"entity-{i}", "title": f"Entity {i}", "description": "Heavy"} for i in range(101)
    ]

    def respond(request):
        assert set(request.url.params) == {"limit", "offset"}
        assert request.url.params["limit"] == str(page_size)
        offset = int(request.url.params["offset"])
        return httpx.Response(200, json=rows[offset : offset + page_size])

    route = respx.get(ORIGIN + PATH).mock(side_effect=respond)
    tool = resolve_tool("group-entities.list-all")
    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "group_uid": "group-1",
                "page_size": page_size,
                "max_pages": 102,
                "fields": "title",
                "compact": True,
            },
        ),
        read_only=True,
    )
    assert result == [{"title": row["title"]} for row in rows]
    assert [int(call.request.url.params["offset"]) for call in route.calls] == list(
        range(0, 102 if page_size == 1 else 101, page_size)
    )
    assert tool.cache_policy == CACHE_POLICY_REQUEST_SCOPE


@pytest.mark.asyncio
@respx.mock
async def test_defaults_empty_and_single_page_shaping():
    route = respx.get(ORIGIN + PATH).mock(return_value=httpx.Response(200, json=[]))
    tool = resolve_tool("group-entities.list-all")
    assert (
        await execute_tool(tool, merge_inputs(tool, {"group_uid": "group-1"}), read_only=True) == []
    )
    assert route.call_count == 1
    assert dict(route.calls[0].request.url.params) == {"limit": "100", "offset": "0"}

    route.mock(return_value=httpx.Response(200, json=[{"uid": "a", "description": "Heavy"}]))
    tool = resolve_tool("group-entities.list")
    assert await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "group_uid": "group-1",
                "fields": "uid",
                "compact": True,
            },
        ),
        read_only=True,
    ) == [{"uid": "a"}]


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    "pages,page_size,match",
    [
        ([[{"uid": "a"}], [{"uid": "a"}]], 1, "repeated"),
        ([[{"uid": "a"}, {"uid": "a"}]], 2, "repeated"),
        ([[{"uid": "a"}], [{"uid": "b"}], [{"uid": "a"}]], 1, "repeated"),
        ([[{"uid": "a"}]], 1, "max_pages"),
        ([{"records": []}], 1, "invalid page"),
        ([None], 1, "invalid page"),
        ([[{"uid": "a"}, {"uid": "b"}]], 1, "invalid page"),
        ([[{"title": "missing uid"}]], 1, "invalid entity"),
        ([[{"uid": None}]], 1, "invalid entity"),
        ([[{"uid": ""}]], 1, "invalid entity"),
        ([[{"uid": 7}]], 1, "invalid entity"),
        ([["bad row"]], 1, "invalid entity"),
    ],
)
async def test_incomplete_results_fail_without_extra_requests(pages, page_size, match):
    route = respx.get(ORIGIN + PATH).mock(
        side_effect=[httpx.Response(200, json=page) for page in pages]
    )
    tool = resolve_tool("group-entities.list-all")
    with pytest.raises(ConfigError, match=match):
        await execute_tool(
            tool,
            merge_inputs(
                tool,
                {
                    "group_uid": "group-1",
                    "page_size": page_size,
                    "max_pages": len(pages),
                },
            ),
            read_only=True,
        )
    assert route.call_count == len(pages)


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status", [401, 403, 404, 405, 422])
async def test_api_errors_preserved_without_fallback(status):
    body = {"message": "Permission or version restriction"}
    route = respx.get(ORIGIN + PATH).mock(
        side_effect=[
            httpx.Response(200, json=[{"uid": "a"}]),
            httpx.Response(status, json=body),
        ]
    )
    tool = resolve_tool("group-entities.list-all")
    with pytest.raises(ApiError) as error:
        await execute_tool(
            tool,
            merge_inputs(
                tool,
                {
                    "group_uid": "group-1",
                    "page_size": 1,
                },
            ),
            read_only=True,
        )
    assert error.value.status_code == status
    assert error.value.body == body
    assert route.call_count == len(respx.calls) == 2


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("action", ["add", "update", "remove"])
async def test_group_writes_blocked_before_http(action):
    with pytest.raises(MutationBlockedError):
        await execute_tool(resolve_tool(f"group-entities.{action}"), {}, read_only=True)
    assert not respx.calls


@respx.mock
def test_cli_discovery_and_stats(runner):
    route = respx.get(ORIGIN + PATH).mock(
        side_effect=[
            httpx.Response(200, json=[{"uid": "a", "title": "A"}]),
            httpx.Response(200, json=[]),
        ]
    )
    result = runner.invoke(
        cli,
        [
            "--locale",
            "ru",
            "--json",
            "--read-only",
            "group-entities",
            "list-all",
            "--group-uid",
            "group-1",
            "--page-size",
            "1",
            "--max-pages",
            "2",
            "--fields",
            "title",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["data"] == [{"title": "A"}]
    assert payload["stats"]["http_request_count"] == route.call_count == 2
    assert describe_tool("group-entities.list-all")["execution_mode"] == "aggregated"
