from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import main
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


@pytest.mark.asyncio
@respx.mock
async def test_execute_card_children_batch_list_deduplicates_and_reports_partial_errors(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/children").mock(
        return_value=Response(
            200,
            json=[{"id": 11, "title": "Child", "owner": {"id": 7, "full_name": "Alice"}}],
        )
    )
    second = respx.get("https://sandbox.kaiten.ru/api/latest/cards/2/children").mock(
        return_value=Response(404, json={"message": "missing"})
    )

    tool = resolve_tool("card-children.batch-list")
    payload = merge_inputs(tool, {"card_ids": "[1,2,1]", "workers": 2, "compact": True, "fields": "id,title"})
    result = await execute_tool(tool, payload)

    assert first.call_count == 1
    assert second.call_count == 1
    assert result["meta"] == {
        "requested": 3,
        "requested_count": 3,
        "unique_count": 2,
        "succeeded": 1,
        "failed": 1,
        "workers": 2,
    }
    assert result["items"] == [{"card_id": 1, "children": [{"id": 11, "title": "Child"}]}]
    assert result["errors"] == [
        {"card_id": 2, "error_type": "api_error", "message": "missing", "status_code": 404}
    ]


@pytest.mark.asyncio
@respx.mock
async def test_execute_comments_batch_list_shapes_nested_payloads(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/comments").mock(
        return_value=Response(
            200,
            json=[{"id": 5, "text": "Looks good", "author": {"id": 7, "full_name": "Alice"}, "avatar": "data:image/png;base64,abc"}],
        )
    )

    tool = resolve_tool("comments.batch-list")
    payload = merge_inputs(tool, {"card_ids": "[1]", "compact": True, "fields": "id,text,author"})
    result = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert result["items"] == [
        {"card_id": 1, "comments": [{"id": 5, "text": "Looks good", "author": {"id": 7, "full_name": "Alice"}}]}
    ]
    assert result["errors"] == []


@pytest.mark.asyncio
@respx.mock
async def test_execute_space_topology_get_returns_board_details(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    boards = respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/boards").mock(
        return_value=Response(200, json=[{"id": 100, "title": "Flow"}])
    )
    detail = respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={"id": 100, "title": "Flow", "columns": [{"id": 1, "title": "Todo"}], "lanes": [{"id": 2, "title": "Default"}]},
        )
    )

    tool = resolve_tool("space-topology.get")
    payload = merge_inputs(tool, {"space_id": 10})
    result = await execute_tool(tool, payload)

    assert boards.called
    assert detail.called
    assert result == {
        "space_id": 10,
        "boards": [{"id": 100, "title": "Flow", "columns": [{"id": 1, "title": "Todo"}], "lanes": [{"id": 2, "title": "Default"}]}],
    }


@respx.mock
def test_trace_file_records_tool_stats_and_batch_meta(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    trace_file = tmp_path / "trace.jsonl"
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-04-15T10:00:00Z", "column_id": 10}])
    )

    exit_code = main(
        [
            "--json",
            "--trace-file",
            str(trace_file),
            "card-location-history",
            "batch-get",
            "--card-ids",
            "[1,1]",
            "--workers",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert route.call_count == 1
    assert json.loads(captured.out)["success"] is True

    entries = [json.loads(line) for line in trace_file.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["canonical_name"] == "card-location-history.batch-get"
    assert entry["execution_mode"] == "aggregated"
    assert entry["http_request_count"] == 1
    assert entry["requested_count"] == 2
    assert entry["unique_count"] == 1
    assert entry["workers"] == 2


def test_trace_file_from_env_redacts_tokens(config_env, monkeypatch, tmp_path, capsys):
    trace_file = tmp_path / "trace.jsonl"
    monkeypatch.setenv("KAITEN_TRACE_FILE", str(trace_file))

    exit_code = main(
        [
            "--json",
            "profile",
            "add",
            "main",
            "--domain",
            "sandbox",
            "--token",
            "super-secret-token",
            "--set-active",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out)["success"] is True
    entry = json.loads(trace_file.read_text(encoding="utf-8").splitlines()[0])
    assert entry["canonical_name"] == "profile.add"
    assert entry["execution_mode"] == "meta"
    token_index = entry["argv"].index("--token")
    assert entry["argv"][token_index + 1] == "[REDACTED]"
