"""Blocker tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import execute_blockers_get


TOOLS = (
    make_tool(
        canonical_name="blockers.list",
        mcp_alias="kaiten_list_card_blockers",
        description="List all blockers on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {
                    "type": "integer",
                    "description": "ID of the card whose blockers to list.",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/cards/{card_id}/blockers", path_fields=("card_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten blockers list --card-id 10 --json",
                description="List blockers on a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blockers.get",
        mcp_alias="kaiten_get_card_blocker",
        description="Get a specific blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to retrieve."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/cards/{card_id}/blockers", path_fields=("card_id",)
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom", custom_executor=execute_blockers_get
        ),
        examples=(
            ExampleSpec(
                command="kaiten blockers get --card-id 10 --blocker-id 20 --json",
                description="Get a blocker by filtering the blocker list.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blockers.create",
        mcp_alias="kaiten_create_card_blocker",
        description="Create a blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {
                    "type": "integer",
                    "description": "ID of the card to add a blocker to.",
                },
                "reason": {"type": "string", "description": "Reason for the blocker."},
                "blocker_card_id": {
                    "type": "integer",
                    "description": "ID of the card that blocks this one.",
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/blockers",
            path_fields=("card_id",),
            body_fields=("reason", "blocker_card_id"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten blockers create --card-id 10 --reason "Waiting for review" --json',
                description="Create a blocker on a card.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blockers.update",
        mcp_alias="kaiten_update_card_blocker",
        description="Update a blocker on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to update."},
                "reason": {"type": "string", "description": "New reason for the blocker."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/blockers/{blocker_id}",
            path_fields=("card_id", "blocker_id"),
            body_fields=("reason",),
        ),
        examples=(
            ExampleSpec(
                command='kaiten blockers update --card-id 10 --blocker-id 20 --reason "Waiting for review" --json',
                description="Update a blocker.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blockers.delete",
        mcp_alias="kaiten_delete_card_blocker",
        description="Delete a blocker from a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "blocker_id": {"type": "integer", "description": "ID of the blocker to delete."},
            },
            "required": ["card_id", "blocker_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/blockers/{blocker_id}",
            path_fields=("card_id", "blocker_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten blockers delete --card-id 10 --blocker-id 20 --json",
                description="Delete a blocker.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-categories.list",
        mcp_alias="kaiten_list_blocker_categories",
        description="List blocker categories.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/categories"),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten blocker-categories list --json",
                description="List blocker categories.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-categories.add",
        mcp_alias="kaiten_add_blocker_category",
        description="Add a category to a blocker.",
        input_schema={
            "type": "object",
            "properties": {
                "blocker_id": {"type": "integer", "description": "Blocker ID."},
                "category_uuid": {"type": "string", "description": "Category UUID."},
            },
            "required": ["blocker_id", "category_uuid"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/blockers/{blocker_id}/categories",
            path_fields=("blocker_id",),
            body_fields=("category_uuid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten blocker-categories add --blocker-id 20 --category-uuid cat-uuid --json",
                description="Add a blocker category.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-categories.remove",
        mcp_alias="kaiten_remove_blocker_category",
        description="Remove a category from a blocker.",
        input_schema={
            "type": "object",
            "properties": {
                "blocker_id": {"type": "integer", "description": "Blocker ID."},
                "category_uuid": {"type": "string", "description": "Category UUID."},
            },
            "required": ["blocker_id", "category_uuid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/blockers/{blocker_id}/categories/{category_uuid}",
            path_fields=("blocker_id", "category_uuid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten blocker-categories remove --blocker-id 20 --category-uuid cat-uuid --json",
                description="Remove a blocker category.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-users.list",
        mcp_alias="kaiten_list_blocker_users",
        description="List users attached to a blocker.",
        input_schema={
            "type": "object",
            "properties": {"blocker_id": {"type": "integer", "description": "Blocker ID."}},
            "required": ["blocker_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/blockers/{blocker_id}/users",
            path_fields=("blocker_id",),
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten blocker-users list --blocker-id 20 --compact --json",
                description="List blocker users.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-users.add",
        mcp_alias="kaiten_add_blocker_user",
        description="Add a user to a blocker.",
        input_schema={
            "type": "object",
            "properties": {
                "blocker_id": {"type": "integer", "description": "Blocker ID."},
                "user_id": {"type": "integer", "description": "User ID."},
            },
            "required": ["blocker_id", "user_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/blockers/{blocker_id}/users",
            path_fields=("blocker_id",),
            body_fields=("user_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten blocker-users add --blocker-id 20 --user-id 7 --json",
                description="Add a blocker user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="blocker-users.remove",
        mcp_alias="kaiten_remove_blocker_user",
        description="Remove a user from a blocker.",
        input_schema={
            "type": "object",
            "properties": {
                "blocker_id": {"type": "integer", "description": "Blocker ID."},
                "user_id": {"type": "integer", "description": "User ID."},
            },
            "required": ["blocker_id", "user_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/blockers/{blocker_id}/users/{user_id}",
            path_fields=("blocker_id", "user_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten blocker-users remove --blocker-id 20 --user-id 7 --json",
                description="Remove a blocker user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="current-user-blockers.list",
        mcp_alias="kaiten_list_current_user_blockers",
        description="List blocker cards assigned to the current user.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/users/current/blockers"),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten current-user-blockers list --json",
                description="List current user blockers.",
            ),
        ),
    ),
)
