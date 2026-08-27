"""Declarative runtime behavior for tools with non-trivial execution."""

from __future__ import annotations

import json
from typing import Any

from kaiten_cli.errors import BatchExecutionError, ValidationError
from kaiten_cli.runtime.support.audit import (
    DEFAULT_HISTORY_WORKERS,
    fetch_all_space_activity,
    fetch_card_location_histories,
)
from kaiten_cli.runtime.support.card_move_url import (
    parse_card_url,
    parse_target_url,
    resolve_move_target,
    validate_url_domain,
)
from kaiten_cli.runtime.support.cards import fetch_all_cards, fetch_cards_batch_get
from kaiten_cli.runtime.support.checklists import extract_card_checklists, extract_checklist_items
from kaiten_cli.runtime.support.documents import prepare_document_body
from kaiten_cli.runtime.support.projects import fetch_project_cards
from kaiten_cli.runtime.support.relations import fetch_card_children_batch, fetch_comments_batch
from kaiten_cli.runtime.support.spaces import fetch_space_topology
from kaiten_cli.runtime.support.batch import MAX_BATCH_WORKERS
from kaiten_cli.runtime.support.time_logs import fetch_time_logs_batch
from kaiten_cli.runtime.support.tree import build_tree, fetch_all_entities, list_children
from kaiten_cli.runtime.transforms import compact_response, select_fields, strip_base64

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


def document_list_search_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    if "search_fields" in payload:
        shaped_query["fields"] = payload["search_fields"]
    return path, shaped_query or None, body


def prevent_redirect_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    shaped_query["prevent_redirect"] = True
    return path, shaped_query, body


def checklist_item_compat_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    card_id = payload.get("card_id")
    if card_id is None:
        return path, query, body
    checklist_id = payload["checklist_id"]
    compatibility_path = f"/cards/{card_id}/checklists/{checklist_id}/items"
    if "item_id" in payload:
        compatibility_path += f"/{payload['item_id']}"
    return compatibility_path, query, body


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


def board_get_scoped_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    space_id = payload.get("space_id")
    if space_id is None:
        return path, query, body
    return f"/spaces/{space_id}/boards/{payload['board_id']}", query, body


def board_place_existing_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    shaped.setdefault("top", 0)
    shaped.setdefault("left", 0)
    return path, query, shaped


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


def company_members_section_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    shaped_query.setdefault("for_members_section", True)
    shaped_query.setdefault("offset", 0)
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


def payload_body_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped = dict(body or {})
    payload_body = shaped.pop("payload", None)
    if payload_body is not None:
        if not isinstance(payload_body, dict):
            raise ValidationError("Field payload must be a JSON object.")
        shaped.update(payload_body)
    return path, query, shaped or None


def encode_object_query_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    for key, value in tuple(shaped_query.items()):
        if isinstance(value, dict):
            shaped_query[key] = json.dumps(value, ensure_ascii=False)
    return path, shaped_query or None, body


def scim_query_request(
    tool, payload: dict[str, Any], path: str, query: Query, body: Body
) -> tuple[str, Query, Body]:
    shaped_query = dict(query or {})
    if "start_index" in shaped_query:
        shaped_query["startIndex"] = shaped_query.pop("start_index")
    return path, shaped_query or None, body


def validate_cards_list_all_selection(tool, payload: dict[str, Any]) -> None:
    selection = payload.get("selection")
    if selection is None:
        return
    if "archived" in payload or "condition" in payload:
        raise ValidationError("Field selection cannot be combined with archived or condition.")


def validate_card_id_batch(tool, payload: dict[str, Any]) -> None:
    card_ids = payload.get("card_ids")
    if not isinstance(card_ids, list) or not card_ids:
        raise ValidationError("Field card_ids must be a non-empty array.")
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if workers < 1 or workers > MAX_BATCH_WORKERS:
        raise ValidationError(f"Field workers must be between 1 and {MAX_BATCH_WORKERS}.")


validate_history_batch_get = validate_card_id_batch
validate_cards_batch_get = validate_card_id_batch
validate_time_logs_batch_list = validate_card_id_batch


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
    return await fetch_project_cards(
        client, str(payload["project_id"]), timeout=timeout, reporter=reporter
    )


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


def _shape_move_by_url_card(card: Any, payload: dict[str, Any]) -> Any:
    shaped = compact_response(card, bool(payload.get("compact", False)))
    shaped = select_fields(shaped, payload.get("fields"))
    shaped, _ = strip_base64(shaped)
    return shaped


def _verify_moved_card(card: Any, target: dict[str, Any]) -> None:
    if not isinstance(card, dict):
        raise ValidationError("Move verification failed: final card response is not an object.")

    expected = {
        "board_id": target["board_id"],
        "column_id": target["column_id"],
    }
    if target.get("lane_id") is not None:
        expected["lane_id"] = target["lane_id"]

    mismatches = [
        f"{key}: expected {value}, got {card.get(key)}"
        for key, value in expected.items()
        if card.get(key) != value
    ]
    if mismatches:
        raise ValidationError("Move verification failed: " + "; ".join(mismatches))


async def execute_cards_move_by_url(
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
        reporter("execution: aggregated card move by Kaiten UI URLs")

    card_url = parse_card_url(payload["card_url"])
    target_url = parse_target_url(payload["target_url"])
    validate_url_domain(card_url.domain, client.domain, label="Card URL")
    validate_url_domain(target_url.domain, client.domain, label="Target URL")

    target = await resolve_move_target(
        client,
        target_url,
        lane_id=payload.get("lane_id"),
        timeout=timeout,
    )
    patch_body: dict[str, Any] = {
        "board_id": target["board_id"],
        "column_id": target["column_id"],
    }
    if target.get("lane_id") is not None:
        patch_body["lane_id"] = target["lane_id"]
    if "sort_order" in payload:
        patch_body["sort_order"] = payload["sort_order"]

    if payload.get("dry_run", False):
        return {
            "card_ref": card_url.card_ref,
            "card_space_id": card_url.space_id,
            "target": target,
            "dry_run": True,
            "would_patch": patch_body,
        }

    moved_card = await client.patch(f"/cards/{card_url.card_ref}", json=patch_body, timeout=timeout)
    verified = False
    card = moved_card
    if payload.get("verify", True):
        card = await client.get(f"/cards/{card_url.card_ref}", timeout=timeout)
        _verify_moved_card(card, target)
        verified = True

    return {
        "card_ref": card_url.card_ref,
        "target": target,
        "card": _shape_move_by_url_card(card, payload),
        "verified": verified,
    }


async def execute_card_location_history_batch_get(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if reporter:
        reporter(
            "execution: aggregated batch history fetch over /cards/{card_id}/location-history "
            f"with workers={workers}"
        )
    result = await fetch_card_location_histories(
        domain=client.domain,
        token=client.token,
        card_ids=list(payload["card_ids"]),
        workers=workers,
        fields=payload.get("fields"),
        timeout=timeout,
        reporter=reporter,
        execution_context=client.execution_context,
        cache_policy=client.cache_policy,
    )
    if reporter:
        meta = result["meta"]
        reporter(
            "batch-history: "
            f"requested={meta['requested_count']} unique={meta['unique_count']} "
            f"succeeded={meta['succeeded']} failed={meta['failed']}"
        )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError(
            "Failed to fetch location history for all requested cards.", result
        )
    return result


async def execute_card_children_batch_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if reporter:
        reporter(
            "execution: aggregated batch relation fetch over /cards/{card_id}/children "
            f"with workers={workers}"
        )
    result = await fetch_card_children_batch(
        domain=client.domain,
        token=client.token,
        card_ids=list(payload["card_ids"]),
        workers=workers,
        compact=bool(payload.get("compact", False)),
        fields=payload.get("fields"),
        timeout=timeout,
        reporter=reporter,
        execution_context=client.execution_context,
        cache_policy=client.cache_policy,
    )
    if reporter:
        meta = result["meta"]
        reporter(
            "batch-children: "
            f"requested={meta['requested_count']} unique={meta['unique_count']} "
            f"succeeded={meta['succeeded']} failed={meta['failed']}"
        )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError("Failed to fetch child cards for all requested cards.", result)
    return result


async def execute_cards_batch_get(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if reporter:
        reporter(
            f"execution: aggregated batch card read over /cards/{{card_id}} with workers={workers}"
        )
    result = await fetch_cards_batch_get(
        domain=client.domain,
        token=client.token,
        card_ids=list(payload["card_ids"]),
        workers=workers,
        compact=bool(payload.get("compact", False)),
        fields=payload.get("fields"),
        timeout=timeout,
        reporter=reporter,
        execution_context=client.execution_context,
        cache_policy=client.cache_policy,
    )
    if reporter:
        meta = result["meta"]
        reporter(
            "batch-cards: "
            f"requested={meta['requested_count']} unique={meta['unique_count']} "
            f"succeeded={meta['succeeded']} failed={meta['failed']}"
        )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError("Failed to fetch cards for all requested card IDs.", result)
    return result


async def execute_checklists_list(
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
        reporter("execution: synthetic checklist read from /cards/{card_id} payload")
    card = await client.get(path, timeout=timeout)
    return extract_card_checklists(card if isinstance(card, dict) else {})


async def execute_checklist_items_list(
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
        reporter("execution: synthetic checklist item read from /cards/{card_id} payload")
    card = await client.get(path, timeout=timeout)
    return extract_checklist_items(card if isinstance(card, dict) else {}, payload["checklist_id"])


async def execute_comments_batch_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if reporter:
        reporter(
            "execution: aggregated batch comment fetch over /cards/{card_id}/comments "
            f"with workers={workers}"
        )
    result = await fetch_comments_batch(
        domain=client.domain,
        token=client.token,
        card_ids=list(payload["card_ids"]),
        workers=workers,
        compact=bool(payload.get("compact", False)),
        fields=payload.get("fields"),
        timeout=timeout,
        reporter=reporter,
        execution_context=client.execution_context,
        cache_policy=client.cache_policy,
    )
    if reporter:
        meta = result["meta"]
        reporter(
            "batch-comments: "
            f"requested={meta['requested_count']} unique={meta['unique_count']} "
            f"succeeded={meta['succeeded']} failed={meta['failed']}"
        )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError("Failed to fetch comments for all requested cards.", result)
    return result


async def execute_time_logs_batch_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: Query,
    body: Body,
    timeout: float,
    reporter,
) -> Any:
    workers = payload.get("workers", DEFAULT_HISTORY_WORKERS)
    if reporter:
        reporter(
            "execution: aggregated batch time-log fetch over /cards/{card_id}/time-logs "
            f"with workers={workers}"
        )
    result = await fetch_time_logs_batch(
        domain=client.domain,
        token=client.token,
        card_ids=list(payload["card_ids"]),
        workers=workers,
        for_date=payload.get("for_date"),
        personal=payload.get("personal"),
        compact=bool(payload.get("compact", False)),
        fields=payload.get("fields"),
        timeout=timeout,
        reporter=reporter,
        execution_context=client.execution_context,
        cache_policy=client.cache_policy,
    )
    if reporter:
        meta = result["meta"]
        reporter(
            "batch-time-logs: "
            f"requested={meta['requested_count']} unique={meta['unique_count']} "
            f"succeeded={meta['succeeded']} failed={meta['failed']}"
        )
    if result["meta"]["succeeded"] == 0:
        raise BatchExecutionError("Failed to fetch time logs for all requested cards.", result)
    return result


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


async def execute_space_topology_get(
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
        reporter(
            "execution: aggregated topology read over /spaces/{space_id}/boards and /boards/{board_id}"
        )
    return await fetch_space_topology(client, payload["space_id"], timeout=timeout)
