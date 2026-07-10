from __future__ import annotations

import json
from dataclasses import replace

import pytest

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.input import merge_inputs, validate_payload
from kaiten_cli.models import UNSET
from kaiten_cli.registry import resolve_tool


def test_merge_inputs_from_file_with_override(tmp_path):
    tool = resolve_tool("cards.create")
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(
        json.dumps({"title": "From file", "board_id": 7, "description": "draft"}), encoding="utf-8"
    )

    result = merge_inputs(
        tool,
        {"title": "Explicit", "board_id": UNSET, "description": UNSET},
        from_file=str(payload_file),
    )

    assert result["title"] == "Explicit"
    assert result["board_id"] == 7
    assert result["description"] == "draft"


def test_merge_inputs_parses_array_from_file(tmp_path):
    tool = resolve_tool("cards.create")
    tags_file = tmp_path / "tags.json"
    tags_file.write_text('["one","two"]', encoding="utf-8")

    result = merge_inputs(
        tool,
        {"title": "Task", "board_id": 1, "tags": f"@{tags_file}"},
    )

    assert result["tags"] == ["one", "two"]


def test_merge_inputs_parses_nullable_null_literal():
    tool = resolve_tool("cards.update")
    result = merge_inputs(tool, {"card_id": "PROJ-1", "description": "null"})
    assert result["description"] is None


def test_merge_inputs_accepts_nullable_enum_null_literal():
    tool = resolve_tool("planned-relations.update")
    result = merge_inputs(
        tool,
        {"card_id": 10, "target_card_id": 11, "gap": "null", "gap_type": "null"},
    )

    assert result["gap"] is None
    assert result["gap_type"] is None


def test_merge_inputs_rejects_invalid_nullable_enum_value():
    tool = resolve_tool("planned-relations.update")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_id": 10, "target_card_id": 11, "gap": 2, "gap_type": "weeks"})


def test_merge_inputs_rejects_unknown_fields(tmp_path):
    tool = resolve_tool("spaces.create")
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps({"title": "Space", "unknown": 1}), encoding="utf-8")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"title": UNSET}, from_file=str(payload_file))


def test_merge_inputs_rejects_empty_history_batch_ids():
    tool = resolve_tool("card-location-history.batch-get")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_ids": "[]"})


def test_merge_inputs_rejects_history_batch_workers_above_limit():
    tool = resolve_tool("card-location-history.batch-get")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_ids": "[1,2]", "workers": 7})


def test_merge_inputs_rejects_empty_cards_batch_ids():
    tool = resolve_tool("cards.batch-get")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_ids": "[]"})


def test_merge_inputs_rejects_time_logs_batch_workers_above_limit():
    tool = resolve_tool("time-logs.batch-list")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_ids": "[1,2]", "workers": 7})


def test_merge_inputs_rejects_invalid_automation_action_item_with_path():
    tool = resolve_tool("automations.create")

    with pytest.raises(ValidationError, match=r"actions\[0\].*expected object"):
        merge_inputs(
            tool,
            {
                "space_id": 1,
                "name": "Invalid automation",
                "trigger": {"type": "card_created"},
                "actions": [1],
            },
        )


def test_validate_payload_recurses_through_objects_arrays_required_and_enum():
    tool = replace(
        resolve_tool("spaces.create"),
        input_schema={
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {
                        "rules": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "mode": {"type": "string", "enum": ["safe", "fast"]},
                                    "limit": {"type": "integer"},
                                },
                                "required": ["mode", "limit"],
                            },
                        }
                    },
                    "required": ["rules"],
                }
            },
            "required": ["config"],
        },
    )

    with pytest.raises(ValidationError, match=r"config\.rules\[0\].*limit"):
        validate_payload(tool, {"config": {"rules": [{"mode": "safe"}]}})

    with pytest.raises(ValidationError, match=r"config\.rules\[0\]\.mode.*safe, fast"):
        validate_payload(tool, {"config": {"rules": [{"mode": "unsafe", "limit": 1}]}})

    with pytest.raises(ValidationError, match=r"config\.rules\[0\]\.limit.*expected integer"):
        validate_payload(tool, {"config": {"rules": [{"mode": "safe", "limit": True}]}})


def test_validate_payload_rejects_additional_properties_only_when_explicitly_false():
    nested_schema = {
        "type": "object",
        "properties": {"known": {"type": "string"}},
    }
    tool = replace(
        resolve_tool("spaces.create"),
        input_schema={
            "type": "object",
            "properties": {"config": nested_schema},
            "required": ["config"],
        },
    )

    validate_payload(tool, {"config": {"known": "yes"}, "extension": 1})
    validate_payload(tool, {"config": {"known": "yes", "extension": 1}})

    strict_tool = replace(
        tool,
        input_schema={
            "type": "object",
            "properties": {
                "config": {**nested_schema, "additionalProperties": False},
            },
            "required": ["config"],
        },
    )
    with pytest.raises(ValidationError, match=r"Unknown field\(s\) at config: extension"):
        validate_payload(strict_tool, {"config": {"known": "yes", "extension": 1}})

    strict_root_tool = replace(
        tool, input_schema={**tool.input_schema, "additionalProperties": False}
    )
    with pytest.raises(ValidationError, match=r"Unknown field\(s\) at payload: extension"):
        validate_payload(strict_root_tool, {"config": {"known": "yes"}, "extension": 1})
