from __future__ import annotations

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import ApiError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def _built(name: str, payload: dict):
    tool = resolve_tool(name)
    return tool, build_request(tool, merge_inputs(tool, payload))


def test_iteration_registry_aliases_and_beta_notes():
    aliases = {
        "kaiten_list_iterations": "iterations.list",
        "kaiten_create_iteration": "iterations.create",
        "kaiten_add_iteration_card": "iteration-cards.add",
        "kaiten_list_card_iterations_history": "card-iterations-history.list",
    }
    for alias, canonical in aliases.items():
        tool = resolve_tool(alias)
        assert tool.canonical_name == canonical
        assert any("beta" in note.lower() for note in tool.usage_notes)


def test_iterations_list_parameters_and_default_page_size():
    tool, request = _built(
        "iterations.list",
        {
            "space_uid": "s1",
            "status": "planned,active",
            "with_data": "cards",
            "offset": 10,
            "order": "desc",
        },
    )

    assert tool.operation.method == "GET"
    assert request == (
        "/spaces/s1/iterations",
        {
            "status": "planned,active",
            "with_data": "cards",
            "offset": 10,
            "order": "desc",
            "limit": 100,
        },
        None,
    )


@pytest.mark.parametrize(
    ("name", "payload", "method", "path", "query", "body"),
    [
        (
            "iterations.get",
            {"space_uid": "s1", "iteration_id": "i1"},
            "GET",
            "/spaces/s1/iterations/i1",
            None,
            None,
        ),
        (
            "iterations.create",
            {
                "space_uid": "s1",
                "title": "Iteration 1",
                "goal": "Ship",
                "start_date": "2026-08-03",
                "finish_date": "2026-08-17",
            },
            "POST",
            "/spaces/s1/iterations",
            None,
            {
                "title": "Iteration 1",
                "goal": "Ship",
                "start_date": "2026-08-03",
                "finish_date": "2026-08-17",
            },
        ),
        (
            "iterations.update",
            {
                "space_uid": "s1",
                "iteration_id": "i1",
                "status": "closed",
                "actual_finish_date": "2026-08-16",
                "new_iteration_id": "i2",
            },
            "PATCH",
            "/spaces/s1/iterations/i1",
            None,
            {
                "status": "closed",
                "actual_finish_date": "2026-08-16",
                "new_iteration_id": "i2",
            },
        ),
        (
            "iterations.delete",
            {"space_uid": "s1", "iteration_id": "i1", "new_iteration_id": "i2"},
            "DELETE",
            "/spaces/s1/iterations/i1",
            None,
            {"new_iteration_id": "i2"},
        ),
        (
            "iteration-cards.list",
            {"space_uid": "s1", "iteration_id": "i1", "status": "removed"},
            "GET",
            "/spaces/s1/iterations/i1/cards",
            {"status": "removed"},
            None,
        ),
        (
            "iteration-cards.add",
            {"space_uid": "s1", "iteration_id": "i1", "card_uid": "c1"},
            "POST",
            "/spaces/s1/iterations/i1/cards",
            None,
            {"card_uid": "c1"},
        ),
        (
            "iteration-cards.remove",
            {"space_uid": "s1", "iteration_id": "i1", "card_uid": "c1"},
            "DELETE",
            "/spaces/s1/iterations/i1/cards/c1",
            None,
            None,
        ),
        (
            "card-iterations-history.list",
            {"card_uid": "c1"},
            "GET",
            "/cards/c1/iterations-history",
            None,
            None,
        ),
    ],
)
def test_iteration_routes(name, payload, method, path, query, body):
    tool, request = _built(name, payload)
    assert tool.operation.method == method
    assert request == (path, query, body)


@pytest.mark.parametrize(
    ("name", "payload", "method", "path"),
    [
        (
            "iterations.get",
            {"space_uid": "s1", "iteration_id": "i1"},
            "GET",
            "/spaces/s1/iterations/i1",
        ),
        (
            "iterations.create",
            {"space_uid": "s1", "title": "Iteration"},
            "POST",
            "/spaces/s1/iterations",
        ),
        (
            "iterations.update",
            {"space_uid": "s1", "iteration_id": "i1", "status": "active"},
            "PATCH",
            "/spaces/s1/iterations/i1",
        ),
        (
            "iterations.delete",
            {"space_uid": "s1", "iteration_id": "i1", "new_iteration_id": "i2"},
            "DELETE",
            "/spaces/s1/iterations/i1",
        ),
        (
            "iteration-cards.list",
            {"space_uid": "s1", "iteration_id": "i1"},
            "GET",
            "/spaces/s1/iterations/i1/cards",
        ),
        (
            "iteration-cards.add",
            {"space_uid": "s1", "iteration_id": "i1", "card_uid": "c1"},
            "POST",
            "/spaces/s1/iterations/i1/cards",
        ),
        (
            "iteration-cards.remove",
            {"space_uid": "s1", "iteration_id": "i1", "card_uid": "c1"},
            "DELETE",
            "/spaces/s1/iterations/i1/cards/c1",
        ),
        (
            "card-iterations-history.list",
            {"card_uid": "c1"},
            "GET",
            "/cards/c1/iterations-history",
        ),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_iteration_routes_execute_over_http(monkeypatch, name, payload, method, path):
    _env(monkeypatch)
    route = respx.route(method=method, url=f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"ok": True})
    )
    tool = resolve_tool(name)

    result = await execute_tool(tool, merge_inputs(tool, payload))

    assert route.called
    assert result == {"ok": True}


@pytest.mark.asyncio
@respx.mock
async def test_iterations_list_applies_fields_and_compact(monkeypatch):
    _env(monkeypatch)
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/spaces/s1/iterations",
        params={"limit": "2"},
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "i1",
                    "title": "Iteration 1",
                    "status": "active",
                    "avatar": "data:image/png;base64,abc",
                }
            ],
        )
    )
    tool = resolve_tool("iterations.list")
    payload = merge_inputs(
        tool,
        {"space_uid": "s1", "limit": 2, "compact": True, "fields": "id,status"},
    )

    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "i1", "status": "active"}]


@pytest.mark.asyncio
@respx.mock
async def test_iterations_tariff_and_invalid_transition_errors_are_preserved(monkeypatch):
    _env(monkeypatch)
    list_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/spaces/s1/iterations",
        params={"limit": "100"},
    ).mock(
        return_value=Response(
            402,
            json={"message": 'Your tariff does not include "Iterations" feature'},
        )
    )
    update_route = respx.patch("https://sandbox.kaiten.ru/api/latest/spaces/s1/iterations/i1").mock(
        return_value=Response(
            400,
            json={
                "code": "invalid_status_transition",
                "message": "Invalid status transition: planned -> closed",
            },
        )
    )

    list_tool = resolve_tool("iterations.list")
    with pytest.raises(ApiError) as tariff_error:
        await execute_tool(list_tool, merge_inputs(list_tool, {"space_uid": "s1"}))

    update_tool = resolve_tool("iterations.update")
    with pytest.raises(ApiError) as transition_error:
        await execute_tool(
            update_tool,
            merge_inputs(
                update_tool,
                {"space_uid": "s1", "iteration_id": "i1", "status": "closed"},
            ),
        )

    assert tariff_error.value.status_code == 402
    assert transition_error.value.status_code == 400
    assert transition_error.value.body["code"] == "invalid_status_transition"
    assert list_route.called
    assert update_route.called
