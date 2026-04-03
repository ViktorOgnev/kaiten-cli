"""Blocker tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="blockers.list",
        mcp_alias="kaiten_list_card_blockers",
        description="List all blockers on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card whose blockers to list."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/blockers", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten blockers list --card-id 10 --json", description="List blockers on a card."),
        ),
    ),
    make_tool(
        canonical_name="blockers.get",
        mcp_alias="kaiten_get_card_blocker",
        description="Get a specific blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to retrieve."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/blockers", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten blockers get --card-id 10 --blocker-id 20 --json", description="Get a blocker by filtering the blocker list."),
        ),
    ),
    make_tool(
        canonical_name="blockers.create",
        mcp_alias="kaiten_create_card_blocker",
        description="Create a blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card to add a blocker to."},
                "reason": {"type": "string", "description": "Reason for the blocker."},
                "blocker_card_id": {"type": "integer", "description": "ID of the card that blocks this one."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/blockers",
            path_fields=("card_id",),
            body_fields=("reason", "blocker_card_id"),
        ),
        examples=(
            ExampleSpec(command='kaiten blockers create --card-id 10 --reason "Waiting for review" --json', description="Create a blocker on a card."),
        ),
    ),
    make_tool(
        canonical_name="blockers.update",
        mcp_alias="kaiten_update_card_blocker",
        description="Update a blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to update."},
                "reason": {"type": "string", "description": "New reason for the blocker."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/blockers/{blocker_id}",
            path_fields=("card_id", "blocker_id"),
            body_fields=("reason",),
        ),
        examples=(
            ExampleSpec(command='kaiten blockers update --card-id 10 --blocker-id 20 --reason "Waiting for review" --json', description="Update a blocker."),
        ),
    ),
    make_tool(
        canonical_name="blockers.delete",
        mcp_alias="kaiten_delete_card_blocker",
        description="Delete a blocker from a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to delete."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/blockers/{blocker_id}", path_fields=("card_id", "blocker_id")),
        examples=(
            ExampleSpec(command="kaiten blockers delete --card-id 10 --blocker-id 20 --json", description="Delete a blocker."),
        ),
    ),
)
