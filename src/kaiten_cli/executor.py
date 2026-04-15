"""Request planning and tool execution."""

from __future__ import annotations

import asyncio
from typing import Any

from kaiten_cli.audit_support import fetch_all_space_activity
from kaiten_cli.cards_support import fetch_all_cards
from kaiten_cli.client import DEFAULT_TIMEOUT, HEAVY_TIMEOUT, KaitenClient
from kaiten_cli.document_support import prepare_document_body
from kaiten_cli.errors import ConfigError
from kaiten_cli.models import ResolvedProfile, ToolSpec
from kaiten_cli.project_support import fetch_project_cards
from kaiten_cli.profiles import resolve_profile
from kaiten_cli.tree_support import build_tree, fetch_all_entities, list_children
from kaiten_cli.transforms import compact_response, select_fields, strip_base64


def build_request(tool: ToolSpec, payload: dict[str, Any]) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    path_values = {name: str(payload[name]) for name in tool.operation.path_fields}
    path = tool.operation.path_template.format(**path_values)
    query = {
        field: payload[field]
        for field in tool.operation.query_fields
        if field in payload and payload[field] is not None
    } or None
    body = {
        field: payload[field]
        for field in tool.operation.body_fields
        if field in payload
    } or None

    if tool.canonical_name == "cards.archive":
        body = {"condition": 2}
    if tool.canonical_name == "cards.list" and body:
        body = None
    if tool.canonical_name == "planned-relations.add" and body:
        body.setdefault("type", "end-start")
    if tool.canonical_name in {"projects.create", "projects.update"} and body and "title" in body:
        body["name"] = body.pop("title")
    if tool.canonical_name == "card-children.add" and body:
        body = {"card_id": body["child_card_id"]}
    if tool.canonical_name == "card-parents.add" and body:
        body = {"card_id": body["parent_card_id"]}
    if tool.canonical_name == "time-logs.create" and body:
        body.setdefault("role_id", -1)
    if tool.canonical_name in {"documents.create", "documents.update", "document-groups.create"} and body:
        body = prepare_document_body(tool.canonical_name, body)
    if tool.canonical_name == "custom-properties.select-values.delete":
        body = {"deleted": True}
    if tool.canonical_name == "column-subscribers.add" and body:
        body.setdefault("type", 1)
    if tool.canonical_name == "automations.copy" and body and "target_space_id" in body:
        body["targetSpaceId"] = body.pop("target_space_id")
    if tool.canonical_name == "service-desk.services.delete":
        body = {"archived": True}
    if tool.canonical_name == "boards.delete" and "force" in payload:
        query = dict(query or {})
        query["force"] = payload["force"]
        body = {"force": payload["force"]}
    if tool.canonical_name == "saved-filters.create" and body and "name" in body:
        body["title"] = body.pop("name")
    if tool.canonical_name == "saved-filters.update" and body and "name" in body:
        body["title"] = body.pop("name")
    if "limit" in tool.operation.query_fields and tool.response_policy.default_limit is not None:
        query = dict(query or {})
        query.setdefault("limit", tool.response_policy.default_limit)
    if tool.canonical_name == "service-desk.stats.get" and query:
        if "date_from" in query:
            query["date-from"] = query.pop("date_from")
        if "date_to" in query:
            query["date-to"] = query.pop("date_to")
    if tool.canonical_name in {"comments.create", "comments.update"} and body:
        format_value = body.pop("format", None)
        if format_value == "html":
            body["type"] = 2
        elif format_value == "markdown":
            body["type"] = 1
    return path, query, body


def timeout_for_tool(tool: ToolSpec) -> float:
    return HEAVY_TIMEOUT if tool.response_policy.heavy else DEFAULT_TIMEOUT


def is_mutation(tool: ToolSpec) -> bool:
    return tool.operation.method.upper() in {"POST", "PATCH", "DELETE"}


def enforce_mutation_safety(tool: ToolSpec, profile: ResolvedProfile) -> None:
    if not is_mutation(tool):
        return
    if profile.sandbox or profile.domain == "sandbox":
        return
    raise ConfigError(
        "Mutation commands are blocked unless the selected profile is marked sandbox or uses the sandbox domain."
    )


async def execute_tool(tool: ToolSpec, payload: dict[str, Any], *, profile_name: str | None = None) -> Any:
    profile = resolve_profile(profile_name)
    enforce_mutation_safety(tool, profile)
    client = KaitenClient(domain=profile.domain, token=profile.token)
    path, query, body = build_request(tool, payload)
    timeout = timeout_for_tool(tool)
    try:
        method = tool.operation.method.upper()
        if tool.canonical_name == "blockers.get":
            blockers = await client.get(path, params=query, timeout=timeout)
            if not isinstance(blockers, list):
                result = blockers
            else:
                blocker_id = payload["blocker_id"]
                result = next((item for item in blockers if isinstance(item, dict) and item.get("id") == blocker_id), None)
        elif tool.canonical_name == "tree.children.list":
            entities = await fetch_all_entities(client, timeout=timeout)
            result = list_children(entities, payload.get("parent_entity_uid"))
        elif tool.canonical_name == "tree.get":
            entities = await fetch_all_entities(client, timeout=timeout)
            result = build_tree(entities, payload.get("root_uid"), payload.get("depth", 0))
        elif tool.canonical_name == "projects.cards.list":
            result = await fetch_project_cards(client, str(payload["project_id"]), timeout=timeout)
        elif tool.canonical_name == "cards.list-all":
            result = await fetch_all_cards(client, payload, timeout=timeout)
        elif tool.canonical_name == "space-activity-all.get":
            result = await fetch_all_space_activity(client, payload, timeout=timeout)
        elif method == "GET":
            result = await client.get(path, params=query, timeout=timeout)
        elif method == "POST":
            result = await client.post(path, json=body, timeout=timeout)
        elif method == "PATCH":
            result = await client.patch(path, json=body, timeout=timeout)
        elif method == "DELETE":
            result = await client.delete(path, json=body, timeout=timeout)
        else:  # pragma: no cover - impossible with current registry
            raise ConfigError(f"Unsupported method: {method}")
    finally:
        await client.close()

    compact_enabled = bool(payload.get("compact", False))
    if tool.canonical_name == "cards.list-all" and "compact" not in payload:
        compact_enabled = True
    if tool.canonical_name == "space-activity-all.get" and "compact" not in payload:
        compact_enabled = True
    if tool.response_policy.compact_supported:
        result = compact_response(result, compact_enabled)
    if tool.response_policy.fields_supported:
        result = select_fields(result, payload.get("fields"))
    result, _ = strip_base64(result)
    return result


def execute_tool_sync(tool: ToolSpec, payload: dict[str, Any], *, profile_name: str | None = None) -> Any:
    return asyncio.run(execute_tool(tool, payload, profile_name=profile_name))
