"""Helpers for entity tree commands."""

from __future__ import annotations

from typing import Any

from kaiten_cli.errors import ConfigError
from kaiten_cli.runtime.support.pagination import fetch_all_offset_pages

TREE_PAGE_LIMIT = 100
TREE_MAX_PAGES = 200


def sort_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    type_order = {"document_group": 0, "space": 1, "document": 2}
    return sorted(
        entities, key=lambda entity: (type_order.get(entity["type"], 99), entity.get("title", ""))
    )


def strip_id_none(entity: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entity.items() if not (key == "id" and value is None)}


async def fetch_paginated_entities(
    client,
    path: str,
    *,
    timeout: float,
    limit: int = TREE_PAGE_LIMIT,
    max_pages: int = TREE_MAX_PAGES,
    reporter=None,
) -> list[dict[str, Any]]:
    rows = await fetch_all_offset_pages(
        client,
        path,
        timeout=timeout,
        page_size=limit,
        max_pages=max_pages,
        reporter=reporter,
    )
    return [row for row in rows if isinstance(row, dict)]


async def fetch_all_entities(client, *, timeout: float, reporter=None) -> list[dict[str, Any]]:
    spaces_resp = await fetch_paginated_entities(
        client, "/spaces", timeout=timeout, reporter=reporter
    )
    docs_resp = await fetch_paginated_entities(
        client, "/documents", timeout=timeout, reporter=reporter
    )
    groups_resp = await fetch_paginated_entities(
        client, "/document-groups", timeout=timeout, reporter=reporter
    )

    entities: list[dict[str, Any]] = []

    for space in spaces_resp if isinstance(spaces_resp, list) else []:
        uid = space.get("uid")
        if uid is None:
            continue
        entities.append(
            {
                "type": "space",
                "uid": uid,
                "id": space.get("id"),
                "title": space.get("title", ""),
                "parent_entity_uid": space.get("parent_entity_uid"),
            }
        )

    for document in docs_resp if isinstance(docs_resp, list) else []:
        entities.append(
            {
                "type": "document",
                "uid": document.get("uid", ""),
                "id": None,
                "title": document.get("title", ""),
                "parent_entity_uid": document.get("parent_entity_uid"),
            }
        )

    for group in groups_resp if isinstance(groups_resp, list) else []:
        entities.append(
            {
                "type": "document_group",
                "uid": group.get("uid", ""),
                "id": None,
                "title": group.get("title", ""),
                "parent_entity_uid": group.get("parent_entity_uid"),
            }
        )

    return entities


def list_children(entities: list[dict[str, Any]], parent_uid: str | None) -> list[dict[str, Any]]:
    if parent_uid is None:
        known_uids = {entity.get("uid") for entity in entities}
        children = [
            entity for entity in entities if effective_parent_uid(entity, known_uids) is None
        ]
    else:
        children = [entity for entity in entities if entity.get("parent_entity_uid") == parent_uid]
    return [strip_id_none(entity) for entity in sort_entities(children)]


def effective_parent_uid(entity: dict[str, Any], known_uids: set[Any]) -> Any:
    parent_uid = entity.get("parent_entity_uid")
    if parent_uid is not None and parent_uid not in known_uids:
        return None
    return parent_uid


def build_tree(
    entities: list[dict[str, Any]], root_uid: str | None, max_depth: int
) -> list[dict[str, Any]]:
    if root_uid is not None and not any(entity["uid"] == root_uid for entity in entities):
        raise ConfigError(f"Entity with uid '{root_uid}' not found")

    known_uids = {entity.get("uid") for entity in entities}
    by_parent: dict[str | None, list[dict[str, Any]]] = {}
    for entity in entities:
        by_parent.setdefault(effective_parent_uid(entity, known_uids), []).append(entity)

    def recurse(parent_uid: str | None, depth: int) -> list[dict[str, Any]]:
        children = sort_entities(by_parent.get(parent_uid, []))
        result = []
        for child in children:
            node = strip_id_none(child)
            node.pop("parent_entity_uid", None)
            if max_depth == 0 or depth < max_depth:
                node["children"] = recurse(child["uid"], depth + 1)
            else:
                node["children"] = []
            result.append(node)
        return result

    return recurse(root_uid, 0)
