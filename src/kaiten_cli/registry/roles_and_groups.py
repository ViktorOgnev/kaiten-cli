"""Roles, groups, and space-user tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="space-users.list",
        mcp_alias="kaiten_list_space_users",
        description="List users of a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "compact": {"type": "boolean", "description": "Return compact response without heavy fields."},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/users", path_fields=("space_id",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten space-users list --space-id 1 --compact --json", description="List space users."),
        ),
    ),
    make_tool(
        canonical_name="space-users.add",
        mcp_alias="kaiten_add_space_user",
        description="Add a user to a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "user_id": {"type": "integer", "description": "User ID to add"},
                "role_id": {"type": "string", "description": "Role ID (UUID) to assign"},
            },
            "required": ["space_id", "user_id"],
        },
        operation=OperationSpec(method="POST", path_template="/spaces/{space_id}/users", path_fields=("space_id",), body_fields=("user_id", "role_id")),
        examples=(
            ExampleSpec(command="kaiten space-users add --space-id 1 --user-id 7 --json", description="Add a user to a space."),
        ),
    ),
    make_tool(
        canonical_name="space-users.update",
        mcp_alias="kaiten_update_space_user",
        description="Update a user's role in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "user_id": {"type": "integer", "description": "User ID to update"},
                "role_id": {"type": "string", "description": "New role ID (UUID)"},
            },
            "required": ["space_id", "user_id"],
        },
        operation=OperationSpec(method="PATCH", path_template="/spaces/{space_id}/users/{user_id}", path_fields=("space_id", "user_id"), body_fields=("role_id",)),
        examples=(
            ExampleSpec(command="kaiten space-users update --space-id 1 --user-id 7 --role-id 9 --json", description="Update a space user role."),
        ),
    ),
    make_tool(
        canonical_name="space-users.remove",
        mcp_alias="kaiten_remove_space_user",
        description="Remove a user from a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "user_id": {"type": "integer", "description": "User ID to remove"},
            },
            "required": ["space_id", "user_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/spaces/{space_id}/users/{user_id}", path_fields=("space_id", "user_id")),
        examples=(
            ExampleSpec(command="kaiten space-users remove --space-id 1 --user-id 7 --json", description="Remove a user from a space."),
        ),
    ),
    make_tool(
        canonical_name="company-groups.list",
        mcp_alias="kaiten_list_company_groups",
        description="List company groups in Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results to return"},
                "offset": {"type": "integer", "description": "Offset for pagination"},
            },
        },
        operation=OperationSpec(method="GET", path_template="/company/groups", query_fields=("query", "limit", "offset")),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten company-groups list --query "Engineering" --json', description="List company groups."),
        ),
    ),
    make_tool(
        canonical_name="company-groups.create",
        mcp_alias="kaiten_create_company_group",
        description="Create a new company group in Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Group name"},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="POST", path_template="/company/groups", body_fields=("name",)),
        examples=(
            ExampleSpec(command='kaiten company-groups create --name "Engineering" --json', description="Create a company group."),
        ),
    ),
    make_tool(
        canonical_name="company-groups.get",
        mcp_alias="kaiten_get_company_group",
        description="Get a company group by UID.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(method="GET", path_template="/company/groups/{group_uid}", path_fields=("group_uid",)),
        examples=(
            ExampleSpec(command="kaiten company-groups get --group-uid grp-1 --json", description="Get a company group."),
        ),
    ),
    make_tool(
        canonical_name="company-groups.update",
        mcp_alias="kaiten_update_company_group",
        description="Update a company group in Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "name": {"type": "string", "description": "New group name"},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(method="PATCH", path_template="/company/groups/{group_uid}", path_fields=("group_uid",), body_fields=("name",)),
        examples=(
            ExampleSpec(command='kaiten company-groups update --group-uid grp-1 --name "Docs" --json', description="Update a company group."),
        ),
    ),
    make_tool(
        canonical_name="company-groups.delete",
        mcp_alias="kaiten_delete_company_group",
        description="Delete a company group in Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(method="DELETE", path_template="/company/groups/{group_uid}", path_fields=("group_uid",)),
        examples=(
            ExampleSpec(command="kaiten company-groups delete --group-uid grp-1 --json", description="Delete a company group."),
        ),
    ),
    make_tool(
        canonical_name="group-users.list",
        mcp_alias="kaiten_list_group_users",
        description="List users in a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "compact": {"type": "boolean", "description": "Return compact response without heavy fields."},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(method="GET", path_template="/groups/{group_uid}/users", path_fields=("group_uid",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten group-users list --group-uid grp-1 --compact --json", description="List group users."),
        ),
    ),
    make_tool(
        canonical_name="group-users.add",
        mcp_alias="kaiten_add_group_user",
        description="Add a user to a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "user_id": {"type": "integer", "description": "User ID to add"},
            },
            "required": ["group_uid", "user_id"],
        },
        operation=OperationSpec(method="POST", path_template="/groups/{group_uid}/users", path_fields=("group_uid",), body_fields=("user_id",)),
        examples=(
            ExampleSpec(command="kaiten group-users add --group-uid grp-1 --user-id 7 --json", description="Add a user to a group."),
        ),
    ),
    make_tool(
        canonical_name="group-users.remove",
        mcp_alias="kaiten_remove_group_user",
        description="Remove a user from a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "user_id": {"type": "integer", "description": "User ID to remove"},
            },
            "required": ["group_uid", "user_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/groups/{group_uid}/users/{user_id}", path_fields=("group_uid", "user_id")),
        examples=(
            ExampleSpec(command="kaiten group-users remove --group-uid grp-1 --user-id 7 --json", description="Remove a user from a group."),
        ),
    ),
    make_tool(
        canonical_name="roles.list",
        mcp_alias="kaiten_list_roles",
        description="List available roles in Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results to return"},
                "offset": {"type": "integer", "description": "Offset for pagination"},
            },
        },
        operation=OperationSpec(method="GET", path_template="/tree-entity-roles", query_fields=("query", "limit", "offset")),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten roles list --query "admin" --json', description="List roles."),
        ),
    ),
    make_tool(
        canonical_name="roles.get",
        mcp_alias="kaiten_get_role",
        description="Get a role by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "role_id": {"type": "string", "description": "Role ID (UUID)"},
            },
            "required": ["role_id"],
        },
        operation=OperationSpec(method="GET", path_template="/tree-entity-roles/{role_id}", path_fields=("role_id",)),
        examples=(
            ExampleSpec(command="kaiten roles get --role-id role-1 --json", description="Get a role."),
        ),
    ),
)
