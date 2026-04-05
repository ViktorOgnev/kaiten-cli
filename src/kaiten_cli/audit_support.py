"""Support helpers for audit/activity commands."""

from __future__ import annotations

from typing import Any

MAX_ACTIVITY_PAGES = 50
MAX_ACTIVITY_PAGE_SIZE = 100


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
