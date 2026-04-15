"""Card relation tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    card_child_add_request,
    card_parent_add_request,
    planned_relation_add_request,
)


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
        runtime_behavior=RuntimeBehavior(request_shaper=card_child_add_request),
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
        runtime_behavior=RuntimeBehavior(request_shaper=card_parent_add_request),
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
    make_tool(
        canonical_name="planned-relations.add",
        mcp_alias="kaiten_add_planned_relation",
        description=(
            "Create a planned relation (successor link) between two cards on Timeline/Gantt. "
            "The source card becomes a predecessor and the target card becomes its successor."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the source (predecessor) card."},
                "target_card_id": {"type": "integer", "description": "ID of the target (successor) card."},
                "type": {
                    "type": "string",
                    "enum": ["end-start"],
                    "description": "Relation type. Defaults to 'end-start'.",
                },
            },
            "required": ["card_id", "target_card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/planned-relation",
            path_fields=("card_id",),
            body_fields=("target_card_id", "type"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=planned_relation_add_request),
        examples=(
            ExampleSpec(
                command="kaiten planned-relations add --card-id 10 --target-card-id 11 --json",
                description="Create a finish-to-start planned relation.",
            ),
        ),
    ),
    make_tool(
        canonical_name="planned-relations.update",
        mcp_alias="kaiten_update_planned_relation",
        description="Update the lag/lead gap of a planned relation between two cards.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the source (predecessor) card."},
                "target_card_id": {"type": "integer", "description": "ID of the target (successor) card."},
                "gap": {
                    "type": ["integer", "null"],
                    "description": "Distance between cards (-1000..1000). Positive = lag, negative = lead. null to clear.",
                },
                "gap_type": {
                    "type": ["string", "null"],
                    "enum": ["hours", "days"],
                    "description": "Unit of the gap: 'hours', 'days', or null to clear.",
                },
            },
            "required": ["card_id", "target_card_id", "gap", "gap_type"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/planned-relation/{target_card_id}",
            path_fields=("card_id", "target_card_id"),
            body_fields=("gap", "gap_type"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten planned-relations update --card-id 10 --target-card-id 11 --gap 2 --gap-type days --json",
                description="Set a 2-day lag for a planned relation.",
            ),
        ),
    ),
    make_tool(
        canonical_name="planned-relations.remove",
        mcp_alias="kaiten_remove_planned_relation",
        description="Remove a planned relation (successor link) between two cards.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the source (predecessor) card."},
                "target_card_id": {"type": "integer", "description": "ID of the target (successor) card to unlink."},
            },
            "required": ["card_id", "target_card_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/planned-relation/{target_card_id}",
            path_fields=("card_id", "target_card_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten planned-relations remove --card-id 10 --target-card-id 11 --json",
                description="Remove a planned relation.",
            ),
        ),
    ),
)
