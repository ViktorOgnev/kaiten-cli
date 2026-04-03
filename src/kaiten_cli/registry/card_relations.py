"""Card child and parent relation tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="card-children.list",
        mcp_alias="kaiten_list_card_children",
        description="List all child cards of a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the parent card."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/children", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten card-children list --card-id 10 --json", description="List child cards."),
        ),
    ),
    make_tool(
        canonical_name="card-children.add",
        mcp_alias="kaiten_add_card_child",
        description="Add a child card to a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the parent card."},
                "child_card_id": {"type": "integer", "description": "ID of the card to add as a child."},
            },
            "required": ["card_id", "child_card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/children",
            path_fields=("card_id",),
            body_fields=("child_card_id",),
        ),
        examples=(
            ExampleSpec(command="kaiten card-children add --card-id 10 --child-card-id 11 --json", description="Add a child card relation."),
        ),
    ),
    make_tool(
        canonical_name="card-children.remove",
        mcp_alias="kaiten_remove_card_child",
        description="Remove a child card from a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the parent card."},
                "child_id": {"type": "integer", "description": "ID of the child card to remove."},
            },
            "required": ["card_id", "child_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/children/{child_id}", path_fields=("card_id", "child_id")),
        examples=(
            ExampleSpec(command="kaiten card-children remove --card-id 10 --child-id 11 --json", description="Remove a child card relation."),
        ),
    ),
    make_tool(
        canonical_name="card-parents.list",
        mcp_alias="kaiten_list_card_parents",
        description="List all parent cards of a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the child card."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/parents", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten card-parents list --card-id 10 --json", description="List parent cards."),
        ),
    ),
    make_tool(
        canonical_name="card-parents.add",
        mcp_alias="kaiten_add_card_parent",
        description="Add a parent card to a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the child card."},
                "parent_card_id": {"type": "integer", "description": "ID of the card to add as a parent."},
            },
            "required": ["card_id", "parent_card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/parents",
            path_fields=("card_id",),
            body_fields=("parent_card_id",),
        ),
        examples=(
            ExampleSpec(command="kaiten card-parents add --card-id 10 --parent-card-id 11 --json", description="Add a parent card relation."),
        ),
    ),
    make_tool(
        canonical_name="card-parents.remove",
        mcp_alias="kaiten_remove_card_parent",
        description="Remove a parent card from a given card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the child card."},
                "parent_id": {"type": "integer", "description": "ID of the parent card to remove."},
            },
            "required": ["card_id", "parent_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/parents/{parent_id}", path_fields=("card_id", "parent_id")),
        examples=(
            ExampleSpec(command="kaiten card-parents remove --card-id 10 --parent-id 11 --json", description="Remove a parent card relation."),
        ),
    ),
)
