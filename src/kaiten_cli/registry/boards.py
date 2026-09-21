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
                    "description": "Optional space ID. When provided, use the documented /spaces/{space_id}/boards/{board_id} route.",
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
                "title": {
                    "type": ["string", "number"],
                    "description": "Board title",
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 128,
                            "description": "Title of the new board",
                        },
                        {"type": "number"},
                    ],
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "Board description",
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Description"},
                        {"type": "null", "description": "Description"},
                    ],
                },
                "external_id": {
                    "type": ["string", "number", "null"],
                    "description": "External ID",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 1024,
                            "description": "Any external id you want to assign to board. Not exposed in web interface",
                        },
                        {
                            "type": "null",
                            "description": "Any external id you want to assign to board. Not exposed in web interface",
                        },
                    ],
                },
                "top": {"type": ["number", "integer"], "description": "Top position (px)"},
                "left": {"type": ["number", "integer"], "description": "Left position (px)"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "default_card_type_id": {
                    "type": "integer",
                    "description": "Default card type ID for new cards",
                },
                "columns": {
                    "type": "array",
                    "description": "Board columns.\nIf not passed, a default column will be created.\nIf an empty array is passed, an error will be returned.\nPreviously created boards without columns will not be included in responses, except for requests by ID, until they have at least one column and one track.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "minLength": 0,
                                "maxLength": 128,
                                "description": "Title",
                            },
                            "sort_order": {
                                "type": "number",
                                "description": "Position",
                                "exclusiveMinimum": 0,
                            },
                            "type": {
                                "enum": [1, 2, 3],
                                "description": "1 - queue, 2 – in progress, 3 – done",
                                "type": "integer",
                            },
                            "wip_limit": {
                                "type": "integer",
                                "description": "Work in progress recommended limit for column",
                            },
                            "col_count": {"type": "integer", "description": "Width"},
                            "archive_after_days": {
                                "type": "integer",
                                "description": "Specify amont of days after which cards will be automatically archived. Works only for columns with type **done**",
                            },
                            "months_to_hide_cards": {
                                "type": ["integer", "null"],
                                "description": "[Deprecated] Hide cards not moved for the last N months",
                            },
                            "card_hide_after_days": {
                                "type": ["integer", "null"],
                                "description": "Hide cards not moved for the last N days",
                            },
                            "rules": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Bit mask for column rules. Rules: 1 - checklists must be checked, 2 - display FIFO order",
                            },
                            "external_id": {
                                "maxLength": 1024,
                                "description": "Any external id you want to assign to column. Not exposed in web interface",
                                "type": ["number", "string", "null"],
                                "x-documentation-alternatives": [
                                    {
                                        "type": ["number", "string"],
                                        "maxLength": 1024,
                                        "description": "Any external id you want to assign to column. Not exposed in web interface",
                                    },
                                    {
                                        "type": "null",
                                        "description": "Any external id you want to assign to column. Not exposed in web interface",
                                    },
                                ],
                            },
                            "default_tags": {
                                "type": ["string", "null"],
                                "description": "Default tags",
                            },
                        },
                        "required": ["title", "type"],
                    },
                },
                "lanes": {
                    "type": "array",
                    "description": "Board lanes.\nIf not passed, a default lane will be created.\nIf an empty array is passed, an error will be returned and the board will not be created.\nPreviously created boards without lanes will not be included in responses, except for requests by ID, until they have at least one column and one lane.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "minLength": 0,
                                "maxLength": 128,
                                "description": "Title",
                            },
                            "sort_order": {
                                "type": "number",
                                "description": "Position",
                                "exclusiveMinimum": 0,
                            },
                            "wip_limit": {
                                "type": "integer",
                                "description": "Work in progress recommended limit for lane",
                            },
                            "row_count": {"type": "integer", "description": "Height"},
                            "default_tags": {
                                "type": ["string", "null"],
                                "description": "Default tags",
                            },
                        },
                        "required": ["title"],
                    },
                },
                "first_image_is_cover": {
                    "type": "boolean",
                    "description": "Automatically mark first uploaded card's image as card's cover",
                },
                "reset_lane_spent_time": {
                    "type": "boolean",
                    "description": "Reset lane spent time when card changed lane",
                },
                "automove_cards": {
                    "type": "boolean",
                    "description": "Automatically move cards depending on their children state",
                },
                "backward_moves_enabled": {
                    "type": "boolean",
                    "description": "Allow automatic backward movement for summary boards",
                },
                "auto_assign_enabled": {
                    "type": "boolean",
                    "description": 'Automatically assign the author as a member (or responsible if the first member) when a card is moved to the column with type "in progress" or "done"',
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
                "columns",
                "lanes",
                "first_image_is_cover",
                "reset_lane_spent_time",
                "automove_cards",
                "backward_moves_enabled",
                "auto_assign_enabled",
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
                "title": {
                    "type": ["string", "number"],
                    "description": "New title",
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 128,
                            "description": "Title of the new board",
                        },
                        {"type": "number"},
                    ],
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "New description",
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Description"},
                        {"type": "null", "description": "Description"},
                    ],
                },
                "external_id": {
                    "type": ["string", "number", "null"],
                    "description": "External ID",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 1024,
                            "description": "Any external id you want to assign to board. Not exposed in web interface",
                        },
                        {
                            "type": "null",
                            "description": "Any external id you want to assign to board. Not exposed in web interface",
                        },
                    ],
                },
                "top": {"type": ["number", "integer"], "description": "Top position (px)"},
                "left": {"type": ["number", "integer"], "description": "Left position (px)"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "default_card_type_id": {
                    "type": "integer",
                    "description": "Default card type ID for new cards",
                },
                "type": {
                    "enum": [1, 5],
                    "description": "1 - place on space with coordinates (top, left), 5 - attach to space as sidebar",
                    "type": "integer",
                },
                "cell_wip_limits": {
                    "type": "array",
                    "description": "JSON containing wip limits rules for cells",
                },
                "default_tags": {"type": ["string", "null"], "description": "Default tags"},
                "first_image_is_cover": {
                    "type": "boolean",
                    "description": "Automatically mark first uploaded card's image as card's cover",
                },
                "reset_lane_spent_time": {
                    "type": "boolean",
                    "description": "Reset lane spent time when card changed lane",
                },
                "automove_cards": {
                    "type": "boolean",
                    "description": "Automatically move cards depending on their children state",
                },
                "backward_moves_enabled": {
                    "type": "boolean",
                    "description": "Allow automatic backward movement for summary boards",
                },
                "move_parents_to_done": {
                    "type": "boolean",
                    "description": "Automatically move parent cards to done when their children cards on this board is done",
                },
                "hide_done_policies": {
                    "type": "boolean",
                    "description": "Hide done checklist policies",
                },
                "hide_done_policies_in_done_column": {
                    "type": "boolean",
                    "description": "Hide done checklist policies only in done column",
                },
                "move_from_space_id": {"type": "integer", "description": "Move board from space"},
                "auto_assign_enabled": {
                    "type": "boolean",
                    "description": 'Automatically assign the author as a member (or responsible if the first member) when a card is moved to the column with type "in progress" or "done"',
                },
                "card_properties": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "required": {"type": "boolean"},
                            "laneIds": {"type": ["array", "null"]},
                            "columnIds": {"type": ["array", "null"]},
                            "cardTypeIds": {"type": ["array", "null"]},
                        },
                    },
                    "description": "Suggested to fill card properties",
                    "type": ["array", "null"],
                    "x-documentation-alternatives": [
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "required": {"type": "boolean"},
                                    "laneIds": {"oneOf": [{"type": "array"}, {"type": "null"}]},
                                    "columnIds": {"oneOf": [{"type": "array"}, {"type": "null"}]},
                                    "cardTypeIds": {"oneOf": [{"type": "array"}, {"type": "null"}]},
                                },
                            },
                            "description": "Suggested to fill card properties",
                        },
                        {"type": "null", "description": "Empty suggested to fill card properties"},
                    ],
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
                "type",
                "cell_wip_limits",
                "default_tags",
                "first_image_is_cover",
                "reset_lane_spent_time",
                "automove_cards",
                "backward_moves_enabled",
                "move_parents_to_done",
                "hide_done_policies",
                "hide_done_policies_in_done_column",
                "move_from_space_id",
                "auto_assign_enabled",
                "card_properties",
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
            body_fields=("force",),
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
