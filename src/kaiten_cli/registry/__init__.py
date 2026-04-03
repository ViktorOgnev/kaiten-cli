"""Tool registry and discovery helpers."""

from __future__ import annotations

import difflib
from collections import defaultdict
from collections.abc import Iterable

from kaiten_cli.models import ToolSpec
from kaiten_cli.registry.boards import TOOLS as BOARD_TOOLS
from kaiten_cli.registry.blockers import TOOLS as BLOCKER_TOOLS
from kaiten_cli.registry.card_relations import TOOLS as CARD_RELATION_TOOLS
from kaiten_cli.registry.cards import TOOLS as CARD_TOOLS
from kaiten_cli.registry.checklists import TOOLS as CHECKLIST_TOOLS
from kaiten_cli.registry.columns import TOOLS as COLUMN_TOOLS
from kaiten_cli.registry.comments import TOOLS as COMMENT_TOOLS
from kaiten_cli.registry.external_links import TOOLS as EXTERNAL_LINK_TOOLS
from kaiten_cli.registry.files import TOOLS as FILE_TOOLS
from kaiten_cli.registry.lanes import TOOLS as LANE_TOOLS
from kaiten_cli.registry.members import TOOLS as MEMBER_TOOLS
from kaiten_cli.registry.projects import TOOLS as PROJECT_TOOLS
from kaiten_cli.registry.spaces import TOOLS as SPACE_TOOLS
from kaiten_cli.registry.tags import TOOLS as TAG_TOOLS
from kaiten_cli.registry.time_logs import TOOLS as TIME_LOG_TOOLS
from kaiten_cli.registry.utilities import TOOLS as UTILITY_TOOLS

TOOL_SET: tuple[ToolSpec, ...] = (
    SPACE_TOOLS
    + BOARD_TOOLS
    + CARD_TOOLS
    + BLOCKER_TOOLS
    + CARD_RELATION_TOOLS
    + COLUMN_TOOLS
    + LANE_TOOLS
    + CHECKLIST_TOOLS
    + COMMENT_TOOLS
    + EXTERNAL_LINK_TOOLS
    + FILE_TOOLS
    + TAG_TOOLS
    + MEMBER_TOOLS
    + PROJECT_TOOLS
    + TIME_LOG_TOOLS
    + UTILITY_TOOLS
)
TOOLS_BY_CANONICAL: dict[str, ToolSpec] = {tool.canonical_name: tool for tool in TOOL_SET}
TOOLS_BY_ALIAS: dict[str, ToolSpec] = {tool.mcp_alias: tool for tool in TOOL_SET}


def iter_tools() -> tuple[ToolSpec, ...]:
    return TOOL_SET


def iter_namespaces() -> dict[str, list[ToolSpec]]:
    grouped: dict[str, list[ToolSpec]] = defaultdict(list)
    for tool in TOOL_SET:
        grouped[tool.namespace].append(tool)
    return {key: sorted(value, key=lambda item: item.action) for key, value in grouped.items()}


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
    return [example.command for example in tool.examples]


def describe(identifier: str) -> dict:
    tool = resolve_tool(identifier)
    properties = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))
    return {
        "canonical_name": tool.canonical_name,
        "mcp_alias": tool.mcp_alias,
        "description": tool.description,
        "method": tool.operation.method,
        "path_template": tool.operation.path_template,
        "arguments": [
            {
                "name": name,
                "required": name in required,
                "type": definition.get("type"),
                "enum": definition.get("enum"),
                "description": definition.get("description", ""),
            }
            for name, definition in properties.items()
        ],
        "examples": examples_for(identifier),
    }
