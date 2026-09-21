"""Card tool specs."""

from __future__ import annotations

from kaiten_cli.models import (
    CACHE_POLICY_PERSISTENT_OPT_IN,
    ExampleSpec,
    OperationSpec,
    ResponsePolicy,
    RuntimeBehavior,
)
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    archive_card_request,
    execute_cards_batch_get,
    execute_cards_list_all,
    execute_cards_move_by_url,
    payload_body_request,
    validate_cards_batch_get,
    validate_cards_list_all_selection,
)
from kaiten_cli.runtime.support.markdown_export import (
    execute_card_get,
    validate_card_get_markdown_options,
)
from kaiten_cli.runtime.transforms import DEFAULT_LIMIT


LIST_CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Full-text search query"},
        "space_id": {"type": "integer", "description": "Filter by space ID"},
        "board_id": {"type": "integer", "description": "Filter by board ID"},
        "column_id": {"type": "integer", "description": "Filter by column ID"},
        "lane_id": {"type": "integer", "description": "Filter by lane ID"},
        "condition": {"type": "integer", "enum": [1, 2], "description": "1=active, 2=archived"},
        "type_id": {"type": "integer", "description": "Filter by card type ID"},
        "owner_id": {"type": "integer", "description": "Filter by owner user ID"},
        "responsible_id": {"type": "integer", "description": "Filter by responsible user ID"},
        "tag_ids": {"type": "string", "description": "Comma-separated tag IDs"},
        "member_ids": {"type": "string", "description": "Comma-separated member IDs"},
        "states": {
            "type": "string",
            "description": "Comma-separated states (1=queued,2=inProgress,3=done)",
        },
        "created_after": {"type": "string", "description": "ISO datetime filter"},
        "created_before": {"type": "string", "description": "ISO datetime filter"},
        "updated_after": {"type": "string", "description": "ISO datetime filter"},
        "updated_before": {"type": "string", "description": "ISO datetime filter"},
        "first_moved_in_progress_after": {
            "type": "string",
            "description": "ISO datetime filter for first move into in-progress state",
        },
        "first_moved_in_progress_before": {
            "type": "string",
            "description": "ISO datetime filter for first move into in-progress state",
        },
        "last_moved_to_done_at_after": {
            "type": "string",
            "description": "ISO datetime filter for last move to done column",
        },
        "last_moved_to_done_at_before": {
            "type": "string",
            "description": "ISO datetime filter for last move to done column",
        },
        "due_date_after": {"type": "string", "description": "ISO datetime filter"},
        "due_date_before": {"type": "string", "description": "ISO datetime filter"},
        "tag": {"type": "string", "description": "Filter by tag name"},
        "type_ids": {"type": "string", "description": "Comma-separated card type IDs"},
        "owner_ids": {"type": "string", "description": "Comma-separated owner user IDs"},
        "responsible_ids": {
            "type": "string",
            "description": "Comma-separated responsible user IDs",
        },
        "column_ids": {"type": "string", "description": "Comma-separated column IDs"},
        "exclude_board_ids": {
            "type": "string",
            "description": "Comma-separated board IDs to exclude",
        },
        "exclude_lane_ids": {
            "type": "string",
            "description": "Comma-separated lane IDs to exclude",
        },
        "exclude_column_ids": {
            "type": "string",
            "description": "Comma-separated column IDs to exclude",
        },
        "exclude_owner_ids": {
            "type": "string",
            "description": "Comma-separated owner IDs to exclude",
        },
        "exclude_card_ids": {
            "type": "string",
            "description": "Comma-separated card IDs to exclude",
        },
        "organization_ids": {
            "type": "string",
            "description": "Comma-separated Service Desk organization IDs",
        },
        "additional_card_fields": {
            "type": "string",
            "description": "Comma-separated extra fields to request. Supported by API: description",
        },
        "search_fields": {
            "type": "string",
            "description": "Comma-separated fields to search in for version=2",
        },
        "start_position": {
            "type": "string",
            "description": "Search cursor for version=2 pagination",
        },
        "filter": {"type": "string", "description": "Encoded Kaiten filter query"},
        "order_by": {"type": "string", "description": "Sort field list"},
        "order_direction": {"type": "string", "description": "Sort direction list"},
        "external_id": {"type": "string", "description": "External ID filter"},
        "version": {
            "type": "integer",
            "description": "Search version. Use 2 for OpenSearch result/position response.",
        },
        "overdue": {"type": "boolean", "description": "Filter overdue cards"},
        "asap": {"type": "boolean", "description": "Filter ASAP cards"},
        "done_on_time": {"type": "boolean", "description": "Filter cards done on time"},
        "with_due_date": {"type": "boolean", "description": "Filter cards with due date"},
        "is_request": {"type": "boolean", "description": "Filter Service Desk request cards"},
        "include_search_preview": {
            "type": "boolean",
            "description": "Include search preview objects for version=2",
        },
        "visible": {"type": "string", "description": "JSON-encoded visibility filter"},
        "archived": {"type": "boolean", "description": "Include archived"},
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "description": "Max results (default 50, max 100)",
        },
        "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
        "compact": {
            "type": "boolean",
            "description": "Return compact response without heavy fields (avatars, nested user objects)",
            "default": False,
        },
        "relations": {
            "type": "string",
            "description": "Comma-separated relations to include (members,type,custom_properties,...) or 'none' to exclude all. Default: include all.",
        },
        "fields": {
            "type": "string",
            "description": "Comma-separated field names to return per card. Strips everything else. Example: 'id,title,created,last_moved_to_done_at'",
        },
        "order_space_id": {"type": "integer", "description": "Order by space id"},
        "organizations_ids": {
            "type": "string",
            "description": "Search by organizations filter, comma separated",
        },
        "broken_api": {
            "type": "boolean",
            "description": "Backward compatibility flag for user-type custom properties. true (default until 2026-04-01): returns user UID strings. false: returns user integer IDs. Recommended: use broken_api=false for new integrations.",
        },
    },
}


TOOLS = (
    make_tool(
        canonical_name="cards.list",
        mcp_alias="kaiten_list_cards",
        description="Search and list Kaiten cards with filtering. Conditions: 1=active, 2=archived. States: 1=queued, 2=inProgress, 3=done.",
        input_schema=LIST_CARD_SCHEMA,
        operation=OperationSpec(
            method="GET",
            path_template="/cards",
            query_fields=(
                "query",
                "space_id",
                "board_id",
                "column_id",
                "lane_id",
                "condition",
                "type_id",
                "owner_id",
                "responsible_id",
                "tag_ids",
                "member_ids",
                "states",
                "created_after",
                "created_before",
                "updated_after",
                "updated_before",
                "first_moved_in_progress_after",
                "first_moved_in_progress_before",
                "last_moved_to_done_at_after",
                "last_moved_to_done_at_before",
                "due_date_after",
                "due_date_before",
                "tag",
                "type_ids",
                "owner_ids",
                "responsible_ids",
                "column_ids",
                "exclude_board_ids",
                "exclude_lane_ids",
                "exclude_column_ids",
                "exclude_owner_ids",
                "exclude_card_ids",
                "organization_ids",
                "additional_card_fields",
                "search_fields",
                "start_position",
                "filter",
                "order_by",
                "order_direction",
                "external_id",
                "version",
                "overdue",
                "asap",
                "done_on_time",
                "with_due_date",
                "is_request",
                "include_search_preview",
                "visible",
                "archived",
                "limit",
                "offset",
                "relations",
                "order_space_id",
                "organizations_ids",
                "broken_api",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=DEFAULT_LIMIT,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json cards list --board-id 10 --limit 5 --compact",
                description="List cards on a board.",
            ),
            ExampleSpec(
                command='kaiten cards list --query "bug" --fields id,title,state',
                description="Search cards by query.",
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.get",
        mcp_alias="kaiten_get_card",
        description="Get a Kaiten card by ID. Supports numeric ID or card key (e.g. PROJ-123).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {
                    "type": ["integer", "string"],
                    "description": "Card ID or key (e.g. PROJ-123)",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
                "markdown": {
                    "type": "boolean",
                    "description": "Save the card as Markdown instead of returning JSON.",
                },
                "output": {
                    "type": "string",
                    "description": "Markdown output file or directory. Defaults to the current working directory.",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Replace an existing Markdown output file.",
                },
                "broken_api": {
                    "type": "boolean",
                    "description": "Backward compatibility flag for user-type custom properties. true (default until 2026-04-01): returns user UID strings. false: returns user integer IDs. Recommended: use broken_api=false for new integrations.",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}",
            path_fields=("card_id",),
            query_fields=("broken_api",),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            payload_validator=validate_card_get_markdown_options,
            custom_executor=execute_card_get,
            cache_policy=CACHE_POLICY_PERSISTENT_OPT_IN,
        ),
        examples=(
            ExampleSpec(
                command="kaiten cards get --card-id 123", description="Get a card by numeric ID."
            ),
            ExampleSpec(
                command="kaiten --json cards get --card-id 123 --compact --fields id,title,state",
                description="Get a narrow card response.",
            ),
            ExampleSpec(
                command="kaiten --json cards get --card-id 123 --markdown --output ./card.md",
                description="Save a card as Markdown.",
            ),
        ),
        usage_notes=(
            "This is a per-card entity read and becomes expensive when repeated over large card populations.",
            "For detail enrichment after candidate reduction, prefer cards.batch-get over one-card-at-a-time loops.",
            "`--markdown` does the same card GET, renders the result locally, and saves a Markdown file instead of returning the card JSON.",
            "`--markdown` keeps card attachment links as Kaiten `/api/cards/<card>/files/<file_id>` URLs.",
            "Use `--output` for the target file/directory and `--overwrite` to replace an existing Markdown file.",
            "Separate CLI processes do not share in-memory results, so default `--cache-mode auto` persists repeated safe card reads.",
        ),
        bulk_alternative="cards.batch-get",
    ),
    make_tool(
        canonical_name="cards.batch-get",
        mcp_alias="kaiten_batch_get_cards",
        description="Fetch multiple cards by ID with bounded worker concurrency.",
        input_schema={
            "type": "object",
            "properties": {
                "card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Card IDs to fetch",
                },
                "workers": {
                    "type": "integer",
                    "description": "Parallel workers (default 2, max 6)",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Strip heavy nested fields from card payloads",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated card field names to keep",
                },
            },
            "required": ["card_ids"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/batch"),
        response_policy=ResponsePolicy(result_kind="entity", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            payload_validator=validate_cards_batch_get,
            custom_executor=execute_cards_batch_get,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json cards batch-get --card-ids '[1,2,3]'",
                description="Fetch several cards in one CLI call.",
            ),
            ExampleSpec(
                command="kaiten --json cards batch-get --card-ids '[1,2,3]' --workers 2 --compact --fields id,title,state,description",
                description="Fetch narrowed card detail payloads with bounded concurrency.",
            ),
        ),
        usage_notes=(
            "The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.",
            "Use this bulk path for detail enrichment after local candidate reduction or before building evidence-heavy snapshots.",
        ),
    ),
    make_tool(
        canonical_name="cards.create",
        mcp_alias="kaiten_create_card",
        description="Create a new Kaiten card. Title max 1024 chars, description max 32768 chars.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": ["string", "number"], "description": "Card title (1-1024 chars)"},
                "board_id": {"type": "integer", "description": "Target board ID"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
                "column_id": {"type": "integer", "description": "Target column ID"},
                "lane_id": {"type": "integer", "description": "Target lane ID"},
                "description": {
                    "type": ["string", "number", "null"],
                    "description": "Card description (max 32768)",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 32768,
                            "description": "Description for card",
                        },
                        {"type": "null", "description": "Empty card description"},
                    ],
                },
                "due_date": {
                    "type": ["string", "null"],
                    "description": "Deadline (ISO 8601)",
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Deadline. ISO 8601 format"},
                        {"type": "null", "description": "Empty due date"},
                    ],
                },
                "asap": {"type": "boolean", "description": "ASAP marker", "default": False},
                "size_text": {
                    "type": ["string", "number", "null"],
                    "description": "Size (e.g. S, M, L, 1, 23.45)",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 267,
                            "description": "Size. Example of acceptable values: '1', '23.45', '.5', 'S', '3 M', 'L', 'XL', etc...",
                        },
                        {"type": "null", "description": "Empty size text"},
                    ],
                },
                "owner_id": {"type": "integer", "description": "Owner user ID"},
                "type_id": {"type": "integer", "description": "Card type ID"},
                "external_id": {
                    "type": ["string", "number", "null"],
                    "description": "External ID (max 1024)",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 1024,
                            "description": "Any external id you want to assign to card. Not exposed in web interface",
                        },
                        {
                            "type": "null",
                            "description": "Any external id you want to assign to card. Not exposed in web interface",
                        },
                    ],
                },
                "sort_order": {"type": "number", "description": "Position in cell"},
                "position": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "1=first, 2=last in cell",
                },
                "properties": {
                    "type": "object",
                    "description": "Custom properties as {id_N: value}",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags to attach",
                },
                "sprint_id": {"type": "integer", "description": "Sprint ID to assign card to"},
                "planned_start": {
                    "type": ["string", "null"],
                    "description": "Planned start date (ISO 8601)",
                },
                "planned_end": {
                    "type": ["string", "null"],
                    "description": "Planned end date (ISO 8601)",
                },
                "responsible_id": {"type": "integer", "description": "Responsible user ID"},
                "condition": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "1=active, 2=archived",
                },
                "due_date_time_present": {
                    "type": "boolean",
                    "description": "True if due_date includes time component",
                },
                "expires_later": {"type": "boolean", "description": "Expires later flag"},
                "estimate_workload": {
                    "type": "integer",
                    "description": "Estimated workload in minutes (resource planning)",
                },
                "child_card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Child card IDs to link (max 1)",
                },
                "parent_card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Parent card IDs to link (max 1)",
                },
                "project_id": {"type": "string", "description": "Project UUID to attach card to"},
                "owner_email": {
                    "type": "string",
                    "description": "Owner email address. Only works if email belongs to company user",
                },
                "service_id": {
                    "description": "Service ID",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Service ID"},
                        {"type": "null", "description": "Empty service ID"},
                    ],
                },
                "text_format_type_id": {
                    "enum": [1, 2, 3],
                    "description": "1 - markdown (default), 2 – html, 3 - jira wiki format",
                    "type": "integer",
                },
            },
            "required": ["title", "board_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards",
            body_fields=(
                "title",
                "board_id",
                "column_id",
                "lane_id",
                "description",
                "due_date",
                "asap",
                "size_text",
                "owner_id",
                "type_id",
                "external_id",
                "sort_order",
                "position",
                "properties",
                "tags",
                "sprint_id",
                "planned_start",
                "planned_end",
                "responsible_id",
                "condition",
                "due_date_time_present",
                "expires_later",
                "estimate_workload",
                "child_card_ids",
                "parent_card_ids",
                "project_id",
                "owner_email",
                "service_id",
                "text_format_type_id",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json cards create --title "Smoke task" --board-id 10',
                description="Create a card.",
            ),
            ExampleSpec(
                command='kaiten --json cards create --title "Smoke task" --board-id 10 --compact --fields id,title,state',
                description="Create a card with a narrow response.",
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.update",
        mcp_alias="kaiten_update_card",
        description="Update a Kaiten card. Use condition=2 to archive, set column_id/board_id to move.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
                "title": {"type": ["string", "number"], "description": "New title"},
                "description": {
                    "type": ["string", "null", "number"],
                    "description": "New description",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 32768,
                            "description": "Description for card",
                        },
                        {"type": "null", "description": "Empty card description"},
                    ],
                },
                "board_id": {"type": "integer", "description": "Move to board"},
                "column_id": {"type": "integer", "description": "Move to column"},
                "lane_id": {"type": "integer", "description": "Move to lane"},
                "sort_order": {"type": "number", "description": "Position in cell"},
                "owner_id": {"type": "integer", "description": "New owner user ID"},
                "type_id": {"type": "integer", "description": "Card type ID"},
                "condition": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "1=active, 2=archived",
                },
                "due_date": {
                    "type": ["string", "null"],
                    "description": "Deadline (ISO 8601 or null)",
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Deadline. ISO 8601 format"},
                        {"type": "null", "description": "Empty card description"},
                    ],
                },
                "asap": {"type": "boolean", "description": "ASAP marker", "default": False},
                "size_text": {
                    "type": ["string", "null", "number"],
                    "description": "Size",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 267,
                            "description": "Size. Example of acceptable values: '1', '23.45', '.5', 'S', '3 M', 'L', 'XL', etc...",
                        },
                        {"type": "null", "description": "Empty size text"},
                    ],
                },
                "blocked": {"type": "boolean", "description": "Set to false to unblock"},
                "external_id": {
                    "type": ["string", "null", "number"],
                    "description": "External ID",
                    "x-documentation-alternatives": [
                        {
                            "type": ["number", "string"],
                            "maxLength": 1024,
                            "description": "Any external id you want to assign to card. Not exposed in web interface",
                        },
                        {
                            "type": "null",
                            "description": "Any external id you want to assign to card. Not exposed in web interface",
                        },
                    ],
                },
                "properties": {
                    "type": "object",
                    "description": "Custom properties as {id_N: value}",
                },
                "sprint_id": {
                    "type": ["integer", "null"],
                    "description": "Sprint ID (null to remove)",
                },
                "planned_start": {
                    "type": ["string", "null"],
                    "description": "Planned start date (ISO 8601)",
                },
                "planned_end": {
                    "type": ["string", "null"],
                    "description": "Planned end date (ISO 8601)",
                },
                "state": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "Card state: 1=queued, 2=inProgress, 3=done",
                },
                "block_reason": {
                    "type": ["string", "null"],
                    "description": "Block reason text (null to clear)",
                },
                "locked": {
                    "type": ["string", "null"],
                    "description": "Lock identifier (null to unlock)",
                },
                "due_date_time_present": {
                    "type": "boolean",
                    "description": "True if due_date includes time component",
                },
                "expires_later": {"type": "boolean", "description": "Expires later flag"},
                "estimate_workload": {
                    "type": ["integer", "number"],
                    "description": "Estimated workload in minutes (resource planning)",
                },
                "child_card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Child card IDs to link",
                },
                "parent_card_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Parent card IDs to link",
                },
                "service_id": {
                    "description": "Service ID",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Service ID"},
                        {"type": "null", "description": "Empty service ID"},
                    ],
                },
                "text_format_type_id": {
                    "enum": [1, 2, 3],
                    "description": "1 - markdown (default), 2 – html, 3 - jira wiki format",
                    "type": "integer",
                },
                "sd_new_comment": {
                    "type": "boolean",
                    "description": "Has unseen Service Desk request author comments",
                },
                "owner_email": {"type": "string", "description": "Owner email address"},
                "prev_card_id": {
                    "type": "integer",
                    "description": "Specifies optional ID of the card that was previous one and will be positioned after the current card after repositioning",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}",
            path_fields=("card_id",),
            body_fields=(
                "title",
                "description",
                "board_id",
                "column_id",
                "lane_id",
                "sort_order",
                "owner_id",
                "type_id",
                "condition",
                "due_date",
                "asap",
                "size_text",
                "blocked",
                "external_id",
                "properties",
                "sprint_id",
                "planned_start",
                "planned_end",
                "state",
                "block_reason",
                "locked",
                "due_date_time_present",
                "expires_later",
                "estimate_workload",
                "child_card_ids",
                "parent_card_ids",
                "service_id",
                "text_format_type_id",
                "sd_new_comment",
                "owner_email",
                "prev_card_id",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        examples=(
            ExampleSpec(
                command='kaiten cards update --card-id 123 --title "Renamed"',
                description="Update a card.",
            ),
            ExampleSpec(
                command='kaiten --json cards update --card-id 123 --title "Renamed" --compact --fields id,title,state',
                description="Update a card with a narrow response.",
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.batch-update",
        mcp_alias="kaiten_batch_update_cards",
        description="Batch update cards matching criteria. Kaiten runs the update as a background job.",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "integer", "description": "Criteria board ID."},
                "column_id": {"type": "integer", "description": "Criteria column ID."},
                "lane_id": {"type": "integer", "description": "Criteria lane ID."},
                "owner_id": {"type": "integer", "description": "Criteria owner user ID."},
                "type_id": {"type": "integer", "description": "Criteria card type ID."},
                "condition": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "Criteria condition: 1=active, 2=archived.",
                },
                "attributes": {
                    "type": "object",
                    "description": "Attributes to change on matching cards.",
                    "properties": {
                        "board_id": {"type": "integer", "description": "Board ID"},
                        "column_id": {"type": "integer", "description": "Column ID"},
                        "lane_id": {"type": "integer", "description": "Lane ID"},
                        "owner_id": {"type": "integer", "description": "Owner ID"},
                        "type_id": {"type": "integer", "description": "Card type ID"},
                        "condition": {
                            "enum": [1, 2],
                            "description": "1 - live, 2 - archived",
                            "type": "integer",
                        },
                        "title": {
                            "type": ["number", "string"],
                            "minLength": 1,
                            "maxLength": 1024,
                            "description": "Title",
                        },
                        "asap": {"type": "boolean", "description": "ASAP marker", "default": False},
                        "due_date": {
                            "description": "Deadline. ISO 8601 format",
                            "type": ["string", "null"],
                            "x-documentation-alternatives": [
                                {"type": "string", "description": "Deadline. ISO 8601 format"},
                                {"type": "null", "description": "Empty card description"},
                            ],
                        },
                        "due_date_time_present": {
                            "type": "boolean",
                            "description": "Flag indicating that deadline is specified up to hours and minutes",
                        },
                        "sort_order": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "description": "Position in the cell (board_id, column_id, lane_id)",
                        },
                        "description": {
                            "maxLength": 32768,
                            "description": "Description for card",
                            "type": ["number", "string", "null"],
                            "x-documentation-alternatives": [
                                {
                                    "type": ["number", "string"],
                                    "maxLength": 32768,
                                    "description": "Description for card",
                                },
                                {"type": "null", "description": "Empty card description"},
                            ],
                        },
                        "expires_later": {
                            "type": "boolean",
                            "description": "Fixed deadline or not. Date dependant flag in terms of Kanban",
                        },
                        "size_text": {
                            "maxLength": 267,
                            "description": "Size. Example of acceptable values: '1', '23.45', '.5', 'S', '3 M', 'L', 'XL', etc...",
                            "type": ["number", "string", "null"],
                            "x-documentation-alternatives": [
                                {
                                    "type": ["number", "string"],
                                    "maxLength": 267,
                                    "description": "Size. Example of acceptable values: '1', '23.45', '.5', 'S', '3 M', 'L', 'XL', etc...",
                                },
                                {"type": "null", "description": "Empty size text"},
                            ],
                        },
                        "service_id": {
                            "description": "Service ID",
                            "type": ["integer", "null"],
                            "x-documentation-alternatives": [
                                {"type": "integer", "description": "Service ID"},
                                {"type": "null", "description": "Empty service ID"},
                            ],
                        },
                        "blocked": {
                            "type": "boolean",
                            "description": "Send false to release all blocks related to this card",
                        },
                        "external_id": {
                            "maxLength": 1024,
                            "description": "Any external id you want to assign to card. Not exposed in web interface",
                            "type": ["number", "string", "null"],
                            "x-documentation-alternatives": [
                                {
                                    "type": ["number", "string"],
                                    "maxLength": 1024,
                                    "description": "Any external id you want to assign to card. Not exposed in web interface",
                                },
                                {
                                    "type": "null",
                                    "description": "Any external id you want to assign to card. Not exposed in web interface",
                                },
                            ],
                        },
                    },
                    "x-documentation-alternatives": [
                        {"required": ["board_id"]},
                        {"required": ["column_id"]},
                        {"required": ["lane_id"]},
                        {"required": ["owner_id"]},
                        {"required": ["type_id"]},
                        {"required": ["condition"]},
                    ],
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
                "order_by": {
                    "type": "object",
                    "description": "Sorting parameters",
                    "properties": {
                        "field_type": {
                            "enum": ["cp", "size", "created", "due_date", "title"],
                            "description": "Field type to sort by",
                            "type": "string",
                        },
                        "id": {"type": "integer", "description": "Field id to sort by"},
                        "direction": {
                            "enum": ["asc", "desc"],
                            "description": "Sorting direction",
                            "type": "string",
                        },
                    },
                    "x-documentation-alternatives": [{"required": ["field_type", "direction"]}],
                },
            },
            "required": ["attributes"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards",
            body_fields=(
                "board_id",
                "column_id",
                "lane_id",
                "owner_id",
                "type_id",
                "condition",
                "attributes",
                "payload",
                "order_by",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json cards batch-update --board-id 10 --attributes '{\"owner_id\":7}'",
                description="Batch update matching cards.",
            ),
        ),
        usage_notes=(
            "This endpoint updates all cards matching the criteria and returns a background job ID.",
            "Use narrow criteria first; this is intentionally separate from per-card cards.update.",
        ),
    ),
    make_tool(
        canonical_name="cards.delete",
        mcp_alias="kaiten_delete_card",
        description="Soft-delete a Kaiten card (sets condition to deleted). Cards with time logs cannot be deleted.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/cards/{card_id}", path_fields=("card_id",)
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        examples=(
            ExampleSpec(command="kaiten cards delete --card-id 123", description="Delete a card."),
        ),
    ),
    make_tool(
        canonical_name="cards.archive",
        mcp_alias="kaiten_archive_card",
        description="Archive a Kaiten card (set condition to archived).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}",
            path_fields=("card_id",),
            body_fields=("condition",),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=archive_card_request),
        examples=(
            ExampleSpec(
                command="kaiten cards archive --card-id 123", description="Archive a card."
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.move",
        mcp_alias="kaiten_move_card",
        description="Move a Kaiten card to a different board, column, or lane.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
                "board_id": {"type": "integer", "description": "Target board ID"},
                "column_id": {"type": "integer", "description": "Target column ID"},
                "lane_id": {"type": "integer", "description": "Target lane ID"},
                "sort_order": {"type": "number", "description": "Position in cell"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title,state'",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}",
            path_fields=("card_id",),
            body_fields=("board_id", "column_id", "lane_id", "sort_order"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json cards move --card-id 123 --column-id 10",
                description="Move a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.move-by-url",
        mcp_alias="kaiten_move_card_by_url",
        description="Move a Kaiten card by resolving card and target Kaiten UI URLs.",
        input_schema={
            "type": "object",
            "properties": {
                "card_url": {
                    "type": "string",
                    "description": "Kaiten card URL containing /boards/card/<id-or-key>",
                },
                "target_url": {
                    "type": "string",
                    "description": "Kaiten board URL with focus=column and focusId=<column_id>",
                },
                "lane_id": {
                    "type": "integer",
                    "description": "Target lane ID; required for boards with multiple lanes.",
                },
                "sort_order": {"type": "number", "description": "Position in cell"},
                "dry_run": {
                    "type": "boolean",
                    "description": "Resolve the move target without patching the card",
                    "default": False,
                },
                "verify": {
                    "type": "boolean",
                    "description": "Fetch the card after moving and verify its final location",
                    "default": True,
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact card response without heavy fields",
                    "default": False,
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated card fields to keep inside the returned card",
                },
            },
            "required": ["card_url", "target_url"],
        },
        operation=OperationSpec(method="PATCH", path_template="/cards/move-by-url"),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="entity"
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_cards_move_by_url,
            apply_common_transforms=False,
        ),
        examples=(
            ExampleSpec(
                command=(
                    "kaiten --json cards move-by-url "
                    '--card-url "https://hq.kaiten.ru/space/1/boards/card/STORY-1" '
                    '--target-url "https://hq.kaiten.ru/space/2/boards?focus=column&focusId=10" '
                    "--lane-id 20"
                ),
                description="Move a card by resolving card and target UI URLs.",
            ),
            ExampleSpec(
                command=(
                    "kaiten --json cards move-by-url "
                    '--card-url "https://hq.kaiten.ru/space/1/boards/card/STORY-1" '
                    '--target-url "https://hq.kaiten.ru/space/2/boards?focus=column&focusId=10" '
                    "--dry-run"
                ),
                description="Preview the resolved move target without changing the card.",
            ),
        ),
        usage_notes=(
            "The command does discovery inside the target space, then calls cards.move semantics.",
            "URL hosts must match the resolved profile domain; profiles are not auto-selected.",
            "When the target board has multiple lanes, pass --lane-id explicitly.",
            "`--fields` and `--compact` apply to the returned card inside the result envelope.",
        ),
    ),
    make_tool(
        canonical_name="card-baselines.list",
        mcp_alias="kaiten_list_card_baselines",
        description="List card baselines.",
        input_schema={
            "type": "object",
            "properties": {"card_id": {"type": "integer", "description": "Card ID."}},
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/baselines",
            path_fields=("card_id",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json card-baselines list --card-id 123",
                description="List baselines for a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-allowed-users.list",
        mcp_alias="kaiten_list_card_allowed_users",
        description="List one page of users allowed to access a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results (default 50, max 100).",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset."},
                "type": {
                    "description": "sd-owner - returns a list of company users with access to service-desk. virtual-users - returns a list of company virtual users.",
                    "x-documentation-constraints": "sd-owners \nvirtual-users \nmention",
                    "type": "string",
                },
                "search": {
                    "type": "string",
                    "description": "Filter by full_name, email or username",
                },
                "orderBy": {
                    "type": "string",
                    "description": "The field to sort by",
                    "x-documentation-constraints": "Default: id",
                },
                "role": {"type": "integer", "description": "Filter by role"},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/allowed-users",
            path_fields=("card_id",),
            query_fields=("limit", "offset", "type", "search", "orderBy", "role"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, default_limit=50, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json card-allowed-users list --card-id 123 --compact",
                description="List card allowed users.",
            ),
        ),
        usage_notes=(
            "This direct command returns one page; increase offset to read subsequent pages.",
        ),
    ),
    make_tool(
        canonical_name="card-service-desk-external-recipients.add",
        mcp_alias="kaiten_add_card_sd_external_recipient",
        description="Add a Service Desk external recipient to a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "email": {"type": "string", "description": "External recipient email."},
                "name": {"type": "string", "description": "External recipient display name."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["card_id", "email"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/sd-external-recipients",
            path_fields=("card_id",),
            body_fields=("email", "name", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json card-service-desk-external-recipients add --card-id 123 --email user@example.com",
                description="Add a Service Desk external recipient.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-service-desk-external-recipients.remove",
        mcp_alias="kaiten_remove_card_sd_external_recipient",
        description="Remove a Service Desk external recipient from a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "email": {"type": "string", "description": "External recipient email."},
            },
            "required": ["card_id", "email"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/sd-external-recipients/{email}",
            path_fields=("card_id", "email"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json card-service-desk-external-recipients remove --card-id 123 --email user@example.com",
                description="Remove a Service Desk external recipient.",
            ),
        ),
    ),
    make_tool(
        canonical_name="cards.list-all",
        mcp_alias="kaiten_list_all_cards",
        description="Fetch all cards matching filters with automatic pagination.",
        input_schema={
            "type": "object",
            "properties": {
                **LIST_CARD_SCHEMA["properties"],
                "owner_ids": {"type": "string", "description": "Comma-separated owner IDs"},
                "responsible_ids": {
                    "type": "string",
                    "description": "Comma-separated responsible IDs",
                },
                "column_ids": {"type": "string", "description": "Comma-separated column IDs"},
                "type_ids": {"type": "string", "description": "Comma-separated type IDs"},
                "selection": {
                    "type": "string",
                    "enum": ["all", "active_only", "archived_only"],
                    "description": "Normalized bulk selection: all, active_only, or archived_only.",
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Cards per page (default 100, max 100)",
                },
                "max_pages": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "description": "Safety limit on pages to fetch (default 50, max 1000)",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (default true for bulk)",
                    "default": True,
                },
                "relations": {
                    "type": "string",
                    "description": "Relations to include or 'none' to exclude all nested objects (default 'none' for bulk).",
                    "default": "none",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to return per card after pagination.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/cards"),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="list", heavy=True
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            payload_validator=validate_cards_list_all_selection,
            custom_executor=execute_cards_list_all,
            compact_default=True,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json cards list-all --board-id 10 --page-size 20 --max-pages 2",
                description="Fetch all matching cards with bounded pagination.",
            ),
            ExampleSpec(
                command="kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title",
                description="Fetch only active cards via normalized bulk selection.",
            ),
        ),
        usage_notes=(
            "For bulk reads, prefer selection=all|active_only|archived_only over raw archived/condition filters.",
            "active_only is computed as all_cards minus the archived subset to match the documented bulk CLI behavior.",
            "If max_pages is reached on a full page, the command fails instead of returning a partial card list.",
        ),
    ),
)
