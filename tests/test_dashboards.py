from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ApiError, ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def _request(name: str, payload: dict) -> tuple[str, dict | None, dict | None]:
    tool = resolve_tool(name)
    return build_request(tool, merge_inputs(tool, payload))


def test_dashboard_registry_aliases_and_contract_metadata():
    aliases = {
        "kaiten_list_dashboards": "dashboards.list",
        "kaiten_clone_dashboard": "dashboards.clone",
        "kaiten_add_dashboard_user": "dashboard-users.add",
        "kaiten_create_dashboard_widget": "dashboard-widgets.create",
        "kaiten_get_dashboard_compute_job": "dashboard-compute-jobs.get",
    }
    for alias, canonical in aliases.items():
        assert resolve_tool(alias).canonical_name == canonical

    compute_get = resolve_tool("dashboard-compute-jobs.get")
    assert compute_get.cache_policy == "none"
    assert any("experimental" in note.lower() for note in compute_get.usage_notes)


def test_dashboard_list_get_create_clone_and_update_requests():
    assert _request("dashboards.list", {"search": "bugs", "offset": 2}) == (
        "/dashboards",
        {"search": "bugs", "offset": 2, "limit": 50},
        None,
    )
    assert _request("dashboards.get", {"dashboard_id": "dashboard-1", "include": "widgets"}) == (
        "/dashboards/dashboard-1",
        {"include": "widgets"},
        None,
    )
    assert _request("dashboards.create", {"title": "Private"}) == (
        "/dashboards",
        None,
        {"title": "Private"},
    )
    assert _request("dashboards.create", {"title": "Public", "is_public": True}) == (
        "/dashboards",
        None,
        {"title": "Public", "is_public": True},
    )
    assert _request(
        "dashboards.clone",
        {"source_dashboard_id": "source-1", "title": "Copy", "is_public": False},
    ) == (
        "/dashboards",
        None,
        {"source_dashboard_id": "source-1", "title": "Copy", "is_public": False},
    )
    assert _request(
        "dashboards.update",
        {
            "dashboard_id": "dashboard-1",
            "layout": {"lg": {}},
            "filter": "null",
        },
    ) == (
        "/dashboards/dashboard-1",
        None,
        {"layout": {"lg": {}}, "filter": None},
    )


@pytest.mark.parametrize(
    ("name", "payload", "method", "path", "body"),
    [
        (
            "dashboard-users.add",
            {"dashboard_id": "d1", "user_uid": "u1", "role": "viewer"},
            "POST",
            "/dashboards/d1/users",
            {"user_uid": "u1", "role": "viewer"},
        ),
        (
            "dashboard-users.update",
            {"dashboard_id": "d1", "user_uid": "u1", "role": "editor"},
            "PATCH",
            "/dashboards/d1/users/u1",
            {"role": "editor"},
        ),
        (
            "dashboard-users.remove",
            {"dashboard_id": "d1", "user_uid": "u1"},
            "DELETE",
            "/dashboards/d1/users/u1",
            None,
        ),
        (
            "dashboard-widgets.create",
            {
                "dashboard_id": "d1",
                "title": "Cards",
                "source": "cardList",
                "visualization": "table",
                "config": {"filter": {}},
            },
            "POST",
            "/dashboards/d1/widgets",
            {
                "title": "Cards",
                "source": "cardList",
                "visualization": "table",
                "config": {"filter": {}},
            },
        ),
        (
            "dashboard-widgets.update",
            {"dashboard_id": "d1", "widget_id": "w1", "config": {"limit": 10}},
            "PATCH",
            "/dashboards/d1/widgets/w1",
            {"config": {"limit": 10}},
        ),
        (
            "dashboard-widgets.delete",
            {"dashboard_id": "d1", "widget_id": "w1"},
            "DELETE",
            "/dashboards/d1/widgets/w1",
            None,
        ),
    ],
)
def test_dashboard_collaboration_and_widget_requests(name, payload, method, path, body):
    tool = resolve_tool(name)
    built_path, query, built_body = build_request(tool, merge_inputs(tool, payload))
    assert tool.operation.method == method
    assert (built_path, query, built_body) == (path, None, body)


def test_dashboard_users_list_is_capped_at_50_by_default():
    assert _request("dashboard-users.list", {"dashboard_id": "d1"}) == (
        "/dashboards/d1/users",
        {"limit": 50},
        None,
    )


@pytest.mark.asyncio
@respx.mock
async def test_dashboard_widgets_list_extracts_and_shapes_widgets(monkeypatch):
    _env(monkeypatch)
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/dashboards/d1",
        params={"include": "widgets"},
    ).mock(
        return_value=Response(
            200,
            json={
                "id": "d1",
                "widgets": [
                    {
                        "id": "w1",
                        "title": "Cards",
                        "source": "cardList",
                        "config": {"secretly_heavy": "value"},
                    }
                ],
            },
        )
    )
    tool = resolve_tool("dashboard-widgets.list")
    payload = merge_inputs(tool, {"dashboard_id": "d1", "fields": "id,title"})

    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "w1", "title": "Cards"}]


@pytest.mark.asyncio
@respx.mock
async def test_dashboard_compute_create_202_and_uncached_status(monkeypatch):
    _env(monkeypatch)
    create_route = respx.post(
        "https://sandbox.kaiten.ru/api/latest/dashboards/d1/compute-jobs",
        json={"widget_ids": ["w1"], "force": True},
    ).mock(return_value=Response(202, json={"compute_job_id": 42}))
    get_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/dashboards/d1/compute-jobs/42"
    ).mock(
        side_effect=[
            Response(200, json={"id": 42, "status": "queued"}),
            Response(200, json={"id": 42, "status": "completed", "result": {"w1": 7}}),
        ]
    )

    create_tool = resolve_tool("dashboard-compute-jobs.create")
    create_result = await execute_tool(
        create_tool,
        merge_inputs(
            create_tool,
            {"dashboard_id": "d1", "widget_ids": ["w1"], "force": True},
        ),
    )
    get_tool = resolve_tool("dashboard-compute-jobs.get")
    get_payload = merge_inputs(get_tool, {"dashboard_id": "d1", "job_id": 42})
    first = await execute_tool(get_tool, get_payload)
    second = await execute_tool(get_tool, get_payload)

    assert create_route.called
    assert create_result == {"compute_job_id": 42}
    assert first["status"] == "queued"
    assert second["status"] == "completed"
    assert get_route.call_count == 2


def test_dashboard_compute_rejects_empty_or_oversized_widget_ids():
    tool = resolve_tool("dashboard-compute-jobs.create")
    with pytest.raises(ValidationError, match="non-empty"):
        merge_inputs(tool, {"dashboard_id": "d1", "widget_ids": []})
    with pytest.raises(ValidationError, match="at most 100"):
        merge_inputs(tool, {"dashboard_id": "d1", "widget_ids": [str(i) for i in range(101)]})


@pytest.mark.asyncio
@respx.mock
async def test_dashboard_server_permission_outcomes_are_preserved(monkeypatch):
    _env(monkeypatch)
    route = respx.patch("https://sandbox.kaiten.ru/api/latest/dashboards/d1").mock(
        side_effect=[
            Response(200, json={"id": "d1", "title": "Owner title"}),
            Response(200, json={"id": "d1", "layout": {"lg": {}}}),
            Response(403, json={"message": "Forbidden"}),
        ]
    )
    tool = resolve_tool("dashboards.update")

    owner = await execute_tool(
        tool, merge_inputs(tool, {"dashboard_id": "d1", "title": "Owner title"})
    )
    editor = await execute_tool(
        tool, merge_inputs(tool, {"dashboard_id": "d1", "layout": {"lg": {}}})
    )
    with pytest.raises(ApiError) as exc_info:
        await execute_tool(tool, merge_inputs(tool, {"dashboard_id": "d1", "layout": {"lg": [1]}}))

    assert owner["title"] == "Owner title"
    assert editor["layout"] == {"lg": {}}
    assert exc_info.value.status_code == 403
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_dashboard_http_crud_users_and_widgets(monkeypatch):
    _env(monkeypatch)
    routes = [
        respx.get(
            "https://sandbox.kaiten.ru/api/latest/dashboards",
            params={"search": "team", "limit": "50"},
        ).mock(return_value=Response(200, json=[{"id": "d1", "title": "Team"}])),
        respx.get(
            "https://sandbox.kaiten.ru/api/latest/dashboards/d1",
            params={"include": "widgets"},
        ).mock(return_value=Response(200, json={"id": "d1", "widgets": []})),
        respx.post("https://sandbox.kaiten.ru/api/latest/dashboards").mock(
            side_effect=[
                Response(200, json={"id": "private", "title": "Private", "is_public": False}),
                Response(200, json={"id": "public", "title": "Public", "is_public": True}),
                Response(200, json={"id": "copy", "title": "Copy", "is_public": False}),
            ]
        ),
        respx.delete("https://sandbox.kaiten.ru/api/latest/dashboards/d1").mock(
            return_value=Response(200, json={"id": "d1", "archived": True})
        ),
        respx.get(
            "https://sandbox.kaiten.ru/api/latest/dashboards/d1/users",
            params={"limit": "50"},
        ).mock(return_value=Response(200, json=[{"user_uid": "u1", "role": "viewer"}])),
        respx.post("https://sandbox.kaiten.ru/api/latest/dashboards/d1/users").mock(
            return_value=Response(200, json={"user_uid": "u1", "role": "viewer"})
        ),
        respx.patch("https://sandbox.kaiten.ru/api/latest/dashboards/d1/users/u1").mock(
            return_value=Response(200, json={"user_uid": "u1", "role": "editor"})
        ),
        respx.delete("https://sandbox.kaiten.ru/api/latest/dashboards/d1/users/u1").mock(
            return_value=Response(200, json={"user_uid": "u1", "removed": True})
        ),
        respx.post("https://sandbox.kaiten.ru/api/latest/dashboards/d1/widgets").mock(
            return_value=Response(200, json={"id": "w1", "source": "metric"})
        ),
        respx.patch("https://sandbox.kaiten.ru/api/latest/dashboards/d1/widgets/w1").mock(
            return_value=Response(200, json={"id": "w1", "title": "Renamed"})
        ),
        respx.delete("https://sandbox.kaiten.ru/api/latest/dashboards/d1/widgets/w1").mock(
            return_value=Response(200, json={"id": "w1", "archived": True})
        ),
    ]

    calls = [
        ("dashboards.list", {"search": "team"}),
        ("dashboards.get", {"dashboard_id": "d1", "include": "widgets"}),
        ("dashboards.create", {"title": "Private"}),
        ("dashboards.create", {"title": "Public", "is_public": True}),
        ("dashboards.clone", {"source_dashboard_id": "d1", "title": "Copy"}),
        ("dashboards.delete", {"dashboard_id": "d1"}),
        ("dashboard-users.list", {"dashboard_id": "d1"}),
        (
            "dashboard-users.add",
            {"dashboard_id": "d1", "user_uid": "u1", "role": "viewer"},
        ),
        (
            "dashboard-users.update",
            {"dashboard_id": "d1", "user_uid": "u1", "role": "editor"},
        ),
        ("dashboard-users.remove", {"dashboard_id": "d1", "user_uid": "u1"}),
        (
            "dashboard-widgets.create",
            {
                "dashboard_id": "d1",
                "title": "Metric",
                "source": "metric",
                "visualization": "number",
                "config": {},
            },
        ),
        (
            "dashboard-widgets.update",
            {"dashboard_id": "d1", "widget_id": "w1", "title": "Renamed"},
        ),
        ("dashboard-widgets.delete", {"dashboard_id": "d1", "widget_id": "w1"}),
    ]

    results = []
    for name, raw_payload in calls:
        tool = resolve_tool(name)
        results.append(await execute_tool(tool, merge_inputs(tool, raw_payload)))

    assert all(route.called for route in routes)
    assert results[0] == [{"id": "d1", "title": "Team"}]
    assert results[4]["id"] == "copy"
    assert results[-1]["archived"] is True


@pytest.mark.asyncio
@respx.mock
async def test_dashboard_owner_cannot_be_removed(monkeypatch):
    _env(monkeypatch)
    route = respx.delete("https://sandbox.kaiten.ru/api/latest/dashboards/d1/users/owner-1").mock(
        return_value=Response(400, json={"message": "Cannot remove dashboard owner"})
    )
    tool = resolve_tool("dashboard-users.remove")

    with pytest.raises(ApiError) as exc_info:
        await execute_tool(
            tool,
            merge_inputs(tool, {"dashboard_id": "d1", "user_uid": "owner-1"}),
        )

    assert route.called
    assert exc_info.value.status_code == 400
    assert "owner" in str(exc_info.value).lower()


@respx.mock
def test_dashboard_dotted_alias_executes_same_tool(runner):
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/dashboards", params={"limit": "1"}
    ).mock(return_value=Response(200, json=[{"id": "d1", "title": "One"}]))

    result = runner.invoke(
        cli,
        ["--json", "dashboards.list", "--limit", "1"],
        env={"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"},
    )

    assert result.exit_code == 0
    assert route.called
    assert json.loads(result.output)["data"] == [{"id": "d1", "title": "One"}]
