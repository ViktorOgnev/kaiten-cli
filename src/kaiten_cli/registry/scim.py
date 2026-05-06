"""SCIM v2 tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import payload_body_request, scim_query_request


SCIM_PAYLOAD = {
    "type": "object",
    "description": "SCIM JSON payload. Sent as the request body.",
}


TOOLS = (
    make_tool(
        canonical_name="scim.users.list",
        mcp_alias="kaiten_list_scim_users",
        description="List SCIM users.",
        input_schema={
            "type": "object",
            "properties": {
                "start_index": {"type": "integer", "description": "SCIM start index."},
                "count": {"type": "integer", "description": "SCIM page size."},
                "filter": {"type": "string", "description": "SCIM filter expression."},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/scim/v2/Users",
            query_fields=("start_index", "count", "filter"),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=scim_query_request),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten scim users list --json", description="List SCIM users."),
        ),
    ),
    make_tool(
        canonical_name="scim.users.get",
        mcp_alias="kaiten_get_scim_user",
        description="Get a SCIM user.",
        input_schema={
            "type": "object",
            "properties": {"user_id": {"type": "string", "description": "SCIM user ID."}},
            "required": ["user_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/scim/v2/Users/{user_id}",
            path_fields=("user_id",),
            api_base_path="",
        ),
        examples=(
            ExampleSpec(
                command="kaiten scim users get --user-id user-id --json",
                description="Get a SCIM user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="scim.users.create",
        mcp_alias="kaiten_create_scim_user",
        description="Create a SCIM user.",
        input_schema={
            "type": "object",
            "properties": {"payload": SCIM_PAYLOAD},
            "required": ["payload"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/scim/v2/Users",
            body_fields=("payload",),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten scim users create --payload \'{"userName":"alice@example.com"}\' --json',
                description="Create a SCIM user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="scim.users.update",
        mcp_alias="kaiten_update_scim_user",
        description="Update a SCIM user.",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "SCIM user ID."},
                "payload": SCIM_PAYLOAD,
            },
            "required": ["user_id", "payload"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/scim/v2/Users/{user_id}",
            path_fields=("user_id",),
            body_fields=("payload",),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten scim users update --user-id user-id --payload '{\"active\":false}' --json",
                description="Update a SCIM user.",
            ),
        ),
    ),
    make_tool(
        canonical_name="scim.groups.list",
        mcp_alias="kaiten_list_scim_groups",
        description="List SCIM groups.",
        input_schema={
            "type": "object",
            "properties": {
                "start_index": {"type": "integer", "description": "SCIM start index."},
                "count": {"type": "integer", "description": "SCIM page size."},
                "filter": {"type": "string", "description": "SCIM filter expression."},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/scim/v2/Groups",
            query_fields=("start_index", "count", "filter"),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=scim_query_request),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten scim groups list --json", description="List SCIM groups."),
        ),
    ),
    make_tool(
        canonical_name="scim.groups.get",
        mcp_alias="kaiten_get_scim_group",
        description="Get a SCIM group.",
        input_schema={
            "type": "object",
            "properties": {"group_id": {"type": "string", "description": "SCIM group ID."}},
            "required": ["group_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/scim/v2/Groups/{group_id}",
            path_fields=("group_id",),
            api_base_path="",
        ),
        examples=(
            ExampleSpec(
                command="kaiten scim groups get --group-id group-id --json",
                description="Get a SCIM group.",
            ),
        ),
    ),
    make_tool(
        canonical_name="scim.groups.create",
        mcp_alias="kaiten_create_scim_group",
        description="Create a SCIM group.",
        input_schema={
            "type": "object",
            "properties": {"payload": SCIM_PAYLOAD},
            "required": ["payload"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/scim/v2/Groups",
            body_fields=("payload",),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten scim groups create --payload \'{"displayName":"Engineering"}\' --json',
                description="Create a SCIM group.",
            ),
        ),
    ),
    make_tool(
        canonical_name="scim.groups.update",
        mcp_alias="kaiten_update_scim_group",
        description="Update a SCIM group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_id": {"type": "string", "description": "SCIM group ID."},
                "payload": SCIM_PAYLOAD,
            },
            "required": ["group_id", "payload"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/scim/v2/Groups/{group_id}",
            path_fields=("group_id",),
            body_fields=("payload",),
            api_base_path="",
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten scim groups update --group-id group-id --payload \'{"displayName":"Ops"}\' --json',
                description="Update a SCIM group.",
            ),
        ),
    ),
)
