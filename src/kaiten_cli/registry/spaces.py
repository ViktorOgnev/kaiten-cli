"""Space tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import execute_space_topology_get


TOOLS = (
    make_tool(
        canonical_name="spaces.list",
        mcp_alias="kaiten_list_spaces",
        description="List one page of Kaiten spaces with explicit limit/offset pagination.",
        input_schema={
            "type": "object",
            "properties": {
                "archived": {"type": "boolean", "description": "Include archived spaces"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results (default 50, max 100)",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Pagination offset",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'id,title'",
                },
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects)",
                    "default": False,
                },
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces",
            query_fields=("archived", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, default_limit=50, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json spaces list",
                description="List spaces as machine-readable JSON.",
            ),
            ExampleSpec(
                command="kaiten --json spaces list --compact --fields id,title",
                description="List spaces with a narrow response surface.",
            ),
        ),
        usage_notes=(
            "This direct command returns one page; increase offset to read subsequent pages.",
            "Use tree.get or tree.children.list when a complete hierarchy is required.",
        ),
    ),
    make_tool(
        canonical_name="spaces.get",
        mcp_alias="kaiten_get_space",
        description="Get a Kaiten space by ID.",
        input_schema={
            "type": "object",
            "properties": {"space_id": {"type": "integer", "description": "Space ID"}},
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/spaces/{space_id}", path_fields=("space_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten spaces get --space-id 123", description="Get a space by ID."
            ),
        ),
    ),
    make_tool(
        canonical_name="space-topology.get",
        mcp_alias="kaiten_get_space_topology",
        description="Fetch boards with their columns and lanes for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {"space_id": {"type": "integer", "description": "Space ID"}},
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="GET", path_template="/spaces/{space_id}/topology", path_fields=("space_id",)
        ),
        response_policy=ResponsePolicy(result_kind="entity", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_space_topology_get,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json space-topology get --space-id 123",
                description="Fetch board topology for a space.",
            ),
        ),
        usage_notes=(
            "Use this for report scaffolding instead of separate boards.list, columns.list, and lanes.list loops.",
        ),
    ),
    make_tool(
        canonical_name="spaces.create",
        mcp_alias="kaiten_create_space",
        description="Create a new Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Space title"},
                "description": {"type": "string", "description": "Space description"},
                "access": {
                    "type": "string",
                    "enum": ["for_everyone", "by_invite"],
                    "description": "Access type (default: for_everyone)",
                },
                "external_id": {"type": "string", "description": "External ID"},
                "parent_entity_uid": {
                    "type": "string",
                    "description": "Parent entity UID for nesting spaces",
                },
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces",
            body_fields=(
                "title",
                "description",
                "access",
                "external_id",
                "parent_entity_uid",
                "sort_order",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten spaces create --title "CLI smoke"', description="Create a space."
            ),
        ),
    ),
    make_tool(
        canonical_name="spaces.update",
        mcp_alias="kaiten_update_space",
        description="Update a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "title": {"type": "string", "description": "New title"},
                "description": {"type": "string", "description": "New description"},
                "access": {
                    "type": "string",
                    "enum": ["for_everyone", "by_invite"],
                    "description": "Access type",
                },
                "external_id": {"type": "string", "description": "External ID"},
                "parent_entity_uid": {
                    "type": "string",
                    "description": "Parent entity UID for nesting spaces",
                },
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}",
            path_fields=("space_id",),
            body_fields=(
                "title",
                "description",
                "access",
                "external_id",
                "parent_entity_uid",
                "sort_order",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten spaces update --space-id 123 --title "Updated"',
                description="Update a space.",
            ),
        ),
    ),
    make_tool(
        canonical_name="spaces.delete",
        mcp_alias="kaiten_delete_space",
        description="Delete a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {"space_id": {"type": "integer", "description": "Space ID"}},
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="DELETE", path_template="/spaces/{space_id}", path_fields=("space_id",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten spaces delete --space-id 123", description="Delete a space."
            ),
        ),
    ),
)
