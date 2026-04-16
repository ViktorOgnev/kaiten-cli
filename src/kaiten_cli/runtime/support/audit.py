"""Support helpers for audit/activity commands."""

from __future__ import annotations

import asyncio
from typing import Any

from kaiten_cli.runtime.support.batch import (
    DEFAULT_BATCH_WORKERS,
    MAX_BATCH_WORKERS,
    fetch_card_collection_batch,
)
from kaiten_cli.runtime.transforms import select_fields

MAX_ACTIVITY_PAGES = 50
MAX_ACTIVITY_PAGE_SIZE = 100
DEFAULT_HISTORY_WORKERS = DEFAULT_BATCH_WORKERS
MAX_HISTORY_WORKERS = MAX_BATCH_WORKERS


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
    return await fetch_card_collection_batch(
        domain=domain,
        token=token,
        card_ids=card_ids,
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        execution_context=execution_context,
        cache_policy=cache_policy,
        path_for_card=lambda card_id: f"/cards/{card_id}/location-history",
        result_field="history",
        transform_items=lambda items: select_fields(items, fields),
        worker_label="batch-history",
    )
