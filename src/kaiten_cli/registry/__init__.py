"""Tool registry and discovery helpers."""

from __future__ import annotations

import difflib

from kaiten_cli.models import ToolSpec, example_commands, format_schema_type
from kaiten_cli.registry.live_contracts import get_live_contract, has_special_live_contract
from kaiten_cli.registry.automations import TOOLS as AUTOMATION_TOOLS
from kaiten_cli.registry.boards import TOOLS as BOARD_TOOLS
from kaiten_cli.registry.blockers import TOOLS as BLOCKER_TOOLS
from kaiten_cli.registry.card_relations import TOOLS as CARD_RELATION_TOOLS
from kaiten_cli.registry.cards import TOOLS as CARD_TOOLS
from kaiten_cli.registry.card_types import TOOLS as CARD_TYPE_TOOLS
from kaiten_cli.registry.charts import TOOLS as CHART_TOOLS
from kaiten_cli.registry.checklists import TOOLS as CHECKLIST_TOOLS
from kaiten_cli.registry.columns import TOOLS as COLUMN_TOOLS
from kaiten_cli.registry.comments import TOOLS as COMMENT_TOOLS
from kaiten_cli.registry.custom_properties import TOOLS as CUSTOM_PROPERTY_TOOLS
from kaiten_cli.registry.documents import TOOLS as DOCUMENT_TOOLS
from kaiten_cli.registry.external_links import TOOLS as EXTERNAL_LINK_TOOLS
from kaiten_cli.registry.files import TOOLS as FILE_TOOLS
from kaiten_cli.registry.lanes import TOOLS as LANE_TOOLS
from kaiten_cli.registry.members import TOOLS as MEMBER_TOOLS
from kaiten_cli.registry.projects import TOOLS as PROJECT_TOOLS
from kaiten_cli.registry.query import TOOLS as QUERY_TOOLS
from kaiten_cli.registry.roles_and_groups import TOOLS as ROLE_AND_GROUP_TOOLS
from kaiten_cli.registry.service_desk import TOOLS as SERVICE_DESK_TOOLS
from kaiten_cli.registry.audit_and_analytics import TOOLS as AUDIT_AND_ANALYTICS_TOOLS
from kaiten_cli.registry.spaces import TOOLS as SPACE_TOOLS
from kaiten_cli.registry.snapshot import TOOLS as SNAPSHOT_TOOLS
from kaiten_cli.registry.subscribers import TOOLS as SUBSCRIBER_TOOLS
from kaiten_cli.registry.tags import TOOLS as TAG_TOOLS
from kaiten_cli.registry.time_logs import TOOLS as TIME_LOG_TOOLS
from kaiten_cli.registry.tree import TOOLS as TREE_TOOLS
from kaiten_cli.registry.utilities import TOOLS as UTILITY_TOOLS
from kaiten_cli.registry.webhooks import TOOLS as WEBHOOK_TOOLS

TOOL_SET: tuple[ToolSpec, ...] = (
    SPACE_TOOLS
    + AUTOMATION_TOOLS
    + BOARD_TOOLS
    + CARD_TOOLS
    + CARD_TYPE_TOOLS
    + CHART_TOOLS
    + BLOCKER_TOOLS
    + CARD_RELATION_TOOLS
    + COLUMN_TOOLS
    + LANE_TOOLS
    + CHECKLIST_TOOLS
    + COMMENT_TOOLS
    + CUSTOM_PROPERTY_TOOLS
    + DOCUMENT_TOOLS
    + EXTERNAL_LINK_TOOLS
    + FILE_TOOLS
    + TAG_TOOLS
    + MEMBER_TOOLS
    + PROJECT_TOOLS
    + QUERY_TOOLS
    + ROLE_AND_GROUP_TOOLS
    + SERVICE_DESK_TOOLS
    + AUDIT_AND_ANALYTICS_TOOLS
    + SNAPSHOT_TOOLS
    + TIME_LOG_TOOLS
    + SUBSCRIBER_TOOLS
    + TREE_TOOLS
    + UTILITY_TOOLS
    + WEBHOOK_TOOLS
)
TOOLS_BY_CANONICAL: dict[str, ToolSpec] = {tool.canonical_name: tool for tool in TOOL_SET}
TOOLS_BY_ALIAS: dict[str, ToolSpec] = {tool.mcp_alias: tool for tool in TOOL_SET}


def iter_tools() -> tuple[ToolSpec, ...]:
    return TOOL_SET


def resolve_tool(identifier: str) -> ToolSpec:
    if identifier in TOOLS_BY_CANONICAL:
        return TOOLS_BY_CANONICAL[identifier]
    if identifier in TOOLS_BY_ALIAS:
        return TOOLS_BY_ALIAS[identifier]
    raise KeyError(identifier)


def search(query: str, limit: int = 5) -> list[ToolSpec]:
    query_lc = query.strip().lower()
    scores: list[tuple[float, ToolSpec]] = []
    for tool in TOOL_SET:
        haystack_parts = [
            tool.canonical_name,
            tool.mcp_alias,
            tool.namespace,
            tool.action,
            tool.description,
            tool.bulk_alternative or "",
            " ".join(tool.usage_notes),
            " ".join(example.command for example in tool.examples),
            " ".join(example.description for example in tool.examples),
        ]
        haystack = " ".join(haystack_parts).lower()
        score = 0.0
        if tool.canonical_name == query_lc or tool.mcp_alias == query_lc:
            score += 100.0
        if query_lc in tool.canonical_name:
            score += 30.0
        if query_lc in tool.mcp_alias:
            score += 25.0
        tokens = [token for token in query_lc.replace("-", " ").replace("_", " ").split() if token]
        score += sum(8.0 for token in tokens if token in haystack)
        score += difflib.SequenceMatcher(a=query_lc, b=haystack).ratio() * 10.0
        if score > 0:
            scores.append((score, tool))
    return [tool for _, tool in sorted(scores, key=lambda item: (-item[0], item[1].canonical_name))[:limit]]


def examples_for(identifier: str) -> list[str]:
    tool = resolve_tool(identifier)
    return example_commands(tool.examples)


def describe(identifier: str) -> dict:
    tool = resolve_tool(identifier)
    properties = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))
    payload = {
        "canonical_name": tool.canonical_name,
        "mcp_alias": tool.mcp_alias,
        "description": tool.description,
        "method": tool.operation.method,
        "mutation": tool.is_mutation,
        "execution_mode": tool.execution_mode,
        "cache_policy": tool.cache_policy,
        "path_template": tool.operation.path_template,
        "input_modes": ["options", "from_file", "stdin_json"],
        "response_policy": {
            "compact_supported": tool.response_policy.compact_supported,
            "fields_supported": tool.response_policy.fields_supported,
            "default_limit": tool.response_policy.default_limit,
            "heavy": tool.response_policy.heavy,
            "result_kind": tool.response_policy.result_kind,
            "compact_default": tool.runtime_behavior.compact_default,
        },
        "arguments": [
            {
                "name": name,
                "required": name in required,
                "type": definition.get("type"),
                "type_display": format_schema_type(definition),
                "enum": definition.get("enum"),
                "description": definition.get("description", ""),
            }
            for name, definition in properties.items()
        ],
        "examples": examples_for(identifier),
    }
    if has_special_live_contract(tool.canonical_name):
        contract = get_live_contract(tool.canonical_name)
        payload["live_contract"] = {
            "status": contract.status,
            "note": contract.note,
            "expected_statuses": list(contract.expected_statuses),
        }
    if tool.usage_notes:
        payload["usage_notes"] = list(tool.usage_notes)
    if tool.bulk_alternative is not None:
        payload["bulk_alternative"] = tool.bulk_alternative
    return payload
