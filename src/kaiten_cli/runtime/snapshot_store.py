"""SQLite schema and persistence for local Kaiten snapshots."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from kaiten_cli.errors import ConfigError
from kaiten_cli.runtime.fs_security import (
    ensure_private_file,
    secure_directory,
    secure_existing_file,
)
from kaiten_cli.runtime.snapshot_common import (
    SNAPSHOT_DB_SCHEMA_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    _current_stage_entered_at,
    _derive_done_at,
    _duration_days,
    _extract_id,
    _extract_tag_ids,
    _filter_time_logs_to_window,
    _first_history_with_state,
    _iso_timestamp,
    _normalize_bool,
    _normalize_int_list,
    _now_iso,
    _parse_timestamp,
    _search_blob,
    _time_log_minutes,
    _time_log_timestamp,
)
from kaiten_cli.runtime.sqlite_errors import is_corrupt_database_error


def snapshot_db_path() -> Path:
    return user_data_path("kaiten-cli") / "snapshots.sqlite3"


STORAGE_READ_ONLY_ENV = "KAITEN_CLI_STORAGE_READ_ONLY"
_TRUTHY_ENV_VALUES = frozenset({"1", "true", "yes", "on"})


class SnapshotStore:
    def __init__(
        self,
        path: Path | None = None,
        reporter=None,
        *,
        storage_read_only: bool | None = None,
    ):
        self.path = path or snapshot_db_path()
        self.reporter = reporter
        environment_read_only = (
            os.environ.get(STORAGE_READ_ONLY_ENV, "").strip().lower() in _TRUTHY_ENV_VALUES
        )
        self.storage_read_only = bool(storage_read_only) or environment_read_only

    def ensure_writable(self) -> None:
        if self.storage_read_only:
            raise ConfigError(
                "Local snapshot writes are disabled in this storage read-only environment."
            )

    def _debug(self, message: str) -> None:
        if self.reporter is not None:
            self.reporter(message)

    def _open_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except BaseException:
            self._close_quietly(conn)
            raise

    def _open_read_connection(self) -> sqlite3.Connection:
        uri = f"{self.path.absolute().as_uri()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except BaseException:
            self._close_quietly(conn)
            raise

    def _close_quietly(self, conn: sqlite3.Connection | None) -> None:
        if conn is None:
            return
        try:
            conn.close()
        except sqlite3.Error:
            return

    def _reset_error(self, action: str) -> ConfigError:
        return ConfigError(
            f"Unable to {action} local snapshot store at {self.path}. Remove the file and retry."
        )

    def _access_error(self, action: str, error: BaseException) -> ConfigError:
        return ConfigError(f"Unable to {action} local snapshot store at {self.path}: {error}")

    def _reset_store(self, reason: str) -> sqlite3.Connection:
        self._debug(f"snapshot: local store dropped store=snapshots reason={reason}")
        try:
            self.path.unlink(missing_ok=True)
        except OSError as exc:
            raise self._reset_error("reset") from exc
        conn: sqlite3.Connection | None = None
        try:
            ensure_private_file(self.path)
            conn = self._open_connection()
            secure_existing_file(self.path)
            self._initialize_schema(conn)
            self._debug("snapshot: local store recreated store=snapshots")
            return conn
        except (sqlite3.Error, OSError) as exc:
            self._close_quietly(conn)
            raise self._reset_error("recreate") from exc
        except BaseException:
            self._close_quietly(conn)
            raise

    def _connect(self) -> sqlite3.Connection:
        conn: sqlite3.Connection | None = None
        try:
            secure_directory(self.path.parent)
            existing = self.path.exists()
            ensure_private_file(self.path)
            conn = self._open_connection()
            secure_existing_file(self.path)
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if existing and version != SNAPSHOT_DB_SCHEMA_VERSION:
                self._close_quietly(conn)
                return self._reset_store(f"incompatible-schema:{version}")
            self._initialize_schema(conn)
            return conn
        except sqlite3.Error as exc:
            self._close_quietly(conn)
            if is_corrupt_database_error(exc):
                return self._reset_store(type(exc).__name__)
            raise self._access_error("open", exc) from exc
        except OSError as exc:
            self._close_quietly(conn)
            raise self._access_error("open", exc) from exc
        except BaseException:
            self._close_quietly(conn)
            raise

    def _connect_read_only(self) -> sqlite3.Connection:
        conn: sqlite3.Connection | None = None
        try:
            secure_existing_file(self.path)
            conn = self._open_read_connection()
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if version != SNAPSHOT_DB_SCHEMA_VERSION:
                raise ConfigError(
                    f"Local snapshot store at {self.path} has incompatible schema {version}; "
                    "refresh or rebuild it outside the storage read-only sandbox."
                )
            return conn
        except ConfigError:
            self._close_quietly(conn)
            raise
        except (OSError, sqlite3.Error) as exc:
            self._close_quietly(conn)
            raise self._access_error("read", exc) from exc
        except BaseException:
            self._close_quietly(conn)
            raise

    @contextmanager
    def _connection(self, *, read_only: bool = False) -> Iterator[sqlite3.Connection]:
        """Provide transactional access and always release the SQLite handle."""

        if self.storage_read_only and not read_only:
            self.ensure_writable()
        conn = self._connect_read_only() if self.storage_read_only else self._connect()
        try:
            if self.storage_read_only:
                yield conn
            else:
                with conn:
                    yield conn
        except sqlite3.Error as exc:
            if self.storage_read_only:
                raise self._access_error("read", exc) from exc
            raise
        finally:
            self._close_quietly(conn)

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
            conn.execute(
                "ALTER TABLE snapshots ADD COLUMN schema_version INTEGER NOT NULL DEFAULT 2"
            )
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
        card_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(snapshot_cards)").fetchall()
        }
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
        if self.storage_read_only and not self.path.exists() and not self.path.is_symlink():
            return []
        with self._connection(read_only=True) as conn:
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
        if self.storage_read_only and not self.path.exists() and not self.path.is_symlink():
            raise ConfigError(f"Unknown snapshot: {name}")
        with self._connection(read_only=True) as conn:
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
        with self._connection() as conn:
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

            child_titles = [
                str(item.get("title", "")) for item in children if isinstance(item, dict)
            ]
            comment_texts = [
                str(item.get("text", "")) for item in comments if isinstance(item, dict)
            ]
            search_text = _search_blob(
                [str(card.get("title", "")), str(card.get("description", ""))]
            )
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
            age_anchor = (
                current_stage_entered_at
                or _parse_timestamp(card.get("updated"))
                or _parse_timestamp(card.get("created"))
            )
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
            board_rows.append(
                (name, board["id"], json.dumps(board, ensure_ascii=False, separators=(",", ":")))
            )
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

        with self._connection() as conn:
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
            "latest_stage": {
                "column_id": row["latest_column_id"],
                "lane_id": row["latest_lane_id"],
            },
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
        with self._connection(read_only=True) as conn:
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
        for filter_name, column_name in (
            ("has_children", "has_children"),
            ("has_comments", "has_comments"),
        ):
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
        with self._connection(read_only=True) as conn:
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
        with self._connection(read_only=True) as conn:
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
        return [row for row in rows if set(json.loads(row["tag_ids_json"])) & tag_ids]

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
        with self._connection(read_only=True) as conn:
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
