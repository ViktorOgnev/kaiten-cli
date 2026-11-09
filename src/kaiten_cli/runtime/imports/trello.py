"""Bounded Trello reads and conversion to the Kaiten external import profile."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import sqlite3
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import httpx

from kaiten_cli.errors import TransportError, ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.client import KaitenClient
from kaiten_cli.runtime.fs_security import secure_directory
from kaiten_cli.runtime.imports.storage import atomic_json, read_json, require_disk

API_URL = "https://api.trello.com/1/"
PAGE_SIZE = 1000
MAX_RESPONSE = 32 * 1024**2
MAX_EXPORT = 256 * 1024**2
MAX_PAGES = 100_000
KEY_ENV = "KAITEN_IMPORT_TRELLO_KEY"
TOKEN_ENV = "KAITEN_IMPORT_TRELLO_TOKEN"
OMITTED = (
    "archived_boards",
    "archived_lists",
    "archived_cards",
    "activity_history",
    "attachments",
    "comments",
    "checklists",
    "members",
    "custom_fields",
    "unnamed_labels",
)
CARD_FIELDS = "id,name,desc,idList,pos,closed,due,labels,idMembers,idChecklists,badges"
COLUMNS = {"queued", "in_progress", "done"}


def board_id(value: str) -> str:
    if re.fullmatch(r"[a-f0-9]{24}|[A-Za-z0-9]{8}", value):
        return value
    try:
        url = urlsplit(value)
        match = re.fullmatch(r"/b/([A-Za-z0-9]{8})(?:/[^/]+)?/?", url.path)
        if (
            url.scheme == "https"
            and url.netloc.lower() in {"trello.com", "www.trello.com"}
            and match
        ):
            return match[1]
    except ValueError:
        pass
    raise ValidationError(tr("Provide a Trello board ID or an HTTPS Trello board link."))


def credentials(stored: dict) -> tuple[str, str] | None:
    key, token = os.environ.get(KEY_ENV), os.environ.get(TOKEN_ENV)
    if not (key or token):
        key, token = stored.get("key"), stored.get("token")
    if key and token:
        if not all(
            isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_\-]{1,256}", value)
            for value in (key, token)
        ):
            raise ValidationError(tr("Invalid Trello credential format."))
        return key, token
    return None


def _invalid() -> ValidationError:
    return ValidationError(tr("The Trello response or export contains invalid board data."))


def _record_id(record: dict) -> str:
    if not isinstance(record, dict) or not re.fullmatch(r"[a-f0-9]{24}", str(record.get("id", ""))):
        raise _invalid()
    return record["id"]


def _records(value) -> list:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise _invalid()
    return value


def _timestamp(raw: str) -> datetime:
    try:
        value = datetime.fromisoformat(raw)
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        pass
    raise _invalid()


def _created(record_id: str) -> datetime:
    return datetime.fromtimestamp(int(record_id[:8], 16), timezone.utc)


def _title(raw, limit: int) -> str:
    if not isinstance(raw, str) or not 1 <= len(raw) <= limit:
        raise _invalid()
    return raw


def _position(row: dict) -> float:
    pos = row.get("pos", 0)
    if isinstance(pos, (float, int)) and math.isfinite(pos):
        return pos
    raise _invalid()


def export_data(path: Path) -> dict:
    data = read_json(path, MAX_EXPORT)
    _record_id(data)
    _records(data.get("lists"))
    _records(data.get("cards"))
    return data


class Trello:
    def __init__(self, secret: tuple[str, str], stats=None):
        key, token = secret
        self.http = httpx.AsyncClient(
            base_url=API_URL,
            headers={"Authorization": f'OAuth oauth_consumer_key="{key}", oauth_token="{token}"'},
            timeout=30,
            follow_redirects=False,
        )
        self.stats = stats

    async def get(self, path: str, **params):
        for attempt in range(4):
            started = time.monotonic()
            status = None
            delay = min(2**attempt, 10)
            try:
                async with self.http.stream("GET", path, params=params) as response:
                    status = response.status_code
                    if status == 200:
                        content = bytearray()
                        async for block in response.aiter_bytes():
                            content.extend(block)
                            if len(content) > MAX_RESPONSE:
                                raise _invalid()
                        try:
                            return json.loads(content)
                        except (ValueError, RecursionError):
                            raise _invalid() from None
                    if status not in {429, 500, 502, 503, 504}:
                        raise TransportError(
                            tr("Trello read failed with HTTP {value_0}.", value_0=status)
                        )
                    retry_after = KaitenClient._parse_retry_after(
                        response.headers.get("Retry-After")
                    )
                    if retry_after is not None and math.isfinite(retry_after):
                        if retry_after > 60:
                            break
                        delay = max(delay, retry_after)
            except httpx.RequestError:
                pass
            finally:
                if self.stats is not None:
                    self.stats.record_http_attempt(
                        source="trello_api",
                        method="GET",
                        path="/boards/{id}"
                        + ("/" + path.rsplit("/", 1)[-1] if path.count("/") == 2 else ""),
                        wait_ms=(time.monotonic() - started) * 1000,
                        status_code=status,
                        error=status is None,
                    )
            if attempt < 3:
                await asyncio.sleep(delay)
        raise TransportError(
            tr("Trello is unavailable or rate limited. Retry preparation to resume.")
        )

    async def metadata(self, selector: str) -> dict:
        board = await self.get(f"boards/{selector}", fields="id,name,desc,closed,dateLastActivity")
        identity = _record_id(board)
        board["lists"] = _records(
            await self.get(f"boards/{identity}/lists", filter="all", fields="id,name,closed,pos")
        )
        return board

    async def download(self, path: Path, selector: str) -> tuple[dict, int]:
        secure_directory(path)
        board = await self.metadata(selector)
        identity = _record_id(board)
        if not isinstance(board.get("dateLastActivity"), str):
            raise _invalid()
        header = path / "board.json"
        if header.exists() and read_json(header) != board:
            raise ValidationError(
                tr("The Trello board changed since export began. Create a new import plan.")
            )
        if not header.exists():
            atomic_json(header, board)
        cursor = None
        seen = set()
        for index in range(MAX_PAGES):
            checkpoint = path / f"{index:06}.json"
            if checkpoint.exists():
                page = read_json(checkpoint, MAX_RESPONSE * 2)
                rows = _records(page["cards"])
                if page["before"] != cursor:
                    raise _invalid()
                complete = page["complete"]
            else:
                require_disk(path, MAX_RESPONSE * 2)
                rows = _records(
                    await self.get(
                        f"boards/{identity}/cards",
                        **{
                            "filter": "all",
                            "fields": CARD_FIELDS,
                            "limit": PAGE_SIZE,
                            **({"before": cursor} if cursor else {}),
                        },
                    )
                )
                complete = len(rows) < PAGE_SIZE
            dates = [_created(_record_id(row)) for row in rows]
            if len(rows) > PAGE_SIZE or not complete and dates != sorted(dates, reverse=True):
                raise ValidationError(
                    tr("Trello card pagination could not be verified. Use a JSON export.")
                )
            if cursor and any(date >= _timestamp(cursor) for date in dates):
                raise ValidationError(
                    tr("Trello card pagination could not be verified. Use a JSON export.")
                )
            fresh = {_record_id(row) for row in rows} - seen
            if len({_record_id(row) for row in rows}) != len(rows) or not complete and not fresh:
                raise ValidationError(
                    tr("Trello card pagination could not be verified. Use a JSON export.")
                )
            if not checkpoint.exists():
                atomic_json(checkpoint, {"cards": rows, "before": cursor, "complete": complete})
            seen.update(fresh)
            if complete:
                after = await self.get(
                    f"boards/{identity}", fields="id,name,desc,closed,dateLastActivity"
                )
                if after != {k: v for k, v in board.items() if k != "lists"}:
                    raise ValidationError(
                        tr("The Trello board changed since export began. Create a new import plan.")
                    )
                return board, index + 1
            cursor = (dates[-1] + timedelta(seconds=1)).isoformat()
        raise ValidationError(
            tr("Trello card pagination could not be verified. Use a JSON export.")
        )


def board_preview(board: dict, column_types: dict) -> dict:
    lists = sorted(_records(board.get("lists")), key=lambda row: (_position(row), _record_id(row)))
    return {
        "id": _record_id(board),
        "title": _title(board.get("name"), 128),
        "closed": bool(board.get("closed")),
        "columns": [
            {
                "id": row["id"],
                "title": _title(row.get("name"), 128),
                "type": column_types.get(row["id"], "queued"),
            }
            for row in lists
            if not row.get("closed")
        ],
    }


def write_package(
    directory: Path,
    boards: list[tuple[dict, object]],
    owner_email: str,
    column_types: dict,
    work: Path,
) -> dict:
    """Spool and sort card payloads on disk, with one bounded JSON resource shard at a time."""
    if (
        not isinstance(owner_email, str)
        or len(owner_email) > 128
        or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", owner_email)
    ):
        raise ValidationError(
            tr("The target profile must expose a valid email for the card owner.")
        )
    secure_directory(directory / "resources")
    database = work / "sort.sqlite3"
    database.unlink(missing_ok=True)
    fd = os.open(database, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    records = []
    counts: Counter = Counter()
    omitted: Counter = Counter(dict.fromkeys(OMITTED, 0))
    tags = {}
    active_boards = []
    active_columns = []
    board_ids = set()
    used_columns = set()
    package_id = str(uuid4())

    def write(resource: str, rows: list, suffix: str = "") -> None:
        if rows:
            path = f"resources/{resource}{suffix}.json"
            atomic_json(directory / path, rows)
            records.append({"resource": resource, "path": path})
            counts[resource] += len(rows)

    try:
        with sqlite3.connect(database) as conn:
            conn.execute(
                "CREATE TABLE cards (id TEXT PRIMARY KEY, position REAL, body TEXT, source_hash TEXT)"
            )
            for board, pages in boards:
                board_info = board_preview(board, column_types)
                identity = board_info["id"]
                if identity in board_ids:
                    raise _invalid()
                board_ids.add(identity)
                columns = {row["id"] for row in board_info["columns"]}
                all_columns = {_record_id(row) for row in board["lists"]}
                if board_info["closed"]:
                    omitted["archived_boards"] += 1
                elif columns:
                    if len(columns) != len(board_info["columns"]) or columns & used_columns:
                        raise _invalid()
                    used_columns.update(columns)
                    active_boards.append(
                        {
                            "external_id": f"trello:{identity}",
                            "title": board_info["title"],
                            "default_card_type_ref": "trello:card",
                            "card_properties": [
                                {"field": f} for f in ("description", "due_date", "tags")
                            ],
                        }
                    )
                    active_columns.extend(
                        {
                            "external_id": f"trello:{row['id']}",
                            "board_ref": f"trello:{identity}",
                            "title": row["title"],
                            "type": row["type"],
                        }
                        for row in board_info["columns"]
                    )
                omitted["archived_lists"] += sum(bool(row.get("closed")) for row in board["lists"])
                omitted["activity_history"] += len(board.get("actions") or [])
                omitted["custom_fields"] += len(board.get("customFields") or [])
                for page in pages:
                    require_disk(work, 0)
                    for row in page:
                        card = _record_id(row)
                        source_hash = hashlib.sha256(
                            json.dumps(row, sort_keys=True).encode()
                        ).hexdigest()
                        existing = conn.execute(
                            "SELECT source_hash FROM cards WHERE id = ?", (card,)
                        ).fetchone()
                        if existing:
                            if existing[0] != source_hash:
                                raise _invalid()
                            continue
                        converted = None
                        if (
                            board_info["closed"]
                            or row.get("closed")
                            or row.get("idList") not in columns
                        ):
                            if not board_info["closed"] and row.get("idList") not in all_columns:
                                raise _invalid()
                            omitted["archived_cards"] += 1
                        else:
                            converted = _convert_card(row, identity, tags, omitted)
                        conn.execute(
                            "INSERT INTO cards VALUES (?, ?, ?, ?)",
                            (
                                card,
                                _position(row),
                                json.dumps(converted) if converted is not None else None,
                                source_hash,
                            ),
                        )
            if set(column_types) - used_columns:
                raise ValidationError(tr("A configured Trello column is absent or archived."))
            if not active_boards:
                raise ValidationError(tr("No active Trello boards with lists were found."))
            write("boards", active_boards)
            write("columns", active_columns)
            write("card_types", [{"external_id": "trello:card", "name": "Trello Card"}])
            write("users", [{"external_id": "trello:import-owner", "email": owner_email.lower()}])
            write("tags", list(tags.values()))
            cursor = conn.execute(
                "SELECT body FROM cards WHERE body IS NOT NULL ORDER BY position, id"
            )
            while rows := cursor.fetchmany(100):
                write("cards", [json.loads(row[0]) for row in rows], f"-{counts['cards']:08}")
    finally:
        database.unlink(missing_ok=True)

    atomic_json(
        directory / "meta-data.json",
        {
            "profile": {"name": "external"},
            "package_id": package_id,
            "source": {
                "system": "trello",
                "namespace": "trello:"
                + hashlib.sha256(",".join(sorted(board_ids)).encode()).hexdigest(),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            },
            "timeline_mode": "current_state_only",
            "resource_files": records,
            "binary_files": {"base_path": "files/"},
        },
    )
    return {
        "counts": dict(counts),
        "omitted_observed": dict(omitted),
        "omitted_categories": list(OMITTED),
    }


def _convert_card(row: dict, board: str, tags: dict, omitted: Counter) -> dict:
    identity = _record_id(row)
    record = {
        "external_id": f"trello:{identity}",
        "board_ref": f"trello:{board}",
        "column_ref": f"trello:{row['idList']}",
        "owner_ref": "trello:import-owner",
        "type_ref": "trello:card",
        "created_at": _created(identity).isoformat(),
        "title": _title(row.get("name"), 1024),
    }
    if row.get("desc"):
        record["description"] = {"format": "markdown", "text": _title(row["desc"], 1_000_000)}
    if row.get("due"):
        record["due_date"] = {"precision": "date_time", "value": _timestamp(row["due"]).isoformat()}
    refs = []
    for label in _records(row.get("labels", [])):
        name = label.get("name")
        if not name:
            omitted["unnamed_labels"] += 1
            continue
        name = _title(name, 255)
        key = name.casefold()
        if key not in tags:
            tag_id = hashlib.sha256(key.encode()).hexdigest()
            tags[key] = {"external_id": f"trello:label:{tag_id}", "name": name}
        refs.append(tags[key]["external_id"])
    if refs:
        record["tag_refs"] = list(dict.fromkeys(refs))
    badges = row.get("badges") or {}
    if not isinstance(badges, dict):
        raise _invalid()
    for key in ("attachments", "comments"):
        count = badges.get(key, 0)
        if isinstance(count, int) and count > 0:
            omitted[key] += count
    for key, field in (
        ("members", "idMembers"),
        ("checklists", "idChecklists"),
        ("custom_fields", "customFieldItems"),
    ):
        values = row.get(field) or []
        if not isinstance(values, list):
            raise _invalid()
        omitted[key] += len(values)
    return record
