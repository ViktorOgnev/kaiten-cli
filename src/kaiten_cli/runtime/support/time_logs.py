"""Support helpers for batch time-log reads."""

from __future__ import annotations

from typing import Any

from kaiten_cli.runtime.support.batch import DEFAULT_BATCH_WORKERS, fetch_card_collection_batch
from kaiten_cli.runtime.transforms import compact_response, select_fields


def _shape_time_log_items(items: list[Any], *, compact: bool, fields: str | None) -> list[Any]:
    shaped = compact_response(items, compact)
    return select_fields(shaped, fields)


async def fetch_time_logs_batch(
    *,
    domain: str,
    token: str,
    card_ids: list[int],
    workers: int = DEFAULT_BATCH_WORKERS,
    for_date: str | None = None,
    personal: bool | None = None,
    compact: bool = False,
    fields: str | None = None,
    timeout: float,
    reporter,
    execution_context=None,
    cache_policy: str = "request_scope",
) -> dict[str, Any]:
    def query_for_card(card_id: int) -> dict[str, Any] | None:
        params: dict[str, Any] = {}
        if for_date:
            params["for_date"] = for_date
        if personal is not None:
            params["personal"] = personal
        return params or None

    return await fetch_card_collection_batch(
        domain=domain,
        token=token,
        card_ids=card_ids,
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        execution_context=execution_context,
        cache_policy=cache_policy,
        path_for_card=lambda card_id: f"/cards/{card_id}/time-logs",
        query_for_card=query_for_card,
        result_field="time_logs",
        transform_items=lambda items: _shape_time_log_items(items, compact=compact, fields=fields),
        worker_label="batch-time-logs",
    )
