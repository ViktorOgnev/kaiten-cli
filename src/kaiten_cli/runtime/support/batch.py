"""Shared batch-fetch helpers for card-scoped endpoints."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from kaiten_cli.errors import ApiError, CliError
from kaiten_cli.runtime.client import KaitenClient

DEFAULT_BATCH_WORKERS = 2
MAX_BATCH_WORKERS = 6


def _normalize_batch_error(card_id: int, exc: Exception) -> dict[str, Any]:
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


def unique_card_ids(card_ids: list[int]) -> list[int]:
    unique: list[int] = []
    seen: set[int] = set()
    for card_id in card_ids:
        if card_id in seen:
            continue
        seen.add(card_id)
        unique.append(card_id)
    return unique


async def fetch_card_collection_batch(
    *,
    domain: str,
    token: str,
    card_ids: list[int],
    workers: int,
    timeout: float,
    reporter,
    execution_context=None,
    cache_policy: str = "request_scope",
    path_for_card: Callable[[int], str],
    query_for_card: Callable[[int], dict[str, Any] | None] | None = None,
    result_field: str,
    transform_items: Callable[[list[Any]], list[Any] | Any],
    worker_label: str,
) -> dict[str, Any]:
    unique_ids = unique_card_ids(card_ids)
    queue: asyncio.Queue[tuple[int, int]] = asyncio.Queue()
    for index, card_id in enumerate(unique_ids):
        queue.put_nowait((index, card_id))

    ordered_items: list[dict[str, Any] | None] = [None] * len(unique_ids)
    ordered_errors: list[dict[str, Any] | None] = [None] * len(unique_ids)
    bounded_workers = max(workers, 1)

    async def worker(worker_index: int) -> None:
        client = KaitenClient(
            domain=domain,
            token=token,
            reporter=reporter,
            execution_context=execution_context,
            cache_policy=cache_policy,
        )
        if reporter is not None:
            reporter(f"{worker_label}: worker={worker_index} started")
        try:
            while True:
                try:
                    index, card_id = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                try:
                    result = await client.get(
                        path_for_card(card_id),
                        params=query_for_card(card_id) if query_for_card is not None else None,
                        timeout=timeout,
                    )
                    items = result if isinstance(result, list) else []
                    ordered_items[index] = {
                        "card_id": card_id,
                        result_field: transform_items(items),
                    }
                except Exception as exc:  # noqa: BLE001 - per-card failures stay in-band.
                    ordered_errors[index] = _normalize_batch_error(card_id, exc)
                finally:
                    queue.task_done()
        finally:
            await client.close()
            if reporter is not None:
                reporter(f"{worker_label}: worker={worker_index} finished")

    await asyncio.gather(*(worker(i + 1) for i in range(bounded_workers)))

    items = [item for item in ordered_items if item is not None]
    errors = [item for item in ordered_errors if item is not None]
    return {
        "items": items,
        "errors": errors,
        "meta": {
            "requested": len(card_ids),
            "requested_count": len(card_ids),
            "unique_count": len(unique_ids),
            "succeeded": len(items),
            "failed": len(errors),
            "workers": bounded_workers,
        },
    }


async def fetch_card_entity_batch(
    *,
    domain: str,
    token: str,
    card_ids: list[int],
    workers: int,
    timeout: float,
    reporter,
    execution_context=None,
    cache_policy: str = "request_scope",
    path_for_card: Callable[[int], str],
    query_for_card: Callable[[int], dict[str, Any] | None] | None = None,
    result_field: str,
    transform_item: Callable[[dict[str, Any]], dict[str, Any] | Any],
    worker_label: str,
) -> dict[str, Any]:
    unique_ids = unique_card_ids(card_ids)
    queue: asyncio.Queue[tuple[int, int]] = asyncio.Queue()
    for index, card_id in enumerate(unique_ids):
        queue.put_nowait((index, card_id))

    ordered_items: list[dict[str, Any] | None] = [None] * len(unique_ids)
    ordered_errors: list[dict[str, Any] | None] = [None] * len(unique_ids)
    bounded_workers = max(workers, 1)

    async def worker(worker_index: int) -> None:
        client = KaitenClient(
            domain=domain,
            token=token,
            reporter=reporter,
            execution_context=execution_context,
            cache_policy=cache_policy,
        )
        if reporter is not None:
            reporter(f"{worker_label}: worker={worker_index} started")
        try:
            while True:
                try:
                    index, card_id = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                try:
                    result = await client.get(
                        path_for_card(card_id),
                        params=query_for_card(card_id) if query_for_card is not None else None,
                        timeout=timeout,
                    )
                    payload = result if isinstance(result, dict) else {}
                    ordered_items[index] = {
                        "card_id": card_id,
                        result_field: transform_item(payload),
                    }
                except Exception as exc:  # noqa: BLE001 - per-card failures stay in-band.
                    ordered_errors[index] = _normalize_batch_error(card_id, exc)
                finally:
                    queue.task_done()
        finally:
            await client.close()
            if reporter is not None:
                reporter(f"{worker_label}: worker={worker_index} finished")

    await asyncio.gather(*(worker(i + 1) for i in range(bounded_workers)))

    items = [item for item in ordered_items if item is not None]
    errors = [item for item in ordered_errors if item is not None]
    return {
        "items": items,
        "errors": errors,
        "meta": {
            "requested": len(card_ids),
            "requested_count": len(card_ids),
            "unique_count": len(unique_ids),
            "succeeded": len(items),
            "failed": len(errors),
            "workers": bounded_workers,
        },
    }
