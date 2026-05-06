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
                command="kaiten card-members list --card-id 10 --compact --json",
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
                command="kaiten card-members add --card-id 10 --user-id 7 --json",
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
                command="kaiten card-members remove --card-id 10 --user-id 7 --json",
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
            },
            "required": ["card_id", "member_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/members/{member_id}",
            path_fields=("card_id", "member_id"),
            body_fields=("role_id", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten card-members update --card-id 10 --member-id 7 --role-id role-uuid --json",
                description="Update a card member role.",
            ),
        ),
    ),
    make_tool(
        canonical_name="users.list",
        mcp_alias="kaiten_list_users",
        description="List company users. Supports search, pagination, and filtering inactive users. Response includes: last_request_date, activated, role, created.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search filter for user names or emails.",
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
            query_fields=("query", "limit", "offset", "include_inactive"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, default_limit=DEFAULT_LIMIT, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command='kaiten users list --query "alice" --compact --json',
                description="Search users by name.",
            ),
        ),
    ),
    make_tool(
        canonical_name="users.current",
        mcp_alias="kaiten_get_current_user",
        description="Get the current authenticated Kaiten user profile.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/users/current"),
        examples=(
            ExampleSpec(command="kaiten users current --json", description="Get the current user."),
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
            },
            "required": ["user_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/users/{user_id}",
            path_fields=("user_id",),
            body_fields=("full_name", "email", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten users update --user-id 7 --full-name "Alice Smith" --json',
                description="Update a user.",
            ),
        ),
    ),
)
