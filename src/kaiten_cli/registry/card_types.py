"""Card type tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import payload_body_request


TOOLS = (
    make_tool(
        canonical_name="card-types.list",
        mcp_alias="kaiten_list_card_types",
        description="List Kaiten card types.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search filter"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/card-types", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten card-types list --query "bug" --json',
                description="List card types.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.get",
        mcp_alias="kaiten_get_card_type",
        description="Get a Kaiten card type by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "type_id": {"type": "integer", "description": "Card type ID"},
            },
            "required": ["type_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/card-types/{type_id}", path_fields=("type_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten card-types get --type-id 42 --json", description="Get a card type."
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.create",
        mcp_alias="kaiten_create_card_type",
        description="Create a Kaiten card type.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Type name (1-64 chars)"},
                "letter": {"type": "string", "description": "Single letter or emoji"},
                "color": {"type": "integer", "description": "Color (2-25)"},
                "description_template": {
                    "type": "string",
                    "description": "Template for card description",
                },
            },
            "required": ["name", "letter", "color"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/card-types",
            body_fields=("name", "letter", "color", "description_template"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten card-types create --name "Feature" --letter F --color 3 --json',
                description="Create a card type.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.update",
        mcp_alias="kaiten_update_card_type",
        description="Update a Kaiten card type.",
        input_schema={
            "type": "object",
            "properties": {
                "type_id": {"type": "integer", "description": "Card type ID"},
                "name": {"type": "string", "description": "New name"},
                "letter": {"type": "string", "description": "New letter"},
                "color": {"type": "integer", "description": "New color (2-25)"},
                "description_template": {"type": "string", "description": "Description template"},
            },
            "required": ["type_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/card-types/{type_id}",
            path_fields=("type_id",),
            body_fields=("name", "letter", "color", "description_template"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten card-types update --type-id 42 --name "Bug" --json',
                description="Update a card type.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.delete",
        mcp_alias="kaiten_delete_card_type",
        description="Delete a Kaiten card type.",
        input_schema={
            "type": "object",
            "properties": {
                "type_id": {"type": "integer", "description": "Card type ID to delete"},
                "replace_type_id": {"type": "integer", "description": "Replacement card type ID"},
                "has_to_replace_in_automation": {
                    "type": "boolean",
                    "description": "Replace this type in automations.",
                },
                "has_to_replace_in_restriction": {
                    "type": "boolean",
                    "description": "Replace this type in restrictions.",
                },
                "has_to_replace_in_workflow": {
                    "type": "boolean",
                    "description": "Replace this type in workflows.",
                },
            },
            "required": ["type_id", "replace_type_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/card-types/{type_id}",
            path_fields=("type_id",),
            body_fields=(
                "replace_type_id",
                "has_to_replace_in_automation",
                "has_to_replace_in_restriction",
                "has_to_replace_in_workflow",
            ),
        ),
        examples=(
            ExampleSpec(
                command="kaiten card-types delete --type-id 42 --replace-type-id 1 --json",
                description="Delete a card type with replacement.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.tree-entities.list",
        mcp_alias="kaiten_list_card_type_tree_entities",
        description="List tree entities attached to a card type.",
        input_schema={
            "type": "object",
            "properties": {"type_id": {"type": "integer", "description": "Card type ID"}},
            "required": ["type_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/card-types/{type_id}/tree-entities",
            path_fields=("type_id",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten card-types tree-entities list --type-id 42 --json",
                description="List card type tree entities.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.tree-entities.add",
        mcp_alias="kaiten_add_card_type_tree_entity",
        description="Attach a tree entity to a card type.",
        input_schema={
            "type": "object",
            "properties": {
                "type_id": {"type": "integer", "description": "Card type ID"},
                "tree_entity_uid": {"type": "string", "description": "Tree entity UID"},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["type_id", "tree_entity_uid"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/card-types/{type_id}/tree-entities",
            path_fields=("type_id",),
            body_fields=("tree_entity_uid", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten card-types tree-entities add --type-id 42 --tree-entity-uid entity-uuid --json",
                description="Attach a tree entity to a card type.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-types.tree-entities.remove",
        mcp_alias="kaiten_remove_card_type_tree_entity",
        description="Remove a tree entity from a card type.",
        input_schema={
            "type": "object",
            "properties": {
                "type_id": {"type": "integer", "description": "Card type ID"},
                "tree_entity_uid": {"type": "string", "description": "Tree entity UID"},
            },
            "required": ["type_id", "tree_entity_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/card-types/{type_id}/tree-entities/{tree_entity_uid}",
            path_fields=("type_id", "tree_entity_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten card-types tree-entities remove --type-id 42 --tree-entity-uid entity-uuid --json",
                description="Remove a tree entity from a card type.",
            ),
        ),
    ),
)
