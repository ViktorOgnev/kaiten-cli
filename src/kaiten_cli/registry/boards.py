"""Board tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime_behaviors import board_delete_force_request


TOOLS = (
    make_tool(
        canonical_name="boards.list",
        mcp_alias="kaiten_list_boards",
        description="List boards in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title'",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/boards", path_fields=("space_id",)),
        response_policy=ResponsePolicy(compact_supported=True, fields_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten boards list --space-id 1 --compact", description="List boards in a space."),
            ExampleSpec(command="kaiten boards list --space-id 1 --fields id,title --json", description="List boards with narrow fields."),
        ),
    ),
    make_tool(
        canonical_name="boards.get",
        mcp_alias="kaiten_get_board",
        description="Get a Kaiten board by ID. Returns board with columns and lanes.",
        input_schema={
            "type": "object",
            "properties": {"board_id": {"type": "integer", "description": "Board ID"}},
            "required": ["board_id"],
        },
        operation=OperationSpec(method="GET", path_template="/boards/{board_id}", path_fields=("board_id",)),
        examples=(
            ExampleSpec(command="kaiten boards get --board-id 10", description="Get a board."),
        ),
    ),
    make_tool(
        canonical_name="boards.create",
        mcp_alias="kaiten_create_board",
        description="Create a new board in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "title": {"type": "string", "description": "Board title"},
                "description": {"type": "string", "description": "Board description"},
                "external_id": {"type": "string", "description": "External ID"},
                "top": {"type": "number", "description": "Top position (px)"},
                "left": {"type": "number", "description": "Left position (px)"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards"},
            },
            "required": ["space_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/boards",
            path_fields=("space_id",),
            body_fields=("title", "description", "external_id", "top", "left", "sort_order", "default_card_type_id"),
        ),
        examples=(
            ExampleSpec(command='kaiten boards create --space-id 1 --title "Smoke"', description="Create a board."),
        ),
    ),
    make_tool(
        canonical_name="boards.update",
        mcp_alias="kaiten_update_board",
        description="Update a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "board_id": {"type": "integer", "description": "Board ID"},
                "title": {"type": "string", "description": "New title"},
                "description": {"type": "string", "description": "New description"},
                "external_id": {"type": "string", "description": "External ID"},
                "top": {"type": "number", "description": "Top position (px)"},
                "left": {"type": "number", "description": "Left position (px)"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards"},
            },
            "required": ["space_id", "board_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/boards/{board_id}",
            path_fields=("space_id", "board_id"),
            body_fields=("title", "description", "external_id", "top", "left", "sort_order", "default_card_type_id"),
        ),
        examples=(
            ExampleSpec(command='kaiten boards update --space-id 1 --board-id 10 --title "Updated"', description="Update a board."),
        ),
    ),
    make_tool(
        canonical_name="boards.delete",
        mcp_alias="kaiten_delete_board",
        description="Delete a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "board_id": {"type": "integer", "description": "Board ID"},
                "force": {"type": "boolean", "description": "Force deletion when the board contains child entities"},
            },
            "required": ["space_id", "board_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_id}/boards/{board_id}",
            path_fields=("space_id", "board_id"),
            query_fields=("force",),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=board_delete_force_request),
        examples=(
            ExampleSpec(command="kaiten boards delete --space-id 1 --board-id 10 --force", description="Delete a board."),
        ),
    ),
)
