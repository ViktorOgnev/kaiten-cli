"""Time-log tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="time-logs.list",
        mcp_alias="kaiten_list_card_time_logs",
        description="List time logs for a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "for_date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)."},
                "personal": {"type": "boolean", "description": "Return only the current user's time logs."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/time-logs", path_fields=("card_id",), query_fields=("for_date", "personal")),
        examples=(
            ExampleSpec(command="kaiten time-logs list --card-id 10 --json", description="List time logs on a card."),
        ),
    ),
    make_tool(
        canonical_name="time-logs.create",
        mcp_alias="kaiten_create_time_log",
        description="Log time spent on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "time_spent": {"type": "integer", "description": "Time spent in minutes (minimum 1)."},
                "role_id": {"type": "integer", "description": "Role ID for the time log. Use -1 for the default role."},
                "for_date": {"type": "string", "description": "Date for the time log (YYYY-MM-DD). Defaults to today."},
                "comment": {"type": "string", "description": "Optional comment for the time log."},
            },
            "required": ["card_id", "time_spent"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/time-logs",
            path_fields=("card_id",),
            body_fields=("time_spent", "role_id", "for_date", "comment"),
        ),
        examples=(
            ExampleSpec(command='kaiten time-logs create --card-id 10 --time-spent 15 --comment "Analysis" --json', description="Create a time log entry."),
        ),
    ),
    make_tool(
        canonical_name="time-logs.update",
        mcp_alias="kaiten_update_time_log",
        description="Update a time log entry on a card (author only).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "time_log_id": {"type": "integer", "description": "ID of the time log to update."},
                "time_spent": {"type": "integer", "description": "Updated time spent in minutes."},
                "role_id": {"type": "integer", "description": "Updated role ID."},
                "comment": {"type": "string", "description": "Updated comment."},
                "for_date": {"type": "string", "description": "Updated date (YYYY-MM-DD)."},
            },
            "required": ["card_id", "time_log_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/time-logs/{time_log_id}",
            path_fields=("card_id", "time_log_id"),
            body_fields=("time_spent", "role_id", "comment", "for_date"),
        ),
        examples=(
            ExampleSpec(command='kaiten time-logs update --card-id 10 --time-log-id 20 --time-spent 20 --json', description="Update a time log."),
        ),
    ),
    make_tool(
        canonical_name="time-logs.delete",
        mcp_alias="kaiten_delete_time_log",
        description="Delete a time log entry from a card (author only).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "time_log_id": {"type": "integer", "description": "ID of the time log to delete."},
            },
            "required": ["card_id", "time_log_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/time-logs/{time_log_id}", path_fields=("card_id", "time_log_id")),
        examples=(
            ExampleSpec(command="kaiten time-logs delete --card-id 10 --time-log-id 20 --json", description="Delete a time log."),
        ),
    ),
)
