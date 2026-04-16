"""Discovery wrappers."""

from __future__ import annotations

from kaiten_cli.registry import describe, examples_for, search
from kaiten_cli.registry.live_contracts import has_special_live_contract


def search_tools(query: str, limit: int = 5) -> list[dict]:
    return [
        {
            "canonical_name": tool.canonical_name,
            "mcp_alias": tool.mcp_alias,
            "description": tool.description,
            "method": tool.operation.method,
            "mutation": tool.is_mutation,
            "heavy": tool.response_policy.heavy,
            "execution_mode": tool.execution_mode,
            "cache_policy": tool.cache_policy,
            "has_special_live_contract": has_special_live_contract(tool.canonical_name),
        }
        for tool in search(query, limit=limit)
    ]


def describe_tool(identifier: str) -> dict:
    return describe(identifier)


def tool_examples(identifier: str) -> list[str]:
    return examples_for(identifier)
