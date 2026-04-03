"""Lane tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="lanes.list",
        mcp_alias="kaiten_list_lanes",
        description="List lanes (swimlanes) on a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
            },
            "required": ["board_id"],
        },
        operation=OperationSpec(method="GET", path_template="/boards/{board_id}/lanes", path_fields=("board_id",)),
        examples=(
            ExampleSpec(command="kaiten lanes list --board-id 10 --json", description="List lanes on a board."),
        ),
    ),
    make_tool(
        canonical_name="lanes.create",
        mcp_alias="kaiten_create_lane",
        description="Create a lane (swimlane) on a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "title": {"type": "string", "description": "Lane title"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "row_count": {"type": "integer", "description": "Number of sub-rows to split into"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
                "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards in this lane"},
            },
            "required": ["board_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/boards/{board_id}/lanes",
            path_fields=("board_id",),
            body_fields=("title", "sort_order", "row_count", "wip_limit", "wip_limit_type", "default_card_type_id"),
        ),
        examples=(
            ExampleSpec(command='kaiten lanes create --board-id 10 --title "Backend" --json', description="Create a board lane."),
        ),
    ),
    make_tool(
        canonical_name="lanes.update",
        mcp_alias="kaiten_update_lane",
        description="Update a lane on a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "lane_id": {"type": "integer", "description": "Lane ID"},
                "title": {"type": "string", "description": "New title"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "row_count": {"type": "integer", "description": "Number of sub-rows to split into"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
                "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards in this lane"},
                "condition": {"type": "integer", "enum": [1, 2], "description": "1=active, 2=archived"},
            },
            "required": ["board_id", "lane_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/boards/{board_id}/lanes/{lane_id}",
            path_fields=("board_id", "lane_id"),
            body_fields=("title", "sort_order", "row_count", "wip_limit", "wip_limit_type", "default_card_type_id", "condition"),
        ),
        examples=(
            ExampleSpec(command='kaiten lanes update --board-id 10 --lane-id 20 --title "Backend" --json', description="Update a lane."),
        ),
    ),
    make_tool(
        canonical_name="lanes.delete",
        mcp_alias="kaiten_delete_lane",
        description="Delete a lane from a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "lane_id": {"type": "integer", "description": "Lane ID"},
            },
            "required": ["board_id", "lane_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/boards/{board_id}/lanes/{lane_id}", path_fields=("board_id", "lane_id")),
        examples=(
            ExampleSpec(command="kaiten lanes delete --board-id 10 --lane-id 20 --json", description="Delete a lane."),
        ),
    ),
)
