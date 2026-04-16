"""Time-log tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    default_role_time_log_request,
    execute_time_logs_batch_list,
    validate_time_logs_batch_list,
)


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
                "compact": {"type": "boolean", "description": "Strip heavy nested fields from time-log payloads."},
                "fields": {"type": "string", "description": "Comma-separated field names to keep for each time log."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/time-logs", path_fields=("card_id",), query_fields=("for_date", "personal")),
        response_policy=ResponsePolicy(compact_supported=True, fields_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten time-logs list --card-id 10 --json", description="List time logs on a card."),
        ),
        usage_notes=(
            "This is a per-card read and becomes expensive when repeated across large card populations.",
            "For analytics snapshots and work-log investigations, prefer time-logs.batch-list over one-card-at-a-time loops.",
        ),
        bulk_alternative="time-logs.batch-list",
    ),
    make_tool(
        canonical_name="time-logs.batch-list",
        mcp_alias="kaiten_batch_list_time_logs",
        description="Fetch time logs for multiple cards with bounded worker concurrency.",
        input_schema={
            "type": "object",
            "properties": {
                "card_ids": {"type": "array", "items": {"type": "integer"}, "description": "Card IDs to inspect"},
                "workers": {"type": "integer", "description": "Parallel workers (default 2, max 6)"},
                "for_date": {"type": "string", "description": "Optional YYYY-MM-DD filter passed to each per-card request."},
                "personal": {"type": "boolean", "description": "Only include the current user's time logs."},
                "compact": {"type": "boolean", "description": "Strip heavy nested fields from time-log payloads"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep for each time log"},
            },
            "required": ["card_ids"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/time-logs/batch"),
        response_policy=ResponsePolicy(result_kind="entity", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            payload_validator=validate_time_logs_batch_list,
            custom_executor=execute_time_logs_batch_list,
        ),
        examples=(
            ExampleSpec(command="kaiten time-logs batch-list --card-ids '[1,2,3]' --json", description="Fetch time logs for several cards in one CLI call."),
            ExampleSpec(command="kaiten time-logs batch-list --card-ids '[1,2,3]' --workers 2 --fields id,time_spent,for_date --json", description="Fetch narrowed time-log payloads with bounded concurrency."),
        ),
        usage_notes=(
            "The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.",
            "Use this bulk path for work-log analytics and snapshot builds instead of repeating time-logs.list for every card.",
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
        runtime_behavior=RuntimeBehavior(request_shaper=default_role_time_log_request),
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
