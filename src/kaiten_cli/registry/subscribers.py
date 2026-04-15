"""Subscriber tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import column_subscriber_default_type_request


TOOLS = (
    make_tool(
        canonical_name="card-subscribers.list",
        mcp_alias="kaiten_list_card_subscribers",
        description="List all subscribers of a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "compact": {"type": "boolean", "description": "Return compact response without heavy fields."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/subscribers", path_fields=("card_id",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten card-subscribers list --card-id 10 --compact --json", description="List card subscribers."),
        ),
    ),
    make_tool(
        canonical_name="card-subscribers.add",
        mcp_alias="kaiten_add_card_subscriber",
        description="Add a subscriber to a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "user_id": {"type": "integer", "description": "User ID to subscribe"},
            },
            "required": ["card_id", "user_id"],
        },
        operation=OperationSpec(method="POST", path_template="/cards/{card_id}/subscribers", path_fields=("card_id",), body_fields=("user_id",)),
        examples=(
            ExampleSpec(command="kaiten card-subscribers add --card-id 10 --user-id 7 --json", description="Add a card subscriber."),
        ),
    ),
    make_tool(
        canonical_name="card-subscribers.remove",
        mcp_alias="kaiten_remove_card_subscriber",
        description="Remove a subscriber from a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "user_id": {"type": "integer", "description": "User ID to unsubscribe"},
            },
            "required": ["card_id", "user_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/subscribers/{user_id}", path_fields=("card_id", "user_id")),
        examples=(
            ExampleSpec(command="kaiten card-subscribers remove --card-id 10 --user-id 7 --json", description="Remove a card subscriber."),
        ),
    ),
    make_tool(
        canonical_name="column-subscribers.list",
        mcp_alias="kaiten_list_column_subscribers",
        description="List all subscribers of a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "compact": {"type": "boolean", "description": "Return compact response without heavy fields."},
            },
            "required": ["column_id"],
        },
        operation=OperationSpec(method="GET", path_template="/columns/{column_id}/subscribers", path_fields=("column_id",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten column-subscribers list --column-id 10 --compact --json", description="List column subscribers."),
        ),
    ),
    make_tool(
        canonical_name="column-subscribers.add",
        mcp_alias="kaiten_add_column_subscriber",
        description="Add a subscriber to a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "user_id": {"type": "integer", "description": "User ID to subscribe"},
                "type": {"type": "integer", "description": "Subscription type (1=all, 2=mentions only)."},
            },
            "required": ["column_id", "user_id"],
        },
        operation=OperationSpec(method="POST", path_template="/columns/{column_id}/subscribers", path_fields=("column_id",), body_fields=("user_id", "type")),
        runtime_behavior=RuntimeBehavior(request_shaper=column_subscriber_default_type_request),
        examples=(
            ExampleSpec(command="kaiten column-subscribers add --column-id 10 --user-id 7 --json", description="Add a column subscriber."),
        ),
    ),
    make_tool(
        canonical_name="column-subscribers.remove",
        mcp_alias="kaiten_remove_column_subscriber",
        description="Remove a subscriber from a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "user_id": {"type": "integer", "description": "User ID to unsubscribe"},
            },
            "required": ["column_id", "user_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/columns/{column_id}/subscribers/{user_id}", path_fields=("column_id", "user_id")),
        examples=(
            ExampleSpec(command="kaiten column-subscribers remove --column-id 10 --user-id 7 --json", description="Remove a column subscriber."),
        ),
    ),
)
