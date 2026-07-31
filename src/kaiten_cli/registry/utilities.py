"""Utility tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.transforms import DEFAULT_LIMIT


TOOLS = (
    make_tool(
        canonical_name="api-keys.list",
        mcp_alias="kaiten_list_api_keys",
        description="List all API keys for the current user.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/api-keys"),
        examples=(
            ExampleSpec(command="kaiten --json api-keys list", description="List API keys."),
        ),
    ),
    make_tool(
        canonical_name="api-keys.create",
        mcp_alias="kaiten_create_api_key",
        description="Create a new API key.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the API key"},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="POST", path_template="/api-keys", body_fields=("name",)),
        examples=(
            ExampleSpec(
                command='kaiten --json api-keys create --name "local-dev"',
                description="Create an API key.",
            ),
        ),
    ),
    make_tool(
        canonical_name="api-keys.delete",
        mcp_alias="kaiten_delete_api_key",
        description="Delete an API key.",
        input_schema={
            "type": "object",
            "properties": {
                "key_id": {"type": "integer", "description": "API key ID"},
            },
            "required": ["key_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/api-keys/{key_id}", path_fields=("key_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json api-keys delete --key-id 1", description="Delete an API key."
            ),
        ),
    ),
    make_tool(
        canonical_name="company.current",
        mcp_alias="kaiten_get_company",
        description="Get current company information.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/companies/current"),
        examples=(
            ExampleSpec(
                command="kaiten --json company current",
                description="Get current company information.",
            ),
        ),
    ),
    make_tool(
        canonical_name="company.socket-token",
        mcp_alias="kaiten_get_company_socket_token",
        description="Get a websocket JWT for the current user.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/token-please"),
        examples=(
            ExampleSpec(
                command="kaiten --json company socket-token", description="Get a websocket JWT."
            ),
        ),
    ),
    make_tool(
        canonical_name="company.update",
        mcp_alias="kaiten_update_company",
        description="Update current company information.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Company name"},
            },
        },
        operation=OperationSpec(
            method="PATCH", path_template="/companies/current", body_fields=("name",)
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json company update --name "Acme"',
                description="Update current company information.",
            ),
        ),
    ),
    make_tool(
        canonical_name="calendars.list",
        mcp_alias="kaiten_list_calendars",
        description="List calendars.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/calendars", query_fields=("limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json calendars list --limit 5", description="List calendars."
            ),
        ),
    ),
    make_tool(
        canonical_name="calendars.get",
        mcp_alias="kaiten_get_calendar",
        description="Get a specific calendar by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string", "description": "Calendar ID (UUID)"},
            },
            "required": ["calendar_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/calendars/{calendar_id}", path_fields=("calendar_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json calendars get --calendar-id cal-1",
                description="Get a calendar by ID.",
            ),
        ),
    ),
    make_tool(
        canonical_name="removed-cards.list",
        mcp_alias="kaiten_list_removed_cards",
        description="List removed cards from the recycle bin.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/removed/cards", query_fields=("limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json removed-cards list", description="List removed cards."
            ),
        ),
    ),
    make_tool(
        canonical_name="removed-boards.list",
        mcp_alias="kaiten_list_removed_boards",
        description="List removed boards from the recycle bin.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/removed/boards", query_fields=("limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json removed-boards list", description="List removed boards."
            ),
        ),
    ),
    make_tool(
        canonical_name="user-timers.list",
        mcp_alias="kaiten_list_user_timers",
        description="List all user timers.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/user-timers"),
        examples=(
            ExampleSpec(command="kaiten --json user-timers list", description="List user timers."),
        ),
    ),
    make_tool(
        canonical_name="user-timers.create",
        mcp_alias="kaiten_create_user_timer",
        description="Create a new user timer for a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID to start timer for"},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="POST", path_template="/user-timers", body_fields=("card_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json user-timers create --card-id 10",
                description="Create a user timer.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-timers.get",
        mcp_alias="kaiten_get_user_timer",
        description="Get a specific user timer by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "timer_id": {"type": "integer", "description": "Timer ID"},
            },
            "required": ["timer_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/user-timers/{timer_id}", path_fields=("timer_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json user-timers get --timer-id 10",
                description="Get a user timer.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-timers.update",
        mcp_alias="kaiten_update_user_timer",
        description="Update a user timer (e.g. pause or resume).",
        input_schema={
            "type": "object",
            "properties": {
                "timer_id": {"type": "integer", "description": "Timer ID"},
                "paused": {"type": "boolean", "description": "Whether the timer is paused"},
            },
            "required": ["timer_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/user-timers/{timer_id}",
            path_fields=("timer_id",),
            body_fields=("paused",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json user-timers update --timer-id 10 --paused",
                description="Pause a user timer.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-timers.delete",
        mcp_alias="kaiten_delete_user_timer",
        description="Delete a user timer.",
        input_schema={
            "type": "object",
            "properties": {
                "timer_id": {"type": "integer", "description": "Timer ID"},
            },
            "required": ["timer_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/user-timers/{timer_id}", path_fields=("timer_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json user-timers delete --timer-id 10",
                description="Delete a user timer.",
            ),
        ),
    ),
)
