"""Custom property and select-value tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="custom-properties.list",
        mcp_alias="kaiten_list_custom_properties",
        description="List company custom properties.",
        input_schema={
            "type": "object",
            "properties": {
                "include_values": {"type": "boolean", "description": "Include select/catalog values"},
                "include_author": {"type": "boolean", "description": "Include author user object"},
                "types": {"type": "string", "description": "Comma-separated type names to filter"},
                "conditions": {"type": "string", "description": "Comma-separated conditions to filter"},
                "query": {"type": "string", "description": "Search filter by name"},
                "order_by": {"type": "string", "description": "Sort column"},
                "order_direction": {"type": "string", "description": "Sort direction (asc or desc)"},
                "board_id": {"type": "integer", "description": "Filter properties available on a specific board"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties",
            query_fields=(
                "include_values",
                "include_author",
                "types",
                "conditions",
                "query",
                "order_by",
                "order_direction",
                "board_id",
                "limit",
                "offset",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten custom-properties list --types select --json', description="List custom properties."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.get",
        mcp_alias="kaiten_get_custom_property",
        description="Get a custom property by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(method="GET", path_template="/company/custom-properties/{property_id}", path_fields=("property_id",)),
        examples=(
            ExampleSpec(command="kaiten custom-properties get --property-id 5 --json", description="Get a custom property."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.create",
        mcp_alias="kaiten_create_custom_property",
        description="Create a company custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Property name (1-255 chars)"},
                "type": {
                    "type": "string",
                    "enum": [
                        "string",
                        "number",
                        "date",
                        "email",
                        "checkbox",
                        "select",
                        "formula",
                        "url",
                        "collective_score",
                        "vote",
                        "collective_vote",
                        "catalog",
                        "phone",
                        "user",
                        "attachment",
                    ],
                    "description": "Property type",
                },
                "show_on_facade": {"type": "boolean", "description": "Show on card facade"},
                "multi_select": {"type": "boolean", "description": "Enable multi-select"},
                "colorful": {"type": "boolean", "description": "Enable colors for select values"},
                "multiline": {"type": "boolean", "description": "Multiline text field"},
                "values_creatable_by_users": {"type": "boolean", "description": "Allow regular users to create values"},
                "values_type": {"type": "string", "enum": ["number", "text"], "description": "Values type (required for collective_score)"},
                "vote_variant": {"type": "string", "enum": ["rating", "scale", "emoji_set"], "description": "Vote variant (required for vote/collective_vote)"},
                "color": {"type": "integer", "description": "Color index"},
                "data": {"type": "object", "description": "Type-specific data; required for vote/collective_vote and some other typed properties"},
            },
            "required": ["name", "type"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-properties",
            body_fields=(
                "name",
                "type",
                "show_on_facade",
                "multi_select",
                "colorful",
                "multiline",
                "values_creatable_by_users",
                "values_type",
                "vote_variant",
                "color",
                "data",
            ),
        ),
        examples=(
            ExampleSpec(command='kaiten custom-properties create --name Status --type select --json', description="Create a custom property."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.update",
        mcp_alias="kaiten_update_custom_property",
        description="Update a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "name": {"type": "string", "description": "New name"},
                "condition": {"type": "string", "enum": ["active", "inactive"], "description": "Status"},
                "show_on_facade": {"type": "boolean", "description": "Show on card facade"},
                "multi_select": {"type": "boolean", "description": "Multi-select mode"},
                "colorful": {"type": "boolean", "description": "Enable colors"},
                "multiline": {"type": "boolean", "description": "Multiline mode"},
                "values_creatable_by_users": {"type": "boolean", "description": "Allow users to create values"},
                "is_used_as_progress": {"type": "boolean", "description": "Use this formula property as progress"},
                "color": {"type": "integer", "description": "Color index"},
                "data": {"type": "object", "description": "Type-specific data"},
                "fields_settings": {"type": "object", "description": "Catalog fields configuration"},
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}",
            path_fields=("property_id",),
            body_fields=(
                "name",
                "condition",
                "show_on_facade",
                "multi_select",
                "colorful",
                "multiline",
                "values_creatable_by_users",
                "is_used_as_progress",
                "color",
                "data",
                "fields_settings",
            ),
        ),
        examples=(
            ExampleSpec(command='kaiten custom-properties update --property-id 5 --name Priority --json', description="Update a custom property."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.delete",
        mcp_alias="kaiten_delete_custom_property",
        description="Delete a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/company/custom-properties/{property_id}", path_fields=("property_id",)),
        examples=(
            ExampleSpec(command="kaiten custom-properties delete --property-id 5 --json", description="Delete a custom property."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.list",
        mcp_alias="kaiten_list_select_values",
        description="List select values for a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "query": {"type": "string", "description": "Search filter by value text"},
                "order_by": {
                    "type": "string",
                    "enum": ["id", "sort_order", "match_query_priority"],
                    "description": "Sort order mode",
                },
                "conditions": {"type": "string", "description": "Comma-separated conditions"},
                "v2_select_search": {"type": "boolean", "description": "Use v2 search mode"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/select-values",
            path_fields=("property_id",),
            query_fields=("query", "order_by", "conditions", "v2_select_search", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten custom-properties select-values list --property-id 3 --json", description="List select values."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.get",
        mcp_alias="kaiten_get_select_value",
        description="Get a single select value by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Select value ID"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/select-values/{value_id}",
            path_fields=("property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(command="kaiten custom-properties select-values get --property-id 3 --value-id 10 --json", description="Get a select value."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.create",
        mcp_alias="kaiten_create_select_value",
        description="Create a select value for a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value": {"type": "string", "description": "Select value text"},
                "color": {"type": "integer", "description": "Color index"},
                "sort_order": {"type": "number", "description": "Sort order (float)"},
            },
            "required": ["property_id", "value"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-properties/{property_id}/select-values",
            path_fields=("property_id",),
            body_fields=("value", "color", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten custom-properties select-values create --property-id 3 --value High --json', description="Create a select value."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.update",
        mcp_alias="kaiten_update_select_value",
        description="Update a select value for a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Select value ID"},
                "value": {"type": "string", "description": "New value text"},
                "condition": {"type": "string", "enum": ["active", "inactive"], "description": "Value status"},
                "color": {"type": "integer", "description": "Color index"},
                "sort_order": {"type": "number", "description": "Sort order (float)"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}/select-values/{value_id}",
            path_fields=("property_id", "value_id"),
            body_fields=("value", "condition", "color", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten custom-properties select-values update --property-id 3 --value-id 10 --value Critical --json', description="Update a select value."),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.delete",
        mcp_alias="kaiten_delete_select_value",
        description="Delete (soft) a select value by marking it as deleted.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Select value ID"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}/select-values/{value_id}",
            path_fields=("property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(command="kaiten custom-properties select-values delete --property-id 3 --value-id 10 --json", description="Soft-delete a select value."),
        ),
    ),
)
