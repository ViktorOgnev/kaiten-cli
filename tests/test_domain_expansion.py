from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_new_namespaces(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "columns" in result.output
    assert "lanes" in result.output
    assert "checklists" in result.output
    assert "comments" in result.output
    assert "external-links" in result.output
    assert "tags" in result.output
    assert "card-tags" in result.output
    assert "card-members" in result.output
    assert "users" in result.output
    assert "blockers" in result.output
    assert "files" in result.output
    assert "card-children" in result.output
    assert "card-parents" in result.output
    assert "planned-relations" in result.output
    assert "projects" in result.output
    assert "time-logs" in result.output
    assert "company" in result.output
    assert "calendars" in result.output
    assert "user-timers" in result.output
    assert "space-topology" in result.output


def test_help_shows_nested_project_card_group(runner):
    top_level = runner.invoke(cli, ["projects", "--help"])
    nested = runner.invoke(cli, ["projects", "cards", "--help"])

    assert top_level.exit_code == 0
    assert nested.exit_code == 0
    assert "cards" in top_level.output
    assert "list" in nested.output
    assert "add" in nested.output
    assert "remove" in nested.output


def test_resolve_new_aliases():
    assert resolve_tool("kaiten_list_columns").canonical_name == "columns.list"
    assert resolve_tool("kaiten_create_lane").canonical_name == "lanes.create"
    assert resolve_tool("kaiten_create_checklist").canonical_name == "checklists.create"
    assert resolve_tool("kaiten_create_comment").canonical_name == "comments.create"
    assert resolve_tool("kaiten_create_external_link").canonical_name == "external-links.create"
    assert resolve_tool("kaiten_add_card_tag").canonical_name == "card-tags.add"
    assert resolve_tool("kaiten_add_card_member").canonical_name == "card-members.add"
    assert resolve_tool("kaiten_get_current_user").canonical_name == "users.current"
    assert resolve_tool("kaiten_get_card_blocker").canonical_name == "blockers.get"
    assert resolve_tool("kaiten_create_card_file").canonical_name == "files.create"
    assert resolve_tool("kaiten_add_card_child").canonical_name == "card-children.add"
    assert resolve_tool("kaiten_batch_list_card_children").canonical_name == "card-children.batch-list"
    assert resolve_tool("kaiten_add_card_parent").canonical_name == "card-parents.add"
    assert resolve_tool("kaiten_add_planned_relation").canonical_name == "planned-relations.add"
    assert resolve_tool("kaiten_update_planned_relation").canonical_name == "planned-relations.update"
    assert resolve_tool("kaiten_remove_planned_relation").canonical_name == "planned-relations.remove"
    assert resolve_tool("kaiten_batch_get_cards").canonical_name == "cards.batch-get"
    assert resolve_tool("kaiten_batch_list_comments").canonical_name == "comments.batch-list"
    assert resolve_tool("kaiten_create_project").canonical_name == "projects.create"
    assert resolve_tool("kaiten_create_time_log").canonical_name == "time-logs.create"
    assert resolve_tool("kaiten_batch_list_time_logs").canonical_name == "time-logs.batch-list"
    assert resolve_tool("kaiten_get_company").canonical_name == "company.current"
    assert resolve_tool("kaiten_list_calendars").canonical_name == "calendars.list"
    assert resolve_tool("kaiten_create_user_timer").canonical_name == "user-timers.create"
    assert resolve_tool("kaiten_get_space_topology").canonical_name == "space-topology.get"


def test_build_request_for_create_checklist_item():
    tool = resolve_tool("checklist-items.create")
    payload = merge_inputs(
        tool,
        {"card_id": 10, "checklist_id": 20, "text": "Review", "checked": True, "user_id": 7},
    )

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/checklists/20/items"
    assert query is None
    assert body == {"text": "Review", "checked": True, "user_id": 7}


def test_build_request_for_update_comment_html_format():
    tool = resolve_tool("comments.update")
    payload = merge_inputs(tool, {"card_id": 10, "comment_id": 30, "text": "<b>hi</b>", "format": "html"})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/comments/30"
    assert query is None
    assert body == {"text": "<b>hi</b>", "type": 2}


def test_build_request_for_add_card_tag():
    tool = resolve_tool("card-tags.add")
    payload = merge_inputs(tool, {"card_id": 10, "name": "urgent"})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/tags"
    assert query is None
    assert body == {"name": "urgent"}


def test_build_request_for_create_card_file():
    tool = resolve_tool("files.create")
    payload = merge_inputs(tool, {"card_id": 10, "url": "https://example.com/a.png", "name": "a.png", "card_cover": True})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/files"
    assert query is None
    assert body == {"url": "https://example.com/a.png", "name": "a.png", "card_cover": True}


def test_build_request_for_add_card_child():
    tool = resolve_tool("card-children.add")
    payload = merge_inputs(tool, {"card_id": 10, "child_card_id": 11})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/children"
    assert query is None
    assert body == {"card_id": 11}


def test_build_request_for_add_planned_relation_defaults_type():
    tool = resolve_tool("planned-relations.add")
    payload = merge_inputs(tool, {"card_id": 10, "target_card_id": 11})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/planned-relation"
    assert query is None
    assert body == {"target_card_id": 11, "type": "end-start"}


def test_build_request_for_update_planned_relation():
    tool = resolve_tool("planned-relations.update")
    payload = merge_inputs(tool, {"card_id": 10, "target_card_id": 11, "gap": 2, "gap_type": "days"})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/planned-relation/11"
    assert query is None
    assert body == {"gap": 2, "gap_type": "days"}


def test_build_request_for_remove_planned_relation():
    tool = resolve_tool("planned-relations.remove")
    payload = merge_inputs(tool, {"card_id": 10, "target_card_id": 11})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/planned-relation/11"
    assert query is None
    assert body is None


def test_build_request_for_create_project_maps_title_to_name():
    tool = resolve_tool("projects.create")
    payload = merge_inputs(tool, {"title": "Platform", "description": "Infra"})

    path, query, body = build_request(tool, payload)

    assert path == "/projects"
    assert query is None
    assert body == {"name": "Platform", "description": "Infra"}


def test_build_request_for_create_time_log_sets_default_role_id():
    tool = resolve_tool("time-logs.create")
    payload = merge_inputs(tool, {"card_id": 10, "time_spent": 15})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/time-logs"
    assert query is None
    assert body == {"time_spent": 15, "role_id": -1}


def test_build_request_for_create_user_timer():
    tool = resolve_tool("user-timers.create")
    payload = merge_inputs(tool, {"card_id": 10})

    path, query, body = build_request(tool, payload)

    assert path == "/user-timers"
    assert query is None
    assert body == {"card_id": 10}


def test_build_request_for_delete_board_force():
    tool = resolve_tool("boards.delete")
    payload = merge_inputs(tool, {"space_id": 10, "board_id": 20, "force": True})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/10/boards/20"
    assert query == {"force": True}
    assert body == {"force": True}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_columns(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/boards/10/columns").mock(
        return_value=Response(200, json=[{"id": 1, "title": "Todo", "type": 1}])
    )

    tool = resolve_tool("columns.list")
    payload = merge_inputs(tool, {"board_id": 10})
    result = await execute_tool(tool, payload, profile_name=None)

    assert route.called
    assert result == [{"id": 1, "title": "Todo", "type": 1}]


@respx.mock
def test_cli_columns_alias_and_canonical_match(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/boards/10/columns").mock(
        return_value=Response(200, json=[{"id": 1, "title": "Todo", "type": 1}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "columns", "list", "--board-id", "10"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_columns", "--board-id", "10"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called


@respx.mock
def test_cli_project_cards_alias_and_nested_canonical_match(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/projects/p1/cards").mock(
        return_value=Response(200, json=[{"id": 1, "title": "Task"}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "projects", "cards", "list", "--project-id", "p1"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_project_cards", "--project-id", "p1"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called


@respx.mock
def test_cli_planned_relation_add_alias_and_canonical_match(runner):
    route = respx.post(
        "https://sandbox.kaiten.ru/api/latest/cards/10/planned-relation",
        json={"target_card_id": 11, "type": "end-start"},
    ).mock(return_value=Response(200, json={"source_id": 10, "target_id": 11, "type": "end-start"}))
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(
        cli,
        ["--json", "planned-relations", "add", "--card-id", "10", "--target-card-id", "11"],
        env=env,
    )
    alias = runner.invoke(
        cli,
        ["--json", "kaiten_add_planned_relation", "--card-id", "10", "--target-card-id", "11"],
        env=env,
    )

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called


@respx.mock
def test_cli_planned_relation_update_alias_and_canonical_match(runner):
    route = respx.patch(
        "https://sandbox.kaiten.ru/api/latest/cards/10/planned-relation/11",
        json={"gap": 2, "gap_type": "days"},
    ).mock(return_value=Response(200, json={"source_id": 10, "target_id": 11, "gap": 2, "gap_type": "days"}))
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(
        cli,
        ["--json", "planned-relations", "update", "--card-id", "10", "--target-card-id", "11", "--gap", "2", "--gap-type", "days"],
        env=env,
    )
    alias = runner.invoke(
        cli,
        ["--json", "kaiten_update_planned_relation", "--card-id", "10", "--target-card-id", "11", "--gap", "2", "--gap-type", "days"],
        env=env,
    )

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_users_compact(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/users").mock(
        return_value=Response(
            200,
            json=[{"id": 7, "full_name": "Alice", "avatar": "data:image/png;base64,abc"}],
        )
    )

    tool = resolve_tool("users.list")
    payload = merge_inputs(tool, {"compact": True})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 7, "full_name": "Alice"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_get_blocker_filters_list(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/10/blockers").mock(
        return_value=Response(200, json=[{"id": 2, "reason": "Blocked"}, {"id": 3, "reason": "Waiting"}])
    )

    tool = resolve_tool("blockers.get")
    payload = merge_inputs(tool, {"card_id": 10, "blocker_id": 3})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == {"id": 3, "reason": "Waiting"}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_project_cards_compact(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/projects/p1/cards").mock(
        return_value=Response(200, json=[{"id": 1, "title": "Task", "owner": {"id": 7, "full_name": "Alice"}, "description": "secret"}])
    )

    tool = resolve_tool("projects.cards.list")
    payload = merge_inputs(tool, {"project_id": "p1", "compact": True})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "title": "Task", "owner": {"id": 7, "full_name": "Alice"}}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_project_cards_falls_back_to_project_payload_on_405(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    direct_route = respx.get("https://sandbox.kaiten.ru/api/latest/projects/p1/cards").mock(
        return_value=Response(405, json={"message": "Method Not Allowed"})
    )
    project_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/projects/p1",
        params={"with_cards_data": "true"},
    ).mock(
        return_value=Response(
            200,
            json={"project": {"cards": [{"id": 1, "title": "Task", "description": "hidden"}]}},
        )
    )

    tool = resolve_tool("projects.cards.list")
    payload = merge_inputs(tool, {"project_id": "p1", "compact": True})
    result = await execute_tool(tool, payload)

    assert direct_route.called
    assert project_route.called
    assert result == [{"id": 1, "title": "Task"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_calendars_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/calendars", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": "cal-1", "name": "Default"}])
    )

    tool = resolve_tool("calendars.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "cal-1", "name": "Default"}]
