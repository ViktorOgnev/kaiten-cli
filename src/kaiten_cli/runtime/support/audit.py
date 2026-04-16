"""Support helpers for audit/activity commands."""

from __future__ import annotations

import asyncio
from typing import Any

from kaiten_cli.errors import ApiError, CliError
from kaiten_cli.runtime.client import KaitenClient
from kaiten_cli.runtime.transforms import select_fields

MAX_ACTIVITY_PAGES = 50
MAX_ACTIVITY_PAGE_SIZE = 100
DEFAULT_HISTORY_WORKERS = 2
MAX_HISTORY_WORKERS = 6


async def fetch_all_space_activity(client, args: dict[str, Any], *, timeout: float) -> list[Any]:
    """Fetch space activity with bounded pagination."""
    page_size = min(args.get("page_size", MAX_ACTIVITY_PAGE_SIZE), MAX_ACTIVITY_PAGE_SIZE)
    max_pages = min(args.get("max_pages", MAX_ACTIVITY_PAGES), MAX_ACTIVITY_PAGES)

    params: dict[str, Any] = {}
    for key in ("actions", "created_after", "created_before", "author_id"):
        if args.get(key) is not None:
            params[key] = args[key]

    all_activity: list[Any] = []
    for page in range(max_pages):
        params["limit"] = page_size
        params["offset"] = page * page_size
        result = await client.get(f"/spaces/{args['space_id']}/activity", params=params, timeout=timeout)
        if not result:
            break
        all_activity.extend(result)
        if len(result) < page_size:
            break
    return all_activity


def _normalize_history_error(card_id: int, exc: Exception) -> dict[str, Any]:
    payload = {
        "card_id": card_id,
        "error_type": "internal_error",
        "message": str(exc),
    }
    if isinstance(exc, CliError):
        payload["error_type"] = exc.error_type
    if isinstance(exc, ApiError):
        payload["status_code"] = exc.status_code
    return payload


def _unique_card_ids(card_ids: list[int]) -> list[int]:
    unique: list[int] = []
    seen: set[int] = set()
    for card_id in card_ids:
        if card_id in seen:
            continue
        seen.add(card_id)
        unique.append(card_id)
    return unique


async def fetch_card_location_histories(
    *,
    domain: str,
    token: str,
    card_ids: list[int],
    workers: int,
    fields: str | None,
    timeout: float,
    reporter,
    execution_context=None,
    cache_policy: str = "request_scope",
) -> dict[str, Any]:
    unique_card_ids = _unique_card_ids(card_ids)
    queue: asyncio.Queue[tuple[int, int]] = asyncio.Queue()
    for index, card_id in enumerate(unique_card_ids):
        queue.put_nowait((index, card_id))

    ordered_items: list[dict[str, Any] | None] = [None] * len(unique_card_ids)
    ordered_errors: list[dict[str, Any] | None] = [None] * len(unique_card_ids)

    async def worker(worker_index: int) -> None:
        client = KaitenClient(
            domain=domain,
            token=token,
            reporter=reporter,
            execution_context=execution_context,
            cache_policy=cache_policy,
        )
        if reporter is not None:
            reporter(f"batch-history: worker={worker_index} started")
        try:
            while True:
                try:
                    index, card_id = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                try:
                    result = await client.get(f"/cards/{card_id}/location-history", timeout=timeout)
                    history = result if isinstance(result, list) else []
                    ordered_items[index] = {
                        "card_id": card_id,
                        "history": select_fields(history, fields),
                    }
                except Exception as exc:  # noqa: BLE001 - per-card failures are reported in-band.
                    ordered_errors[index] = _normalize_history_error(card_id, exc)
                finally:
                    queue.task_done()
        finally:
            await client.close()
            if reporter is not None:
                reporter(f"batch-history: worker={worker_index} finished")

    await asyncio.gather(*(worker(i + 1) for i in range(max(workers, 1))))

    items = [item for item in ordered_items if item is not None]
    errors = [item for item in ordered_errors if item is not None]
    return {
        "items": items,
        "errors": errors,
        "meta": {
            "requested": len(card_ids),
            "requested_count": len(card_ids),
            "unique_count": len(unique_card_ids),
            "succeeded": len(items),
            "failed": len(errors),
            "workers": max(workers, 1),
        },
    }
