"""Roles, groups, and space-user tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import company_members_section_request, payload_body_request


COMPANY_USERS_DEFAULT_LIMIT = 100


TOOLS = (
    make_tool(
        canonical_name="space-users.list",
        mcp_alias="kaiten_list_space_users",
        description="List users of a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields.",
                },
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/spaces/{space_id}/users", path_fields=("space_id",)
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten space-users list --space-id 1 --compact --json",
                description="List space users.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-users.get",
        mcp_alias="kaiten_get_space_user",
        description="Get a user in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "user_id": {"type": "integer", "description": "User ID"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields.",
                },
            },
            "required": ["space_id", "user_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_id}/users/{user_id}",
            path_fields=("space_id", "user_id"),
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="entity"),
        examples=(
            ExampleSpec(
                command="kaiten space-users get --space-id 1 --user-id 7 --compact --json",
                description="Get a space user.",
            ),
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
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/users",
            path_fields=("space_id",),
            body_fields=("user_id", "role_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten space-users add --space-id 1 --user-id 7 --json",
                description="Add a user to a space.",
            ),
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
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/users/{user_id}",
            path_fields=("space_id", "user_id"),
            body_fields=("role_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten space-users update --space-id 1 --user-id 7 --role-id 9 --json",
                description="Update a space user role.",
            ),
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
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_id}/users/{user_id}",
            path_fields=("space_id", "user_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten space-users remove --space-id 1 --user-id 7 --json",
                description="Remove a user from a space.",
            ),
        ),
    ),
    make_tool(
        canonical_name="company-users.list",
        mcp_alias="kaiten_list_company_users",
        description=(
            "List company users from the administrative Members section. "
            "Defaults to for_members_section=true with paginated limit/offset."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "for_members_section": {
                    "type": "boolean",
                    "description": "Use the administrative Members section response shape (default true).",
                },
                "query": {
                    "type": "string",
                    "description": "Search by email or full name.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of users to return (default 100).",
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of users to skip (default 0).",
                },
                "only_records_count": {
                    "type": "boolean",
                    "description": "Return only the filtered user count.",
                },
                "access_type_permissions": {
                    "type": "string",
                    "enum": ["member", "guest", "denied"],
                    "description": "Filter by Kaiten access type.",
                },
                "sd_access_type": {
                    "type": "string",
                    "enum": ["any", "has_access", "has_no_access"],
                    "description": "Filter by Service Desk access.",
                },
                "take_licence": {
                    "type": "string",
                    "enum": ["any", "yes", "no"],
                    "description": "Filter by users who take a paid license.",
                },
                "temporarily_inactive_status": {
                    "type": "string",
                    "enum": [
                        "all_users",
                        "only_temporarily_inactive_users",
                        "only_active_users",
                    ],
                    "description": "Filter by temporary deactivation status.",
                },
                "group_ids": {
                    "type": "array",
                    "description": "JSON array of company group IDs.",
                },
                "permissions": {
                    "type": "array",
                    "description": "JSON array of company permission criteria.",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields.",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to return per user.",
                },
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/users",
            query_fields=(
                "for_members_section",
                "query",
                "limit",
                "offset",
                "only_records_count",
                "access_type_permissions",
                "sd_access_type",
                "take_licence",
                "temporarily_inactive_status",
                "group_ids",
                "permissions",
            ),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=COMPANY_USERS_DEFAULT_LIMIT,
            result_kind="list",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=company_members_section_request),
        examples=(
            ExampleSpec(
                command="kaiten company-users list --limit 100 --offset 0 --compact --json",
                description="List administrative company members.",
            ),
            ExampleSpec(
                command=(
                    "kaiten company-users list --only-records-count "
                    "--temporarily-inactive-status all_users --json"
                ),
                description="Count company members including temporarily inactive users.",
            ),
        ),
        usage_notes=(
            "Use this command for paginated administrative member exports. "
            "`users.list` is a generic users endpoint and may not be reliable for full member paging.",
        ),
    ),
    make_tool(
        canonical_name="company-users.update",
        mcp_alias="kaiten_update_company_user",
        description="Update a company user.",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User ID"},
                "full_name": {"type": "string", "description": "Full name"},
                "email": {"type": "string", "description": "Email"},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["user_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/users/{user_id}",
            path_fields=("user_id",),
            body_fields=("full_name", "email", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten company-users update --user-id 7 --full-name "Alice Smith" --json',
                description="Update a company user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="company-users.remove-virtual",
        mcp_alias="kaiten_remove_virtual_company_user",
        description="Remove a virtual company user.",
        input_schema={
            "type": "object",
            "properties": {"user_id": {"type": "integer", "description": "Virtual user ID"}},
            "required": ["user_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/company/users/{user_id}", path_fields=("user_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten company-users remove-virtual --user-id 7 --json",
                description="Remove a virtual company user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-roles.list",
        mcp_alias="kaiten_list_user_roles",
        description="List user roles.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/user-roles", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten user-roles list --json", description="List user roles."),
        ),
    ),
    make_tool(
        canonical_name="user-roles.get",
        mcp_alias="kaiten_get_user_role",
        description="Get a user role.",
        input_schema={
            "type": "object",
            "properties": {"role_id": {"type": "integer", "description": "User role ID"}},
            "required": ["role_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/user-roles/{role_id}", path_fields=("role_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten user-roles get --role-id 1 --json", description="Get a user role."
            ),
        ),
    ),
    make_tool(
        canonical_name="user-roles.create",
        mcp_alias="kaiten_create_user_role",
        description="Create a user role.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Role name"},
                "permissions": {"type": "object", "description": "Role permissions JSON."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/user-roles",
            body_fields=("name", "permissions", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten user-roles create --name "Manager" --json',
                description="Create a user role.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-roles.update",
        mcp_alias="kaiten_update_user_role",
        description="Update a user role.",
        input_schema={
            "type": "object",
            "properties": {
                "role_id": {"type": "integer", "description": "User role ID"},
                "name": {"type": "string", "description": "Role name"},
                "permissions": {"type": "object", "description": "Role permissions JSON."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["role_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/user-roles/{role_id}",
            path_fields=("role_id",),
            body_fields=("name", "permissions", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten user-roles update --role-id 1 --name "Manager" --json',
                description="Update a user role.",
            ),
        ),
    ),
    make_tool(
        canonical_name="user-roles.delete",
        mcp_alias="kaiten_delete_user_role",
        description="Delete a user role.",
        input_schema={
            "type": "object",
            "properties": {"role_id": {"type": "integer", "description": "User role ID"}},
            "required": ["role_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/user-roles/{role_id}", path_fields=("role_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten user-roles delete --role-id 1 --json",
                description="Delete a user role.",
            ),
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
        operation=OperationSpec(
            method="GET", path_template="/company/groups", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten company-groups list --query "Engineering" --json',
                description="List company groups.",
            ),
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
        operation=OperationSpec(
            method="POST", path_template="/company/groups", body_fields=("name",)
        ),
        examples=(
            ExampleSpec(
                command='kaiten company-groups create --name "Engineering" --json',
                description="Create a company group.",
            ),
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
        operation=OperationSpec(
            method="GET", path_template="/company/groups/{group_uid}", path_fields=("group_uid",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten company-groups get --group-uid grp-1 --json",
                description="Get a company group.",
            ),
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
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/groups/{group_uid}",
            path_fields=("group_uid",),
            body_fields=("name",),
        ),
        examples=(
            ExampleSpec(
                command='kaiten company-groups update --group-uid grp-1 --name "Docs" --json',
                description="Update a company group.",
            ),
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
        operation=OperationSpec(
            method="DELETE", path_template="/company/groups/{group_uid}", path_fields=("group_uid",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten company-groups delete --group-uid grp-1 --json",
                description="Delete a company group.",
            ),
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
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields.",
                },
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="GET", path_template="/groups/{group_uid}/users", path_fields=("group_uid",)
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten group-users list --group-uid grp-1 --compact --json",
                description="List group users.",
            ),
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
        operation=OperationSpec(
            method="POST",
            path_template="/groups/{group_uid}/users",
            path_fields=("group_uid",),
            body_fields=("user_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten group-users add --group-uid grp-1 --user-id 7 --json",
                description="Add a user to a group.",
            ),
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
        operation=OperationSpec(
            method="DELETE",
            path_template="/groups/{group_uid}/users/{user_id}",
            path_fields=("group_uid", "user_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten group-users remove --group-uid grp-1 --user-id 7 --json",
                description="Remove a user from a group.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-admins.list",
        mcp_alias="kaiten_list_group_admins",
        description="List admins of a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields.",
                },
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="GET", path_template="/groups/{group_uid}/admins", path_fields=("group_uid",)
        ),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten group-admins list --group-uid grp-1 --compact --json",
                description="List group admins.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-admins.add",
        mcp_alias="kaiten_add_group_admin",
        description="Add an admin to a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "user_id": {"type": "integer", "description": "User ID to add as admin"},
            },
            "required": ["group_uid", "user_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/groups/{group_uid}/admins",
            path_fields=("group_uid",),
            body_fields=("user_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten group-admins add --group-uid grp-1 --user-id 7 --json",
                description="Add a group admin.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-admins.remove",
        mcp_alias="kaiten_remove_group_admin",
        description="Remove an admin from a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "user_id": {"type": "integer", "description": "User ID to remove"},
            },
            "required": ["group_uid", "user_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/groups/{group_uid}/admins/{user_id}",
            path_fields=("group_uid", "user_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten group-admins remove --group-uid grp-1 --user-id 7 --json",
                description="Remove a group admin.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-entities.list",
        mcp_alias="kaiten_list_group_entities",
        description="List tree entities attached to a company group.",
        input_schema={
            "type": "object",
            "properties": {"group_uid": {"type": "string", "description": "Group UID"}},
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/groups/{group_uid}/entities",
            path_fields=("group_uid",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten group-entities list --group-uid grp-1 --json",
                description="List group entities.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-entities.add",
        mcp_alias="kaiten_add_group_entity",
        description="Attach a tree entity to a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "entity_uid": {"type": "string", "description": "Tree entity UID"},
                "role_ids": {"type": "array", "description": "Tree entity role IDs."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["group_uid", "entity_uid", "role_ids"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/groups/{group_uid}/entities",
            path_fields=("group_uid",),
            body_fields=("entity_uid", "role_ids", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten group-entities add --group-uid grp-1 --entity-uid entity-1 --role-ids '[\"role-1\"]' --json",
                description="Attach a group entity.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-entities.update",
        mcp_alias="kaiten_update_group_entity",
        description="Update a tree entity attached to a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "entity_uid": {"type": "string", "description": "Tree entity UID"},
                "role_ids": {"type": "array", "description": "Tree entity role IDs."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["group_uid", "entity_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/groups/{group_uid}/entities/{entity_uid}",
            path_fields=("group_uid", "entity_uid"),
            body_fields=("role_ids", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten group-entities update --group-uid grp-1 --entity-uid entity-1 --role-ids '[\"role-1\"]' --json",
                description="Update a group entity.",
            ),
        ),
    ),
    make_tool(
        canonical_name="group-entities.remove",
        mcp_alias="kaiten_remove_group_entity",
        description="Remove a tree entity from a company group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Group UID"},
                "entity_uid": {"type": "string", "description": "Tree entity UID"},
            },
            "required": ["group_uid", "entity_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/groups/{group_uid}/entities/{entity_uid}",
            path_fields=("group_uid", "entity_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten group-entities remove --group-uid grp-1 --entity-uid entity-1 --json",
                description="Remove a group entity.",
            ),
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
        operation=OperationSpec(
            method="GET",
            path_template="/tree-entity-roles",
            query_fields=("query", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten roles list --query "admin" --json', description="List roles."
            ),
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
        operation=OperationSpec(
            method="GET", path_template="/tree-entity-roles/{role_id}", path_fields=("role_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten roles get --role-id role-1 --json", description="Get a role."
            ),
        ),
    ),
)
