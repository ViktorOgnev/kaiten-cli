from __future__ import annotations

import json
import sqlite3
import time

import pytest
import respx
from httpx import Response

from kaiten_cli.discovery import describe_tool, search_tools
from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.snapshots import SNAPSHOT_DB_SCHEMA_VERSION, SnapshotStore
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.registry import resolve_tool


def _seed_snapshot(tmp_path, monkeypatch) -> SnapshotStore:
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: tmp_path / "snapshots.sqlite3")
    store = SnapshotStore(tmp_path / "snapshots.sqlite3")
    store.replace_snapshot(
        name="team-basic",
        profile_name="main",
        domain="sandbox",
        space_id=10,
        board_ids=[100],
        preset="analytics",
        window_start="2026-01-01T00:00:00Z",
        window_end="2026-03-31T23:59:59Z",
        spec={
            "name": "team-basic",
            "space_id": 10,
            "board_ids": [100],
            "preset": "analytics",
            "window_start": "2026-01-01T00:00:00Z",
            "window_end": "2026-03-31T23:59:59Z",
        },
        dataset_counts={
            "boards": 1,
            "columns": 2,
            "lanes": 1,
            "cards": 2,
            "activity_rows": 1,
            "history_cards": 2,
            "history_rows": 3,
            "time_log_cards": 1,
            "time_logs": 1,
            "child_relations": 1,
            "comments": 1,
            "card_detail_errors": 0,
            "history_errors": 0,
            "time_log_errors": 0,
            "relation_errors": 0,
            "comment_errors": 0,
        },
        build_trace={
            "total_http_request_count": 6,
            "total_retry_count": 0,
            "stages": [{"name": "topology", "duration_ms": 10.0, "http_request_count": 2, "retry_count": 0, "cache_hits": {"request": 0, "inflight_dedup": 0, "disk": 0}, "cache_misses": {"request": 0, "disk": 0}}],
        },
        topology={
            "space_id": 10,
            "boards": [
                {
                    "id": 100,
                    "title": "Flow",
                    "columns": [{"id": 1, "title": "Queue"}, {"id": 2, "title": "Done"}],
                    "lanes": [{"id": 5, "title": "Default"}],
                }
            ],
        },
        cards=[
            {
                "id": 1,
                "title": "Alpha",
                "description": "Important blocker",
                "board_id": 100,
                "column_id": 1,
                "lane_id": 5,
                "type_id": 11,
                "owner_id": 7,
                "responsible_id": 9,
                "state": 2,
                "condition": 1,
                "created": "2026-01-05T00:00:00Z",
                "updated": "2026-03-10T00:00:00Z",
                "tags": [{"id": 50, "title": "risk"}],
            },
            {
                "id": 2,
                "title": "Beta",
                "description": "Delivered",
                "board_id": 100,
                "column_id": 2,
                "lane_id": 5,
                "type_id": 12,
                "owner_id": 7,
                "responsible_id": 10,
                "state": 3,
                "condition": 1,
                "created": "2026-01-10T00:00:00Z",
                "updated": "2026-03-20T00:00:00Z",
                "last_moved_to_done_at": "2026-03-20T12:00:00Z",
            },
        ],
        history_map={
            1: [
                {"changed": "2026-01-05T00:00:00Z", "column_id": 1, "lane_id": 5, "condition": 1, "state": 1},
                {"changed": "2026-03-01T00:00:00Z", "column_id": 1, "lane_id": 5, "condition": 1, "state": 2},
            ],
            2: [
                {"changed": "2026-01-10T00:00:00Z", "column_id": 1, "lane_id": 5, "condition": 1, "state": 1},
                {"changed": "2026-02-15T00:00:00Z", "column_id": 1, "lane_id": 5, "condition": 1, "state": 2},
                {"changed": "2026-03-20T12:00:00Z", "column_id": 2, "lane_id": 5, "condition": 1, "state": 3},
            ],
        },
        children_map={1: [{"id": 101, "title": "Alpha child"}]},
        comments_map={1: [{"id": 201, "text": "blocked by dependency"}]},
        time_logs_map={
            1: [{"id": 301, "time_spent": 45, "for_date": "2026-03-05", "comment": "analysis"}],
        },
        activity_rows=[{"id": 1, "created": "2026-03-01T00:00:00Z", "action": "move"}],
    )
    return store


@pytest.mark.asyncio
@respx.mock
async def test_snapshot_build_basic_persists_metadata_and_counts(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: tmp_path / "snapshots.sqlite3")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/boards").mock(
        return_value=Response(200, json=[{"id": 100, "title": "Flow"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={"id": 100, "title": "Flow", "columns": [{"id": 1, "title": "Queue"}], "lanes": [{"id": 5, "title": "Default"}]},
        )
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards", params__contains={"board_id": 100}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Alpha", "board_id": 100, "column_id": 1, "lane_id": 5, "state": 1, "condition": 1, "created": "2026-01-01T00:00:00Z", "updated": "2026-01-02T00:00:00Z"}])
    )

    tool = resolve_tool("snapshot.build")
    payload = merge_inputs(tool, {"name": "team-basic", "space_id": 10, "preset": "basic"})
    result = await execute_tool(tool, payload)

    assert result["name"] == "team-basic"
    assert result["schema_version"] == 2
    assert result["datasets"]["boards"] == 1
    assert result["datasets"]["cards"] == 1
    assert [stage["name"] for stage in result["meta"]["trace"]["stages"]] == ["topology", "cards"]

    show_tool = resolve_tool("snapshot.show")
    show_payload = merge_inputs(show_tool, {"name": "team-basic"})
    show = await execute_tool(show_tool, show_payload)

    assert show["space_id"] == 10
    assert show["schema_version"] == 2
    assert show["datasets"]["cards"] == 1
    assert show["last_build_trace"]["stages"][0]["name"] == "topology"


def test_snapshot_build_analytics_requires_window():
    tool = resolve_tool("snapshot.build")
    with pytest.raises(ValidationError):
        merge_inputs(tool, {"name": "team-q1", "space_id": 10, "preset": "analytics"})


@pytest.mark.asyncio
@respx.mock
async def test_snapshot_build_analytics_includes_time_logs(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: tmp_path / "snapshots.sqlite3")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/boards").mock(
        return_value=Response(200, json=[{"id": 100, "title": "Flow"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(200, json={"id": 100, "title": "Flow", "columns": [], "lanes": []})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards", params__contains={"board_id": 100}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Alpha", "board_id": 100, "state": 2, "condition": 1, "created": "2026-01-01T00:00:00Z", "updated": "2026-03-01T00:00:00Z"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/activity").mock(
        return_value=Response(200, json=[{"id": 1, "created": "2026-03-01T00:00:00Z"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/location-history").mock(
        return_value=Response(200, json=[{"changed": "2026-03-01T00:00:00Z", "column_id": 1, "lane_id": 5, "condition": 1, "state": 2}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/time-logs").mock(
        return_value=Response(200, json=[{"id": 301, "time_spent": 30, "for_date": "2026-03-01"}])
    )

    tool = resolve_tool("snapshot.build")
    payload = merge_inputs(
        tool,
        {
            "name": "team-analytics",
            "space_id": 10,
            "preset": "analytics",
            "window_start": "2026-01-01T00:00:00Z",
            "window_end": "2026-03-31T23:59:59Z",
        },
    )
    result = await execute_tool(tool, payload)

    assert result["datasets"]["time_log_cards"] == 1
    assert result["datasets"]["time_logs"] == 1
    assert [stage["name"] for stage in result["meta"]["trace"]["stages"]] == [
        "topology",
        "cards",
        "activity",
        "history",
        "time-logs",
    ]


@pytest.mark.asyncio
@respx.mock
async def test_snapshot_build_evidence_enriches_cards_with_batch_get(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: tmp_path / "snapshots.sqlite3")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/boards").mock(
        return_value=Response(200, json=[{"id": 100, "title": "Flow"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(200, json={"id": 100, "title": "Flow", "columns": [], "lanes": []})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards", params__contains={"board_id": 100}).mock(
        return_value=Response(200, json=[{"id": 1, "title": "Alpha", "board_id": 100, "state": 1, "condition": 1}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(200, json={"id": 1, "title": "Alpha", "description": "full detail", "board_id": 100, "state": 1, "condition": 1})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/children").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/comments").mock(
        return_value=Response(200, json=[])
    )

    build_tool = resolve_tool("snapshot.build")
    build_payload = merge_inputs(build_tool, {"name": "team-evidence", "space_id": 10, "preset": "evidence"})
    build = await execute_tool(build_tool, build_payload)

    assert [stage["name"] for stage in build["meta"]["trace"]["stages"]] == [
        "topology",
        "cards",
        "card-details",
        "relations",
        "comments",
    ]

    query_tool = resolve_tool("query.cards")
    query_payload = merge_inputs(
        query_tool,
        {"snapshot": "team-evidence", "view": "detail", "fields": "id,title,description"},
    )
    query = await execute_tool(query_tool, query_payload)
    assert query["items"] == [{"id": 1, "title": "Alpha", "description": "full detail"}]


@pytest.mark.asyncio
@respx.mock
async def test_query_cards_uses_local_snapshot_without_http(monkeypatch, tmp_path):
    _seed_snapshot(tmp_path, monkeypatch)

    tool = resolve_tool("query.cards")
    payload = merge_inputs(
        tool,
        {
            "snapshot": "team-basic",
            "filter": '{"has_comments": true, "comment_text_query": "dependency"}',
            "view": "evidence",
            "fields": "id,title,has_comments,comment_text",
            "compact": True,
        },
    )
    result = await execute_tool(tool, payload)

    assert not respx.calls
    assert result["meta"]["total"] == 1
    assert result["meta"]["view"] == "evidence"
    assert result["items"] == [{"id": 1, "title": "Alpha", "has_comments": True, "comment_text": "blocked by dependency"}]


@pytest.mark.asyncio
@respx.mock
async def test_query_cards_defaults_to_summary_view(monkeypatch, tmp_path):
    _seed_snapshot(tmp_path, monkeypatch)

    tool = resolve_tool("query.cards")
    payload = merge_inputs(tool, {"snapshot": "team-basic"})
    result = await execute_tool(tool, payload)

    assert not respx.calls
    assert result["meta"]["view"] == "summary"
    assert "description" not in result["items"][0]
    assert "comment_text" not in result["items"][0]
    assert "time_spent_total_minutes" in result["items"][0]


@pytest.mark.asyncio
@respx.mock
async def test_query_metrics_computes_local_throughput_and_aging(monkeypatch, tmp_path):
    _seed_snapshot(tmp_path, monkeypatch)

    tool = resolve_tool("query.metrics")
    throughput_payload = merge_inputs(tool, {"snapshot": "team-basic", "metric": "throughput", "group_by": "board_id"})
    throughput = await execute_tool(tool, throughput_payload)
    assert not respx.calls
    assert throughput["rows"] == [{"group": "100", "value": 1, "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-03-31T23:59:59Z"}}]

    aging_payload = merge_inputs(tool, {"snapshot": "team-basic", "metric": "aging", "group_by": "column_id"})
    aging = await execute_tool(tool, aging_payload)
    assert aging["rows"][0]["group"] == "1"
    assert aging["rows"][0]["stats"]["count"] == 1
    assert aging["rows"][1]["group"] == "2"
    assert aging["rows"][1]["stats"] is None


@pytest.mark.asyncio
@respx.mock
async def test_snapshot_refresh_rebuilds_existing_snapshot(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: tmp_path / "snapshots.sqlite3")

    for title in ("Alpha", "Gamma"):
        respx.routes.clear()
        respx.get("https://sandbox.kaiten.ru/api/latest/spaces/10/boards").mock(
            return_value=Response(200, json=[{"id": 100, "title": "Flow"}])
        )
        respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
            return_value=Response(200, json={"id": 100, "title": "Flow", "columns": [], "lanes": []})
        )
        respx.get("https://sandbox.kaiten.ru/api/latest/cards", params__contains={"board_id": 100}).mock(
            return_value=Response(200, json=[{"id": 1, "title": title, "board_id": 100, "state": 1, "condition": 1}])
        )
        tool_name = "snapshot.build" if title == "Alpha" else "snapshot.refresh"
        tool = resolve_tool(tool_name)
        payload = merge_inputs(tool, {"name": "team-basic", "space_id": 10} if tool_name == "snapshot.build" else {"name": "team-basic"})
        await execute_tool(tool, payload)
        time.sleep(0.01)

    query_tool = resolve_tool("query.cards")
    query_payload = merge_inputs(query_tool, {"snapshot": "team-basic", "fields": "id,title"})
    result = await execute_tool(query_tool, query_payload)
    assert result["items"] == [{"id": 1, "title": "Gamma"}]


def test_discovery_exposes_snapshot_and_query_tools():
    snapshot = describe_tool("snapshot.build")
    assert snapshot["execution_mode"] == "custom"
    assert snapshot["mutation"] is True

    query = describe_tool("query.cards")
    assert query["cache_policy"] == "none"
    assert query["response_policy"]["compact_supported"] is True
    assert query["response_policy"]["fields_supported"] is True
    assert any(arg["name"] == "view" for arg in query["arguments"])
    assert any("never calls the Kaiten API" in note for note in query["usage_notes"])

    results = search_tools("local snapshot analytics")
    assert any(item["canonical_name"] == "snapshot.build" for item in results)


@pytest.mark.asyncio
async def test_snapshot_list_exposes_schema_version(monkeypatch, tmp_path):
    _seed_snapshot(tmp_path, monkeypatch)

    tool = resolve_tool("snapshot.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert result["items"] == [
        {
            "name": "team-basic",
            "profile_name": "main",
            "domain": "sandbox",
            "space_id": 10,
            "preset": "analytics",
            "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-03-31T23:59:59Z"},
            "schema_version": 2,
            "built_at": result["items"][0]["built_at"],
            "datasets": {
                "boards": 1,
                "columns": 2,
                "lanes": 1,
                "cards": 2,
                "activity_rows": 1,
                "history_cards": 2,
                "history_rows": 3,
                "time_log_cards": 1,
                "time_logs": 1,
                "child_relations": 1,
                "comments": 1,
                "card_detail_errors": 0,
                "history_errors": 0,
                "time_log_errors": 0,
                "relation_errors": 0,
                "comment_errors": 0,
            },
        }
    ]


def test_snapshot_store_resets_incompatible_db(monkeypatch, tmp_path):
    snapshot_path = tmp_path / "snapshots.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: snapshot_path)
    with sqlite3.connect(snapshot_path) as conn:
        conn.execute("CREATE TABLE legacy_snapshot_store (id INTEGER PRIMARY KEY)")
        conn.execute("PRAGMA user_version = 99")
        conn.commit()

    store = SnapshotStore(snapshot_path)
    assert store.list_snapshots() == []

    with sqlite3.connect(snapshot_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }

    assert version == SNAPSHOT_DB_SCHEMA_VERSION
    assert "snapshots" in tables


def test_snapshot_store_resets_corrupt_db(monkeypatch, tmp_path):
    snapshot_path = tmp_path / "snapshots.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: snapshot_path)
    snapshot_path.write_text("not-a-sqlite-db", encoding="utf-8")

    store = SnapshotStore(snapshot_path)
    assert store.list_snapshots() == []

    with sqlite3.connect(snapshot_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]

    assert version == SNAPSHOT_DB_SCHEMA_VERSION


def test_snapshot_store_reset_failure_raises_clear_config_error(monkeypatch, tmp_path):
    snapshot_path = tmp_path / "snapshots.sqlite3"
    monkeypatch.setattr("kaiten_cli.runtime.snapshots.snapshot_db_path", lambda: snapshot_path)
    with sqlite3.connect(snapshot_path) as conn:
        conn.execute("CREATE TABLE legacy_snapshot_store (id INTEGER PRIMARY KEY)")
        conn.execute("PRAGMA user_version = 99")
        conn.commit()

    def fail_reset(self, reason: str):
        raise self._reset_error("reset")

    monkeypatch.setattr(SnapshotStore, "_reset_store", fail_reset)

    with pytest.raises(ConfigError, match="Unable to reset local snapshot store"):
        SnapshotStore(snapshot_path).list_snapshots()
