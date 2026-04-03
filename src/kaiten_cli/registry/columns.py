"""Column and subcolumn tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="columns.list",
        mcp_alias="kaiten_list_columns",
        description="List columns on a Kaiten board. Column types: 1=queue, 2=in_progress, 3=done. Response includes: wip_limit, wip_limit_type (1=cards count, 2=size sum), last_moved_warning_after_days, archive_after_days, card_hide_after_days.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
            },
            "required": ["board_id"],
        },
        operation=OperationSpec(method="GET", path_template="/boards/{board_id}/columns", path_fields=("board_id",)),
        examples=(
            ExampleSpec(command="kaiten columns list --board-id 10 --json", description="List columns on a board."),
        ),
    ),
    make_tool(
        canonical_name="columns.create",
        mcp_alias="kaiten_create_column",
        description="Create a column on a Kaiten board. Type: 1=queue, 2=in_progress, 3=done.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "title": {"type": "string", "description": "Column title"},
                "type": {"type": "integer", "enum": [1, 2, 3], "description": "Column type: 1=queue, 2=in_progress, 3=done"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
                "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["board_id", "title", "type"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/boards/{board_id}/columns",
            path_fields=("board_id",),
            body_fields=("title", "type", "wip_limit", "wip_limit_type", "col_count", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten columns create --board-id 10 --title "Doing" --type 2 --json', description="Create a board column."),
        ),
    ),
    make_tool(
        canonical_name="columns.update",
        mcp_alias="kaiten_update_column",
        description="Update a column on a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "column_id": {"type": "integer", "description": "Column ID"},
                "title": {"type": "string", "description": "New title"},
                "type": {"type": "integer", "enum": [1, 2, 3], "description": "Column type"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
                "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["board_id", "column_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/boards/{board_id}/columns/{column_id}",
            path_fields=("board_id", "column_id"),
            body_fields=("title", "type", "wip_limit", "wip_limit_type", "col_count", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten columns update --board-id 10 --column-id 20 --title "Review" --json', description="Rename a board column."),
        ),
    ),
    make_tool(
        canonical_name="columns.delete",
        mcp_alias="kaiten_delete_column",
        description="Delete a column from a Kaiten board.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Board ID"},
                "column_id": {"type": "integer", "description": "Column ID"},
            },
            "required": ["board_id", "column_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/boards/{board_id}/columns/{column_id}", path_fields=("board_id", "column_id")),
        examples=(
            ExampleSpec(command="kaiten columns delete --board-id 10 --column-id 20 --json", description="Delete a board column."),
        ),
    ),
    make_tool(
        canonical_name="subcolumns.list",
        mcp_alias="kaiten_list_subcolumns",
        description="List all subcolumns of a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
            },
            "required": ["column_id"],
        },
        operation=OperationSpec(method="GET", path_template="/columns/{column_id}/subcolumns", path_fields=("column_id",)),
        examples=(
            ExampleSpec(command="kaiten subcolumns list --column-id 20 --json", description="List subcolumns for a column."),
        ),
    ),
    make_tool(
        canonical_name="subcolumns.create",
        mcp_alias="kaiten_create_subcolumn",
        description="Create a subcolumn inside a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "title": {"type": "string", "description": "Subcolumn title"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
            },
            "required": ["column_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/columns/{column_id}/subcolumns",
            path_fields=("column_id",),
            body_fields=("title", "sort_order", "wip_limit", "col_count"),
        ),
        examples=(
            ExampleSpec(command='kaiten subcolumns create --column-id 20 --title "Blocked" --json', description="Create a subcolumn."),
        ),
    ),
    make_tool(
        canonical_name="subcolumns.update",
        mcp_alias="kaiten_update_subcolumn",
        description="Update a subcolumn of a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "subcolumn_id": {"type": "integer", "description": "Subcolumn ID"},
                "title": {"type": "string", "description": "New title"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
            },
            "required": ["column_id", "subcolumn_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/columns/{column_id}/subcolumns/{subcolumn_id}",
            path_fields=("column_id", "subcolumn_id"),
            body_fields=("title", "sort_order", "wip_limit", "col_count"),
        ),
        examples=(
            ExampleSpec(command='kaiten subcolumns update --column-id 20 --subcolumn-id 30 --title "Blocked" --json', description="Update a subcolumn."),
        ),
    ),
    make_tool(
        canonical_name="subcolumns.delete",
        mcp_alias="kaiten_delete_subcolumn",
        description="Delete a subcolumn from a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {
                "column_id": {"type": "integer", "description": "Column ID"},
                "subcolumn_id": {"type": "integer", "description": "Subcolumn ID"},
            },
            "required": ["column_id", "subcolumn_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/columns/{column_id}/subcolumns/{subcolumn_id}", path_fields=("column_id", "subcolumn_id")),
        examples=(
            ExampleSpec(command="kaiten subcolumns delete --column-id 20 --subcolumn-id 30 --json", description="Delete a subcolumn."),
        ),
    ),
)
