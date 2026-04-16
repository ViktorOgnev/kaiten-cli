"""Persistent local snapshots and local-only query helpers."""

from __future__ import annotations

import json
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.models import CACHE_POLICY_REQUEST_SCOPE
from kaiten_cli.runtime.support.audit import (
    DEFAULT_HISTORY_WORKERS,
    fetch_all_space_activity,
    fetch_card_location_histories,
)
from kaiten_cli.runtime.support.cards import fetch_all_cards, fetch_cards_batch_get
from kaiten_cli.runtime.support.relations import fetch_card_children_batch, fetch_comments_batch
from kaiten_cli.runtime.support.spaces import fetch_space_topology
from kaiten_cli.runtime.support.time_logs import fetch_time_logs_batch
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


def snapshot_db_path() -> Path:
    return user_data_path("kaiten-cli") / "snapshots.sqlite3"


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
        "retry_count": stats.retry_count,
        "request_cache_hits": stats.request_cache_hits,
        "request_cache_misses": stats.request_cache_misses,
        "inflight_dedup_hits": stats.inflight_dedup_hits,
        "disk_cache_hits": stats.disk_cache_hits,
        "disk_cache_misses": stats.disk_cache_misses,
        "disk_cache_expired": stats.disk_cache_expired,
        "disk_cache_bypasses": stats.disk_cache_bypasses,
    }


def _stats_delta(after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
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
        key=lambda row: (str(row.get("changed", "")), int(row.get("column_id") or 0), int(row.get("lane_id") or 0)),
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


def _within_window(changed: datetime | None, window_start: datetime | None, window_end: datetime | None) -> bool:
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
        if isinstance(row, dict) and _within_window(_time_log_timestamp(row), window_start, window_end)
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


class SnapshotStore:
    def __init__(self, path: Path | None = None, reporter=None):
        self.path = path or snapshot_db_path()
        self.reporter = reporter

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _open_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _close_quietly(self, conn: sqlite3.Connection | None) -> None:
        if conn is None:
            return
        try:
            conn.close()
        except sqlite3.Error:
            return

    def _reset_error(self, action: str) -> ConfigError:
        return ConfigError(f"Unable to {action} local snapshot store at {self.path}. Remove the file and retry.")

    def _reset_store(self, reason: str) -> sqlite3.Connection:
        self._debug(f"snapshot: local store dropped store=snapshots reason={reason}")
        try:
            self.path.unlink(missing_ok=True)
        except OSError as exc:
            raise self._reset_error("reset") from exc
        conn: sqlite3.Connection | None = None
        try:
            conn = self._open_connection()
            self._initialize_schema(conn)
            self._debug("snapshot: local store recreated store=snapshots")
            return conn
        except sqlite3.Error as exc:
            self._close_quietly(conn)
            raise self._reset_error("recreate") from exc

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.path.exists()
        conn: sqlite3.Connection | None = None
        try:
            conn = self._open_connection()
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if existing and version != SNAPSHOT_DB_SCHEMA_VERSION:
                self._close_quietly(conn)
                return self._reset_store(f"incompatible-schema:{version}")
            self._initialize_schema(conn)
            return conn
        except sqlite3.Error as exc:
            self._close_quietly(conn)
            return self._reset_store(type(exc).__name__)

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                name TEXT PRIMARY KEY,
                profile_name TEXT,
                domain TEXT,
                space_id INTEGER NOT NULL,
                board_ids_json TEXT NOT NULL,
                preset TEXT NOT NULL,
                window_start TEXT,
                window_end TEXT,
                schema_version INTEGER NOT NULL DEFAULT 2,
                built_at TEXT NOT NULL,
                spec_json TEXT NOT NULL,
                dataset_counts_json TEXT NOT NULL,
                build_trace_json TEXT NOT NULL
            )
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(snapshots)").fetchall()}
        if "schema_version" not in columns:
            conn.execute("ALTER TABLE snapshots ADD COLUMN schema_version INTEGER NOT NULL DEFAULT 2")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_cards (
                snapshot_name TEXT NOT NULL,
                card_id INTEGER NOT NULL,
                board_id INTEGER,
                column_id INTEGER,
                lane_id INTEGER,
                type_id INTEGER,
                owner_id INTEGER,
                responsible_id INTEGER,
                state INTEGER,
                condition INTEGER,
                created TEXT,
                updated TEXT,
                last_moved_to_done_at TEXT,
                has_children INTEGER NOT NULL DEFAULT 0,
                has_comments INTEGER NOT NULL DEFAULT 0,
                children_count INTEGER NOT NULL DEFAULT 0,
                comments_count INTEGER NOT NULL DEFAULT 0,
                time_spent_total_minutes INTEGER NOT NULL DEFAULT 0,
                last_time_log_at TEXT,
                latest_column_id INTEGER,
                latest_lane_id INTEGER,
                current_stage_entered_at TEXT,
                commitment_at TEXT,
                work_started_at TEXT,
                done_at TEXT,
                age_days REAL,
                lead_time_days REAL,
                cycle_time_days REAL,
                tag_ids_json TEXT NOT NULL,
                search_text TEXT NOT NULL,
                child_text TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                card_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, card_id),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_boards (
                snapshot_name TEXT NOT NULL,
                board_id INTEGER NOT NULL,
                board_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, board_id),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_columns (
                snapshot_name TEXT NOT NULL,
                board_id INTEGER NOT NULL,
                column_id INTEGER NOT NULL,
                title TEXT,
                column_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, column_id),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_lanes (
                snapshot_name TEXT NOT NULL,
                board_id INTEGER NOT NULL,
                lane_id INTEGER NOT NULL,
                title TEXT,
                lane_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, lane_id),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_activity (
                snapshot_name TEXT NOT NULL,
                row_index INTEGER NOT NULL,
                created TEXT,
                activity_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, row_index),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_history (
                snapshot_name TEXT NOT NULL,
                card_id INTEGER NOT NULL,
                row_index INTEGER NOT NULL,
                changed TEXT,
                column_id INTEGER,
                lane_id INTEGER,
                condition INTEGER,
                state INTEGER,
                history_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, card_id, row_index),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_relations (
                snapshot_name TEXT NOT NULL,
                parent_card_id INTEGER NOT NULL,
                child_card_id INTEGER NOT NULL,
                relation_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, parent_card_id, child_card_id),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_comments (
                snapshot_name TEXT NOT NULL,
                card_id INTEGER NOT NULL,
                row_index INTEGER NOT NULL,
                comment_id TEXT,
                text TEXT,
                comment_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, card_id, row_index),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_time_logs (
                snapshot_name TEXT NOT NULL,
                card_id INTEGER NOT NULL,
                row_index INTEGER NOT NULL,
                time_log_id TEXT,
                created TEXT,
                for_date TEXT,
                time_spent INTEGER,
                comment TEXT,
                time_log_json TEXT NOT NULL,
                PRIMARY KEY (snapshot_name, card_id, row_index),
                FOREIGN KEY (snapshot_name) REFERENCES snapshots(name) ON DELETE CASCADE
            )
            """
        )
        card_columns = {row["name"] for row in conn.execute("PRAGMA table_info(snapshot_cards)").fetchall()}
        card_alter_statements = {
            "children_count": "ALTER TABLE snapshot_cards ADD COLUMN children_count INTEGER NOT NULL DEFAULT 0",
            "comments_count": "ALTER TABLE snapshot_cards ADD COLUMN comments_count INTEGER NOT NULL DEFAULT 0",
            "time_spent_total_minutes": "ALTER TABLE snapshot_cards ADD COLUMN time_spent_total_minutes INTEGER NOT NULL DEFAULT 0",
            "last_time_log_at": "ALTER TABLE snapshot_cards ADD COLUMN last_time_log_at TEXT",
            "age_days": "ALTER TABLE snapshot_cards ADD COLUMN age_days REAL",
            "lead_time_days": "ALTER TABLE snapshot_cards ADD COLUMN lead_time_days REAL",
            "cycle_time_days": "ALTER TABLE snapshot_cards ADD COLUMN cycle_time_days REAL",
        }
        for column_name, statement in card_alter_statements.items():
            if column_name not in card_columns:
                conn.execute(statement)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_board ON snapshot_cards(snapshot_name, board_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_column ON snapshot_cards(snapshot_name, column_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_lane ON snapshot_cards(snapshot_name, lane_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_state ON snapshot_cards(snapshot_name, state)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_condition ON snapshot_cards(snapshot_name, condition)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_done ON snapshot_cards(snapshot_name, done_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_cards_last_time_log ON snapshot_cards(snapshot_name, last_time_log_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_history_changed ON snapshot_history(snapshot_name, changed)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshot_time_logs_created ON snapshot_time_logs(snapshot_name, created)"
        )
        try:
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS snapshot_card_search
                USING fts5(
                    snapshot_name UNINDEXED,
                    card_id UNINDEXED,
                    search_text,
                    child_text,
                    comment_text
                )
                """
            )
        except sqlite3.OperationalError:
            pass
        conn.execute(f"PRAGMA user_version = {SNAPSHOT_DB_SCHEMA_VERSION}")
        conn.commit()

    def list_snapshots(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT name, profile_name, domain, space_id, preset, window_start, window_end, built_at, dataset_counts_json
                     , schema_version
                FROM snapshots
                ORDER BY name
                """
            ).fetchall()
        return [
            {
                "name": row["name"],
                "profile_name": row["profile_name"],
                "domain": row["domain"],
                "space_id": row["space_id"],
                "preset": row["preset"],
                "window": {"start": row["window_start"], "end": row["window_end"]},
                "schema_version": row["schema_version"],
                "built_at": row["built_at"],
                "datasets": json.loads(row["dataset_counts_json"]),
            }
            for row in rows
        ]

    def get_snapshot(self, name: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT name, profile_name, domain, space_id, board_ids_json, preset, window_start, window_end,
                       schema_version,
                       built_at, spec_json, dataset_counts_json, build_trace_json
                FROM snapshots
                WHERE name = ?
                """,
                (name,),
            ).fetchone()
        if row is None:
            raise ConfigError(f"Unknown snapshot: {name}")
        built_at = _parse_timestamp(row["built_at"])
        now = datetime.now(timezone.utc)
        staleness_seconds = None
        if built_at is not None:
            staleness_seconds = max(0, int((now - built_at).total_seconds()))
        return {
            "name": row["name"],
            "profile_name": row["profile_name"],
            "domain": row["domain"],
            "space_id": row["space_id"],
            "board_ids": json.loads(row["board_ids_json"]),
            "preset": row["preset"],
            "window": {"start": row["window_start"], "end": row["window_end"]},
            "schema_version": row["schema_version"],
            "built_at": row["built_at"],
            "spec": json.loads(row["spec_json"]),
            "datasets": json.loads(row["dataset_counts_json"]),
            "last_build_trace": json.loads(row["build_trace_json"]),
            "staleness_seconds": staleness_seconds,
        }

    def delete_snapshot(self, name: str) -> dict[str, Any]:
        with self._connect() as conn:
            deleted = conn.execute("DELETE FROM snapshots WHERE name = ?", (name,)).rowcount
            try:
                conn.execute("DELETE FROM snapshot_card_search WHERE snapshot_name = ?", (name,))
            except sqlite3.OperationalError:
                pass
            conn.commit()
        if not deleted:
            raise ConfigError(f"Unknown snapshot: {name}")
        return {"name": name, "deleted": True}

    def replace_snapshot(
        self,
        *,
        name: str,
        profile_name: str | None,
        domain: str,
        space_id: int,
        board_ids: list[int],
        preset: str,
        window_start: str | None,
        window_end: str | None,
        spec: dict[str, Any],
        dataset_counts: dict[str, int],
        build_trace: dict[str, Any],
        topology: dict[str, Any],
        cards: list[dict[str, Any]],
        history_map: dict[int, list[dict[str, Any]]],
        children_map: dict[int, list[dict[str, Any]]],
        comments_map: dict[int, list[dict[str, Any]]],
        time_logs_map: dict[int, list[dict[str, Any]]],
        activity_rows: list[dict[str, Any]],
    ) -> None:
        built_at = _now_iso()
        built_at_dt = _parse_timestamp(built_at)
        window_start_dt = _parse_timestamp(window_start)
        window_end_dt = _parse_timestamp(window_end)
        cutoff_dt = window_end_dt or built_at_dt or datetime.now(timezone.utc)
        card_rows: list[tuple[Any, ...]] = []
        relation_rows: list[tuple[Any, ...]] = []
        comment_rows: list[tuple[Any, ...]] = []
        history_rows: list[tuple[Any, ...]] = []
        time_log_rows: list[tuple[Any, ...]] = []
        search_rows: list[tuple[str, int, str, str, str]] = []

        for card in cards:
            if not isinstance(card, dict) or "id" not in card:
                continue
            card_id = int(card["id"])
            history = history_map.get(card_id, [])
            children = children_map.get(card_id, [])
            comments = comments_map.get(card_id, [])
            time_logs = _filter_time_logs_to_window(
                time_logs_map.get(card_id, []),
                window_start=window_start_dt,
                window_end=window_end_dt,
            )
            type_id = card.get("type_id")
            if type_id is None and isinstance(card.get("type"), dict):
                type_id = card["type"].get("id")
            owner_id = card.get("owner_id")
            if owner_id is None and isinstance(card.get("owner"), dict):
                owner_id = card["owner"].get("id")
            responsible_id = card.get("responsible_id")
            if responsible_id is None and isinstance(card.get("responsible"), dict):
                responsible_id = card["responsible"].get("id")

            child_titles = [str(item.get("title", "")) for item in children if isinstance(item, dict)]
            comment_texts = [str(item.get("text", "")) for item in comments if isinstance(item, dict)]
            search_text = _search_blob([str(card.get("title", "")), str(card.get("description", ""))])
            child_text = _search_blob(child_titles)
            comment_text = _search_blob(comment_texts)
            done_at = _derive_done_at(card, history)
            work_started_at = _first_history_with_state(history, 2)
            current_stage_entered_at = _current_stage_entered_at(history)
            latest = history[-1] if history else {}
            latest_column_id = latest.get("column_id", card.get("column_id"))
            latest_lane_id = latest.get("lane_id", card.get("lane_id"))
            last_time_log_at = None
            time_spent_total_minutes = 0
            for item in time_logs:
                if not isinstance(item, dict):
                    continue
                time_spent_total_minutes += _time_log_minutes(item)
                changed = _time_log_timestamp(item)
                if changed is not None and (last_time_log_at is None or changed > last_time_log_at):
                    last_time_log_at = changed
            age_anchor = current_stage_entered_at or _parse_timestamp(card.get("updated")) or _parse_timestamp(card.get("created"))
            age_days = None
            if card.get("condition") == 1 and card.get("state") != 3:
                age_days = _duration_days(age_anchor, cutoff_dt)
            lead_time_days = _duration_days(_parse_timestamp(card.get("created")), done_at)
            cycle_time_days = _duration_days(work_started_at, done_at)

            derived = {
                "has_children": bool(children),
                "has_comments": bool(comments),
                "children_count": len(children),
                "comments_count": len(comments),
                "time_spent_total_minutes": time_spent_total_minutes,
                "last_time_log_at": _iso_timestamp(last_time_log_at),
                "latest_stage": {"column_id": latest_column_id, "lane_id": latest_lane_id},
                "latest_column_id": latest_column_id,
                "latest_lane_id": latest_lane_id,
                "search_text": search_text,
                "child_text": child_text,
                "comment_text": comment_text,
                "current_stage_entered_at": _iso_timestamp(current_stage_entered_at),
                "commitment_at": None,
                "work_started_at": _iso_timestamp(work_started_at),
                "done_at": _iso_timestamp(done_at),
                "age_days": age_days,
                "lead_time_days": lead_time_days,
                "cycle_time_days": cycle_time_days,
            }
            card_rows.append(
                (
                    name,
                    card_id,
                    card.get("board_id"),
                    card.get("column_id"),
                    card.get("lane_id"),
                    type_id,
                    owner_id,
                    responsible_id,
                    card.get("state"),
                    card.get("condition"),
                    card.get("created"),
                    card.get("updated"),
                    card.get("last_moved_to_done_at"),
                    1 if children else 0,
                    1 if comments else 0,
                    len(children),
                    len(comments),
                    time_spent_total_minutes,
                    derived["last_time_log_at"],
                    latest_column_id,
                    latest_lane_id,
                    derived["current_stage_entered_at"],
                    derived["commitment_at"],
                    derived["work_started_at"],
                    derived["done_at"],
                    derived["age_days"],
                    derived["lead_time_days"],
                    derived["cycle_time_days"],
                    json.dumps(_extract_tag_ids(card), ensure_ascii=False, separators=(",", ":")),
                    search_text,
                    child_text,
                    comment_text,
                    json.dumps(card, ensure_ascii=False, separators=(",", ":")),
                )
            )
            search_rows.append((name, card_id, search_text, child_text, comment_text))
            for child in children:
                if not isinstance(child, dict):
                    continue
                child_id = _extract_id(child)
                if child_id is None:
                    continue
                relation_rows.append(
                    (
                        name,
                        card_id,
                        child_id,
                        json.dumps(child, ensure_ascii=False, separators=(",", ":")),
                    )
                )
            for index, comment in enumerate(comments):
                if not isinstance(comment, dict):
                    continue
                comment_rows.append(
                    (
                        name,
                        card_id,
                        index,
                        str(comment.get("id")) if comment.get("id") is not None else None,
                        str(comment.get("text", "")),
                        json.dumps(comment, ensure_ascii=False, separators=(",", ":")),
                    )
                )
            for index, row in enumerate(history):
                history_rows.append(
                    (
                        name,
                        card_id,
                        index,
                        row.get("changed"),
                        row.get("column_id"),
                        row.get("lane_id"),
                        row.get("condition"),
                        row.get("state"),
                        json.dumps(row, ensure_ascii=False, separators=(",", ":")),
                    )
                )
            for index, time_log in enumerate(time_logs):
                if not isinstance(time_log, dict):
                    continue
                time_log_rows.append(
                    (
                        name,
                        card_id,
                        index,
                        str(time_log.get("id")) if time_log.get("id") is not None else None,
                        _iso_timestamp(_time_log_timestamp(time_log)),
                        str(time_log.get("for_date") or time_log.get("forDate") or "") or None,
                        _time_log_minutes(time_log),
                        str(time_log.get("comment", "")),
                        json.dumps(time_log, ensure_ascii=False, separators=(",", ":")),
                    )
                )

        board_rows: list[tuple[Any, ...]] = []
        column_rows: list[tuple[Any, ...]] = []
        lane_rows: list[tuple[Any, ...]] = []
        for board in topology.get("boards", []):
            if not isinstance(board, dict) or "id" not in board:
                continue
            board_rows.append((name, board["id"], json.dumps(board, ensure_ascii=False, separators=(",", ":"))))
            for column in board.get("columns", []):
                if isinstance(column, dict) and "id" in column:
                    column_rows.append(
                        (
                            name,
                            board["id"],
                            column["id"],
                            column.get("title"),
                            json.dumps(column, ensure_ascii=False, separators=(",", ":")),
                        )
                    )
            for lane in board.get("lanes", []):
                if isinstance(lane, dict) and "id" in lane:
                    lane_rows.append(
                        (
                            name,
                            board["id"],
                            lane["id"],
                            lane.get("title"),
                            json.dumps(lane, ensure_ascii=False, separators=(",", ":")),
                        )
                    )

        activity_insert_rows = [
            (
                name,
                index,
                row.get("created") if isinstance(row, dict) else None,
                json.dumps(row, ensure_ascii=False, separators=(",", ":")),
            )
            for index, row in enumerate(activity_rows)
            if isinstance(row, dict)
        ]

        with self._connect() as conn:
            conn.execute("DELETE FROM snapshots WHERE name = ?", (name,))
            try:
                conn.execute("DELETE FROM snapshot_card_search WHERE snapshot_name = ?", (name,))
            except sqlite3.OperationalError:
                pass
            conn.execute(
                """
                INSERT INTO snapshots (
                    name, profile_name, domain, space_id, board_ids_json, preset, window_start, window_end,
                    schema_version, built_at, spec_json, dataset_counts_json, build_trace_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    profile_name,
                    domain,
                    space_id,
                    json.dumps(board_ids, ensure_ascii=False, separators=(",", ":")),
                    preset,
                    window_start,
                    window_end,
                    SNAPSHOT_SCHEMA_VERSION,
                    built_at,
                    json.dumps(spec, ensure_ascii=False, separators=(",", ":")),
                    json.dumps(dataset_counts, ensure_ascii=False, separators=(",", ":")),
                    json.dumps(build_trace, ensure_ascii=False, separators=(",", ":")),
                ),
            )
            if board_rows:
                conn.executemany(
                    "INSERT INTO snapshot_boards (snapshot_name, board_id, board_json) VALUES (?, ?, ?)",
                    board_rows,
                )
            if column_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_columns (snapshot_name, board_id, column_id, title, column_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    column_rows,
                )
            if lane_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_lanes (snapshot_name, board_id, lane_id, title, lane_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    lane_rows,
                )
            if card_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_cards (
                        snapshot_name, card_id, board_id, column_id, lane_id, type_id, owner_id, responsible_id,
                        state, condition, created, updated, last_moved_to_done_at, has_children, has_comments,
                        children_count, comments_count, time_spent_total_minutes, last_time_log_at,
                        latest_column_id, latest_lane_id, current_stage_entered_at, commitment_at, work_started_at,
                        done_at, age_days, lead_time_days, cycle_time_days, tag_ids_json, search_text, child_text,
                        comment_text, card_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    card_rows,
                )
            if history_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_history (
                        snapshot_name, card_id, row_index, changed, column_id, lane_id, condition, state, history_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    history_rows,
                )
            if relation_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_relations (snapshot_name, parent_card_id, child_card_id, relation_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    relation_rows,
                )
            if comment_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_comments (snapshot_name, card_id, row_index, comment_id, text, comment_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    comment_rows,
                )
            if time_log_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_time_logs (
                        snapshot_name, card_id, row_index, time_log_id, created, for_date, time_spent, comment, time_log_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    time_log_rows,
                )
            if activity_insert_rows:
                conn.executemany(
                    """
                    INSERT INTO snapshot_activity (snapshot_name, row_index, created, activity_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    activity_insert_rows,
                )
            if search_rows:
                try:
                    conn.executemany(
                        """
                        INSERT INTO snapshot_card_search (snapshot_name, card_id, search_text, child_text, comment_text)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        search_rows,
                    )
                except sqlite3.OperationalError:
                    pass
            conn.commit()

    def _row_to_card_record(self, row: sqlite3.Row) -> dict[str, Any]:
        card = json.loads(row["card_json"])
        derived = {
            "has_children": bool(row["has_children"]),
            "has_comments": bool(row["has_comments"]),
            "children_count": row["children_count"],
            "comments_count": row["comments_count"],
            "time_spent_total_minutes": row["time_spent_total_minutes"],
            "last_time_log_at": row["last_time_log_at"],
            "latest_stage": {"column_id": row["latest_column_id"], "lane_id": row["latest_lane_id"]},
            "latest_column_id": row["latest_column_id"],
            "latest_lane_id": row["latest_lane_id"],
            "search_text": row["search_text"],
            "child_text": row["child_text"],
            "comment_text": row["comment_text"],
            "current_stage_entered_at": row["current_stage_entered_at"],
            "commitment_at": row["commitment_at"],
            "work_started_at": row["work_started_at"],
            "done_at": row["done_at"],
            "age_days": row["age_days"],
            "lead_time_days": row["lead_time_days"],
            "cycle_time_days": row["cycle_time_days"],
        }
        return {
            "card_id": row["card_id"],
            "board_id": row["board_id"],
            "column_id": row["column_id"],
            "lane_id": row["lane_id"],
            "type_id": row["type_id"],
            "owner_id": row["owner_id"],
            "responsible_id": row["responsible_id"],
            "state": row["state"],
            "condition": row["condition"],
            "created": row["created"],
            "updated": row["updated"],
            "done_at": row["done_at"],
            "work_started_at": row["work_started_at"],
            "current_stage_entered_at": row["current_stage_entered_at"],
            "has_children": bool(row["has_children"]),
            "has_comments": bool(row["has_comments"]),
            "children_count": row["children_count"],
            "comments_count": row["comments_count"],
            "time_spent_total_minutes": row["time_spent_total_minutes"],
            "last_time_log_at": row["last_time_log_at"],
            "age_days": row["age_days"],
            "lead_time_days": row["lead_time_days"],
            "cycle_time_days": row["cycle_time_days"],
            "tag_ids": json.loads(row["tag_ids_json"]),
            "search_text": row["search_text"],
            "child_text": row["child_text"],
            "comment_text": row["comment_text"],
            "card": card,
            "derived": derived,
        }

    def load_card_records(self, snapshot_name: str) -> list[dict[str, Any]]:
        self.get_snapshot(snapshot_name)
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM snapshot_cards
                WHERE snapshot_name = ?
                ORDER BY card_id
                """,
                (snapshot_name,),
            ).fetchall()
        return [self._row_to_card_record(row) for row in rows]

    def _build_card_query_parts(
        self,
        snapshot_name: str,
        filters: dict[str, Any],
        candidate_ids: set[int] | None,
        *,
        include_tag_filter: bool,
    ) -> tuple[list[str], list[Any], bool]:
        clauses = ["snapshot_name = ?"]
        params: list[Any] = [snapshot_name]
        fallback_tag_filter = False
        mapping = {
            "board_ids": "board_id",
            "column_ids": "column_id",
            "lane_ids": "lane_id",
            "type_ids": "type_id",
            "owner_ids": "owner_id",
            "responsible_ids": "responsible_id",
            "states": "state",
        }
        for filter_name, column_name in mapping.items():
            values = _normalize_int_list(filters.get(filter_name))
            if values:
                placeholders = ",".join("?" for _ in values)
                clauses.append(f"{column_name} IN ({placeholders})")
                params.extend(values)
        condition_values = _normalize_int_list(filters.get("condition"))
        if condition_values:
            placeholders = ",".join("?" for _ in condition_values)
            clauses.append(f"condition IN ({placeholders})")
            params.extend(condition_values)
        range_filters = (
            ("created_after", "created", ">="),
            ("created_before", "created", "<="),
            ("updated_after", "updated", ">="),
            ("updated_before", "updated", "<="),
        )
        for filter_name, column_name, operator in range_filters:
            value = filters.get(filter_name)
            if value:
                clauses.append(f"{column_name} {operator} ?")
                params.append(value)
        for filter_name, column_name in (("has_children", "has_children"), ("has_comments", "has_comments")):
            value = _normalize_bool(filters.get(filter_name))
            if value is not None:
                clauses.append(f"{column_name} = ?")
                params.append(1 if value else 0)
        if candidate_ids is not None:
            if not candidate_ids:
                clauses.append("1 = 0")
            else:
                ordered_ids = sorted(candidate_ids)
                placeholders = ",".join("?" for _ in ordered_ids)
                clauses.append(f"card_id IN ({placeholders})")
                params.extend(ordered_ids)
        if include_tag_filter:
            tag_ids = _normalize_int_list(filters.get("tag_ids"))
            if tag_ids:
                placeholders = ",".join("?" for _ in tag_ids)
                clauses.append(
                    "EXISTS (SELECT 1 FROM json_each(snapshot_cards.tag_ids_json) WHERE json_each.value IN "
                    f"({placeholders}))"
                )
                params.extend(tag_ids)
                fallback_tag_filter = True
        return clauses, params, fallback_tag_filter

    def query_card_records(
        self,
        snapshot_name: str,
        filters: dict[str, Any],
        candidate_ids: set[int] | None,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        self.get_snapshot(snapshot_name)
        clauses, params, fallback_tag_filter = self._build_card_query_parts(
            snapshot_name,
            filters,
            candidate_ids,
            include_tag_filter=True,
        )
        where_sql = " AND ".join(clauses)
        with self._connect() as conn:
            try:
                total = int(
                    conn.execute(
                        f"SELECT COUNT(*) AS total FROM snapshot_cards WHERE {where_sql}",
                        params,
                    ).fetchone()["total"]
                )
                rows = conn.execute(
                    f"""
                    SELECT *
                    FROM snapshot_cards
                    WHERE {where_sql}
                    ORDER BY card_id
                    LIMIT ? OFFSET ?
                    """,
                    [*params, limit, offset],
                ).fetchall()
                return [self._row_to_card_record(row) for row in rows], total
            except sqlite3.OperationalError:
                if not fallback_tag_filter:
                    raise
                fallback_clauses, fallback_params, _ = self._build_card_query_parts(
                    snapshot_name,
                    {**filters, "tag_ids": None},
                    candidate_ids,
                    include_tag_filter=False,
                )
                fallback_where_sql = " AND ".join(fallback_clauses)
                rows = conn.execute(
                    f"""
                    SELECT *
                    FROM snapshot_cards
                    WHERE {fallback_where_sql}
                    ORDER BY card_id
                    """,
                    fallback_params,
                ).fetchall()
        matched = [
            record
            for record in (self._row_to_card_record(row) for row in rows)
            if not _normalize_int_list(filters.get("tag_ids"))
            or (set(record["tag_ids"]) & set(_normalize_int_list(filters.get("tag_ids"))))
        ]
        return matched[offset : offset + limit], len(matched)

    def load_metric_rows(
        self,
        snapshot_name: str,
        filters: dict[str, Any],
        candidate_ids: set[int] | None,
        columns: tuple[str, ...],
    ) -> list[sqlite3.Row]:
        self.get_snapshot(snapshot_name)
        clauses, params, fallback_tag_filter = self._build_card_query_parts(
            snapshot_name,
            filters,
            candidate_ids,
            include_tag_filter=True,
        )
        where_sql = " AND ".join(clauses)
        selected_columns = ", ".join(columns)
        with self._connect() as conn:
            try:
                return conn.execute(
                    f"""
                    SELECT {selected_columns}
                    FROM snapshot_cards
                    WHERE {where_sql}
                    ORDER BY card_id
                    """,
                    params,
                ).fetchall()
            except sqlite3.OperationalError:
                if not fallback_tag_filter:
                    raise
                fallback_clauses, fallback_params, _ = self._build_card_query_parts(
                    snapshot_name,
                    {**filters, "tag_ids": None},
                    candidate_ids,
                    include_tag_filter=False,
                )
                fallback_where_sql = " AND ".join(fallback_clauses)
                rows = conn.execute(
                    f"""
                    SELECT {selected_columns}, tag_ids_json
                    FROM snapshot_cards
                    WHERE {fallback_where_sql}
                    ORDER BY card_id
                    """,
                    fallback_params,
                ).fetchall()
        tag_ids = set(_normalize_int_list(filters.get("tag_ids")))
        return [
            row
            for row in rows
            if set(json.loads(row["tag_ids_json"])) & tag_ids
        ]

    def text_candidate_card_ids(self, snapshot_name: str, field: str, text: str) -> set[int]:
        self.get_snapshot(snapshot_name)
        lowered = text.strip().lower()
        if not lowered:
            return set()
        column_map = {
            "search_text": "search_text",
            "child_text": "child_text",
            "comment_text": "comment_text",
        }
        column = column_map[field]
        with self._connect() as conn:
            try:
                tokens = " ".join(part for part in lowered.split() if part)
                if tokens:
                    rows = conn.execute(
                        f"""
                        SELECT card_id
                        FROM snapshot_card_search
                        WHERE snapshot_name = ? AND {column} MATCH ?
                        """,
                        (snapshot_name, tokens),
                    ).fetchall()
                    if rows:
                        return {int(row["card_id"]) for row in rows}
            except sqlite3.OperationalError:
                pass
            rows = conn.execute(
                f"""
                SELECT card_id
                FROM snapshot_cards
                WHERE snapshot_name = ? AND lower({column}) LIKE ?
                """,
                (snapshot_name, f"%{lowered}%"),
            ).fetchall()
        return {int(row["card_id"]) for row in rows}


def _validate_snapshot_build_payload(payload: dict[str, Any]) -> None:
    preset = payload.get("preset", "basic")
    if preset not in SNAPSHOT_PRESETS:
        allowed = ", ".join(sorted(SNAPSHOT_PRESETS))
        raise ValidationError(f"Field preset must be one of: {allowed}.")
    if preset in WINDOW_PRESETS:
        if not payload.get("window_start") or not payload.get("window_end"):
            raise ValidationError("Fields window_start and window_end are required for analytics and full snapshots.")
    start = _parse_timestamp(payload.get("window_start"))
    end = _parse_timestamp(payload.get("window_end"))
    if start is not None and end is not None and start > end:
        raise ValidationError("window_start must be <= window_end.")
    board_ids = payload.get("board_ids")
    if board_ids is not None and (not isinstance(board_ids, list) or not board_ids):
        raise ValidationError("Field board_ids must be a non-empty array when provided.")


def validate_snapshot_build(tool, payload: dict[str, Any]) -> None:
    _validate_snapshot_build_payload(payload)


def validate_query_filter(tool, payload: dict[str, Any]) -> None:
    filter_payload = payload.get("filter")
    if filter_payload is None:
        return
    if not isinstance(filter_payload, dict):
        raise ValidationError("Field filter must be an object.")
    unknown = sorted(set(filter_payload) - QUERY_FILTER_KEYS)
    if unknown:
        raise ValidationError(f"Unknown query filter field(s): {', '.join(unknown)}")


def _board_ids_for_snapshot(topology: dict[str, Any], requested_board_ids: list[int] | None) -> list[int]:
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


async def _fetch_snapshot_cards(client, space_id: int, board_ids: list[int], *, timeout: float) -> list[dict[str, Any]]:
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
            mapping[int(item["card_id"])] = [row for row in item.get("children", []) if isinstance(row, dict)]
    return mapping, len(result.get("errors", []))


def _comments_map(result: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], int]:
    mapping: dict[int, list[dict[str, Any]]] = {}
    for item in result.get("items", []):
        if isinstance(item, dict) and "card_id" in item:
            mapping[int(item["card_id"])] = [row for row in item.get("comments", []) if isinstance(row, dict)]
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
            mapping[int(item["card_id"])] = [row for row in item.get("time_logs", []) if isinstance(row, dict)]
    return mapping, len(result.get("errors", []))


def _merge_card_details(cards: list[dict[str, Any]], details_map: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
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
                cache_policy=CACHE_POLICY_REQUEST_SCOPE,
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
                cache_policy=CACHE_POLICY_REQUEST_SCOPE,
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
                cache_policy=CACHE_POLICY_REQUEST_SCOPE,
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
                cache_policy=CACHE_POLICY_REQUEST_SCOPE,
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
                cache_policy=CACHE_POLICY_REQUEST_SCOPE,
            ),
        )
        comments_map, dataset_errors["comment_errors"] = _comments_map(comments_result)
        comments_stage["rows"] = sum(len(rows) for rows in comments_map.values())
        comments_stage["errors"] = dataset_errors["comment_errors"]
        stages.extend([relations_stage, comments_stage])

    dataset_counts = {
        "boards": len(topology.get("boards", [])),
        "columns": sum(len(board.get("columns", [])) for board in topology.get("boards", []) if isinstance(board, dict)),
        "lanes": sum(len(board.get("lanes", [])) for board in topology.get("boards", []) if isinstance(board, dict)),
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
    return await _build_snapshot(client=client, payload=payload, reporter=reporter, timeout=timeout, spec=spec)


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
    existing = store.get_snapshot(payload["name"])
    if existing["domain"] and existing["domain"] != client.domain:
        raise ConfigError(
            f"Snapshot {payload['name']} was built for domain {existing['domain']}, current profile uses {client.domain}."
        )
    spec = dict(existing["spec"])
    if reporter is not None:
        reporter(f"execution: local snapshot refresh name={spec['name']}")
    return await _build_snapshot(client=client, payload=payload, reporter=reporter, timeout=timeout, spec=spec)


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


def _text_candidate_ids(store: SnapshotStore, snapshot_name: str, filters: dict[str, Any]) -> set[int] | None:
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
    metric_columns = tuple(
        dict.fromkeys(metric_column_map[metric])
    )
    rows_source = store.load_metric_rows(payload["snapshot"], filters, candidate_ids, metric_columns)
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
            count = sum(1 for record in group_records if record["condition"] == 1 and record["state"] != 3)
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
                if done_at is None or duration is None or not _metric_done_in_window(done_at, snapshot):
                    continue
                durations.append(float(duration))
            rows.append({"group": group_value, "stats": _duration_stats(durations)})
            continue
        if metric == "cycle_time":
            durations = []
            for record in group_records:
                done_at = _parse_timestamp(record["done_at"])
                duration = record.get("cycle_time_days")
                if done_at is None or duration is None or not _metric_done_in_window(done_at, snapshot):
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
            rows.append({"group": group_value, "stats": _duration_stats(ages), "as_of": _iso_timestamp(cutoff)})
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
