"""Discovery wrappers."""

from __future__ import annotations

from kaiten_cli.registry import describe, examples_for, search


def search_tools(query: str, limit: int = 5) -> list[dict]:
    return [
        {
            "canonical_name": tool.canonical_name,
            "mcp_alias": tool.mcp_alias,
            "description": tool.description,
        }
        for tool in search(query, limit=limit)
    ]


def describe_tool(identifier: str) -> dict:
    return describe(identifier)


def tool_examples(identifier: str) -> list[str]:
    return examples_for(identifier)

