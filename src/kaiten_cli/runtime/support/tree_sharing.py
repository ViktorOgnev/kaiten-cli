"""Helpers for tree entity public sharing commands."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable
from uuid import UUID

from kaiten_cli.errors import (
    ApiError,
    BatchExecutionError,
    CliError,
    TransportError,
    ValidationError,
)
from kaiten_cli.runtime.client import KaitenClient
from kaiten_cli.runtime.support.batch import DEFAULT_BATCH_WORKERS, MAX_BATCH_WORKERS

DEFAULT_SHARE_WORKERS = DEFAULT_BATCH_WORKERS
MAX_SHARE_WORKERS = MAX_BATCH_WORKERS


def _share_path(entity_uid: str) -> str:
    return f"/tree-entities/{entity_uid}/share"


def _parse_expired_at(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Field expired_at must be a valid ISO-8601 date or datetime.")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError(
            "Field expired_at must be a valid ISO-8601 date or datetime."
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _expiration_matches(current: Any, requested: str | None) -> bool:
    if current is None or requested is None:
        return current is requested
    if not isinstance(current, str):
        return False
    try:
        return _parse_expired_at(current) == _parse_expired_at(requested)
    except ValidationError:
        return current == requested


def _validate_entity_uid(value: Any, *, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field {field} must be a non-empty UUID string.")
    try:
        UUID(value)
    except ValueError as exc:
        raise ValidationError(f"Field {field} must be a valid UUID.") from exc


def validate_tree_entity_share_payload(tool, payload: dict[str, Any]) -> None:
    _validate_entity_uid(payload.get("entity_uid"), field="entity_uid")
    if "expired_at" in payload and payload["expired_at"] is not None:
        parsed = _parse_expired_at(payload["expired_at"])
        if parsed <= datetime.now(UTC):
            raise ValidationError("Field expired_at must be in the future or null.")


def validate_tree_entity_share_batch_payload(tool, payload: dict[str, Any]) -> None:
    entity_uids = payload.get("entity_uids")
    if not isinstance(entity_uids, list) or not entity_uids:
        raise ValidationError("Field entity_uids must be a non-empty array.")
    for index, entity_uid in enumerate(entity_uids):
        _validate_entity_uid(entity_uid, field=f"entity_uids[{index}]")
    workers = payload.get("workers", DEFAULT_SHARE_WORKERS)
    if workers < 1 or workers > MAX_SHARE_WORKERS:
        raise ValidationError(f"Field workers must be between 1 and {MAX_SHARE_WORKERS}.")
    if "expired_at" in payload and payload["expired_at"] is not None:
        parsed = _parse_expired_at(payload["expired_at"])
        if parsed <= datetime.now(UTC):
            raise ValidationError("Field expired_at must be in the future or null.")


def _coerce_share_payload(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TransportError("Kaiten returned an invalid tree entity share response.")
    return value


def shape_tree_entity_share(
    *, entity_uid: str, share: dict[str, Any] | None, origin: str, changed: bool
) -> dict[str, Any]:
    share_uid = share.get("uid") if share else None
    disabled = bool(share.get("disabled", False)) if share_uid else False
    is_expired = bool(share.get("is_expired", False)) if share_uid else False
    return {
        "entity_uid": entity_uid,
        "shared": bool(share_uid) and not disabled and not is_expired,
        "uid": share_uid,
        "public_url": f"{origin.rstrip('/')}/p/{share_uid}" if share_uid else None,
        "expired_at": share.get("expired_at") if share else None,
        "created_at": share.get("created_at") if share else None,
        "updated_at": share.get("updated_at") if share else None,
        "is_expired": is_expired,
        "disabled": disabled,
        "changed": changed,
    }


async def get_tree_entity_share(
    client: KaitenClient, entity_uid: str, *, timeout: float
) -> dict[str, Any]:
    share = _coerce_share_payload(await client.get(_share_path(entity_uid), timeout=timeout))
    return shape_tree_entity_share(
        entity_uid=entity_uid,
        share=share,
        origin=client.root_url,
        changed=False,
    )


async def enable_tree_entity_share(
    client: KaitenClient,
    entity_uid: str,
    *,
    expired_at_provided: bool,
    expired_at: str | None,
    timeout: float,
) -> dict[str, Any]:
    path = _share_path(entity_uid)
    existing = _coerce_share_payload(await client.get(path, timeout=timeout))

    if not existing or not existing.get("uid"):
        body = {"expired_at": expired_at} if expired_at_provided else None
        created = _coerce_share_payload(await client.post(path, json=body, timeout=timeout))
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=created,
            origin=client.root_url,
            changed=True,
        )

    existing_expired_at = existing.get("expired_at")
    is_disabled = bool(existing.get("disabled", False))
    is_expired = bool(existing.get("is_expired", False))

    if is_disabled:
        current = _coerce_share_payload(await client.post(path, json=None, timeout=timeout))
        target_expired_at = expired_at if expired_at_provided else None
        needs_expiry_patch = expired_at_provided or bool(current and current.get("is_expired"))
        if (
            needs_expiry_patch
            and current
            and not _expiration_matches(current.get("expired_at"), target_expired_at)
        ):
            current = _coerce_share_payload(
                await client.patch(
                    path,
                    json={"expired_at": target_expired_at},
                    timeout=timeout,
                )
            )
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=current,
            origin=client.root_url,
            changed=True,
        )

    if is_expired:
        target_expired_at = expired_at if expired_at_provided else None
        renewed = _coerce_share_payload(
            await client.patch(path, json={"expired_at": target_expired_at}, timeout=timeout)
        )
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=renewed,
            origin=client.root_url,
            changed=True,
        )

    if expired_at_provided and not _expiration_matches(existing_expired_at, expired_at):
        updated = _coerce_share_payload(
            await client.patch(path, json={"expired_at": expired_at}, timeout=timeout)
        )
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=updated,
            origin=client.root_url,
            changed=True,
        )

    return shape_tree_entity_share(
        entity_uid=entity_uid,
        share=existing,
        origin=client.root_url,
        changed=False,
    )


async def update_tree_entity_share(
    client: KaitenClient,
    entity_uid: str,
    *,
    expired_at: str | None,
    timeout: float,
) -> dict[str, Any]:
    path = _share_path(entity_uid)
    existing = _coerce_share_payload(await client.get(path, timeout=timeout))
    if (
        existing
        and existing.get("uid")
        and _expiration_matches(existing.get("expired_at"), expired_at)
    ):
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=existing,
            origin=client.root_url,
            changed=False,
        )
    updated = _coerce_share_payload(
        await client.patch(path, json={"expired_at": expired_at}, timeout=timeout)
    )
    return shape_tree_entity_share(
        entity_uid=entity_uid,
        share=updated,
        origin=client.root_url,
        changed=True,
    )


async def disable_tree_entity_share(
    client: KaitenClient, entity_uid: str, *, timeout: float
) -> dict[str, Any]:
    path = _share_path(entity_uid)
    existing = _coerce_share_payload(await client.get(path, timeout=timeout))
    if not existing or not existing.get("uid") or existing.get("disabled", False):
        return shape_tree_entity_share(
            entity_uid=entity_uid,
            share=existing,
            origin=client.root_url,
            changed=False,
        )
    await client.delete(path, timeout=timeout)
    disabled = {**existing, "disabled": True}
    return shape_tree_entity_share(
        entity_uid=entity_uid,
        share=disabled,
        origin=client.root_url,
        changed=True,
    )


def _unique_entity_uids(entity_uids: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for entity_uid in entity_uids:
        normalized = str(UUID(entity_uid))
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(entity_uid)
    return unique


def _normalize_batch_error(entity_uid: str, exc: Exception) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "entity_uid": entity_uid,
        "error_type": "internal_error",
        "message": str(exc),
    }
    if isinstance(exc, CliError):
        payload["error_type"] = exc.error_type
    if isinstance(exc, ApiError):
        payload["status_code"] = exc.status_code
    return payload


async def _run_tree_entity_share_batch(
    *,
    client: KaitenClient,
    entity_uids: list[str],
    workers: int,
    timeout: float,
    reporter,
    worker_label: str,
    operation: Callable[[KaitenClient, str], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    unique_uids = _unique_entity_uids(entity_uids)
    queue: asyncio.Queue[tuple[int, str]] = asyncio.Queue()
    for index, entity_uid in enumerate(unique_uids):
        queue.put_nowait((index, entity_uid))

    ordered_items: list[dict[str, Any] | None] = [None] * len(unique_uids)
    ordered_errors: list[dict[str, Any] | None] = [None] * len(unique_uids)

    async def worker(worker_index: int) -> None:
        worker_client = KaitenClient(
            domain=client.domain,
            token=client.token,
            reporter=reporter,
            execution_context=client.execution_context,
            cache_policy=client.cache_policy,
            mutates_remote_state=client.mutates_remote_state,
        )
        if reporter:
            reporter(f"{worker_label}: worker={worker_index} started")
        try:
            while True:
                try:
                    index, entity_uid = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                try:
                    ordered_items[index] = await operation(worker_client, entity_uid)
                except Exception as exc:  # noqa: BLE001 - failures stay isolated per entity.
                    ordered_errors[index] = _normalize_batch_error(entity_uid, exc)
                finally:
                    queue.task_done()
        finally:
            await worker_client.close()
            if reporter:
                reporter(f"{worker_label}: worker={worker_index} finished")

    await asyncio.gather(*(worker(index + 1) for index in range(workers)))

    items = [item for item in ordered_items if item is not None]
    errors = [item for item in ordered_errors if item is not None]
    changed = sum(1 for item in items if item.get("changed") is True)
    return {
        "items": items,
        "errors": errors,
        "meta": {
            "requested": len(entity_uids),
            "requested_count": len(entity_uids),
            "unique_count": len(unique_uids),
            "succeeded": len(items),
            "failed": len(errors),
            "changed": changed,
            "unchanged": len(items) - changed,
            "workers": workers,
        },
    }


async def execute_tree_entity_share_get(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    return await get_tree_entity_share(client, payload["entity_uid"], timeout=timeout)


async def execute_tree_entity_share_enable(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    return await enable_tree_entity_share(
        client,
        payload["entity_uid"],
        expired_at_provided="expired_at" in payload,
        expired_at=payload.get("expired_at"),
        timeout=timeout,
    )


async def execute_tree_entity_share_update(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    return await update_tree_entity_share(
        client,
        payload["entity_uid"],
        expired_at=payload["expired_at"],
        timeout=timeout,
    )


async def execute_tree_entity_share_disable(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    return await disable_tree_entity_share(client, payload["entity_uid"], timeout=timeout)


async def execute_tree_entity_share_batch_get(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    workers = payload.get("workers", DEFAULT_SHARE_WORKERS)
    result = await _run_tree_entity_share_batch(
        client=client,
        entity_uids=list(payload["entity_uids"]),
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        worker_label="batch-share-get",
        operation=lambda worker_client, entity_uid: get_tree_entity_share(
            worker_client, entity_uid, timeout=timeout
        ),
    )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError("Failed to get shares for all requested tree entities.", result)
    return result


async def execute_tree_entity_share_batch_enable(
    client, tool, payload, path, query, body, timeout, reporter
) -> dict[str, Any]:
    workers = payload.get("workers", DEFAULT_SHARE_WORKERS)
    expired_at_provided = "expired_at" in payload
    expired_at = payload.get("expired_at")
    result = await _run_tree_entity_share_batch(
        client=client,
        entity_uids=list(payload["entity_uids"]),
        workers=workers,
        timeout=timeout,
        reporter=reporter,
        worker_label="batch-share-enable",
        operation=lambda worker_client, entity_uid: enable_tree_entity_share(
            worker_client,
            entity_uid,
            expired_at_provided=expired_at_provided,
            expired_at=expired_at,
            timeout=timeout,
        ),
    )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError(
            "Failed to enable shares for all requested tree entities.", result
        )
    return result
