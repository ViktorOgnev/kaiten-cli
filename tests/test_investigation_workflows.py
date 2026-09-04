from __future__ import annotations

import json
import stat

import pytest
import respx
from httpx import Response

from kaiten_cli.app import main
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.trace import TraceRecorder
from kaiten_cli.registry import resolve_tool


@pytest.mark.asyncio
@respx.mock
async def test_execute_card_children_batch_list_deduplicates_and_reports_partial_errors(
    monkeypatch,
):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/children",
        params={"limit": "100", "offset": "0"},
    ).mock(
        return_value=Response(
            200,
            json=[{"id": 11, "title": "Child", "owner": {"id": 7, "full_name": "Alice"}}],
        )
    )
    second = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/2/children",
        params={"limit": "100", "offset": "0"},
    ).mock(return_value=Response(404, json={"message": "missing"}))

    tool = resolve_tool("card-children.batch-list")
    payload = merge_inputs(
        tool, {"card_ids": "[1,2,1]", "workers": 2, "compact": True, "fields": "id,title"}
    )
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
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/comments",
        params={"limit": "100", "offset": "0"},
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": 5,
                    "text": "Looks good",
                    "author": {"id": 7, "full_name": "Alice"},
                    "avatar": "data:image/png;base64,abc",
                }
            ],
        )
    )

    tool = resolve_tool("comments.batch-list")
    payload = merge_inputs(tool, {"card_ids": "[1]", "compact": True, "fields": "id,text,author"})
    result = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert result["items"] == [
        {
            "card_id": 1,
            "comments": [
                {"id": 5, "text": "Looks good", "author": {"id": 7, "full_name": "Alice"}}
            ],
        }
    ]
    assert result["errors"] == []


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_batch_get_shapes_card_payloads(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(
            200,
            json={
                "id": 1,
                "title": "Alpha",
                "description": "detail",
                "owner": {"id": 7, "full_name": "Alice"},
                "avatar": "data:image/png;base64,abc",
            },
        )
    )

    tool = resolve_tool("cards.batch-get")
    payload = merge_inputs(tool, {"card_ids": "[1,1]", "fields": "id,title,description"})
    result = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert result["meta"]["requested_count"] == 2
    assert result["meta"]["unique_count"] == 1
    assert result["items"] == [
        {"card_id": 1, "card": {"id": 1, "title": "Alpha", "description": "detail"}}
    ]


@pytest.mark.asyncio
@respx.mock
async def test_execute_time_logs_batch_list_propagates_query_and_shapes_payloads(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/time-logs",
        params={
            "for_date": "2026-04-01",
            "personal": "true",
            "limit": "100",
            "offset": "0",
        },
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": 10,
                    "time_spent": 30,
                    "for_date": "2026-04-01",
                    "comment": "analysis",
                    "author": {"id": 7},
                }
            ],
        )
    )

    tool = resolve_tool("time-logs.batch-list")
    payload = merge_inputs(
        tool,
        {
            "card_ids": "[1]",
            "for_date": "2026-04-01",
            "personal": True,
            "fields": "id,time_spent,for_date",
        },
    )
    result = await execute_tool(tool, payload)

    assert route.call_count == 1
    assert result["items"] == [
        {"card_id": 1, "time_logs": [{"id": 10, "time_spent": 30, "for_date": "2026-04-01"}]}
    ]
    assert result["errors"] == []


@pytest.mark.asyncio
@respx.mock
async def test_execute_card_children_batch_list_paginates_each_card(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/children",
        params={"limit": "2", "offset": "0"},
    ).mock(return_value=Response(200, json=[{"id": 11}, {"id": 12}]))
    second = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/children",
        params={"limit": "2", "offset": "2"},
    ).mock(return_value=Response(200, json=[{"id": 13}]))
    tool = resolve_tool("card-children.batch-list")

    result = await execute_tool(
        tool,
        merge_inputs(tool, {"card_ids": "[1]", "page_size": 2, "max_pages": 3}),
    )

    assert first.called and second.called
    assert result["items"] == [{"card_id": 1, "children": [{"id": 11}, {"id": 12}, {"id": 13}]}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_comments_batch_list_keeps_cap_failure_local_to_card(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    for offset in (0, 2):
        respx.get(
            "https://sandbox.kaiten.ru/api/latest/cards/1/comments",
            params={"limit": "2", "offset": str(offset)},
        ).mock(return_value=Response(200, json=[{"id": offset + 1}, {"id": offset + 2}]))
    respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/2/comments",
        params={"limit": "2", "offset": "0"},
    ).mock(return_value=Response(200, json=[{"id": 9}]))
    tool = resolve_tool("comments.batch-list")

    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {"card_ids": "[1,2]", "workers": 2, "page_size": 2, "max_pages": 2},
        ),
    )

    assert result["items"] == [{"card_id": 2, "comments": [{"id": 9}]}]
    assert result["errors"][0]["card_id"] == 1
    assert result["errors"][0]["error_type"] == "config_error"
    assert "possibly truncated" in result["errors"][0]["message"]


@pytest.mark.asyncio
@respx.mock
async def test_execute_time_logs_batch_list_preserves_filters_on_every_page(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    common = {"for_date": "2026-04-01", "personal": "true", "limit": "2"}
    first = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/time-logs",
        params={**common, "offset": "0"},
    ).mock(return_value=Response(200, json=[{"id": 1}, {"id": 2}]))
    second = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/1/time-logs",
        params={**common, "offset": "2"},
    ).mock(return_value=Response(200, json=[]))
    tool = resolve_tool("time-logs.batch-list")

    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "card_ids": "[1]",
                "for_date": "2026-04-01",
                "personal": True,
                "page_size": 2,
                "max_pages": 3,
            },
        ),
    )

    assert first.called and second.called
    assert result["items"] == [{"card_id": 1, "time_logs": [{"id": 1}, {"id": 2}]}]


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
            json={
                "id": 100,
                "title": "Flow",
                "columns": [{"id": 1, "title": "Todo"}],
                "lanes": [{"id": 2, "title": "Default"}],
            },
        )
    )

    tool = resolve_tool("space-topology.get")
    payload = merge_inputs(tool, {"space_id": 10})
    result = await execute_tool(tool, payload)

    assert boards.called
    assert detail.called
    assert result == {
        "space_id": 10,
        "boards": [
            {
                "id": 100,
                "title": "Flow",
                "columns": [{"id": 1, "title": "Todo"}],
                "lanes": [{"id": 2, "title": "Default"}],
            }
        ],
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
    stdout_payload = json.loads(captured.out)
    assert stdout_payload["success"] is True
    assert stdout_payload["stats"]["http_request_count"] == 1
    assert stdout_payload["stats"]["groups"][0]["path_family"] == "/cards/:id/location-history"

    entries = [json.loads(line) for line in trace_file.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["canonical_name"] == "card-location-history.batch-get"
    assert entry["execution_mode"] == "aggregated"
    assert entry["http_request_count"] == 1
    assert entry["stats"]["http_request_count"] == 1
    assert entry["stats"]["groups"][0]["path_family"] == "/cards/:id/location-history"
    assert entry["requested_count"] == 2
    assert entry["unique_count"] == 1
    assert entry["workers"] == 2
    assert entry["cache"] == {
        "mode": "auto",
        "policy": "persistent_heavy",
        "ttl_seconds": None,
    }
    assert stdout_payload["stats"]["cache"] == entry["cache"]
    assert stat.S_IMODE(trace_file.stat().st_mode) == 0o600


def test_trace_file_preserves_existing_parent_mode(tmp_path):
    trace_directory = tmp_path / "shared-traces"
    trace_directory.mkdir(mode=0o755)
    trace_directory.chmod(0o755)
    trace_file = trace_directory / "trace.jsonl"

    TraceRecorder(trace_file).write(
        canonical_name="spaces.list",
        execution_mode="direct_http",
        argv=["kaiten", "spaces", "list"],
        exit_code=0,
        duration_ms=1.0,
    )

    assert stat.S_IMODE(trace_directory.stat().st_mode) == 0o755
    assert stat.S_IMODE(trace_file.stat().st_mode) == 0o600


def test_trace_file_supports_user_selected_symlinked_parent(tmp_path):
    target_directory = tmp_path / "real-traces"
    target_directory.mkdir(mode=0o755)
    linked_directory = tmp_path / "trace-link"
    linked_directory.symlink_to(target_directory, target_is_directory=True)
    trace_file = linked_directory / "trace.jsonl"

    TraceRecorder(trace_file).write(
        canonical_name="spaces.list",
        execution_mode="direct_http",
        argv=["kaiten", "spaces", "list"],
        exit_code=0,
        duration_ms=1.0,
    )

    assert trace_file.exists()
    assert stat.S_IMODE(target_directory.stat().st_mode) == 0o755
    assert stat.S_IMODE(trace_file.stat().st_mode) == 0o600


@respx.mock
def test_trace_failure_does_not_turn_successful_mutation_into_cli_failure(
    config_env, monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.post("https://sandbox.kaiten.ru/api/latest/cards").mock(
        return_value=Response(201, json={"id": 123, "title": "Task"})
    )

    def fail_trace_write(self, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(TraceRecorder, "write", fail_trace_write)
    exit_code = main(
        [
            "--json",
            "--trace-file",
            str(tmp_path / "trace.jsonl"),
            "cards",
            "create",
            "--title",
            "Task",
            "--board-id",
            "1",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out)["success"] is True
    assert route.call_count == 1
    assert "trace record was not written" in captured.err


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


def test_trace_summarize_streams_bounded_payload_free_recommendations(tmp_path, capsys):
    trace_file = tmp_path / "trace.jsonl"
    entries = []
    for index in range(5):
        entries.append(
            {
                "canonical_name": "cards.get",
                "execution_mode": "direct_http",
                "exit_code": 0,
                "duration_ms": 10,
                "argv": [
                    "--json",
                    "--token",
                    f"secret-{index}",
                    "cards",
                    "get",
                    "--card-id",
                    str(index),
                ],
                "stats": {
                    "cache": {
                        "mode": "refresh" if index < 2 else "auto",
                        "policy": "persistent_opt_in",
                        "ttl_seconds": 60,
                    },
                    "http_request_count": 2,
                    "api_wait_ms": 5,
                    "retry_count": 0,
                    "cache_hits": {"request": 0, "inflight_dedup": 0, "disk": 0},
                    "cache_misses": {"request": 1, "disk": 1},
                    "cache_bypasses": {"disk": 1 if index < 2 else 0},
                    "groups": [
                        {
                            "path_family": "/cards/:id",
                            "http_request_count": 2,
                        }
                    ],
                },
            }
        )
    repeated_population = {
        "canonical_name": "cards.list-all",
        "execution_mode": "aggregated",
        "exit_code": 0,
        "duration_ms": 20,
        "argv": ["--json", "cards", "list-all", "--board-id", "10"],
        "stats": {
            "cache": {
                "mode": "auto",
                "policy": "persistent_heavy",
                "ttl_seconds": 60,
            },
            "http_request_count": 1,
            "api_wait_ms": 2,
            "retry_count": 0,
            "groups": [],
        },
    }
    entries.extend([repeated_population, repeated_population])
    trace_file.write_text(
        "\n".join(json.dumps(entry) for entry in entries)
        + '\n{"broken":\n'
        + json.dumps(
            {
                "canonical_name": "unsafe payload",
                "argv": ["private-description"],
                "payload": {"text": "must-not-leak"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert main(["--json", "trace", "summarize", "--file", str(trace_file)]) == 0
    rendered = capsys.readouterr().out
    payload = json.loads(rendered)
    data = payload["data"]

    assert data["lines"] == 9
    assert data["entries"] == 8
    assert data["invalid_lines"] == 1
    assert data["http_request_count"] == 12
    assert data["path_families"] == [{"path_family": "/cards/:id", "count": 10}]
    assert [item["code"] for item in data["recommendations"]] == [
        "prefer_batch",
        "prefer_snapshot",
        "prefer_auto",
    ]
    assert "argv" not in rendered
    assert "private-description" not in rendered
    assert "must-not-leak" not in rendered
    assert "secret-" not in rendered
