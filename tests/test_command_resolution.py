from __future__ import annotations

from kaiten_cli.registry import resolve_tool


def test_resolve_canonical_name():
    tool = resolve_tool("cards.list")
    assert tool.canonical_name == "cards.list"
    assert tool.mcp_alias == "kaiten_list_cards"


def test_resolve_alias_name():
    tool = resolve_tool("kaiten_list_cards")
    assert tool.canonical_name == "cards.list"

