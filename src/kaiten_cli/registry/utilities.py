"""Utility tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool
from kaiten_cli.transforms import DEFAULT_LIMIT


TOOLS = (
    make_tool(
        canonical_name="company.current",
        mcp_alias="kaiten_get_company",
        description="Get current company information.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/companies/current"),
        examples=(
            ExampleSpec(command="kaiten company current --json", description="Get current company information."),
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
        operation=OperationSpec(method="GET", path_template="/calendars", query_fields=("limit", "offset")),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten calendars list --limit 5 --json", description="List calendars."),
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
        operation=OperationSpec(method="GET", path_template="/calendars/{calendar_id}", path_fields=("calendar_id",)),
        examples=(
            ExampleSpec(command="kaiten calendars get --calendar-id cal-1 --json", description="Get a calendar by ID."),
        ),
    ),
    make_tool(
        canonical_name="user-timers.list",
        mcp_alias="kaiten_list_user_timers",
        description="List all user timers.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/user-timers"),
        examples=(
            ExampleSpec(command="kaiten user-timers list --json", description="List user timers."),
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
        operation=OperationSpec(method="POST", path_template="/user-timers", body_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten user-timers create --card-id 10 --json", description="Create a user timer."),
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
        operation=OperationSpec(method="GET", path_template="/user-timers/{timer_id}", path_fields=("timer_id",)),
        examples=(
            ExampleSpec(command="kaiten user-timers get --timer-id 10 --json", description="Get a user timer."),
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
        operation=OperationSpec(method="PATCH", path_template="/user-timers/{timer_id}", path_fields=("timer_id",), body_fields=("paused",)),
        examples=(
            ExampleSpec(command="kaiten user-timers update --timer-id 10 --paused --json", description="Pause a user timer."),
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
        operation=OperationSpec(method="DELETE", path_template="/user-timers/{timer_id}", path_fields=("timer_id",)),
        examples=(
            ExampleSpec(command="kaiten user-timers delete --timer-id 10 --json", description="Delete a user timer."),
        ),
    ),
)
