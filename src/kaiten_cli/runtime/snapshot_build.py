"""Remote data collection and lifecycle executors for local snapshots."""

from __future__ import annotations

import time
from typing import Any

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.models import CACHE_POLICY_PERSISTENT_HEAVY
from kaiten_cli.runtime.snapshot_common import (
    SNAPSHOT_PRESETS,
    SNAPSHOT_SCHEMA_VERSION,
    WINDOW_PRESETS,
    _now_iso,
    _parse_timestamp,
    _sorted_history,
    _stats_delta,
    _stats_snapshot,
)
from kaiten_cli.runtime.snapshot_store import SnapshotStore
from kaiten_cli.runtime.support.audit import (
    DEFAULT_HISTORY_WORKERS,
    fetch_all_space_activity,
    fetch_card_location_histories,
)
from kaiten_cli.runtime.support.cards import fetch_all_cards, fetch_cards_batch_get
from kaiten_cli.runtime.support.relations import fetch_card_children_batch, fetch_comments_batch
from kaiten_cli.runtime.support.spaces import fetch_space_topology
from kaiten_cli.runtime.support.time_logs import fetch_time_logs_batch


def _validate_snapshot_build_payload(payload: dict[str, Any]) -> None:
    preset = payload.get("preset", "basic")
    if preset not in SNAPSHOT_PRESETS:
        allowed = ", ".join(sorted(SNAPSHOT_PRESETS))
        raise ValidationError(f"Field preset must be one of: {allowed}.")
    if preset in WINDOW_PRESETS:
        if not payload.get("window_start") or not payload.get("window_end"):
            raise ValidationError(
                "Fields window_start and window_end are required for analytics and full snapshots."
            )
    start = _parse_timestamp(payload.get("window_start"))
    end = _parse_timestamp(payload.get("window_end"))
    if start is not None and end is not None and start > end:
        raise ValidationError("window_start must be <= window_end.")
    board_ids = payload.get("board_ids")
    if board_ids is not None and (not isinstance(board_ids, list) or not board_ids):
        raise ValidationError("Field board_ids must be a non-empty array when provided.")


def validate_snapshot_build(tool, payload: dict[str, Any]) -> None:
    _validate_snapshot_build_payload(payload)


def _board_ids_for_snapshot(
    topology: dict[str, Any], requested_board_ids: list[int] | None
) -> list[int]:
    boards = []
    for board in topology.get("boards", []):
        if not isinstance(board, dict) or "id" not in board:
            continue
        if requested_board_ids and board["id"] not in requested_board_ids:
            continue
        boards.append(board)
    topology["boards"] = boards
    return [int(board["id"]) for board in boards]


def _dedupe_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[int, dict[str, Any]] = {}
    for card in cards:
        if not isinstance(card, dict) or "id" not in card:
            continue
        by_id[int(card["id"])] = card
    return [by_id[card_id] for card_id in sorted(by_id)]


async def _measure_stage(client, reporter, name: str, callback):
    stats = client.execution_context.stats
    before = _stats_snapshot(stats)
    started = time.perf_counter()
    data = await callback()
    after = _stats_snapshot(stats)
    delta = _stats_delta(after, before)
    stage = {
        "name": name,
        "duration_ms": round((time.perf_counter() - started) * 1000.0, 2),
        "http_request_count": delta["http_request_count"],
        "http_response_count": delta["http_response_count"],
        "http_error_count": delta["http_error_count"],
        "api_wait_ms": round(delta["api_wait_ms"], 2),
        "http_wait_ms": round(delta["http_wait_ms"], 2),
        "retry_count": delta["retry_count"],
        "cache_hits": {
            "request": delta["request_cache_hits"],
            "inflight_dedup": delta["inflight_dedup_hits"],
            "disk": delta["disk_cache_hits"],
        },
        "cache_misses": {
            "request": delta["request_cache_misses"],
            "disk": delta["disk_cache_misses"] + delta["disk_cache_expired"],
        },
    }
    if reporter is not None:
        reporter(
            f"snapshot-stage: name={name} duration_ms={stage['duration_ms']:.2f} "
            f"http_requests={stage['http_request_count']}"
        )
    return data, stage


async def _fetch_snapshot_cards(
    client, space_id: int, board_ids: list[int], *, timeout: float
) -> list[dict[str, Any]]:
    args = {"relations": "none"}
    if board_ids:
        cards: list[dict[str, Any]] = []
        for board_id in board_ids:
            result = await fetch_all_cards(client, {**args, "board_id": board_id}, timeout=timeout)
            cards.extend(item for item in result if isinstance(item, dict))
        return _dedupe_cards(cards)
    result = await fetch_all_cards(client, {**args, "space_id": space_id}, timeout=timeout)
    return [item for item in result if isinstance(item, dict)]


def _children_map(result: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], int]:
    mapping: dict[int, list[dict[str, Any]]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item:
            mapping[int(item["card_id"])] = [
                row for row in item.get("children", []) if isinstance(row, dict)
            ]
    return mapping, len(result.get("errors", []))


def _comments_map(result: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], int]:
    mapping: dict[int, list[dict[str, Any]]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item:
            mapping[int(item["card_id"])] = [
                row for row in item.get("comments", []) if isinstance(row, dict)
            ]
    return mapping, len(result.get("errors", []))


def _history_map(result: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], int]:
    mapping: dict[int, list[dict[str, Any]]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item:
            mapping[int(item["card_id"])] = _sorted_history(item.get("history", []))
    return mapping, len(result.get("errors", []))


def _cards_map(result: dict[str, Any]) -> tuple[dict[int, dict[str, Any]], int]:
    mapping: dict[int, dict[str, Any]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item and isinstance(item.get("card"), dict):
            mapping[int(item["card_id"])] = item["card"]
    return mapping, len(result.get("errors", []))


def _time_logs_map(result: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], int]:
    mapping: dict[int, list[dict[str, Any]]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item:
            mapping[int(item["card_id"])] = [
                row for row in item.get("time_logs", []) if isinstance(row, dict)
            ]
    return mapping, len(result.get("errors", []))


def _merge_card_details(
    cards: list[dict[str, Any]], details_map: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for card in cards:
        if not isinstance(card, dict) or "id" not in card:
            continue
        card_id = int(card["id"])
        detail = details_map.get(card_id)
        if detail:
            payload = dict(card)
            payload.update(detail)
            merged.append(payload)
        else:
            merged.append(card)
    return merged


async def _build_snapshot(
    *,
    client,
    payload: dict[str, Any],
    reporter,
    timeout: float,
    spec: dict[str, Any],
) -> dict[str, Any]:
    store = SnapshotStore(reporter=reporter)
    store.ensure_writable()
    client.cache_policy = CACHE_POLICY_PERSISTENT_HEAVY
    requested_board_ids = payload.get("board_ids")
    topology, topology_stage = await _measure_stage(
        client,
        reporter,
        "topology",
        lambda: fetch_space_topology(client, int(spec["space_id"]), timeout=timeout),
    )
    board_ids = _board_ids_for_snapshot(topology, requested_board_ids)
    cards, cards_stage = await _measure_stage(
        client,
        reporter,
        "cards",
        lambda: _fetch_snapshot_cards(client, int(spec["space_id"]), board_ids, timeout=timeout),
    )
    card_ids = [int(card["id"]) for card in cards if isinstance(card, dict) and "id" in card]

    activity_rows: list[dict[str, Any]] = []
    history_map: dict[int, list[dict[str, Any]]] = {}
    children_map: dict[int, list[dict[str, Any]]] = {}
    comments_map: dict[int, list[dict[str, Any]]] = {}
    time_logs_map: dict[int, list[dict[str, Any]]] = {}
    dataset_errors = {
        "card_detail_errors": 0,
        "history_errors": 0,
        "time_log_errors": 0,
        "relation_errors": 0,
        "comment_errors": 0,
    }
    stages = [topology_stage, cards_stage]

    if spec["preset"] in {"evidence", "full"} and card_ids:
        card_details_result, card_details_stage = await _measure_stage(
            client,
            reporter,
            "card-details",
            lambda: fetch_cards_batch_get(
                domain=client.domain,
                token=client.token,
                card_ids=card_ids,
                workers=DEFAULT_HISTORY_WORKERS,
                compact=False,
                fields=None,
                timeout=timeout,
                reporter=reporter,
                execution_context=client.execution_context,
                cache_policy=CACHE_POLICY_PERSISTENT_HEAVY,
            ),
        )
        card_details_map, dataset_errors["card_detail_errors"] = _cards_map(card_details_result)
        cards = _merge_card_details(cards, card_details_map)
        card_details_stage["rows"] = len(card_details_map)
        card_details_stage["errors"] = dataset_errors["card_detail_errors"]
        stages.append(card_details_stage)

    if spec["preset"] in {"analytics", "full"}:
        activity_rows, activity_stage = await _measure_stage(
            client,
            reporter,
            "activity",
            lambda: fetch_all_space_activity(
                client,
                {
                    "space_id": int(spec["space_id"]),
                    "created_after": spec.get("window_start"),
                    "created_before": spec.get("window_end"),
                },
                timeout=timeout,
            ),
        )
        history_result, history_stage = await _measure_stage(
            client,
            reporter,
            "history",
            lambda: fetch_card_location_histories(
                domain=client.domain,
                token=client.token,
                card_ids=card_ids,
                workers=DEFAULT_HISTORY_WORKERS,
                fields=None,
                timeout=timeout,
                reporter=reporter,
                execution_context=client.execution_context,
                cache_policy=CACHE_POLICY_PERSISTENT_HEAVY,
            ),
        )
        history_map, dataset_errors["history_errors"] = _history_map(history_result)
        history_stage["rows"] = sum(len(rows) for rows in history_map.values())
        history_stage["errors"] = dataset_errors["history_errors"]
        time_logs_result, time_logs_stage = await _measure_stage(
            client,
            reporter,
            "time-logs",
            lambda: fetch_time_logs_batch(
                domain=client.domain,
                token=client.token,
                card_ids=card_ids,
                workers=DEFAULT_HISTORY_WORKERS,
                compact=False,
                fields=None,
                timeout=timeout,
                reporter=reporter,
                execution_context=client.execution_context,
                cache_policy=CACHE_POLICY_PERSISTENT_HEAVY,
            ),
        )
        time_logs_map, dataset_errors["time_log_errors"] = _time_logs_map(time_logs_result)
        time_logs_stage["rows"] = sum(len(rows) for rows in time_logs_map.values())
        time_logs_stage["errors"] = dataset_errors["time_log_errors"]
        stages.extend([activity_stage, history_stage, time_logs_stage])

    if spec["preset"] in {"evidence", "full"} and card_ids:
        relation_result, relations_stage = await _measure_stage(
            client,
            reporter,
            "relations",
            lambda: fetch_card_children_batch(
                domain=client.domain,
                token=client.token,
                card_ids=card_ids,
                workers=DEFAULT_HISTORY_WORKERS,
                compact=False,
                fields=None,
                timeout=timeout,
                reporter=reporter,
                execution_context=client.execution_context,
                cache_policy=CACHE_POLICY_PERSISTENT_HEAVY,
            ),
        )
        children_map, dataset_errors["relation_errors"] = _children_map(relation_result)
        relations_stage["rows"] = sum(len(rows) for rows in children_map.values())
        relations_stage["errors"] = dataset_errors["relation_errors"]
        comments_result, comments_stage = await _measure_stage(
            client,
            reporter,
            "comments",
            lambda: fetch_comments_batch(
                domain=client.domain,
                token=client.token,
                card_ids=card_ids,
                workers=DEFAULT_HISTORY_WORKERS,
                compact=False,
                fields=None,
                timeout=timeout,
                reporter=reporter,
                execution_context=client.execution_context,
                cache_policy=CACHE_POLICY_PERSISTENT_HEAVY,
            ),
        )
        comments_map, dataset_errors["comment_errors"] = _comments_map(comments_result)
        comments_stage["rows"] = sum(len(rows) for rows in comments_map.values())
        comments_stage["errors"] = dataset_errors["comment_errors"]
        stages.extend([relations_stage, comments_stage])

    dataset_counts = {
        "boards": len(topology.get("boards", [])),
        "columns": sum(
            len(board.get("columns", []))
            for board in topology.get("boards", [])
            if isinstance(board, dict)
        ),
        "lanes": sum(
            len(board.get("lanes", []))
            for board in topology.get("boards", [])
            if isinstance(board, dict)
        ),
        "cards": len(cards),
        "activity_rows": len(activity_rows),
        "history_cards": len(history_map),
        "history_rows": sum(len(rows) for rows in history_map.values()),
        "time_log_cards": len(time_logs_map),
        "time_logs": sum(len(rows) for rows in time_logs_map.values()),
        "child_relations": sum(len(rows) for rows in children_map.values()),
        "comments": sum(len(rows) for rows in comments_map.values()),
        **dataset_errors,
    }
    build_trace = {
        "total_http_request_count": client.execution_context.stats.http_request_count,
        "total_retry_count": client.execution_context.stats.retry_count,
        "stages": stages,
    }
    store.replace_snapshot(
        name=spec["name"],
        profile_name=client.execution_context.profile.name,
        domain=client.domain,
        space_id=int(spec["space_id"]),
        board_ids=board_ids,
        preset=spec["preset"],
        window_start=spec.get("window_start"),
        window_end=spec.get("window_end"),
        spec=spec,
        dataset_counts=dataset_counts,
        build_trace=build_trace,
        topology=topology,
        cards=cards,
        history_map=history_map,
        children_map=children_map,
        comments_map=comments_map,
        time_logs_map=time_logs_map,
        activity_rows=activity_rows,
    )
    return {
        "name": spec["name"],
        "profile_name": client.execution_context.profile.name,
        "domain": client.domain,
        "space_id": int(spec["space_id"]),
        "board_ids": board_ids,
        "preset": spec["preset"],
        "window": {"start": spec.get("window_start"), "end": spec.get("window_end")},
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "built_at": _now_iso(),
        "datasets": dataset_counts,
        "meta": {"trace": build_trace},
    }


async def execute_snapshot_build(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    if client is None or client.execution_context is None:
        raise ConfigError("snapshot.build requires an active Kaiten profile.")
    spec = {
        "name": payload["name"],
        "space_id": int(payload["space_id"]),
        "board_ids": payload.get("board_ids"),
        "preset": payload.get("preset", "basic"),
        "window_start": payload.get("window_start"),
        "window_end": payload.get("window_end"),
    }
    _validate_snapshot_build_payload(spec)
    if reporter is not None:
        reporter(
            f"execution: local snapshot build name={spec['name']} preset={spec['preset']} space_id={spec['space_id']}"
        )
    return await _build_snapshot(
        client=client, payload=payload, reporter=reporter, timeout=timeout, spec=spec
    )


async def execute_snapshot_refresh(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    if client is None or client.execution_context is None:
        raise ConfigError("snapshot.refresh requires an active Kaiten profile.")
    store = SnapshotStore(reporter=reporter)
    store.ensure_writable()
    existing = store.get_snapshot(payload["name"])
    if existing["domain"] and existing["domain"] != client.domain:
        raise ConfigError(
            f"Snapshot {payload['name']} was built for domain {existing['domain']}, current profile uses {client.domain}."
        )
    spec = dict(existing["spec"])
    if reporter is not None:
        reporter(f"execution: local snapshot refresh name={spec['name']}")
    await client.execution_context.clear_cache_scope(reason="snapshot-refresh")
    return await _build_snapshot(
        client=client, payload=payload, reporter=reporter, timeout=timeout, spec=spec
    )


async def execute_snapshot_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    return {"items": SnapshotStore(reporter=reporter).list_snapshots()}


async def execute_snapshot_show(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    return SnapshotStore(reporter=reporter).get_snapshot(payload["name"])


async def execute_snapshot_delete(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    return SnapshotStore(reporter=reporter).delete_snapshot(payload["name"])
