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
            "properties": {"board_id": {"type": "integer", "description": "Board ID"}},
            "required": ["board_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/boards/{board_id}/columns", path_fields=("board_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json columns list --board-id 10",
                description="List columns on a board.",
            ),
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
                "type": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "Column type: 1=queue, 2=in_progress, 3=done",
                },
                "wip_limit": {"type": "integer", "description": "WIP limit"},
                "wip_limit_type": {
                    "type": "integer",
                    "description": "WIP limit type (1=cards count, 2=size sum)",
                },
                "col_count": {
                    "type": "integer",
                    "description": "Number of sub-columns to split into",
                },
                "sort_order": {"type": "number", "description": "Sort order"},
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
                "last_moved_warning_after_days": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_hours": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_minutes": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "archive_after_days": {
                    "type": "integer",
                    "description": "Specify amont of days after which cards will be automatically archived. Works only for columns with type **done**",
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
            },
            "required": ["board_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/boards/{board_id}/columns",
            path_fields=("board_id",),
            body_fields=(
                "title",
                "type",
                "wip_limit",
                "wip_limit_type",
                "col_count",
                "sort_order",
                "external_id",
                "last_moved_warning_after_days",
                "last_moved_warning_after_hours",
                "last_moved_warning_after_minutes",
                "archive_after_days",
                "card_hide_after_days",
                "rules",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json columns create --board-id 10 --title "Doing" --type 2',
                description="Create a board column.",
            ),
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
                "wip_limit": {
                    "type": ["integer", "null"],
                    "description": "WIP limit",
                    "x-documentation-alternatives": [
                        {
                            "type": "integer",
                            "description": "Work in progress recommended limit for column",
                        },
                        {
                            "type": "null",
                            "description": "Empty work in progress recommended limit for column",
                        },
                    ],
                },
                "wip_limit_type": {
                    "type": "integer",
                    "description": "WIP limit type (1=cards count, 2=size sum)",
                },
                "col_count": {
                    "type": "integer",
                    "description": "Number of sub-columns to split into",
                },
                "sort_order": {"type": "number", "description": "Sort order"},
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
                "last_moved_warning_after_days": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_hours": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_minutes": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "archive_after_days": {
                    "type": "integer",
                    "description": "Specify amount of days after which cards will be automatically archived. Works only for columns with type **done**",
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
                "default_tags": {"type": ["string", "null"], "description": "Default tags"},
                "prev_column_id": {
                    "description": "Column ID to move column before",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Column ID to move column before"},
                        {
                            "type": "null",
                            "description": "Indicates that column should be moved to the beginning",
                        },
                    ],
                },
                "next_column_id": {
                    "description": "Column ID to move column after",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Column ID to move column after"},
                        {
                            "type": "null",
                            "description": "Indicates that column should be moved to the end",
                        },
                    ],
                },
                "pause_sla": {"type": "boolean"},
            },
            "required": ["board_id", "column_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/boards/{board_id}/columns/{column_id}",
            path_fields=("board_id", "column_id"),
            body_fields=(
                "title",
                "type",
                "wip_limit",
                "wip_limit_type",
                "col_count",
                "sort_order",
                "external_id",
                "last_moved_warning_after_days",
                "last_moved_warning_after_hours",
                "last_moved_warning_after_minutes",
                "archive_after_days",
                "card_hide_after_days",
                "rules",
                "default_tags",
                "prev_column_id",
                "next_column_id",
                "pause_sla",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json columns update --board-id 10 --column-id 20 --title "Review"',
                description="Rename a board column.",
            ),
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
                "force": {
                    "type": "boolean",
                    "description": "Remove cascade (all related data will be gone)",
                },
            },
            "required": ["board_id", "column_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/boards/{board_id}/columns/{column_id}",
            path_fields=("board_id", "column_id"),
            body_fields=("force",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json columns delete --board-id 10 --column-id 20",
                description="Delete a board column.",
            ),
        ),
    ),
    make_tool(
        canonical_name="subcolumns.list",
        mcp_alias="kaiten_list_subcolumns",
        description="List all subcolumns of a Kaiten column.",
        input_schema={
            "type": "object",
            "properties": {"column_id": {"type": "integer", "description": "Column ID"}},
            "required": ["column_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/columns/{column_id}/subcolumns",
            path_fields=("column_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json subcolumns list --column-id 20",
                description="List subcolumns for a column.",
            ),
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
                "col_count": {
                    "type": "integer",
                    "description": "Number of sub-columns to split into",
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
                "type": {
                    "enum": [1, 2, 3],
                    "description": "1 - queue, 2 – in progress, 3 – done",
                    "type": "integer",
                },
                "archive_after_days": {
                    "type": "integer",
                    "description": "Specify amont of days after which cards will be automatically archived. Works only for columns with type **done**",
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
                "last_moved_warning_after_minutes": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_hours": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_days": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
            },
            "required": ["column_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/columns/{column_id}/subcolumns",
            path_fields=("column_id",),
            body_fields=(
                "title",
                "sort_order",
                "wip_limit",
                "col_count",
                "external_id",
                "type",
                "archive_after_days",
                "card_hide_after_days",
                "rules",
                "last_moved_warning_after_minutes",
                "last_moved_warning_after_hours",
                "last_moved_warning_after_days",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json subcolumns create --column-id 20 --title "Blocked"',
                description="Create a subcolumn.",
            ),
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
                "col_count": {
                    "type": "integer",
                    "description": "Number of sub-columns to split into",
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
                "type": {
                    "enum": [1, 2, 3],
                    "description": "1 - queue, 2 – in progress, 3 – done",
                    "type": "integer",
                },
                "archive_after_days": {
                    "type": "integer",
                    "description": "Specify amont of days after which cards will be automatically archived. Works only for columns with type **done**",
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
                "default_tags": {"type": ["string", "null"], "description": "Default tags"},
                "last_moved_warning_after_minutes": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_hours": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "last_moved_warning_after_days": {
                    "type": "integer",
                    "description": "Warning appears on stale cards",
                },
                "prev_column_id": {
                    "description": "Column ID to move column before",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Column ID to move column before"},
                        {
                            "type": "null",
                            "description": "Indicates that column should be moved to the beginning",
                        },
                    ],
                },
                "next_column_id": {
                    "description": "Column ID to move column after",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Column ID to move column after"},
                        {
                            "type": "null",
                            "description": "Indicates that column should be moved to the end",
                        },
                    ],
                },
                "pause_sla": {"type": "boolean"},
            },
            "required": ["column_id", "subcolumn_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/columns/{column_id}/subcolumns/{subcolumn_id}",
            path_fields=("column_id", "subcolumn_id"),
            body_fields=(
                "title",
                "sort_order",
                "wip_limit",
                "col_count",
                "external_id",
                "type",
                "archive_after_days",
                "card_hide_after_days",
                "rules",
                "default_tags",
                "last_moved_warning_after_minutes",
                "last_moved_warning_after_hours",
                "last_moved_warning_after_days",
                "prev_column_id",
                "next_column_id",
                "pause_sla",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json subcolumns update --column-id 20 --subcolumn-id 30 --title "Blocked"',
                description="Update a subcolumn.",
            ),
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
                "force": {
                    "type": "boolean",
                    "description": "Remove cascade (all related data will be gone)",
                },
            },
            "required": ["column_id", "subcolumn_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/columns/{column_id}/subcolumns/{subcolumn_id}",
            path_fields=("column_id", "subcolumn_id"),
            body_fields=("force",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json subcolumns delete --column-id 20 --subcolumn-id 30",
                description="Delete a subcolumn.",
            ),
        ),
    ),
)
