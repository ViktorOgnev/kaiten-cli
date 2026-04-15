from __future__ import annotations

from kaiten_cli.discovery import describe_tool, search_tools, tool_examples


def test_search_tools_finds_cards():
    results = search_tools("find cards by title")
    assert results
    assert results[0]["canonical_name"] == "cards.list"
    assert results[0]["method"] == "GET"
    assert results[0]["mutation"] is False
    assert results[0]["heavy"] is False
    assert results[0]["execution_mode"] == "direct_http"
    assert results[0]["has_special_live_contract"] is False


def test_describe_tool_contains_alias_and_arguments():
    description = describe_tool("cards.create")
    assert description["mcp_alias"] == "kaiten_create_card"
    assert description["mutation"] is True
    assert description["execution_mode"] == "direct_http"
    assert description["input_modes"] == ["options", "from_file", "stdin_json"]
    assert "compact_supported" in description["response_policy"]
    assert description["response_policy"]["result_kind"] == "entity"
    assert any(arg["name"] == "title" and arg["required"] for arg in description["arguments"])
    assert any(arg["name"] == "board_id" and arg["type_display"] == "integer" for arg in description["arguments"])


def test_describe_tool_includes_live_contract_and_response_policy_metadata():
    description = describe_tool("boards.delete")

    assert description["mutation"] is True
    assert description["execution_mode"] == "direct_http"
    assert description["response_policy"]["heavy"] is False
    assert description["live_contract"]["status"] == "live_passed_with_runtime_fix"
    assert "force flag" in description["live_contract"]["note"]


def test_tool_examples_non_empty():
    examples = tool_examples("cards.list")
    assert examples
    assert examples[0].startswith("kaiten cards list")
