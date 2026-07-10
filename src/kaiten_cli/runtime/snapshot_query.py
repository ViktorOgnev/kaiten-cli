"""Local-only snapshot card queries and generic metric aggregation."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.snapshot_common import (
    DEFAULT_LOCAL_LIMIT,
    QUERY_FILTER_KEYS,
    _duration_stats,
    _iso_timestamp,
    _normalize_bool,
    _normalize_int_list,
    _normalize_string,
    _parse_timestamp,
    _shape_card_for_output,
)
from kaiten_cli.runtime.snapshot_store import SnapshotStore


def validate_query_filter(tool, payload: dict[str, Any]) -> None:
    filter_payload = payload.get("filter")
    if filter_payload is None:
        return
    if not isinstance(filter_payload, dict):
        raise ValidationError("Field filter must be an object.")
    unknown = sorted(set(filter_payload) - QUERY_FILTER_KEYS)
    if unknown:
        raise ValidationError(f"Unknown query filter field(s): {', '.join(unknown)}")


def _matches_query_filter(record: dict[str, Any], filters: dict[str, Any]) -> bool:
    board_ids = _normalize_int_list(filters.get("board_ids"))
    if board_ids and record["board_id"] not in board_ids:
        return False
    column_ids = _normalize_int_list(filters.get("column_ids"))
    if column_ids and record["column_id"] not in column_ids:
        return False
    lane_ids = _normalize_int_list(filters.get("lane_ids"))
    if lane_ids and record["lane_id"] not in lane_ids:
        return False
    type_ids = _normalize_int_list(filters.get("type_ids"))
    if type_ids and record["type_id"] not in type_ids:
        return False
    owner_ids = _normalize_int_list(filters.get("owner_ids"))
    if owner_ids and record["owner_id"] not in owner_ids:
        return False
    responsible_ids = _normalize_int_list(filters.get("responsible_ids"))
    if responsible_ids and record["responsible_id"] not in responsible_ids:
        return False
    states = _normalize_int_list(filters.get("states"))
    if states and record["state"] not in states:
        return False
    condition_values = _normalize_int_list(filters.get("condition"))
    if condition_values and record["condition"] not in condition_values:
        return False
    tag_ids = _normalize_int_list(filters.get("tag_ids"))
    if tag_ids and not (set(record["tag_ids"]) & set(tag_ids)):
        return False

    created = _parse_timestamp(record["created"])
    updated = _parse_timestamp(record["updated"])
    created_after = _parse_timestamp(filters.get("created_after"))
    if created_after is not None and (created is None or created < created_after):
        return False
    created_before = _parse_timestamp(filters.get("created_before"))
    if created_before is not None and (created is None or created > created_before):
        return False
    updated_after = _parse_timestamp(filters.get("updated_after"))
    if updated_after is not None and (updated is None or updated < updated_after):
        return False
    updated_before = _parse_timestamp(filters.get("updated_before"))
    if updated_before is not None and (updated is None or updated > updated_before):
        return False

    has_children = _normalize_bool(filters.get("has_children"))
    if has_children is not None and record["has_children"] != has_children:
        return False
    has_comments = _normalize_bool(filters.get("has_comments"))
    if has_comments is not None and record["has_comments"] != has_comments:
        return False

    text_query = _normalize_string(filters.get("text_query"))
    if text_query and text_query not in record["search_text"].lower():
        return False
    child_text_query = _normalize_string(filters.get("child_text_query"))
    if child_text_query and child_text_query not in record["child_text"].lower():
        return False
    comment_text_query = _normalize_string(filters.get("comment_text_query"))
    if comment_text_query and comment_text_query not in record["comment_text"].lower():
        return False
    return True


def _text_candidate_ids(
    store: SnapshotStore, snapshot_name: str, filters: dict[str, Any]
) -> set[int] | None:
    candidate_sets: list[set[int]] = []
    mapping = {
        "text_query": "search_text",
        "child_text_query": "child_text",
        "comment_text_query": "comment_text",
    }
    for filter_name, column_name in mapping.items():
        query = _normalize_string(filters.get(filter_name))
        if query:
            candidate_sets.append(store.text_candidate_card_ids(snapshot_name, column_name, query))
    if not candidate_sets:
        return None
    candidates = candidate_sets[0]
    for subset in candidate_sets[1:]:
        candidates &= subset
    return candidates


async def execute_query_cards(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    store = SnapshotStore(reporter=reporter)
    snapshot = store.get_snapshot(payload["snapshot"])
    filters = payload.get("filter") or {}
    candidate_ids = _text_candidate_ids(store, payload["snapshot"], filters)
    offset = max(int(payload.get("offset", 0)), 0)
    limit = max(int(payload.get("limit", DEFAULT_LOCAL_LIMIT)), 1)
    view = payload.get("view", "summary")
    sliced, total = store.query_card_records(
        payload["snapshot"],
        filters,
        candidate_ids,
        limit=limit,
        offset=offset,
    )
    items = [
        _shape_card_for_output(
            record,
            view=view,
            compact=bool(payload.get("compact", False)),
            fields=payload.get("fields"),
        )
        for record in sliced
    ]
    return {
        "snapshot": snapshot["name"],
        "items": items,
        "meta": {
            "view": view,
            "total": total,
            "returned": len(items),
            "offset": offset,
            "limit": limit,
            "window": snapshot["window"],
        },
    }


def _group_label(record: dict[str, Any], group_by: str | None) -> str:
    if not group_by:
        return "all"
    value = record.get(group_by)
    return "null" if value is None else str(value)


def _metric_cutoff(snapshot: dict[str, Any]) -> datetime:
    cutoff = _parse_timestamp(snapshot["window"].get("end"))
    if cutoff is not None:
        return cutoff
    built_at = _parse_timestamp(snapshot["built_at"])
    return built_at or datetime.now(timezone.utc)


def _metric_done_in_window(done_at: datetime | None, snapshot: dict[str, Any]) -> bool:
    if done_at is None:
        return False
    start = _parse_timestamp(snapshot["window"].get("start"))
    end = _parse_timestamp(snapshot["window"].get("end"))
    if start is not None and done_at < start:
        return False
    if end is not None and done_at > end:
        return False
    return True


async def execute_query_metrics(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    store = SnapshotStore(reporter=reporter)
    snapshot = store.get_snapshot(payload["snapshot"])
    filters = payload.get("filter") or {}
    candidate_ids = _text_candidate_ids(store, payload["snapshot"], filters)
    metric = payload["metric"]
    group_by = payload.get("group_by")
    cutoff = _metric_cutoff(snapshot)
    metric_column_map = {
        "count": ("card_id", group_by or "card_id"),
        "wip": ("card_id", group_by or "card_id", "condition", "state"),
        "throughput": ("card_id", group_by or "card_id", "done_at"),
        "lead_time": ("card_id", group_by or "card_id", "lead_time_days", "done_at"),
        "cycle_time": ("card_id", group_by or "card_id", "cycle_time_days", "done_at"),
        "aging": ("card_id", group_by or "card_id", "age_days", "condition", "state"),
    }
    metric_columns = tuple(dict.fromkeys(metric_column_map[metric]))
    rows_source = store.load_metric_rows(
        payload["snapshot"], filters, candidate_ids, metric_columns
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    matched_cards = 0
    for row in rows_source:
        matched_cards += 1
        row_payload = dict(row)
        grouped[_group_label(row_payload, group_by)].append(row_payload)

    rows: list[dict[str, Any]] = []
    for group_value, group_records in sorted(grouped.items()):
        if metric == "count":
            rows.append({"group": group_value, "value": len(group_records)})
            continue
        if metric == "wip":
            count = sum(
                1 for record in group_records if record["condition"] == 1 and record["state"] != 3
            )
            rows.append({"group": group_value, "value": count, "as_of": _iso_timestamp(cutoff)})
            continue
        if metric == "throughput":
            count = 0
            for record in group_records:
                if _metric_done_in_window(_parse_timestamp(record["done_at"]), snapshot):
                    count += 1
            rows.append({"group": group_value, "value": count, "window": snapshot["window"]})
            continue
        if metric == "lead_time":
            durations = []
            for record in group_records:
                done_at = _parse_timestamp(record["done_at"])
                duration = record.get("lead_time_days")
                if (
                    done_at is None
                    or duration is None
                    or not _metric_done_in_window(done_at, snapshot)
                ):
                    continue
                durations.append(float(duration))
            rows.append({"group": group_value, "stats": _duration_stats(durations)})
            continue
        if metric == "cycle_time":
            durations = []
            for record in group_records:
                done_at = _parse_timestamp(record["done_at"])
                duration = record.get("cycle_time_days")
                if (
                    done_at is None
                    or duration is None
                    or not _metric_done_in_window(done_at, snapshot)
                ):
                    continue
                durations.append(float(duration))
            rows.append({"group": group_value, "stats": _duration_stats(durations)})
            continue
        if metric == "aging":
            ages = []
            for record in group_records:
                if record["condition"] != 1 or record["state"] == 3:
                    continue
                age_days = record.get("age_days")
                if age_days is None:
                    continue
                ages.append(float(age_days))
            rows.append(
                {
                    "group": group_value,
                    "stats": _duration_stats(ages),
                    "as_of": _iso_timestamp(cutoff),
                }
            )
            continue

    return {
        "snapshot": snapshot["name"],
        "metric": metric,
        "group_by": group_by,
        "rows": rows,
        "meta": {
            "matched_cards": matched_cards,
            "window": snapshot["window"],
            "built_at": snapshot["built_at"],
        },
    }
