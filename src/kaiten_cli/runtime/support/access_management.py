"""Request validation and bounded reads for access-management endpoints."""

from __future__ import annotations

import time

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.behaviors import payload_body_request
from kaiten_cli.runtime.support.pagination import validate_page_bounds


def story_map_create_request(tool, payload, path, query, body):
    """Match document creation: some server versions require an explicit position."""
    prepared = dict(body or {})
    prepared.setdefault("sort_order", int(time.time()))
    return path, query, prepared


def company_permissions_request(tool, payload, path, query, body):
    """Flatten the existing payload input before checking permission formats."""
    path, query, body = payload_body_request(tool, payload, path, query, body)
    attributes = body or {}
    if "permissions" in attributes and "named_permissions" in attributes:
        raise ValidationError(tr("Send permissions or named_permissions, not both."))
    if "named_permissions" in attributes:
        named = attributes["named_permissions"]
        if not isinstance(named, dict) or any(type(value) is not bool for value in named.values()):
            raise ValidationError(tr("named_permissions must map permission names to booleans."))
    return path, query, body


def validate_entity_user(tool, payload):
    if tool.action == "add" and not (payload.get("user_id") or payload.get("email")):
        raise ValidationError(tr("Provide user_id or email to add an entity user."))


def validate_access_list_all(tool, payload):
    del tool
    validate_page_bounds(
        page_size=payload.get("page_size", 100), max_pages=payload.get("max_pages", 100)
    )


async def execute_admin_list_all(client, tool, payload, path, query, body, timeout, reporter):
    params = dict(query or {})
    params.setdefault("entity_types", "space,document,document_group,story_map")
    return await execute_access_list_all(
        client, tool, payload, path, params, body, timeout, reporter
    )


async def execute_access_list_all(client, tool, payload, path, query, body, timeout, reporter):
    """Read UID entities; never accept repeated pages as legacy success."""
    del tool, body
    validate_access_list_all(None, payload)
    page_size = payload.get("page_size", 100)
    max_pages = payload.get("max_pages", 100)
    params = dict(query or {})
    rows = []
    seen = set()
    for page_index in range(max_pages):
        if reporter:
            reporter(tr("Reading entity page {value_0}.", value_0=page_index + 1))
        page = await client.get(
            path,
            params={**params, "limit": page_size, "offset": page_index * page_size},
            timeout=timeout,
        )
        if not isinstance(page, list) or len(page) > page_size:
            raise ConfigError(tr("Entity pagination returned an invalid page."))
        for row in page:
            if not isinstance(row, dict) or not isinstance(row.get("uid"), str) or not row["uid"]:
                raise ConfigError(tr("Entity pagination returned an invalid entity."))
            if row["uid"] in seen:
                raise ConfigError(
                    tr("Entity pagination repeated an entity; the result may be incomplete.")
                )
            seen.add(row["uid"])
        rows.extend(page)
        if len(page) < page_size:
            return rows
    raise ConfigError(tr("Entity pagination reached max_pages; refusing an incomplete result."))
