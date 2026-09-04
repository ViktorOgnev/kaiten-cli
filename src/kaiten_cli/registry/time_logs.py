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
        canonical_name="timesheet.list",
        mcp_alias="kaiten_list_timesheet",
        description="List time logs across cards from the company timesheet endpoint.",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "Filter by user ID."},
                "card_id": {"type": "integer", "description": "Filter by card ID."},
                "for_date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)."},
                "date_from": {"type": "string", "description": "Start date filter."},
                "date_to": {"type": "string", "description": "End date filter."},
                "limit": {"type": "integer", "description": "Max results."},
                "offset": {"type": "integer", "description": "Pagination offset."},
                "compact": {
                    "type": "boolean",
                    "description": "Strip heavy nested fields from time-log payloads.",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep for each time log.",
                },
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/time-logs",
            query_fields=(
                "user_id",
                "card_id",
                "for_date",
                "date_from",
                "date_to",
                "limit",
                "offset",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, default_limit=50, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json timesheet list --limit 50",
                description="List company time logs.",
            ),
        ),
    ),
    make_tool(
        canonical_name="time-logs.list",
        mcp_alias="kaiten_list_card_time_logs",
        description="List one page of time logs for a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "for_date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)."},
                "personal": {
                    "type": "boolean",
                    "description": "Return only the current user's time logs.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results (default 50, max 100).",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Pagination offset.",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Strip heavy nested fields from time-log payloads.",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep for each time log.",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/time-logs",
            path_fields=("card_id",),
            query_fields=("for_date", "personal", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=50,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json time-logs list --card-id 10",
                description="List time logs on a card.",
            ),
        ),
        usage_notes=(
            "This direct command returns one page; increase offset to read subsequent pages.",
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
                "card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Card IDs to inspect",
                },
                "workers": {
                    "type": "integer",
                    "description": "Parallel workers (default 2, max 6)",
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Time logs per request (default 100, max 100).",
                },
                "max_pages": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "description": "Safety limit per card (default 100, max 1000).",
                },
                "for_date": {
                    "type": "string",
                    "description": "Optional YYYY-MM-DD filter passed to each per-card request.",
                },
                "personal": {
                    "type": "boolean",
                    "description": "Only include the current user's time logs.",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Strip heavy nested fields from time-log payloads",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep for each time log",
                },
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
            ExampleSpec(
                command="kaiten --json time-logs batch-list --card-ids '[1,2,3]'",
                description="Fetch time logs for several cards in one CLI call.",
            ),
            ExampleSpec(
                command="kaiten --json time-logs batch-list --card-ids '[1,2,3]' --workers 2 --fields id,time_spent,for_date",
                description="Fetch narrowed time-log payloads with bounded concurrency.",
            ),
        ),
        usage_notes=(
            "The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.",
            "Each card is paginated to completion; a full max_pages boundary becomes a per-card error instead of a partial time-log list.",
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
                "time_spent": {
                    "type": "integer",
                    "description": "Time spent in minutes (minimum 1).",
                },
                "role_id": {
                    "type": "integer",
                    "description": "Role ID for the time log. Use -1 for the default role.",
                },
                "for_date": {
                    "type": "string",
                    "description": "Date for the time log (YYYY-MM-DD). Defaults to today.",
                },
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
            ExampleSpec(
                command='kaiten --json time-logs create --card-id 10 --time-spent 15 --comment "Analysis"',
                description="Create a time log entry.",
            ),
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
            ExampleSpec(
                command="kaiten --json time-logs update --card-id 10 --time-log-id 20 --time-spent 20",
                description="Update a time log.",
            ),
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
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/time-logs/{time_log_id}",
            path_fields=("card_id", "time_log_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json time-logs delete --card-id 10 --time-log-id 20",
                description="Delete a time log.",
            ),
        ),
    ),
)
