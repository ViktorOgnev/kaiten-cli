from __future__ import annotations

from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_spaces_list_accepts_fields():
    tool = resolve_tool("spaces.list")
    payload = merge_inputs(tool, {"compact": True, "fields": "id,title"})
    assert payload["fields"] == "id,title"


def test_boards_list_accepts_fields():
    tool = resolve_tool("boards.list")
    payload = merge_inputs(tool, {"space_id": 10, "fields": "id,title"})
    assert payload["fields"] == "id,title"


def test_cards_get_accepts_fields():
    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 10, "fields": "id,title,state", "compact": True})
    assert payload["fields"] == "id,title,state"
    assert payload["compact"] is True
