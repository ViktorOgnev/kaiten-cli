from __future__ import annotations

from kaiten_cli.discovery import describe_tool, search_tools, tool_examples


def test_search_tools_finds_cards():
    results = search_tools("find cards by title")
    assert results
    assert results[0]["canonical_name"] == "cards.list"


def test_describe_tool_contains_alias_and_arguments():
    description = describe_tool("cards.create")
    assert description["mcp_alias"] == "kaiten_create_card"
    assert any(arg["name"] == "title" and arg["required"] for arg in description["arguments"])


def test_tool_examples_non_empty():
    examples = tool_examples("cards.list")
    assert examples
    assert examples[0].startswith("kaiten cards list")

