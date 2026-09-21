from __future__ import annotations

from copy import deepcopy
import json

import pytest

from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request
from kaiten_cli.runtime.input import merge_inputs


ACTION = {"type": "change_asap", "data": {"asap": False}}
DATE = {
    "type": "due_date_on_date",
    "data": {
        "variant": "time_left_before_date",
        "timezone": "UTC",
        "offset": 0,
        "offset_unit": "day",
    },
}


def create(payload):
    tool = resolve_tool("automations.create")
    return build_request(tool, merge_inputs(tool, {"space_id": 1} | payload))[2]


def test_three_documented_variants_and_legacy_omission():
    button = {
        "name": "Done",
        "type": "on_demand",
        "actions": [{"type": "complete_checklists", "data": {}}],
    }
    assert create(button) == button
    event = {"type": "on_action", "trigger": {"type": "card_created"}, "actions": [ACTION]}
    assert create(event) == event
    date = {"type": "on_date", "trigger": DATE, "actions": [ACTION]}
    assert create(date) == date
    legacy = {"name": "Legacy", "trigger": {"type": "card_created"}, "actions": [ACTION]}
    assert create(legacy) == legacy
    assert "type" not in create(legacy)


def test_nested_condition_groups_and_zero_false_survive_round_trip():
    condition = {
        "clause": "or",
        "conditions": [
            {
                "clause": "and",
                "conditions": [
                    {"type": "tag", "operator": "eq", "data": {"tagIds": [1]}, "future": False}
                ],
            }
        ],
    }
    payload = {
        "type": "on_action",
        "trigger": {"type": "card_created", "future": []},
        "actions": [ACTION | {"future": 0}],
        "conditions": condition,
    }
    assert create(payload) == payload
    assert create(json.loads(json.dumps(payload))) == create(payload)


@pytest.mark.parametrize(
    ("changes", "path"),
    [
        ({"actions": []}, "actions"),
        ({"actions": [ACTION] * 11}, "actions"),
        (
            {"actions": [{"type": "change_asap", "data": {"asap": "false"}}]},
            r"actions\[0\].data.asap",
        ),
        ({"actions": [{"type": "move_to_path", "data": {"boardId": 1}}]}, r"actions\[0\].data"),
        ({"conditions": {"clause": "xor", "conditions": []}}, "conditions.clause"),
        (
            {
                "conditions": {
                    "clause": "and",
                    "conditions": [{"type": "tag", "operator": "eq", "data": {"tagIds": ["1"]}}],
                }
            },
            r"conditions.conditions\[0\].data.tagIds\[0\]",
        ),
        ({"name": "x" * 257}, "name"),
        ({"trigger": {"type": 123}}, "trigger.type"),
    ],
)
def test_known_invalid_shapes_report_field_paths(changes, path):
    payload = {"type": "on_action", "trigger": {"type": "card_created"}, "actions": [ACTION]}
    with pytest.raises(ValidationError, match=path):
        create(payload | changes)


def test_known_incompatible_type_trigger_and_action():
    with pytest.raises(ValidationError, match="trigger.type"):
        create({"type": "on_action", "trigger": DATE, "actions": [ACTION]})
    with pytest.raises(ValidationError, match=r"actions\[0\].type"):
        create(
            {
                "type": "on_action",
                "trigger": {"type": "card_type_changed"},
                "actions": [{"type": "change_type", "data": {"typeId": 1}}],
            }
        )


def test_future_variants_and_on_workflow_are_preserved():
    for kind in ["on_workflow", "on_future"]:
        payload = {
            "type": kind,
            "trigger": {"type": "future_trigger", "data": {"v": None}},
            "actions": [{"type": "future_action", "data": {"v": False}}],
            "conditions": {"type": "future_condition", "newOperator": 17},
        }
        assert create(payload) == payload
    # A new server action remains valid alongside a known trigger.
    payload = {
        "type": "on_action",
        "trigger": {"type": "card_created"},
        "actions": [{"type": "future_action", "arbitrary": []}],
    }
    assert create(payload) == payload


def test_partial_patch_does_not_require_unmodified_fields():
    tool = resolve_tool("automations.update")
    for patch in [
        {"name": "Renamed"},
        {"status": "disabled"},
        {"trigger": {"hasToFireOnCardCreation": False}},
        {"conditions": {}},
    ]:
        payload = merge_inputs(tool, {"space_id": 1, "automation_id": "auto"} | patch)
        assert build_request(tool, payload)[2] == patch


def test_deep_conditions_fail_with_validation_error():
    conditions = {"type": "future_condition"}
    for _ in range(66):
        conditions = {"clause": "and", "conditions": [conditions]}
    with pytest.raises(ValidationError, match="maximum condition nesting"):
        create(
            {"type": "on_demand", "name": "Nested", "actions": [ACTION], "conditions": conditions}
        )


def test_source_schema_is_not_mutated_by_validation():
    tool = resolve_tool("automations.create")
    before = deepcopy(tool.input_schema)
    create({"type": "on_action", "trigger": {"type": "card_created"}, "actions": [ACTION]})
    assert tool.input_schema == before


def test_dynamic_custom_property_keys_and_numeric_enum():
    from kaiten_cli.registry.automation_schema import AUTOMATION_SCHEMAS
    from kaiten_cli.runtime.input import _validate_schema

    action = AUTOMATION_SCHEMAS["actions"]["property_add_to_child_card"]
    schema = action["properties"]["data"]["properties"]["customProperties"]
    # The portal's {custom_property_id} is a key template, not a literal required key.
    _validate_schema(
        {"customProperty_97": {"id": 97, "value": "value"}}, schema, path="data.customProperties"
    )
    value_schema = next(iter(schema["patternProperties"].values()))["properties"]["value"]
    date = {"apply_date_mode": 1, "timezone": "UTC", "tzOffset": 0, "relative_days_offset": 0}
    _validate_schema(date, value_schema, path="value")
    with pytest.raises(ValidationError, match="apply_date_mode"):
        _validate_schema(date | {"apply_date_mode": True}, value_schema, path="value")


def test_calendar_tables_with_missing_header_are_normalized():
    from kaiten_cli.registry.automation_schema import AUTOMATION_SCHEMAS

    fields = AUTOMATION_SCHEMAS["triggers"]["custom_property_date_on_date"]["properties"]["data"]
    assert {"timezone", "variant", "propertyId"} <= set(fields["required"])
    assert fields["properties"]["offset_units"]["enum"] == ["hour", "day"]
    assert fields["properties"]["offset_unit"]["enum"] == ["hour", "day"]


def test_date_offset_variants_require_offset_and_accept_both_unit_spellings():
    for field in ("offset_unit", "offset_units"):
        trigger = deepcopy(DATE)
        trigger["data"].pop("offset_unit")
        trigger["data"][field] = "day"
        payload = {"type": "on_date", "trigger": trigger, "actions": [ACTION]}
        assert create(payload) == payload
    trigger = deepcopy(DATE)
    trigger["data"].pop("offset")
    with pytest.raises(ValidationError, match="trigger.data: offset"):
        create({"type": "on_date", "trigger": trigger, "actions": [ACTION]})
