"""Undocumented space restriction extension, based on Kaiten server schemas."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool, shaping_properties
from kaiten_cli.runtime.behaviors import execute_restriction_get, restriction_copy_request
from kaiten_cli.runtime.support.restrictions import validate_restriction_payload


EXTENSION_NOTE = "Undocumented API extension derived from Kaiten server code; live compatibility is not yet verified."
SPACE_NOTE = (
    "Restrictions belong to a space; boards and columns are selected inside conditions. "
    "Workflow transition restrictions are managed through Workflow API."
)
OPERATORS = [
    "eq",
    "ne",
    "contains",
    "not_contains",
    "start_with",
    "in_groups",
    "not_in_groups",
    "in_company",
    "not_in_company",
    "in_role",
    "not_in_role",
    "is_less",
    "is_more",
    "is_between",
    "any",
    "none",
    "exceeded",
    "not_exceeded",
]


def rule_array(description: str) -> dict:
    return {
        "type": "array",
        "description": description,
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "Condition or restriction type"},
                "created": {"type": "string", "description": "Rule element creation timestamp"},
                "operator": {"type": "string", "enum": OPERATORS, "description": "Rule operator"},
                "data": {"type": "object", "description": "Rule data passed through unchanged"},
            },
            "required": ["type", "created", "operator", "data"],
        },
    }


def rule_properties() -> dict:
    return {
        "name": {"type": ["string", "null"], "maxLength": 256, "description": "Restriction name"},
        "error_text": {
            "type": ["string", "null"],
            "maxLength": 4096,
            "description": "Message shown when the restriction rejects an action",
        },
        "conditions": rule_array("Conditions selecting cards and actions"),
        "restrictions": rule_array("Restrictions on card creation or movement"),
    }


SPACE = {"type": "integer", "description": "Space ID"}
IDENTIFIER = {"type": "string", "format": "uuid", "description": "Restriction ID (UUID)"}
IDS = {"space_id": SPACE, "restriction_id": IDENTIFIER}
BASE_PATH = "/spaces/{space_id}/restrictions"
RULE_ID = "a52165d4-26cc-4483-a272-edfaeff2b1b2"

TOOLS = (
    make_tool(
        canonical_name="restrictions.list",
        mcp_alias="kaiten_list_restrictions",
        description="List all non-removed, non-workflow restrictions in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {"space_id": SPACE, **shaping_properties()},
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template=BASE_PATH, path_fields=("space_id",)),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="list"
        ),
        usage_notes=(
            EXTENSION_NOTE,
            SPACE_NOTE,
            "The server returns the full list without pagination.",
        ),
        search_terms=("ограничения правила создание перемещение карточек", "restriction rules"),
        examples=(
            ExampleSpec(
                command="kaiten --json restrictions list --space-id 1 --compact --fields id,name,status",
                description="List space restrictions.",
            ),
        ),
    ),
    make_tool(
        canonical_name="restrictions.get",
        mcp_alias="kaiten_get_restriction",
        description="Get a space restriction by selecting its UUID from the full list.",
        input_schema={"type": "object", "properties": IDS, "required": list(IDS)},
        operation=OperationSpec(method="GET", path_template=BASE_PATH, path_fields=("space_id",)),
        runtime_behavior=RuntimeBehavior(
            execution_mode="synthetic",
            custom_executor=execute_restriction_get,
            payload_validator=validate_restriction_payload,
        ),
        usage_notes=(
            EXTENSION_NOTE,
            SPACE_NOTE,
            "No single-rule GET handler exists; a missing rule is an explicit error.",
        ),
        search_terms=("ограничения просмотр правила",),
        examples=(
            ExampleSpec(
                command=f"kaiten --json restrictions get --space-id 1 --restriction-id {RULE_ID}",
                description="Read a restriction from its space.",
            ),
        ),
    ),
    make_tool(
        canonical_name="restrictions.create",
        mcp_alias="kaiten_create_restriction",
        description="Create a restriction on card creation or movement in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {"space_id": SPACE, **rule_properties()},
            "required": ["space_id", "conditions", "restrictions"],
        },
        operation=OperationSpec(
            method="POST",
            path_template=BASE_PATH,
            path_fields=("space_id",),
            body_fields=("name", "error_text", "conditions", "restrictions"),
        ),
        usage_notes=(
            EXTENSION_NOTE,
            SPACE_NOTE,
            "Creation does not accept status; use update to disable the new rule.",
        ),
        search_terms=("ограничения создать правило обязательные поля",),
        examples=(
            ExampleSpec(
                command='kaiten --json restrictions create --space-id 1 --name "Require size before moving" --conditions \'[{"type":"cardProperty","created":"2026-01-01T00:00:00Z","operator":"eq","data":{"properties":[{"propertyKey":"size_text","comparator":"noSet","value":null}]}}]\' --restrictions \'[{"type":"movement","created":"2026-01-01T00:00:00Z","operator":"eq","data":{"pathType":"any"}}]\'',
                description="Create a movement restriction for cards without size.",
            ),
        ),
    ),
    make_tool(
        canonical_name="restrictions.update",
        mcp_alias="kaiten_update_restriction",
        description="Update, enable or disable a Kaiten space restriction.",
        input_schema={
            "type": "object",
            "properties": {
                **IDS,
                **rule_properties(),
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Restriction status",
                },
            },
            "required": list(IDS),
            "anyOf": [
                {"required": [key]} for key in ("name", "conditions", "restrictions", "status")
            ],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template=BASE_PATH + "/{restriction_id}",
            path_fields=tuple(IDS),
            body_fields=("name", "error_text", "conditions", "restrictions", "status"),
        ),
        runtime_behavior=RuntimeBehavior(payload_validator=validate_restriction_payload),
        usage_notes=(
            EXTENSION_NOTE,
            SPACE_NOTE,
            "Only supplied fields are sent. Supplied conditions and restrictions arrays replace the whole arrays.",
            "An update requires name, conditions, restrictions or status; error_text alone is rejected by the server schema.",
        ),
        search_terms=("ограничения изменить включить отключить правило",),
        examples=(
            ExampleSpec(
                command=f"kaiten --json restrictions update --space-id 1 --restriction-id {RULE_ID} --status disabled",
                description="Disable a restriction.",
            ),
            ExampleSpec(
                command=f"kaiten --json restrictions update --space-id 1 --restriction-id {RULE_ID} --status active",
                description="Enable a restriction.",
            ),
        ),
    ),
    make_tool(
        canonical_name="restrictions.delete",
        mcp_alias="kaiten_delete_restriction",
        description="Delete a Kaiten space restriction.",
        input_schema={"type": "object", "properties": IDS, "required": list(IDS)},
        operation=OperationSpec(
            method="DELETE", path_template=BASE_PATH + "/{restriction_id}", path_fields=tuple(IDS)
        ),
        runtime_behavior=RuntimeBehavior(payload_validator=validate_restriction_payload),
        usage_notes=(EXTENSION_NOTE, SPACE_NOTE),
        search_terms=("ограничения удалить правило",),
        examples=(
            ExampleSpec(
                command=f"kaiten --json restrictions delete --space-id 1 --restriction-id {RULE_ID}",
                description="Delete a space restriction.",
            ),
        ),
    ),
    make_tool(
        canonical_name="restrictions.copy",
        mcp_alias="kaiten_copy_restriction",
        description="Copy a restriction to another Kaiten space using the collection POST route.",
        input_schema={
            "type": "object",
            "properties": {
                "restriction_id": IDENTIFIER,
                "target_space_id": {"type": "integer", "description": "Target space ID"},
            },
            "required": ["restriction_id", "target_space_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{target_space_id}/restrictions",
            path_fields=("target_space_id",),
        ),
        runtime_behavior=RuntimeBehavior(
            request_shaper=restriction_copy_request, payload_validator=validate_restriction_payload
        ),
        usage_notes=(
            EXTENSION_NOTE,
            SPACE_NOTE,
            "Copy sends source_restriction_id. The returned status may be broken when references are invalid in the target space.",
        ),
        search_terms=("ограничения копировать правило",),
        examples=(
            ExampleSpec(
                command=f"kaiten --json restrictions copy --restriction-id {RULE_ID} --target-space-id 2",
                description="Copy a restriction to another space.",
            ),
        ),
    ),
)
