"""Support helpers for relation- and comment-heavy investigations."""

from __future__ import annotations

from typing import Any

from kaiten_cli.runtime.support.batch import (
    DEFAULT_BATCH_WORKERS,
    fetch_card_collection_batch,
)
from kaiten_cli.runtime.transforms import compact_response, select_fields


def _shape_nested_items(items: list[Any], *, compact: bool, fields: str | None) -> list[Any]:
    shaped = compact_response(items, compact)
    return select_fields(shaped, fields)


async def fetch_card_children_batch(
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
    return await fetch_card_collection_batch(
        domain=domain,
        token=token,
        card_ids=card_ids,
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        execution_context=execution_context,
        cache_policy=cache_policy,
        path_for_card=lambda card_id: f"/cards/{card_id}/children",
        result_field="children",
        transform_items=lambda items: _shape_nested_items(items, compact=compact, fields=fields),
        worker_label="batch-children",
    )


async def fetch_comments_batch(
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
    return await fetch_card_collection_batch(
        domain=domain,
        token=token,
        card_ids=card_ids,
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        execution_context=execution_context,
        cache_policy=cache_policy,
        path_for_card=lambda card_id: f"/cards/{card_id}/comments",
        result_field="comments",
        transform_items=lambda items: _shape_nested_items(items, compact=compact, fields=fields),
        worker_label="batch-comments",
    )
