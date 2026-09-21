"""Card-member and user tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import payload_body_request
from kaiten_cli.runtime.transforms import DEFAULT_LIMIT


TOOLS = (
    make_tool(
        canonical_name="card-members.list",
        mcp_alias="kaiten_list_card_members",
        description="List all members assigned to a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, etc.).",
                    "default": False,
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/cards/{card_id}/members", path_fields=("card_id",)
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json card-members list --card-id 10 --compact",
                description="List members on a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-members.add",
        mcp_alias="kaiten_add_card_member",
        description="Add a member to a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "user_id": {"type": "integer", "description": "ID of the user to add as a member."},
            },
            "required": ["card_id", "user_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/members",
            path_fields=("card_id",),
            body_fields=("user_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json card-members add --card-id 10 --user-id 7",
                description="Add a member to a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-members.remove",
        mcp_alias="kaiten_remove_card_member",
        description="Remove a member from a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "user_id": {"type": "integer", "description": "ID of the user to remove."},
            },
            "required": ["card_id", "user_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/members/{user_id}",
            path_fields=("card_id", "user_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json card-members remove --card-id 10 --user-id 7",
                description="Remove a member from a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="card-members.update",
        mcp_alias="kaiten_update_card_member",
        description="Update a card member role.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "member_id": {"type": "integer", "description": "Card member ID from Kaiten."},
                "role_id": {"type": "string", "description": "Role ID to assign."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
                "type": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 2,
                    "description": "Make user responsible for card",
                },
            },
            "required": ["card_id", "member_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/members/{member_id}",
            path_fields=("card_id", "member_id"),
            body_fields=("role_id", "payload", "type"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json card-members update --card-id 10 --member-id 7 --role-id role-uuid",
                description="Update a card member role.",
            ),
        ),
    ),
    make_tool(
        canonical_name="users.list",
        mcp_alias="kaiten_list_users",
        description=(
            "List users from the generic /users endpoint. For paginated administrative "
            "Members exports, prefer company-users.list."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["all", "shared", "domain"],
                    "description": "User visibility scope supported by the Kaiten API.",
                },
                "query": {
                    "type": "string",
                    "description": "Search filter for user names or emails.",
                },
                "access_type_permissions": {
                    "type": "string",
                    "enum": ["member", "guest"],
                    "description": "Filter by Kaiten access type when supported by the endpoint.",
                },
                "ids": {"type": "string", "description": "Comma-separated user IDs."},
                "uids": {"type": "string", "description": "Comma-separated user UUIDs."},
                "exclude_directly_added_members_by_entity_uid": {
                    "type": "string",
                    "description": "Exclude users directly added to the given entity UID.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of users to return (default 50).",
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of users to skip (for pagination).",
                },
                "include_inactive": {
                    "type": "boolean",
                    "description": "Include inactive (deactivated) users in results.",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, etc.).",
                    "default": False,
                },
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/users",
            query_fields=(
                "type",
                "query",
                "access_type_permissions",
                "ids",
                "uids",
                "exclude_directly_added_members_by_entity_uid",
                "limit",
                "offset",
                "include_inactive",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, default_limit=DEFAULT_LIMIT, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json users list --query "alice" --compact',
                description="Search users by name.",
            ),
        ),
        usage_notes=(
            "This command maps to `/users`. Use `company-users.list` for the paginated "
            "administrative Members section (`/company/users?for_members_section=true`).",
        ),
    ),
    make_tool(
        canonical_name="users.current",
        mcp_alias="kaiten_get_current_user",
        description="Get the current authenticated Kaiten user profile.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/users/current"),
        examples=(
            ExampleSpec(command="kaiten --json users current", description="Get the current user."),
        ),
    ),
    make_tool(
        canonical_name="users.update",
        mcp_alias="kaiten_update_user",
        description="Update a user.",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User ID."},
                "full_name": {"type": "string", "description": "Full name."},
                "email": {"type": "string", "description": "Email."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
                "username": {
                    "type": "string",
                    "pattern": "^[0-9a-zA-Zа-яА-Я_]{1,}$",
                    "description": "Username for mentions and login",
                },
                "initials": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 2,
                    "description": "Initials",
                },
                "avatar_type": {
                    "enum": [1, 2, 3],
                    "description": "1 – gravatar, 2 – initials, 3 - uploaded",
                    "type": "integer",
                },
                "password": {"type": "string", "minLength": 6, "description": "New password"},
                "old_password": {
                    "minLength": 6,
                    "description": "Old password",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {"type": "string", "minLength": 6, "description": "Old password"},
                        {"type": "null", "description": "Old password"},
                    ],
                },
                "lng": {"type": "string", "description": "Language"},
                "default_space_id": {
                    "description": "Default space",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {"type": "integer", "description": "Default space"},
                        {"type": "null", "description": "Default space"},
                    ],
                },
                "theme": {
                    "enum": ["light", "dark", "auto"],
                    "description": "light - light color theme, dark - dark color theme, auto - color theme based on OS settings",
                    "type": "string",
                },
                "email_frequency": {
                    "enum": [1, 2],
                    "description": "1 - never, 2 – instantly",
                    "type": "integer",
                },
                "timezone": {"type": "string", "description": "Time zone"},
                "subject_by": {
                    "enum": [1, 2],
                    "description": "1 - id and title, 2 – action",
                    "type": "integer",
                },
                "email_settings": {"type": "object", "description": "Email settings"},
                "telegram_settings": {"type": "object", "description": "Telegram settings"},
                "slack_settings": {"type": "object", "description": "Slack settings"},
                "notification_enabled_channels": {
                    "type": "array",
                    "items": {
                        "enum": ["inner", "mobile_app", "email", "slack", "telegram"],
                        "type": "string",
                    },
                    "description": "List of enabled channels for notifications",
                },
                "notification_settings": {
                    "type": "object",
                    "description": "Channel lists where notifications for specified events should be sent",
                },
                "ui_version": {
                    "enum": [1, 2],
                    "description": "1 - old ui. 2 - new ui",
                    "type": "integer",
                },
            },
            "required": ["user_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/users/{user_id}",
            path_fields=("user_id",),
            body_fields=(
                "full_name",
                "email",
                "payload",
                "username",
                "initials",
                "avatar_type",
                "password",
                "old_password",
                "lng",
                "default_space_id",
                "theme",
                "email_frequency",
                "timezone",
                "subject_by",
                "email_settings",
                "telegram_settings",
                "slack_settings",
                "notification_enabled_channels",
                "notification_settings",
                "ui_version",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json users update --user-id 7 --full-name "Alice Smith"',
                description="Update a user.",
            ),
        ),
    ),
)
