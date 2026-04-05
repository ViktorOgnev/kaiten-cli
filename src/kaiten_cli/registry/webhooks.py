"""Webhook tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="webhooks.list",
        mcp_alias="kaiten_list_webhooks",
        description="List all external webhooks for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/external-webhooks", path_fields=("space_id",)),
        examples=(
            ExampleSpec(command="kaiten webhooks list --space-id 1 --json", description="List external webhooks."),
        ),
    ),
    make_tool(
        canonical_name="webhooks.create",
        mcp_alias="kaiten_create_webhook",
        description="Create an external webhook for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "url": {"type": "string", "description": "Webhook URL"},
            },
            "required": ["space_id", "url"],
        },
        operation=OperationSpec(method="POST", path_template="/spaces/{space_id}/external-webhooks", path_fields=("space_id",), body_fields=("url",)),
        examples=(
            ExampleSpec(command='kaiten webhooks create --space-id 1 --url "https://example.test" --json', description="Create an external webhook."),
        ),
    ),
    make_tool(
        canonical_name="webhooks.get",
        mcp_alias="kaiten_get_webhook",
        description="Get a specific external webhook for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "webhook_id": {"type": "integer", "description": "Webhook ID"},
            },
            "required": ["space_id", "webhook_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/external-webhooks/{webhook_id}", path_fields=("space_id", "webhook_id")),
        examples=(
            ExampleSpec(command="kaiten webhooks get --space-id 1 --webhook-id 2 --json", description="Get an external webhook."),
        ),
    ),
    make_tool(
        canonical_name="webhooks.update",
        mcp_alias="kaiten_update_webhook",
        description="Update an external webhook for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "webhook_id": {"type": "integer", "description": "Webhook ID"},
                "url": {"type": "string", "description": "Webhook URL"},
                "enabled": {"type": "boolean", "description": "Whether the webhook is enabled"},
            },
            "required": ["space_id", "webhook_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/external-webhooks/{webhook_id}",
            path_fields=("space_id", "webhook_id"),
            body_fields=("url", "enabled"),
        ),
        examples=(
            ExampleSpec(command='kaiten webhooks update --space-id 1 --webhook-id 2 --enabled --json', description="Update an external webhook."),
        ),
    ),
    make_tool(
        canonical_name="webhooks.delete",
        mcp_alias="kaiten_delete_webhook",
        description="Delete an external webhook from a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "webhook_id": {"type": "integer", "description": "Webhook ID"},
            },
            "required": ["space_id", "webhook_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/spaces/{space_id}/external-webhooks/{webhook_id}", path_fields=("space_id", "webhook_id")),
        examples=(
            ExampleSpec(command="kaiten webhooks delete --space-id 1 --webhook-id 2 --json", description="Delete an external webhook."),
        ),
    ),
    make_tool(
        canonical_name="incoming-webhooks.list",
        mcp_alias="kaiten_list_incoming_webhooks",
        description="List incoming card-creation webhooks for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/webhooks", path_fields=("space_id",)),
        examples=(
            ExampleSpec(command="kaiten incoming-webhooks list --space-id 1 --json", description="List incoming webhooks."),
        ),
    ),
    make_tool(
        canonical_name="incoming-webhooks.create",
        mcp_alias="kaiten_create_incoming_webhook",
        description="Create an incoming card-creation webhook for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "board_id": {"type": "integer", "description": "Board ID"},
                "column_id": {"type": "integer", "description": "Column ID"},
                "lane_id": {"type": "integer", "description": "Lane ID"},
                "owner_id": {"type": "integer", "description": "Owner user ID"},
                "type_id": {"type": "integer", "description": "Card type ID"},
                "position": {"type": "integer", "description": "Position in the column"},
                "format": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7], "description": "Payload format"},
            },
            "required": ["space_id", "board_id", "column_id", "lane_id", "owner_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/webhooks",
            path_fields=("space_id",),
            body_fields=("board_id", "column_id", "lane_id", "owner_id", "type_id", "position", "format"),
        ),
        examples=(
            ExampleSpec(command="kaiten incoming-webhooks create --space-id 1 --board-id 2 --column-id 3 --lane-id 4 --owner-id 5 --json", description="Create an incoming webhook."),
        ),
    ),
    make_tool(
        canonical_name="incoming-webhooks.update",
        mcp_alias="kaiten_update_incoming_webhook",
        description="Update an incoming card-creation webhook in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "webhook_id": {"type": "string", "description": "Webhook ID (hash string)"},
                "board_id": {"type": "integer", "description": "Board ID"},
                "column_id": {"type": "integer", "description": "Column ID"},
                "lane_id": {"type": "integer", "description": "Lane ID"},
                "owner_id": {"type": "integer", "description": "Owner user ID"},
                "type_id": {"type": "integer", "description": "Card type ID"},
                "position": {"type": "integer", "description": "Position in the column"},
                "format": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7], "description": "Payload format"},
            },
            "required": ["space_id", "webhook_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/webhooks/{webhook_id}",
            path_fields=("space_id", "webhook_id"),
            body_fields=("board_id", "column_id", "lane_id", "owner_id", "type_id", "position", "format"),
        ),
        examples=(
            ExampleSpec(command="kaiten incoming-webhooks update --space-id 1 --webhook-id hook-1 --position 1 --json", description="Update an incoming webhook."),
        ),
    ),
    make_tool(
        canonical_name="incoming-webhooks.delete",
        mcp_alias="kaiten_delete_incoming_webhook",
        description="Delete an incoming card-creation webhook from a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "webhook_id": {"type": "string", "description": "Webhook ID (hash string)"},
            },
            "required": ["space_id", "webhook_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/spaces/{space_id}/webhooks/{webhook_id}", path_fields=("space_id", "webhook_id")),
        examples=(
            ExampleSpec(command="kaiten incoming-webhooks delete --space-id 1 --webhook-id hook-1 --json", description="Delete an incoming webhook."),
        ),
    ),
)
