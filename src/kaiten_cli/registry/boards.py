"""Board tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    board_delete_force_request,
    board_get_scoped_request,
    board_place_existing_request,
)


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
        operation=OperationSpec(
            method="GET", path_template="/spaces/{space_id}/boards", path_fields=("space_id",)
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command="kaiten boards list --space-id 1 --compact",
                description="List boards in a space.",
            ),
            ExampleSpec(
                command="kaiten --json boards list --space-id 1 --fields id,title",
                description="List boards with narrow fields.",
            ),
        ),
    ),
    make_tool(
        canonical_name="boards.get",
        mcp_alias="kaiten_get_board",
        description=(
            "Get a Kaiten board by ID, optionally through its space-scoped Public API route. "
            "Returns board placement data, columns and lanes."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "space_id": {
                    "type": "integer",
                    "description": (
                        "Optional space ID. When provided, use the documented "
                        "/spaces/{space_id}/boards/{board_id} route."
                    ),
                },
            },
            "required": ["board_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/boards/{board_id}", path_fields=("board_id",)
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=board_get_scoped_request),
        examples=(
            ExampleSpec(command="kaiten boards get --board-id 10", description="Get a board."),
            ExampleSpec(
                command="kaiten --json boards get --space-id 1 --board-id 10",
                description="Get a board through the space-scoped Public API route.",
            ),
        ),
        usage_notes=(
            "Without --space-id the command preserves the existing GET /boards/{board_id} behavior.",
            "With --space-id it uses GET /spaces/{space_id}/boards/{board_id} from the current Public API documentation.",
            "Cards are not part of this command's guaranteed response contract and disappear from both Public API routes on 2026-11-01.",
            "Fetch active board cards with cards.list-all using board_id and condition=1; this command never performs that extra request implicitly.",
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
                "default_card_type_id": {
                    "type": "integer",
                    "description": "Default card type ID for new cards",
                },
            },
            "required": ["space_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/boards",
            path_fields=("space_id",),
            body_fields=(
                "title",
                "description",
                "external_id",
                "top",
                "left",
                "sort_order",
                "default_card_type_id",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten boards create --space-id 1 --title "Smoke"',
                description="Create a board.",
            ),
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
                "default_card_type_id": {
                    "type": "integer",
                    "description": "Default card type ID for new cards",
                },
            },
            "required": ["space_id", "board_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/boards/{board_id}",
            path_fields=("space_id", "board_id"),
            body_fields=(
                "title",
                "description",
                "external_id",
                "top",
                "left",
                "sort_order",
                "default_card_type_id",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten boards update --space-id 1 --board-id 10 --title "Updated"',
                description="Update a board.",
            ),
        ),
    ),
    make_tool(
        canonical_name="boards.place-existing",
        mcp_alias="kaiten_place_existing_board",
        description="Place an existing board into a target space without moving it from its current primary space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Target space ID"},
                "board_id": {"type": "integer", "description": "Existing board ID"},
                "top": {"type": "number", "description": "Top position (px). Defaults to 0."},
                "left": {"type": "number", "description": "Left position (px). Defaults to 0."},
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["space_id", "board_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/boards/{board_id}",
            path_fields=("space_id", "board_id"),
            body_fields=("top", "left", "sort_order"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=board_place_existing_request),
        examples=(
            ExampleSpec(
                command="kaiten --json boards place-existing --space-id 2 --board-id 10",
                description="Show an existing board in another space without moving it.",
            ),
            ExampleSpec(
                command="kaiten --json boards place-existing --space-id 2 --board-id 10 --top 0 --left 560 --sort-order 2",
                description="Place an existing board at an explicit position.",
            ),
        ),
        usage_notes=(
            "This uses Kaiten's place-existing-board behavior and does not send move_from_space_id.",
            "This command is intentionally separate from Kaiten's move_from_space_id board-move behavior.",
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
                "force": {
                    "type": "boolean",
                    "description": "Force deletion when the board contains child entities",
                },
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
            ExampleSpec(
                command="kaiten boards delete --space-id 1 --board-id 10 --force",
                description="Delete a board.",
            ),
        ),
    ),
)
