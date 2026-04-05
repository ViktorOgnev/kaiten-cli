from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.client import DEFAULT_TIMEOUT, HEAVY_TIMEOUT
from kaiten_cli.executor import build_request, execute_tool, timeout_for_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_charts_and_compute_jobs(runner):
    result = runner.invoke(cli, ["--help"])
    charts_help = runner.invoke(cli, ["charts", "--help"])
    cfd_help = runner.invoke(cli, ["charts", "cfd", "--help"])

    assert result.exit_code == 0
    assert charts_help.exit_code == 0
    assert cfd_help.exit_code == 0
    assert "charts" in result.output
    assert "compute-jobs" in result.output
    assert "boards" in charts_help.output
    assert "create" in cfd_help.output


def test_resolve_chart_aliases():
    assert resolve_tool("kaiten_get_chart_boards").canonical_name == "charts.boards.get"
    assert resolve_tool("kaiten_chart_cfd").canonical_name == "charts.cfd.create"
    assert resolve_tool("kaiten_chart_task_distribution").canonical_name == "charts.task-distribution.create"
    assert resolve_tool("kaiten_get_compute_job").canonical_name == "compute-jobs.get"


def test_build_request_for_chart_summary():
    tool = resolve_tool("charts.summary.get")
    payload = merge_inputs(tool, {"space_id": 1, "date_from": "2026-01-01", "date_to": "2026-01-31", "done_columns": [10, 11]})

    path, query, body = build_request(tool, payload)

    assert path == "/charts/summary"
    assert query is None
    assert body == {"space_id": 1, "date_from": "2026-01-01", "date_to": "2026-01-31", "done_columns": [10, 11]}


def test_build_request_for_chart_cfd():
    tool = resolve_tool("charts.cfd.create")
    payload = merge_inputs(tool, {"space_id": 1, "date_from": "2026-01-01", "date_to": "2026-01-31", "selectedLanes": [4], "cardTypes": [2]})

    path, query, body = build_request(tool, payload)

    assert path == "/charts/cfd"
    assert query is None
    assert body == {
        "space_id": 1,
        "date_from": "2026-01-01",
        "date_to": "2026-01-31",
        "cardTypes": [2],
        "selectedLanes": [4],
    }


def test_timeout_policy_for_charts():
    heavy_tool = resolve_tool("charts.cfd.create")
    light_tool = resolve_tool("compute-jobs.get")

    assert timeout_for_tool(heavy_tool) == HEAVY_TIMEOUT
    assert timeout_for_tool(light_tool) == DEFAULT_TIMEOUT


@pytest.mark.asyncio
@respx.mock
async def test_execute_get_chart_boards(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/charts/1/boards").mock(
        return_value=Response(200, json=[{"id": 10, "title": "Board"}])
    )

    tool = resolve_tool("charts.boards.get")
    payload = merge_inputs(tool, {"space_id": 1})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 10, "title": "Board"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_create_chart_cfd(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.post("https://sandbox.kaiten.ru/api/latest/charts/cfd").mock(
        return_value=Response(200, json={"compute_job_id": 77})
    )

    tool = resolve_tool("charts.cfd.create")
    payload = merge_inputs(tool, {"space_id": 1, "date_from": "2026-01-01", "date_to": "2026-01-31"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == {"compute_job_id": 77}


@respx.mock
def test_cli_chart_boards_alias_and_canonical_match(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/charts/1/boards").mock(
        return_value=Response(200, json=[{"id": 10, "title": "Board"}])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "charts", "boards", "get", "--space-id", "1"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_get_chart_boards", "--space-id", "1"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
    assert route.called
