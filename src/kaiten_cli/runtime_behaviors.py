"""Declarative runtime behavior for tools with non-trivial execution."""

from __future__ import annotations

from typing import Any

from kaiten_cli.audit_support import fetch_all_space_activity
from kaiten_cli.cards_support import fetch_all_cards
from kaiten_cli.document_support import prepare_document_body
from kaiten_cli.project_support import fetch_project_cards
from kaiten_cli.tree_support import build_tree, fetch_all_entities, list_children

Query = dict[str, Any] | None
Body = dict[str, Any] | None


def archive_card_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    return path, query, {"condition": 2}


def planned_relation_add_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    shaped.setdefault("type", "end-start")
    return path, query, shaped


def project_title_to_name_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    if "title" in shaped:
        shaped["name"] = shaped.pop("title")
    return path, query, shaped


def card_child_add_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    return path, query, {"card_id": shaped["child_card_id"]}


def card_parent_add_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    return path, query, {"card_id": shaped["parent_card_id"]}


def default_role_time_log_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    shaped.setdefault("role_id", -1)
    return path, query, shaped


def prepare_document_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    return path, query, prepare_document_body(tool.canonical_name, dict(body or {}))


def select_value_soft_delete_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    return path, query, {"deleted": True}


def column_subscriber_default_type_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    shaped.setdefault("type", 1)
    return path, query, shaped


def automation_copy_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    if "target_space_id" in shaped:
        shaped["targetSpaceId"] = shaped.pop("target_space_id")
    return path, query, shaped


def archive_service_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    return path, query, {"archived": True}


def board_delete_force_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    if "force" not in payload:
        return path, query, body
    shaped_query = dict(query or {})
    shaped_query["force"] = payload["force"]
    return path, shaped_query, {"force": payload["force"]}


def saved_filter_title_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    if "name" in shaped:
        shaped["title"] = shaped.pop("name")
    return path, query, shaped


def service_desk_stats_query_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    if "date_from" in shaped_query:
        shaped_query["date-from"] = shaped_query.pop("date_from")
    if "date_to" in shaped_query:
        shaped_query["date-to"] = shaped_query.pop("date_to")
    return path, shaped_query, body


def comment_format_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    format_value = shaped.pop("format", None)
    if format_value == "html":
        shaped["type"] = 2
    elif format_value == "markdown":
        shaped["type"] = 1
    return path, query, shaped


async def execute_blockers_get(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: custom read by filtering the blockers list")
    blockers = await client.get(path, params=query, timeout=timeout)
    if not isinstance(blockers, list):
        return blockers
    blocker_id = payload["blocker_id"]
    return next(
        (item for item in blockers if isinstance(item, dict) and item.get("id") == blocker_id),
        None,
    )


async def execute_tree_children_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: aggregated read from spaces, documents, and document groups")
    entities = await fetch_all_entities(client, timeout=timeout)
    return list_children(entities, payload.get("parent_entity_uid"))


async def execute_tree_get(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: aggregated tree build from spaces, documents, and document groups")
    entities = await fetch_all_entities(client, timeout=timeout)
    return build_tree(entities, payload.get("root_uid"), payload.get("depth", 0))


async def execute_project_cards_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: synthetic read with direct endpoint and embedded project fallback")
    return await fetch_project_cards(client, str(payload["project_id"]), timeout=timeout, reporter=reporter)


async def execute_cards_list_all(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: aggregated bounded pagination over /cards")
    return await fetch_all_cards(client, payload, timeout=timeout)


async def execute_space_activity_all(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: aggregated bounded pagination over /spaces/{space_id}/activity")
    return await fetch_all_space_activity(client, payload, timeout=timeout)
