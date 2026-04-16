"""Audit, activity, and saved-filter tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    execute_card_location_history_batch_get,
    execute_space_activity_all,
    saved_filter_title_request,
    validate_history_batch_get,
)
from kaiten_cli.runtime.transforms import DEFAULT_LIMIT


TOOLS = (
    make_tool(
        canonical_name="audit-logs.list",
        mcp_alias="kaiten_list_audit_logs",
        description="List Kaiten audit logs for the company.",
        input_schema={
            "type": "object",
            "properties": {
                "categories": {"type": "string", "description": "Comma-separated log categories"},
                "actions": {"type": "string", "description": "Comma-separated audit actions"},
                "from": {"type": "string", "description": "Start of date range filter"},
                "to": {"type": "string", "description": "End of date range filter"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/audit-logs",
            query_fields=("categories", "actions", "from", "to", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list", heavy=True),
        examples=(
            ExampleSpec(command="kaiten audit-logs list --limit 10 --json", description="List audit logs."),
        ),
    ),
    make_tool(
        canonical_name="card-activity.get",
        mcp_alias="kaiten_get_card_activity",
        description="Get activity feed for a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/activity",
            path_fields=("card_id",),
            query_fields=("limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten card-activity get --card-id 1 --json", description="Get card activity."),
        ),
    ),
    make_tool(
        canonical_name="space-activity.get",
        mcp_alias="kaiten_get_space_activity",
        description="Get activity feed for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "actions": {"type": "string", "description": "Comma-separated action types"},
                "created_after": {"type": "string", "description": "Filter activities after this datetime"},
                "created_before": {"type": "string", "description": "Filter activities before this datetime"},
                "author_id": {"type": "integer", "description": "Filter by author user ID"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
                "compact": {"type": "boolean", "description": "Strip heavy fields"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_id}/activity",
            path_fields=("space_id",),
            query_fields=("actions", "created_after", "created_before", "author_id", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=DEFAULT_LIMIT,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(command="kaiten space-activity get --space-id 1 --limit 10 --json", description="Get space activity."),
        ),
    ),
    make_tool(
        canonical_name="company-activity.get",
        mcp_alias="kaiten_get_company_activity",
        description="Get company-wide activity feed.",
        input_schema={
            "type": "object",
            "properties": {
                "actions": {"type": "string", "description": "Comma-separated action types"},
                "created_after": {"type": "string", "description": "Filter activities after this datetime"},
                "created_before": {"type": "string", "description": "Filter activities before this datetime"},
                "author_id": {"type": "integer", "description": "Filter by author user ID"},
                "cursor_created": {"type": "string", "description": "Cursor datetime"},
                "cursor_id": {"type": "integer", "description": "Cursor ID"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
                "compact": {"type": "boolean", "description": "Strip heavy fields"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep"},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/activity",
            query_fields=(
                "actions",
                "created_after",
                "created_before",
                "author_id",
                "cursor_created",
                "cursor_id",
                "limit",
                "offset",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=DEFAULT_LIMIT,
            result_kind="list",
            heavy=True,
        ),
        examples=(
            ExampleSpec(command="kaiten company-activity get --limit 10 --json", description="Get company activity."),
        ),
    ),
    make_tool(
        canonical_name="card-location-history.get",
        mcp_alias="kaiten_get_card_location_history",
        description="Get location history of a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {"card_id": {"type": "integer", "description": "Card ID"}},
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/location-history", path_fields=("card_id",)),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten card-location-history get --card-id 1 --json", description="Get card location history."),
        ),
        usage_notes=(
            "This is a per-card read and becomes expensive when repeated hundreds of times.",
            "For high-cardinality reads, use card-location-history.batch-get instead of spawning one CLI process per card.",
        ),
        bulk_alternative="card-location-history.batch-get",
    ),
    make_tool(
        canonical_name="card-location-history.batch-get",
        mcp_alias="kaiten_batch_get_card_location_history",
        description="Fetch location history for multiple cards with bounded worker concurrency.",
        input_schema={
            "type": "object",
            "properties": {
                "card_ids": {"type": "array", "items": {"type": "integer"}, "description": "Card IDs to fetch"},
                "workers": {"type": "integer", "description": "Parallel workers (default 2, max 6)"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep for each history row"},
            },
            "required": ["card_ids"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/location-history/batch"),
        response_policy=ResponsePolicy(result_kind="entity", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            payload_validator=validate_history_batch_get,
            custom_executor=execute_card_location_history_batch_get,
        ),
        examples=(
            ExampleSpec(command="kaiten card-location-history batch-get --card-ids '[1,2,3]' --json", description="Fetch history for several cards in one CLI call."),
            ExampleSpec(command="kaiten card-location-history batch-get --card-ids '[1,2,3]' --workers 2 --fields changed,column_id,subcolumn_id --json", description="Fetch projected history rows with bounded concurrency."),
        ),
        usage_notes=(
            "The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.",
            "Use conservative workers to avoid shifting the bottleneck from process startup to API rate limiting.",
        ),
    ),
    make_tool(
        canonical_name="space-activity-all.get",
        mcp_alias="kaiten_get_all_space_activity",
        description="Fetch all space activity with automatic pagination.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "actions": {"type": "string", "description": "Comma-separated action types"},
                "created_after": {"type": "string", "description": "Filter activities after this datetime"},
                "created_before": {"type": "string", "description": "Filter activities before this datetime"},
                "author_id": {"type": "integer", "description": "Filter by author user ID"},
                "page_size": {"type": "integer", "description": "Events per page (default 100, max 100)"},
                "max_pages": {"type": "integer", "description": "Safety limit on pages to fetch"},
                "compact": {"type": "boolean", "description": "Strip heavy fields; defaults to true for bulk"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/activity", path_fields=("space_id",)),
        response_policy=ResponsePolicy(compact_supported=True, fields_supported=True, result_kind="list", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_space_activity_all,
            compact_default=True,
        ),
        examples=(
            ExampleSpec(command="kaiten space-activity-all get --space-id 1 --page-size 20 --max-pages 2 --json", description="Fetch all space activity with bounded pagination."),
        ),
    ),
    make_tool(
        canonical_name="saved-filters.list",
        mcp_alias="kaiten_list_saved_filters",
        description="List saved filters.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(method="GET", path_template="/saved-filters", query_fields=("limit", "offset")),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten saved-filters list --json", description="List saved filters."),
        ),
    ),
    make_tool(
        canonical_name="saved-filters.create",
        mcp_alias="kaiten_create_saved_filter",
        description="Create a saved filter.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Filter name"},
                "filter": {"type": "object", "description": "Filter criteria object"},
                "shared": {"type": "boolean", "description": "Whether the filter is shared with the team"},
            },
            "required": ["name", "filter"],
        },
        operation=OperationSpec(method="POST", path_template="/saved-filters", body_fields=("name", "filter", "shared")),
        runtime_behavior=RuntimeBehavior(request_shaper=saved_filter_title_request),
        examples=(
            ExampleSpec(command="kaiten saved-filters create --name MyFilter --filter '{}' --json", description="Create a saved filter."),
        ),
    ),
    make_tool(
        canonical_name="saved-filters.get",
        mcp_alias="kaiten_get_saved_filter",
        description="Get a saved filter by ID.",
        input_schema={
            "type": "object",
            "properties": {"filter_id": {"type": "integer", "description": "Filter ID"}},
            "required": ["filter_id"],
        },
        operation=OperationSpec(method="GET", path_template="/saved-filters/{filter_id}", path_fields=("filter_id",)),
        examples=(
            ExampleSpec(command="kaiten saved-filters get --filter-id 1 --json", description="Get a saved filter."),
        ),
    ),
    make_tool(
        canonical_name="saved-filters.update",
        mcp_alias="kaiten_update_saved_filter",
        description="Update a saved filter.",
        input_schema={
            "type": "object",
            "properties": {
                "filter_id": {"type": "integer", "description": "Filter ID"},
                "name": {"type": "string", "description": "Filter name"},
                "filter": {"type": "object", "description": "Filter criteria object"},
                "shared": {"type": "boolean", "description": "Whether the filter is shared with the team"},
            },
            "required": ["filter_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/saved-filters/{filter_id}",
            path_fields=("filter_id",),
            body_fields=("name", "filter", "shared"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=saved_filter_title_request),
        examples=(
            ExampleSpec(command="kaiten saved-filters update --filter-id 1 --name Renamed --json", description="Update a saved filter."),
        ),
    ),
    make_tool(
        canonical_name="saved-filters.delete",
        mcp_alias="kaiten_delete_saved_filter",
        description="Delete a saved filter.",
        input_schema={
            "type": "object",
            "properties": {"filter_id": {"type": "integer", "description": "Filter ID"}},
            "required": ["filter_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/saved-filters/{filter_id}", path_fields=("filter_id",)),
        examples=(
            ExampleSpec(command="kaiten saved-filters delete --filter-id 1 --json", description="Delete a saved filter."),
        ),
    ),
)
