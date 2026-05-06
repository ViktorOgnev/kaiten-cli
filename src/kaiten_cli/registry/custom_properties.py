"""Custom property and select-value tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import payload_body_request, select_value_soft_delete_request


TOOLS = (
    make_tool(
        canonical_name="custom-properties.list",
        mcp_alias="kaiten_list_custom_properties",
        description="List company custom properties.",
        input_schema={
            "type": "object",
            "properties": {
                "include_values": {
                    "type": "boolean",
                    "description": "Include select/catalog values",
                },
                "include_author": {"type": "boolean", "description": "Include author user object"},
                "types": {"type": "string", "description": "Comma-separated type names to filter"},
                "conditions": {
                    "type": "string",
                    "description": "Comma-separated conditions to filter",
                },
                "query": {"type": "string", "description": "Search filter by name"},
                "order_by": {"type": "string", "description": "Sort column"},
                "order_direction": {
                    "type": "string",
                    "description": "Sort direction (asc or desc)",
                },
                "board_id": {
                    "type": "integer",
                    "description": "Filter properties available on a specific board",
                },
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
            ExampleSpec(
                command="kaiten custom-properties list --types select --json",
                description="List custom properties.",
            ),
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
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}",
            path_fields=("property_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties get --property-id 5 --json",
                description="Get a custom property.",
            ),
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
                "values_creatable_by_users": {
                    "type": "boolean",
                    "description": "Allow regular users to create values",
                },
                "values_type": {
                    "type": "string",
                    "enum": ["number", "text"],
                    "description": "Values type (required for collective_score)",
                },
                "vote_variant": {
                    "type": "string",
                    "enum": ["rating", "scale", "emoji_set"],
                    "description": "Vote variant (required for vote/collective_vote)",
                },
                "color": {"type": "integer", "description": "Color index"},
                "data": {
                    "type": "object",
                    "description": "Type-specific data; required for vote/collective_vote and some other typed properties",
                },
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
            ExampleSpec(
                command="kaiten custom-properties create --name Status --type select --json",
                description="Create a custom property.",
            ),
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
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "description": "Status",
                },
                "show_on_facade": {"type": "boolean", "description": "Show on card facade"},
                "multi_select": {"type": "boolean", "description": "Multi-select mode"},
                "colorful": {"type": "boolean", "description": "Enable colors"},
                "multiline": {"type": "boolean", "description": "Multiline mode"},
                "values_creatable_by_users": {
                    "type": "boolean",
                    "description": "Allow users to create values",
                },
                "is_used_as_progress": {
                    "type": "boolean",
                    "description": "Use this formula property as progress",
                },
                "color": {"type": "integer", "description": "Color index"},
                "data": {"type": "object", "description": "Type-specific data"},
                "fields_settings": {
                    "type": "object",
                    "description": "Catalog fields configuration",
                },
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
            ExampleSpec(
                command="kaiten custom-properties update --property-id 5 --name Priority --json",
                description="Update a custom property.",
            ),
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
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-properties/{property_id}",
            path_fields=("property_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties delete --property-id 5 --json",
                description="Delete a custom property.",
            ),
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
            ExampleSpec(
                command="kaiten custom-properties select-values list --property-id 3 --json",
                description="List select values.",
            ),
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
            ExampleSpec(
                command="kaiten custom-properties select-values get --property-id 3 --value-id 10 --json",
                description="Get a select value.",
            ),
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
            ExampleSpec(
                command="kaiten custom-properties select-values create --property-id 3 --value High --json",
                description="Create a select value.",
            ),
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
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "description": "Value status",
                },
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
            ExampleSpec(
                command="kaiten custom-properties select-values update --property-id 3 --value-id 10 --value Critical --json",
                description="Update a select value.",
            ),
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
        runtime_behavior=RuntimeBehavior(request_shaper=select_value_soft_delete_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties select-values delete --property-id 3 --value-id 10 --json",
                description="Soft-delete a select value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.tree-entities.list",
        mcp_alias="kaiten_list_custom_property_tree_entities",
        description="List tree entities attached to a custom property.",
        input_schema={
            "type": "object",
            "properties": {"property_id": {"type": "integer", "description": "Property ID"}},
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/tree-entities",
            path_fields=("property_id",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties tree-entities list --property-id 5 --json",
                description="List custom property tree entities.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.tree-entities.add",
        mcp_alias="kaiten_add_custom_property_tree_entity",
        description="Attach a tree entity to a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "tree_entity_uid": {"type": "string", "description": "Tree entity UID"},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["property_id", "tree_entity_uid"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-properties/{property_id}/tree-entities",
            path_fields=("property_id",),
            body_fields=("tree_entity_uid", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties tree-entities add --property-id 5 --tree-entity-uid entity-uuid --json",
                description="Attach a tree entity to a custom property.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.tree-entities.remove",
        mcp_alias="kaiten_remove_custom_property_tree_entity",
        description="Remove a tree entity from a custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "tree_entity_uid": {"type": "string", "description": "Tree entity UID"},
            },
            "required": ["property_id", "tree_entity_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-properties/{property_id}/tree-entities/{tree_entity_uid}",
            path_fields=("property_id", "tree_entity_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties tree-entities remove --property-id 5 --tree-entity-uid entity-uuid --json",
                description="Remove a tree entity from a custom property.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.list",
        mcp_alias="kaiten_list_catalog_values",
        description="List catalog values for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "query": {"type": "string", "description": "Text search filter by catalog values"},
                "conditions": {
                    "type": "string",
                    "description": "Condition filter: active or inactive",
                },
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/catalog-values",
            path_fields=("property_id",),
            query_fields=("query", "conditions", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties catalog-values list --property-id 5 --json",
                description="List catalog values.",
            ),
        ),
        usage_notes=(
            "This manages values of a catalog-typed custom property, not the UI `Каталоги` table itself.",
            "For the UI `Каталоги` feature use custom-directories, custom-directory-fields, and custom-directory-records.",
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.get",
        mcp_alias="kaiten_get_catalog_value",
        description="Get a catalog value for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Catalog value ID"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/catalog-values/{value_id}",
            path_fields=("property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties catalog-values get --property-id 5 --value-id 10 --json",
                description="Get a catalog value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.create",
        mcp_alias="kaiten_create_catalog_value",
        description="Create a catalog value for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "name": {"type": "string", "description": "Catalog value display name"},
                "value": {
                    "type": "object",
                    "description": "Catalog value fields keyed by field UID.",
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["property_id", "value"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-properties/{property_id}/catalog-values",
            path_fields=("property_id",),
            body_fields=("name", "value", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten custom-properties catalog-values create --property-id 5 --value \'{"field-uuid":"Alice"}\' --json',
                description="Create a catalog value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.update",
        mcp_alias="kaiten_update_catalog_value",
        description="Update a catalog value for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Catalog value ID"},
                "name": {"type": "string", "description": "Catalog value display name"},
                "value": {
                    "type": "object",
                    "description": "Catalog value fields keyed by field UID.",
                },
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "description": "Value condition",
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}/catalog-values/{value_id}",
            path_fields=("property_id", "value_id"),
            body_fields=("name", "value", "condition", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten custom-properties catalog-values update --property-id 5 --value-id 10 --name "Alice" --json',
                description="Update a catalog value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.delete",
        mcp_alias="kaiten_delete_catalog_value",
        description="Delete a catalog value for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Catalog value ID"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-properties/{property_id}/catalog-values/{value_id}",
            path_fields=("property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties catalog-values delete --property-id 5 --value-id 10 --json",
                description="Delete a catalog value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-score-values.list",
        mcp_alias="kaiten_list_collective_score_values",
        description="List collective score values for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
            },
            "required": ["card_id", "property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-score-values",
            path_fields=("card_id", "property_id"),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-score-values list --card-id 10 --property-id 5 --json",
                description="List collective score values.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-score-values.create",
        mcp_alias="kaiten_create_collective_score_value",
        description="Create a collective score value for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
                "value": {"type": ["string", "number", "object"], "description": "Score value."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["card_id", "property_id", "value"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-score-values",
            path_fields=("card_id", "property_id"),
            body_fields=("value", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-score-values create --card-id 10 --property-id 5 --value 8 --json",
                description="Create a collective score value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-score-values.update",
        mcp_alias="kaiten_update_collective_score_value",
        description="Update a collective score value for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Score value ID"},
                "value": {"type": ["string", "number", "object"], "description": "Score value."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["card_id", "property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-score-values/{value_id}",
            path_fields=("card_id", "property_id", "value_id"),
            body_fields=("value", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-score-values update --card-id 10 --property-id 5 --value-id 1 --value 9 --json",
                description="Update a collective score value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-vote-values.list",
        mcp_alias="kaiten_list_collective_vote_values",
        description="List collective vote values for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
            },
            "required": ["card_id", "property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values",
            path_fields=("card_id", "property_id"),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-vote-values list --card-id 10 --property-id 5 --json",
                description="List collective vote values.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-vote-values.create",
        mcp_alias="kaiten_create_collective_vote_value",
        description="Create a collective vote value for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
                "value": {"type": ["string", "number", "object"], "description": "Vote value."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["card_id", "property_id", "value"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values",
            path_fields=("card_id", "property_id"),
            body_fields=("value", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-vote-values create --card-id 10 --property-id 5 --value 1 --json",
                description="Create a collective vote value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-vote-values.update",
        mcp_alias="kaiten_update_collective_vote_value",
        description="Update a collective vote value for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Vote value ID"},
                "value": {"type": ["string", "number", "object"], "description": "Vote value."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs.",
                },
            },
            "required": ["card_id", "property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}",
            path_fields=("card_id", "property_id", "value_id"),
            body_fields=("value", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-vote-values update --card-id 10 --property-id 5 --value-id 1 --value 2 --json",
                description="Update a collective vote value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.collective-vote-values.delete",
        mcp_alias="kaiten_delete_collective_vote_value",
        description="Delete a collective vote value for a card custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Vote value ID"},
            },
            "required": ["card_id", "property_id", "value_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}",
            path_fields=("card_id", "property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten custom-properties collective-vote-values delete --card-id 10 --property-id 5 --value-id 1 --json",
                description="Delete a collective vote value.",
            ),
        ),
    ),
)
