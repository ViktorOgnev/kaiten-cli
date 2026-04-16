"""Support helpers for bulk card operations."""

from __future__ import annotations

from typing import Any

from kaiten_cli.runtime.support.batch import DEFAULT_BATCH_WORKERS, fetch_card_entity_batch
from kaiten_cli.runtime.transforms import compact_response, select_fields, strip_base64

MAX_CARD_PAGES = 50
MAX_CARD_PAGE_SIZE = 100


def _card_query_params(args: dict[str, Any]) -> dict[str, Any]:
    page_size = min(args.get("page_size", MAX_CARD_PAGE_SIZE), MAX_CARD_PAGE_SIZE)
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
    params["limit"] = page_size
    return params


async def _fetch_cards(client, params: dict[str, Any], *, page_size: int, max_pages: int, timeout: float) -> list[Any]:
    all_cards: list[Any] = []
    for page in range(max_pages):
        page_params = dict(params)
        page_params["limit"] = page_size
        page_params["offset"] = page * page_size
        result = await client.get("/cards", params=page_params, timeout=timeout)
        if not result:
            break
        all_cards.extend(result)
        if len(result) < page_size:
            break
    return all_cards


async def fetch_all_cards(client, args: dict[str, Any], *, timeout: float) -> list[Any]:
    """Fetch cards with bounded pagination and low-load defaults."""
    page_size = min(args.get("page_size", MAX_CARD_PAGE_SIZE), MAX_CARD_PAGE_SIZE)
    max_pages = min(args.get("max_pages", MAX_CARD_PAGES), MAX_CARD_PAGES)
    selection = args.get("selection")

    base_params = _card_query_params(args)
    base_params.pop("selection", None)

    if selection == "archived_only":
        archived_params = dict(base_params)
        archived_params["archived"] = True
        archived_params.pop("condition", None)
        return await _fetch_cards(client, archived_params, page_size=page_size, max_pages=max_pages, timeout=timeout)

    if selection == "active_only":
        all_cards = await _fetch_cards(client, base_params, page_size=page_size, max_pages=max_pages, timeout=timeout)
        archived_params = dict(base_params)
        archived_params["archived"] = True
        archived_params.pop("condition", None)
        archived_cards = await _fetch_cards(client, archived_params, page_size=page_size, max_pages=max_pages, timeout=timeout)
        archived_ids = {
            item["id"]
            for item in archived_cards
            if isinstance(item, dict) and "id" in item
        }
        return [
            item for item in all_cards
            if not (isinstance(item, dict) and item.get("id") in archived_ids)
        ]

    return await _fetch_cards(client, base_params, page_size=page_size, max_pages=max_pages, timeout=timeout)


def _shape_card_entity(item: dict[str, Any], *, compact: bool, fields: str | None) -> dict[str, Any]:
    shaped = compact_response(item, compact)
    shaped = select_fields(shaped, fields)
    shaped, _ = strip_base64(shaped)
    return shaped


async def fetch_cards_batch_get(
    *,
    domain: str,
    token: str,
    card_ids: list[int],
    workers: int = DEFAULT_BATCH_WORKERS,
    compact: bool = False,
    fields: str | None = None,
    timeout: float,
    reporter,
    execution_context=None,
    cache_policy: str = "request_scope",
) -> dict[str, Any]:
    return await fetch_card_entity_batch(
        domain=domain,
        token=token,
        card_ids=card_ids,
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        execution_context=execution_context,
        cache_policy=cache_policy,
        path_for_card=lambda card_id: f"/cards/{card_id}",
        result_field="card",
        transform_item=lambda item: _shape_card_entity(item, compact=compact, fields=fields),
        worker_label="batch-cards",
    )
