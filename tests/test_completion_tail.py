from __future__ import annotations

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.client import HEAVY_TIMEOUT
from kaiten_cli.executor import build_request, execute_tool, timeout_for_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import TOOLS_BY_ALIAS, resolve_tool


def _snapshot_aliases(snapshot_path: Path) -> set[str]:
    return {line.strip() for line in snapshot_path.read_text(encoding="utf-8").splitlines() if line.strip()}


def test_help_shows_completion_tail_namespaces(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "sprints" in result.output


def test_resolve_completion_tail_aliases():
    assert resolve_tool("kaiten_move_card").canonical_name == "cards.move"
    assert resolve_tool("kaiten_list_all_cards").canonical_name == "cards.list-all"
    assert resolve_tool("kaiten_list_sprints").canonical_name == "sprints.list"
    assert resolve_tool("kaiten_update_company").canonical_name == "company.update"


def test_build_request_for_move_card():
    tool = resolve_tool("cards.move")
    payload = merge_inputs(tool, {"card_id": "C-1", "column_id": 10, "sort_order": 1.5})

    path, query, body = build_request(tool, payload)

    assert path == "/cards/C-1"
    assert query is None
    assert body == {"column_id": 10, "sort_order": 1.5}


def test_build_request_for_company_update():
    tool = resolve_tool("company.update")
    payload = merge_inputs(tool, {"name": "Acme"})

    path, query, body = build_request(tool, payload)

    assert path == "/companies/current"
    assert query is None
    assert body == {"name": "Acme"}


def test_timeout_policy_for_list_all_cards():
    tool = resolve_tool("cards.list-all")
    assert timeout_for_tool(tool) == HEAVY_TIMEOUT


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_all_cards_paginates_and_compacts_by_default(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards",
        params={"relations": "none", "board_id": "10", "limit": "2", "offset": "0"},
    ).mock(return_value=Response(200, json=[{"id": 1, "title": "A", "description": "x"}, {"id": 2, "title": "B", "description": "y"}]))
    second = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards",
        params={"relations": "none", "board_id": "10", "limit": "2", "offset": "2"},
    ).mock(return_value=Response(200, json=[{"id": 3, "title": "C", "description": "z"}]))

    tool = resolve_tool("cards.list-all")
    payload = merge_inputs(tool, {"board_id": 10, "page_size": 2, "max_pages": 5, "fields": "id,title"})
    result = await execute_tool(tool, payload)

    assert first.called
    assert second.called
    assert result == [{"id": 1, "title": "A"}, {"id": 2, "title": "B"}, {"id": 3, "title": "C"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_sprints_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/sprints", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Sprint 1"}])
    )

    tool = resolve_tool("sprints.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 1, "title": "Sprint 1"}]


@respx.mock
def test_cli_sprints_alias_and_canonical_match(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/sprints", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Sprint 1"}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "sprints", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_sprints"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called


def test_mcp_tool_alias_parity_against_snapshot():
    snapshot_path = Path(__file__).parent / "data" / "mcp_aliases.txt"
    cli_aliases = set(TOOLS_BY_ALIAS)
    snapshot_aliases = _snapshot_aliases(snapshot_path)
    missing = sorted(snapshot_aliases - cli_aliases)
    extra = sorted(cli_aliases - snapshot_aliases)

    assert not missing and not extra, (
        "CLI alias snapshot differs from current registry.\n"
        f"Missing: {missing}\n"
        f"Extra: {extra}"
    )
