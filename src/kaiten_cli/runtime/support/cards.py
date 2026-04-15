"""Support helpers for bulk card operations."""

from __future__ import annotations

from typing import Any

MAX_CARD_PAGES = 50
MAX_CARD_PAGE_SIZE = 100


async def fetch_all_cards(client, args: dict[str, Any], *, timeout: float) -> list[Any]:
    """Fetch cards with bounded pagination and low-load defaults."""
    page_size = min(args.get("page_size", MAX_CARD_PAGE_SIZE), MAX_CARD_PAGE_SIZE)
    max_pages = min(args.get("max_pages", MAX_CARD_PAGES), MAX_CARD_PAGES)

    params: dict[str, Any] = {"relations": args.get("relations", "none")}
    string_keys = (
        "query",
        "tag_ids",
        "member_ids",
        "owner_ids",
        "responsible_ids",
        "states",
        "column_ids",
        "type_ids",
        "external_id",
        "created_after",
        "created_before",
        "updated_after",
        "updated_before",
        "due_date_after",
        "due_date_before",
    )
    int_keys = (
        "space_id",
        "board_id",
        "column_id",
        "lane_id",
        "condition",
        "type_id",
        "owner_id",
        "responsible_id",
    )
    bool_keys = ("overdue", "asap", "archived")

    for key in string_keys + int_keys + bool_keys:
        if args.get(key) is not None:
            params[key] = args[key]

    all_cards: list[Any] = []
    for page in range(max_pages):
        params["limit"] = page_size
        params["offset"] = page * page_size
        result = await client.get("/cards", params=params, timeout=timeout)
        if not result:
            break
        all_cards.extend(result)
        if len(result) < page_size:
            break
    return all_cards
