"""Tool registry and discovery helpers."""

from __future__ import annotations

import difflib
from typing import Any

from kaiten_cli.models import (
    CACHE_POLICY_NONE,
    CACHE_POLICY_PERSISTENT_HEAVY,
    CACHE_POLICY_PERSISTENT_OPT_IN,
    CACHE_POLICY_REQUEST_SCOPE,
    ToolSpec,
    example_commands,
    format_schema_type,
)
from kaiten_cli.registry.live_contracts import get_live_contract, has_special_live_contract
from kaiten_cli.registry.addons import TOOLS as ADDON_TOOLS
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
from kaiten_cli.registry.custom_directories import TOOLS as CUSTOM_DIRECTORY_TOOLS
from kaiten_cli.registry.custom_properties import TOOLS as CUSTOM_PROPERTY_TOOLS
from kaiten_cli.registry.documents import TOOLS as DOCUMENT_TOOLS
from kaiten_cli.registry.dashboards import TOOLS as DASHBOARD_TOOLS
from kaiten_cli.registry.external_links import TOOLS as EXTERNAL_LINK_TOOLS
from kaiten_cli.registry.files import TOOLS as FILE_TOOLS
from kaiten_cli.registry.github_addon import TOOLS as GITHUB_ADDON_TOOLS
from kaiten_cli.registry.iterations import TOOLS as ITERATION_TOOLS
from kaiten_cli.registry.lanes import TOOLS as LANE_TOOLS
from kaiten_cli.registry.members import TOOLS as MEMBER_TOOLS
from kaiten_cli.registry.projects import TOOLS as PROJECT_TOOLS
from kaiten_cli.registry.query import TOOLS as QUERY_TOOLS
from kaiten_cli.registry.roles_and_groups import TOOLS as ROLE_AND_GROUP_TOOLS
from kaiten_cli.registry.scim import TOOLS as SCIM_TOOLS
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

REGISTRY_MODULES: tuple[tuple[str, tuple[ToolSpec, ...]], ...] = (
    ("spaces", SPACE_TOOLS),
    ("automations", AUTOMATION_TOOLS),
    ("addons", ADDON_TOOLS),
    ("github_addon", GITHUB_ADDON_TOOLS),
    ("boards", BOARD_TOOLS),
    ("cards", CARD_TOOLS),
    ("card_types", CARD_TYPE_TOOLS),
    ("charts", CHART_TOOLS),
    ("blockers", BLOCKER_TOOLS),
    ("card_relations", CARD_RELATION_TOOLS),
    ("columns", COLUMN_TOOLS),
    ("lanes", LANE_TOOLS),
    ("checklists", CHECKLIST_TOOLS),
    ("comments", COMMENT_TOOLS),
    ("custom_directories", CUSTOM_DIRECTORY_TOOLS),
    ("custom_properties", CUSTOM_PROPERTY_TOOLS),
    ("documents", DOCUMENT_TOOLS),
    ("dashboards", DASHBOARD_TOOLS),
    ("external_links", EXTERNAL_LINK_TOOLS),
    ("files", FILE_TOOLS),
    ("iterations", ITERATION_TOOLS),
    ("tags", TAG_TOOLS),
    ("members", MEMBER_TOOLS),
    ("projects", PROJECT_TOOLS),
    ("query", QUERY_TOOLS),
    ("roles_and_groups", ROLE_AND_GROUP_TOOLS),
    ("scim", SCIM_TOOLS),
    ("service_desk", SERVICE_DESK_TOOLS),
    ("audit_and_analytics", AUDIT_AND_ANALYTICS_TOOLS),
    ("snapshot", SNAPSHOT_TOOLS),
    ("time_logs", TIME_LOG_TOOLS),
    ("subscribers", SUBSCRIBER_TOOLS),
    ("tree", TREE_TOOLS),
    ("utilities", UTILITY_TOOLS),
    ("webhooks", WEBHOOK_TOOLS),
)
TOOL_SET: tuple[ToolSpec, ...] = tuple(
    tool for _, module_tools in REGISTRY_MODULES for tool in module_tools
)
TOOLS_BY_CANONICAL: dict[str, ToolSpec] = {tool.canonical_name: tool for tool in TOOL_SET}
TOOLS_BY_ALIAS: dict[str, ToolSpec] = {tool.mcp_alias: tool for tool in TOOL_SET}


def iter_tools() -> tuple[ToolSpec, ...]:
    return TOOL_SET


def iter_module_tools() -> tuple[tuple[str, tuple[ToolSpec, ...]], ...]:
    return REGISTRY_MODULES


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
    return [
        tool
        for _, tool in sorted(scores, key=lambda item: (-item[0], item[1].canonical_name))[:limit]
    ]


def examples_for(identifier: str) -> list[str]:
    tool = resolve_tool(identifier)
    return example_commands(tool.examples)


def cache_guidance_for(tool: ToolSpec) -> dict[str, Any]:
    common = {
        "default_mode": "auto",
        "available_modes": ["auto", "off", "readwrite", "refresh"],
        "recommended_mode": "auto",
        "off_hint": (
            "Use --cache-mode off only for cache debugging, privacy-sensitive reads, "
            "or high-churn polling."
        ),
        "readwrite_hint": (
            "Use --cache-mode readwrite with an explicit --cache-ttl-seconds value "
            "when a fixed TTL is required."
        ),
    }
    if tool.cache_policy == CACHE_POLICY_NONE:
        return {
            **common,
            "strategy": "none",
            "guidance": "This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.",
            "refresh_hint": "No cache refresh is needed.",
        }
    if tool.cache_policy == CACHE_POLICY_PERSISTENT_HEAVY:
        return {
            **common,
            "strategy": "heavy_persistent",
            "guidance": "Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.",
            "refresh_hint": "Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.",
        }
    if tool.cache_policy == CACHE_POLICY_PERSISTENT_OPT_IN:
        return {
            **common,
            "strategy": "entity_or_reference_persistent",
            "guidance": "Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.",
            "refresh_hint": "Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.",
        }
    if tool.cache_policy == CACHE_POLICY_REQUEST_SCOPE:
        return {
            **common,
            "strategy": "request_scope",
            "guidance": "Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.",
            "refresh_hint": "No disk cache is read by default for this command.",
        }
    return {
        **common,
        "strategy": tool.cache_policy,
        "guidance": "Check command notes for cache behavior.",
        "refresh_hint": "Use --cache-mode refresh only if the command supports persistent cache.",
    }


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
        "read_only_allowed": tool.read_only_allowed,
        "remote_side_effects": tool.remote_side_effects,
        "execution_mode": tool.execution_mode,
        "cache_policy": tool.cache_policy,
        "cache_guidance": cache_guidance_for(tool),
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
