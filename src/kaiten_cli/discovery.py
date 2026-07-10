"""Discovery wrappers."""

from __future__ import annotations

from kaiten_cli.registry import cache_guidance_for, describe, examples_for, search
from kaiten_cli.registry.live_contracts import has_special_live_contract


def search_tools(query: str, limit: int = 5) -> list[dict]:
    return [
        {
            "canonical_name": tool.canonical_name,
            "mcp_alias": tool.mcp_alias,
            "description": tool.description,
            "method": tool.operation.method,
            "mutation": tool.is_mutation,
            "read_only_allowed": tool.read_only_allowed,
            "remote_side_effects": tool.remote_side_effects,
            "heavy": tool.response_policy.heavy,
            "execution_mode": tool.execution_mode,
            "cache_policy": tool.cache_policy,
            "cache_guidance": cache_guidance_for(tool),
            "has_special_live_contract": has_special_live_contract(tool.canonical_name),
            "bulk_alternative": tool.bulk_alternative,
            "usage_notes": list(tool.usage_notes),
        }
        for tool in search(query, limit=limit)
    ]


def describe_tool(identifier: str) -> dict:
    return describe(identifier)


def tool_examples(identifier: str) -> list[str]:
    return examples_for(identifier)
