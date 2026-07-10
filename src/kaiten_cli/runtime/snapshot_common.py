"""Shared snapshot constants and pure transformation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.transforms import compact_response, select_fields, strip_base64

SNAPSHOT_PRESETS = {"basic", "analytics", "evidence", "full"}
WINDOW_PRESETS = {"analytics", "full"}
QUERY_METRICS = {"count", "wip", "throughput", "lead_time", "cycle_time", "aging"}
QUERY_GROUP_BY = {
    "board_id",
    "column_id",
    "lane_id",
    "type_id",
    "owner_id",
    "responsible_id",
    "state",
    "condition",
}
QUERY_FILTER_KEYS = {
    "board_ids",
    "column_ids",
    "lane_ids",
    "type_ids",
    "tag_ids",
    "owner_ids",
    "responsible_ids",
    "states",
    "condition",
    "created_after",
    "created_before",
    "updated_after",
    "updated_before",
    "has_children",
    "has_comments",
    "text_query",
    "child_text_query",
    "comment_text_query",
}
DEFAULT_LOCAL_LIMIT = 100
SNAPSHOT_SCHEMA_VERSION = 2
SNAPSHOT_DB_SCHEMA_VERSION = 1
QUERY_CARD_VIEWS = {"summary", "detail", "evidence"}

SUMMARY_VIEW_FIELDS = (
    "id",
    "title",
    "board_id",
    "column_id",
    "lane_id",
    "type_id",
    "owner_id",
    "responsible_id",
    "state",
    "condition",
    "created",
    "updated",
    "has_children",
    "has_comments",
    "children_count",
    "comments_count",
    "time_spent_total_minutes",
    "last_time_log_at",
    "current_stage_entered_at",
    "done_at",
    "age_days",
    "lead_time_days",
    "cycle_time_days",
)
DETAIL_VIEW_FIELDS = SUMMARY_VIEW_FIELDS + (
    "description",
    "tag_ids",
    "latest_stage",
    "latest_column_id",
    "latest_lane_id",
    "work_started_at",
    "commitment_at",
)
EVIDENCE_VIEW_FIELDS = DETAIL_VIEW_FIELDS + (
    "search_text",
    "child_text",
    "comment_text",
)
VIEW_FIELDS = {
    "summary": SUMMARY_VIEW_FIELDS,
    "detail": DETAIL_VIEW_FIELDS,
    "evidence": EVIDENCE_VIEW_FIELDS,
}


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _iso_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _now_iso() -> str:
    return _iso_timestamp(datetime.now(timezone.utc)) or ""


def _stats_snapshot(stats) -> dict[str, int]:
    return {
        "http_request_count": stats.http_request_count,
        "http_response_count": stats.http_response_count,
        "http_error_count": stats.http_error_count,
        "api_wait_ms": stats.api_wait_ms,
        "http_wait_ms": stats.http_wait_ms,
        "retry_count": stats.retry_count,
        "request_cache_hits": stats.request_cache_hits,
        "request_cache_misses": stats.request_cache_misses,
        "inflight_dedup_hits": stats.inflight_dedup_hits,
        "disk_cache_hits": stats.disk_cache_hits,
        "disk_cache_misses": stats.disk_cache_misses,
        "disk_cache_expired": stats.disk_cache_expired,
        "disk_cache_bypasses": stats.disk_cache_bypasses,
    }


def _stats_delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    return {key: after[key] - before.get(key, 0) for key in after}


def _duration_stats(values: list[float]) -> dict[str, Any] | None:
    if not values:
        return None
    ordered = sorted(values)

    def percentile(percent: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        rank = (len(ordered) - 1) * percent
        lower = int(rank)
        upper = min(lower + 1, len(ordered) - 1)
        fraction = rank - lower
        return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction

    return {
        "count": len(ordered),
        "median_days": round(percentile(0.5), 2),
        "p85_days": round(percentile(0.85), 2),
        "max_days": round(ordered[-1], 2),
    }


def _normalize_int_list(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, str):
        raw_items = [item.strip() for item in value.split(",") if item.strip()]
    else:
        raw_items = [value]
    normalized: list[int] = []
    for item in raw_items:
        try:
            normalized.append(int(item))
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid integer list value: {item}") from exc
    return normalized


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ValidationError("Boolean filters must use true or false.")


def _extract_id(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        nested = value.get("id")
        if isinstance(nested, int):
            return nested
    return None


def _extract_tag_ids(card: dict[str, Any]) -> list[int]:
    tags = card.get("tags")
    if not isinstance(tags, list):
        return []
    tag_ids: list[int] = []
    for tag in tags:
        tag_id = _extract_id(tag)
        if tag_id is not None:
            tag_ids.append(tag_id)
    return tag_ids


def _time_log_minutes(entry: dict[str, Any]) -> int:
    for key in ("time_spent", "timeSpent", "minutes"):
        value = entry.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip():
            try:
                return int(value)
            except ValueError:
                continue
    return 0


def _time_log_timestamp(entry: dict[str, Any]) -> datetime | None:
    for key in ("created", "updated", "for_date", "forDate", "date"):
        changed = _parse_timestamp(entry.get(key))
        if changed is not None:
            return changed
    return None


def _search_blob(parts: list[str]) -> str:
    normalized = [part.strip() for part in parts if part and str(part).strip()]
    return "\n".join(normalized)


def _duration_days(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None or start > end:
        return None
    return round((end - start).total_seconds() / 86400, 2)


def _effective_column_id(event: dict[str, Any]) -> int | None:
    for key in ("subcolumn_id", "column_id"):
        value = event.get(key)
        if isinstance(value, int):
            return value
    return None


def _sorted_history(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [row for row in rows if isinstance(row, dict)],
        key=lambda row: (
            str(row.get("changed", "")),
            int(row.get("column_id") or 0),
            int(row.get("lane_id") or 0),
        ),
    )


def _first_history_with_state(history: list[dict[str, Any]], state: int) -> datetime | None:
    for row in history:
        if row.get("state") == state:
            return _parse_timestamp(row.get("changed"))
    return None


def _derive_done_at(card: dict[str, Any], history: list[dict[str, Any]]) -> datetime | None:
    card_done = _parse_timestamp(card.get("last_moved_to_done_at"))
    if card_done is not None:
        return card_done
    latest_done: datetime | None = None
    for row in history:
        changed = _parse_timestamp(row.get("changed"))
        if changed is None:
            continue
        if row.get("state") == 3:
            latest_done = changed
    return latest_done


def _current_stage_entered_at(history: list[dict[str, Any]]) -> datetime | None:
    if not history:
        return None
    latest = history[-1]
    latest_column = _effective_column_id(latest)
    latest_lane = latest.get("lane_id")
    latest_condition = latest.get("condition")
    latest_state = latest.get("state")
    for row in reversed(history):
        if (
            _effective_column_id(row) != latest_column
            or row.get("lane_id") != latest_lane
            or row.get("condition") != latest_condition
            or row.get("state") != latest_state
        ):
            break
        changed = _parse_timestamp(row.get("changed"))
        if changed is not None:
            return changed
    return _parse_timestamp(latest.get("changed"))


def _within_window(
    changed: datetime | None, window_start: datetime | None, window_end: datetime | None
) -> bool:
    if changed is None:
        return False
    if window_start is not None and changed < window_start:
        return False
    if window_end is not None and changed > window_end:
        return False
    return True


def _filter_time_logs_to_window(
    time_logs: list[dict[str, Any]],
    *,
    window_start: datetime | None,
    window_end: datetime | None,
) -> list[dict[str, Any]]:
    if window_start is None and window_end is None:
        return [row for row in time_logs if isinstance(row, dict)]
    return [
        row
        for row in time_logs
        if isinstance(row, dict)
        and _within_window(_time_log_timestamp(row), window_start, window_end)
    ]


def _view_fields(view: str, fields: str | None) -> str | None:
    if fields:
        return fields
    return ",".join(VIEW_FIELDS[view])


def _shape_card_for_output(
    record: dict[str, Any],
    *,
    view: str,
    compact: bool,
    fields: str | None,
) -> dict[str, Any]:
    payload = dict(record["card"])
    payload.update(record["derived"])
    view_field_names = VIEW_FIELDS[view]
    payload = {field: payload[field] for field in view_field_names if field in payload}
    shaped = compact_response(payload, compact)
    shaped = select_fields(shaped, _view_fields(view, fields))
    shaped, _ = strip_base64(shaped)
    return shaped
