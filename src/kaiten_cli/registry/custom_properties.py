"""Custom property and select-value tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.public_validation import validate_public_request
from kaiten_cli.runtime.behaviors import (
    payload_body_request,
    reject_custom_property_include_values,
)


CARD_CATALOG_PROPERTY_USAGE_NOTES = (
    "A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.",
    "Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.",
    "Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.",
    "Allowed entries/options are managed separately from the field definition.",
    "Do not confuse this with UI catalog tables (`custom-directories`) or document groups.",
)

CATALOG_VALUES_USAGE_NOTES = (
    "These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.",
    "Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.",
    "Use these commands for values/options of a card field of type `Справочник` / `справочник`.",
    "Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).",
    "For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.",
    "Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.",
)


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
                    "description": "Deprecated compatibility input. false is ignored; true is rejected. Use select-values.list or catalog-values.list instead.",
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
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
                "compact": {
                    "type": "boolean",
                    "description": "Returns the minimum set of parameters of custom properties",
                },
                "load_by_ids": {
                    "type": "boolean",
                    "description": "Returns custom properties by ids if ids parameter is presented",
                },
                "ids": {"type": "array", "description": "Array of custom property ids"},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties",
            query_fields=(
                "include_author",
                "types",
                "conditions",
                "query",
                "order_by",
                "order_direction",
                "board_id",
                "limit",
                "offset",
                "compact",
                "load_by_ids",
                "ids",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            payload_validator=reject_custom_property_include_values,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties list --types select",
                description="List custom properties.",
            ),
            ExampleSpec(
                command="kaiten --json custom-properties list --types catalog",
                description="List card fields of type Catalog/Справочник.",
            ),
        ),
        usage_notes=CARD_CATALOG_PROPERTY_USAGE_NOTES
        + (
            "include_values is retained only as a migration input: false is ignored and true fails with replacement command guidance.",
        ),
    ),
    make_tool(
        canonical_name="custom-properties.get",
        mcp_alias="kaiten_get_custom_property",
        description="Get a custom property by ID.",
        input_schema={
            "type": "object",
            "properties": {"property_id": {"type": "integer", "description": "Property ID"}},
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}",
            path_fields=("property_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties get --property-id 5",
                description="Get a custom property.",
            ),
        ),
        usage_notes=CARD_CATALOG_PROPERTY_USAGE_NOTES,
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
                "show_on_facade": {
                    "type": "boolean",
                    "description": "Show on card facade",
                    "default": False,
                },
                "multi_select": {
                    "type": ["boolean", "null"],
                    "description": "Enable multi-select",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines is select property used as multi select",
                        },
                        {"type": "null", "description": "Empty multi select value"},
                    ],
                },
                "colorful": {
                    "type": ["boolean", "null"],
                    "description": "Enable colors for select values",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines should select color when creating new select value.",
                        },
                        {"type": "null", "description": "Empty colorful value"},
                    ],
                },
                "multiline": {
                    "type": "boolean",
                    "description": "Multiline text field",
                    "default": False,
                },
                "values_creatable_by_users": {
                    "type": ["boolean", "null"],
                    "description": "Allow regular users to create values",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines if users with writer role are able to create new select property values.",
                        },
                        {"type": "null", "description": "Empty values_creatable_by_users value"},
                    ],
                },
                "values_type": {
                    "type": ["string", "null"],
                    "enum": ["number", "text"],
                    "description": "Values type (required for collective_score)",
                    "x-documentation-alternatives": [
                        {
                            "type": "null",
                            "description": "Empty for any type except collective value",
                        },
                        {"enum": ["number", "text"], "description": "Type of values"},
                    ],
                },
                "vote_variant": {
                    "type": ["string", "null"],
                    "enum": ["rating", "scale", "emoji_set"],
                    "description": "Vote variant (required for vote/collective_vote)",
                    "x-documentation-alternatives": [
                        {
                            "type": "null",
                            "description": "Empty vote variant - for custom properties not of type vote and collective vote",
                        },
                        {
                            "enum": ["rating", "scale", "emoji_set"],
                            "description": "Type of vote or collective vote custom properties",
                        },
                    ],
                },
                "color": {
                    "type": ["integer", "null"],
                    "description": "Color index",
                    "x-documentation-alternatives": [
                        {"type": ["integer"], "description": "Color of catalog custom property"},
                        {"type": "null", "description": "Catalog custom property without color"},
                    ],
                },
                "data": {
                    "type": "object",
                    "description": "Type-specific data; required for vote/collective_vote and some other typed properties",
                    "properties": {
                        "restrictions": {
                            "type": "object",
                            "properties": {
                                "min": {
                                    "description": "Minimum allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Minimum allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty minimum value"},
                                    ],
                                },
                                "max": {
                                    "description": "Maximum allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Maximum allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                                "minLength": {
                                    "minimum": 1,
                                    "description": "Minimum length allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "minimum": 1,
                                            "description": "Minimum length allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty minimum length"},
                                    ],
                                },
                                "maxLength": {
                                    "minimum": 1,
                                    "description": "Minimum length allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "minimum": 1,
                                            "description": "Minimum length allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty maximum length"},
                                    ],
                                },
                                "maxFilesCount": {
                                    "description": "Maximum allowed files count",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Maximum allowed files count",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                                "filesExtensions": {
                                    "description": "Allowed files extensions",
                                    "type": ["string", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "string",
                                            "description": "Allowed files extensions",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                            },
                            "description": "Restrictions on input values",
                            "x-documentation-alternatives": [
                                {"required": ["min"]},
                                {"required": ["max"]},
                                {"required": ["minLength"]},
                                {"required": ["maxLength"]},
                                {"required": ["maxFilesCount"]},
                                {"required": ["filesExtensions"]},
                            ],
                        },
                        "formula": {
                            "type": "string",
                            "description": "Formula content",
                            "minLength": 1,
                        },
                        "emoji": {
                            "type": "string",
                            "description": "Emoji for vote property of variant rating",
                            "minLength": 1,
                        },
                        "count": {
                            "type": "integer",
                            "description": "Count of emojis for vote property",
                            "minimum": 2,
                            "maximum": 10,
                        },
                        "emojis": {
                            "type": "array",
                            "description": "List of emojis for vote property of variant emoji_set",
                            "items": {"type": "string", "minLength": 1},
                        },
                        "min": {
                            "type": "integer",
                            "description": "Min value for vote property of variant scale",
                        },
                        "max": {
                            "type": "integer",
                            "description": "Max value for vote property of variant scale",
                        },
                        "calculation_method": {
                            "enum": ["average", "sum"],
                            "description": "Calculation method for vote property of variant scale",
                            "type": "string",
                        },
                    },
                    "x-documentation-alternatives": [
                        {"required": ["restrictions"]},
                        {"required": ["formula"]},
                        {"required": ["emoji", "count"]},
                        {"required": ["emojis"]},
                        {"required": ["min", "max", "calculation_method"]},
                    ],
                },
                "formula": {"type": "string", "description": "Formula for calculation"},
                "formula_source_card": {
                    "type": "object",
                    "description": "Card data from which are used to calculate the formula",
                },
                "fields_settings": {
                    "type": "object",
                    "minProperties": 1,
                    "patternProperties": {
                        "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Field name",
                                    "minLength": 1,
                                },
                                "required": {
                                    "type": "boolean",
                                    "description": "Determines is field is required",
                                },
                                "deleted": {
                                    "type": "boolean",
                                    "description": "Determines is field is deleted",
                                    "default": False,
                                },
                                "sortOrder": {
                                    "type": "number",
                                    "minimum": 1,
                                    "description": "Minimum sort order of field",
                                },
                            },
                            "x-documentation-additionalProperties": False,
                        }
                    },
                    "x-documentation-additionalProperties": False,
                },
            },
            "required": [],
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
                "formula",
                "formula_source_card",
                "fields_settings",
            ),
        ),
        runtime_behavior=RuntimeBehavior(payload_validator=validate_public_request),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties create --name Status --type select",
                description="Create a custom property.",
            ),
            ExampleSpec(
                command='kaiten --json custom-properties create --name "Client" --type catalog',
                description="Create a card field of type Catalog/Справочник.",
            ),
        ),
        usage_notes=CARD_CATALOG_PROPERTY_USAGE_NOTES,
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
                "show_on_facade": {
                    "type": "boolean",
                    "description": "Show on card facade",
                    "default": False,
                },
                "multi_select": {
                    "type": ["boolean", "null"],
                    "description": "Multi-select mode",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines is select property used as multi select",
                        },
                        {"type": "null", "description": "Empty multi select value"},
                    ],
                },
                "colorful": {
                    "type": ["boolean", "null"],
                    "description": "Enable colors",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines should select color when creating new select value.",
                        },
                        {"type": "null", "description": "Empty colorful value"},
                    ],
                },
                "multiline": {"type": "boolean", "description": "Multiline mode", "default": False},
                "values_creatable_by_users": {
                    "type": ["boolean", "null"],
                    "description": "Allow users to create values",
                    "x-documentation-alternatives": [
                        {
                            "type": ["boolean"],
                            "description": "Used for select properties. Determines if users with writer roles are able to create new select property values.",
                        },
                        {"type": "null", "description": "Empty values_creatable_by_users value"},
                    ],
                },
                "is_used_as_progress": {
                    "type": "boolean",
                    "description": "Use this formula property as progress",
                    "default": False,
                },
                "color": {
                    "type": ["integer", "null"],
                    "description": "Color index",
                    "x-documentation-alternatives": [
                        {"type": ["integer"], "description": "Color of catalog custom property"},
                        {"type": "null", "description": "Catalog custom property without color"},
                    ],
                },
                "data": {
                    "type": "object",
                    "description": "Type-specific data",
                    "properties": {
                        "restrictions": {
                            "type": "object",
                            "properties": {
                                "min": {
                                    "description": "Minimum allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Minimum allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty minimum value"},
                                    ],
                                },
                                "max": {
                                    "description": "Maximum allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Maximum allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                                "minLength": {
                                    "minimum": 1,
                                    "description": "Minimum length allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "minimum": 1,
                                            "description": "Minimum length allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty minimum length"},
                                    ],
                                },
                                "maxLength": {
                                    "minimum": 1,
                                    "description": "Minimum length allowed on input value",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "minimum": 1,
                                            "description": "Minimum length allowed on input value",
                                        },
                                        {"type": "null", "description": "Empty maximum length"},
                                    ],
                                },
                                "maxFilesCount": {
                                    "description": "Maximum allowed files count",
                                    "type": ["number", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "number",
                                            "description": "Maximum allowed files count",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                                "filesExtensions": {
                                    "description": "Allowed files extensions",
                                    "type": ["string", "null"],
                                    "x-documentation-alternatives": [
                                        {
                                            "type": "string",
                                            "description": "Allowed files extensions",
                                        },
                                        {"type": "null", "description": "Empty maximum value"},
                                    ],
                                },
                            },
                            "description": "Restrictions on input values",
                            "x-documentation-alternatives": [
                                {"required": ["min"]},
                                {"required": ["max"]},
                                {"required": ["minLength"]},
                                {"required": ["maxLength"]},
                                {"required": ["maxFilesCount"]},
                                {"required": ["filesExtensions"]},
                            ],
                        },
                        "formula": {
                            "type": "string",
                            "description": "Formula content",
                            "minLength": 1,
                        },
                        "emoji": {
                            "type": "string",
                            "description": "Emoji for vote property of variant rating",
                            "minLength": 1,
                        },
                        "count": {
                            "type": "integer",
                            "description": "Count of emojis for vote property",
                            "minimum": 2,
                            "maximum": 10,
                        },
                        "emojis": {
                            "type": "array",
                            "description": "List of emojis for vote property of variant emoji_set",
                            "items": {"type": "string", "minLength": 1},
                        },
                        "min": {
                            "type": "number",
                            "description": "Min value for vote property of variant scale",
                        },
                        "max": {
                            "type": "number",
                            "description": "Max value for vote property of variant scale",
                        },
                        "calculation_method": {
                            "enum": ["average", "sum"],
                            "description": "Calculation method for vote property of variant scale",
                            "type": "string",
                        },
                    },
                    "x-documentation-alternatives": [
                        {"required": ["restrictions"]},
                        {"required": ["formula"]},
                        {"required": ["emoji", "count"]},
                        {"required": ["emojis"]},
                        {"required": ["min", "max", "calculation_method"]},
                    ],
                },
                "fields_settings": {
                    "type": ["object", "null"],
                    "description": "Catalog fields configuration",
                    "minProperties": 1,
                    "patternProperties": {
                        "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Field name",
                                    "minLength": 1,
                                },
                                "required": {
                                    "type": "boolean",
                                    "description": "Determines is field is required",
                                },
                                "deleted": {
                                    "type": "boolean",
                                    "description": "Determines is field is deleted",
                                    "default": False,
                                },
                                "sortOrder": {
                                    "type": "number",
                                    "minimum": 1,
                                    "description": "Minimum sort order of field",
                                },
                            },
                            "x-documentation-additionalProperties": False,
                        }
                    },
                    "x-documentation-alternatives": [
                        {
                            "type": "object",
                            "minProperties": 1,
                            "additionalProperties": False,
                            "patternProperties": {
                                "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Field name",
                                            "minLength": 1,
                                        },
                                        "required": {
                                            "type": "boolean",
                                            "description": "Determines is field is required",
                                        },
                                        "deleted": {
                                            "type": "boolean",
                                            "description": "Determines is field is deleted",
                                            "default": False,
                                        },
                                        "sortOrder": {
                                            "type": "number",
                                            "minimum": 1,
                                            "description": "Minimum sort order of field",
                                        },
                                    },
                                    "additionalProperties": False,
                                }
                            },
                        },
                        {"type": "null"},
                    ],
                    "x-documentation-additionalProperties": False,
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
                command="kaiten --json custom-properties update --property-id 5 --name Priority",
                description="Update a custom property.",
            ),
        ),
        usage_notes=CARD_CATALOG_PROPERTY_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-properties.delete",
        mcp_alias="kaiten_delete_custom_property",
        description="Delete a custom property.",
        input_schema={
            "type": "object",
            "properties": {"property_id": {"type": "integer", "description": "Property ID"}},
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-properties/{property_id}",
            path_fields=("property_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties delete --property-id 5",
                description="Delete a custom property.",
            ),
        ),
        usage_notes=CARD_CATALOG_PROPERTY_USAGE_NOTES,
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
                "conditions": {
                    "type": ["string", "array"],
                    "description": "Comma-separated conditions",
                },
                "v2_select_search": {"type": "boolean", "description": "Use v2 search mode"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
                "ids": {
                    "type": "array",
                    "description": "Array of ids to filter by. Works only if v2_select_search param is true",
                },
            },
            "required": ["property_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-properties/{property_id}/select-values",
            path_fields=("property_id",),
            query_fields=(
                "query",
                "order_by",
                "conditions",
                "v2_select_search",
                "limit",
                "offset",
                "ids",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties select-values list --property-id 3",
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
                command="kaiten --json custom-properties select-values get --property-id 3 --value-id 10",
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
                "color": {
                    "type": ["integer", "null"],
                    "description": "Color index",
                    "x-documentation-alternatives": [
                        {
                            "type": ["integer"],
                            "description": "Color of custom property select value",
                        },
                        {
                            "type": "null",
                            "description": "Custom property select value without color",
                        },
                    ],
                },
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
                command="kaiten --json custom-properties select-values create --property-id 3 --value High",
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
                "color": {
                    "type": ["integer", "null"],
                    "description": "Color index",
                    "x-documentation-alternatives": [
                        {
                            "type": ["integer"],
                            "description": "Color of custom property select value",
                        },
                        {
                            "type": "null",
                            "description": "Custom property select value without color",
                        },
                    ],
                },
                "sort_order": {"type": "number", "description": "Sort order (float)"},
                "deleted": {
                    "type": "boolean",
                    "description": "Custom property select value delete condition",
                },
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}/select-values/{value_id}",
            path_fields=("property_id", "value_id"),
            body_fields=("value", "condition", "color", "sort_order", "deleted"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties select-values update --property-id 3 --value-id 10 --value Critical",
                description="Update a select value.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.select-values.delete",
        mcp_alias="kaiten_delete_select_value",
        description="Delete (soft) a select value through the official DELETE route.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "value_id": {"type": "integer", "description": "Select value ID"},
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-properties/{property_id}/select-values/{value_id}",
            path_fields=("property_id", "value_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties select-values delete --property-id 3 --value-id 10",
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
                command="kaiten --json custom-properties tree-entities list --property-id 5",
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
                "tree_entity_uid": {
                    "type": "string",
                    "description": "Tree entity UID",
                    "format": "uuid",
                },
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
                command="kaiten --json custom-properties tree-entities add --property-id 5 --tree-entity-uid entity-uuid",
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
                command="kaiten --json custom-properties tree-entities remove --property-id 5 --tree-entity-uid entity-uuid",
                description="Remove a tree entity from a custom property.",
            ),
        ),
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.list",
        mcp_alias="kaiten_list_catalog_values",
        description="List catalog property values for a catalog-typed custom property.",
        input_schema={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID"},
                "query": {"type": "string", "description": "Text search filter by catalog values"},
                "conditions": {
                    "type": "string",
                    "description": "Condition filter: active or inactive",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
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
                command="kaiten --json custom-properties catalog-values list --property-id 5",
                description="List catalog property values.",
            ),
        ),
        usage_notes=CATALOG_VALUES_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.get",
        mcp_alias="kaiten_get_catalog_value",
        description="Get a catalog property value for a catalog-typed custom property.",
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
                command="kaiten --json custom-properties catalog-values get --property-id 5 --value-id 10",
                description="Get a catalog property value.",
            ),
        ),
        usage_notes=CATALOG_VALUES_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.create",
        mcp_alias="kaiten_create_catalog_value",
        description="Create a catalog property value for a catalog-typed custom property.",
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
                command='kaiten --json custom-properties catalog-values create --property-id 5 --value \'{"field-uuid":"Alice"}\'',
                description="Create a catalog property value.",
            ),
        ),
        usage_notes=CATALOG_VALUES_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.update",
        mcp_alias="kaiten_update_catalog_value",
        description="Update a catalog property value for a catalog-typed custom property.",
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
                "deleted": {
                    "type": "boolean",
                    "description": "Custom property catalog value delete condition",
                },
            },
            "required": ["property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-properties/{property_id}/catalog-values/{value_id}",
            path_fields=("property_id", "value_id"),
            body_fields=("name", "value", "condition", "payload", "deleted"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-properties catalog-values update --property-id 5 --value-id 10 --name "Alice"',
                description="Update a catalog property value.",
            ),
        ),
        usage_notes=CATALOG_VALUES_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-properties.catalog-values.delete",
        mcp_alias="kaiten_delete_catalog_value",
        description="Delete a catalog property value for a catalog-typed custom property.",
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
                command="kaiten --json custom-properties catalog-values delete --property-id 5 --value-id 10",
                description="Delete a catalog property value.",
            ),
        ),
        usage_notes=CATALOG_VALUES_USAGE_NOTES,
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
                command="kaiten --json custom-properties collective-score-values list --card-id 10 --property-id 5",
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
                command="kaiten --json custom-properties collective-score-values create --card-id 10 --property-id 5 --value 8",
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
                "value": {
                    "type": ["string", "number", "object", "null"],
                    "description": "Score value.",
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "description": "Value of card collective score custom property",
                            "minLength": 1,
                            "maxLength": 512,
                        },
                        {"type": "null", "description": "Empty value"},
                    ],
                },
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
                command="kaiten --json custom-properties collective-score-values update --card-id 10 --property-id 5 --value-id 1 --value 9",
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
                command="kaiten --json custom-properties collective-vote-values list --card-id 10 --property-id 5",
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
                "emoji_vote": {
                    "type": "string",
                    "description": "Value of card collective vote of type emoji_set",
                    "minLength": 1,
                    "maxLength": 12,
                },
                "number_vote": {
                    "type": "integer",
                    "description": "Value of card collective vote of type scale or rating",
                },
            },
            "required": ["card_id", "property_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values",
            path_fields=("card_id", "property_id"),
            body_fields=("value", "payload", "emoji_vote", "number_vote"),
        ),
        runtime_behavior=RuntimeBehavior(
            request_shaper=payload_body_request, payload_validator=validate_public_request
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties collective-vote-values create --card-id 10 --property-id 5 --value 1",
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
                "number_vote": {
                    "description": "Value of card collective vote of type scale or rating",
                    "type": ["number", "null"],
                    "x-documentation-alternatives": [
                        {
                            "type": "number",
                            "description": "Value of card collective vote of type scale or rating",
                        },
                        {
                            "type": "null",
                            "description": "Empty value of card collective vote of type scale or rating",
                        },
                    ],
                },
            },
            "required": ["card_id", "property_id", "value_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}",
            path_fields=("card_id", "property_id", "value_id"),
            body_fields=("value", "payload", "number_vote"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties collective-vote-values update --card-id 10 --property-id 5 --value-id 1 --value 2",
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
                "emoji_vote": {
                    "type": "string",
                    "description": " removed emoji_vote",
                    "minLength": 1,
                    "maxLength": 12,
                },
            },
            "required": ["card_id", "property_id", "value_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}",
            path_fields=("card_id", "property_id", "value_id"),
            body_fields=("emoji_vote",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-properties collective-vote-values delete --card-id 10 --property-id 5 --value-id 1",
                description="Delete a collective vote value.",
            ),
        ),
    ),
)
