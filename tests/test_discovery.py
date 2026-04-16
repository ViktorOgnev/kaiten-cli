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
    assert results[0]["cache_policy"] == "request_scope"
    assert results[0]["has_special_live_contract"] is False


def test_describe_tool_contains_alias_and_arguments():
    description = describe_tool("cards.create")
    assert description["mcp_alias"] == "kaiten_create_card"
    assert description["mutation"] is True
    assert description["execution_mode"] == "direct_http"
    assert description["cache_policy"] == "none"
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


def test_describe_tool_includes_usage_notes_and_bulk_alternative():
    description = describe_tool("card-location-history.get")

    assert description["bulk_alternative"] == "card-location-history.batch-get"
    assert description["cache_policy"] == "request_scope"
    assert any("per-card read" in note for note in description["usage_notes"])

    bulk_description = describe_tool("cards.list-all")
    assert any("selection=all|active_only|archived_only" in note for note in bulk_description["usage_notes"])

    children = describe_tool("card-children.list")
    assert children["bulk_alternative"] == "card-children.batch-list"
    assert any("per-card read" in note for note in children["usage_notes"])

    comments = describe_tool("comments.list")
    assert comments["bulk_alternative"] == "comments.batch-list"
    assert any("per-card read" in note for note in comments["usage_notes"])

    activity = describe_tool("space-activity.get")
    assert activity["bulk_alternative"] == "space-activity-all.get"
    assert any("manual offset loops" in note for note in activity["usage_notes"])

    chart = describe_tool("charts.summary.get")
    assert any("card-location-history.batch-get" in note for note in chart["usage_notes"])


def test_describe_tool_includes_persistent_cache_policy_for_safe_entity_reads():
    description = describe_tool("cards.get")

    assert description["cache_policy"] == "persistent_opt_in"

    compute_job = describe_tool("compute-jobs.get")
    assert compute_job["cache_policy"] == "none"


def test_tool_examples_non_empty():
    examples = tool_examples("cards.list")
    assert examples
    assert examples[0].startswith("kaiten cards list")


def test_search_tools_exposes_usage_notes_and_bulk_alternative():
    results = search_tools("card-children.batch-list")
    assert results
    assert results[0]["canonical_name"] == "card-children.batch-list"
    assert results[0]["usage_notes"]
    assert results[0]["bulk_alternative"] is None
