"""Custom directory (Kaiten Catalog) tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import encode_object_query_request, payload_body_request

DIRECTORY_ID = {"type": "string", "description": "Custom directory ID (UUID)."}
FIELD_ID = {"type": "string", "description": "Custom directory field ID (UUID)."}
RECORD_ID = {"type": "string", "description": "Custom directory record ID (UUID)."}
CONDITIONS = {
    "type": "array",
    "description": 'Condition filters, for example ["active", "inactive", "removed"].',
}
PAYLOAD = {
    "type": "object",
    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
}

CATALOG_USAGE_NOTES = (
    "Kaiten Catalogs are table-like directories exposed by the Developers API as `custom-directories`.",
    "Use these commands for a catalog table with fields and records.",
    "Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.",
    "`custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.",
    "Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.",
    "Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.",
    "If a request says only `catalog` or `directory` before a mutation, clarify whether it means a catalog table (`custom-directories`), a catalog card field (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.",
    "The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.",
)


TOOLS = (
    make_tool(
        canonical_name="custom-directories.list",
        mcp_alias="kaiten_list_custom_directories",
        description="List Kaiten Catalogs (custom directories).",
        input_schema={
            "type": "object",
            "properties": {
                "include_fields": {"type": "boolean", "description": "Include directory fields"},
                "include_author": {"type": "boolean", "description": "Include author user object"},
                "include_records_count": {
                    "type": "boolean",
                    "description": "Include records_count in each directory",
                },
                "query": {
                    "type": "string",
                    "description": "Search by directory name (case-insensitive)",
                },
                "conditions": {
                    "type": "array",
                    "description": "Filter by condition values: active | inactive | removed",
                    "items": {"type": "string"},
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results, capped by Kaiten at 200.",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories",
            query_fields=(
                "include_fields",
                "include_author",
                "include_records_count",
                "query",
                "conditions",
                "limit",
                "offset",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=200, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directories list --include-fields --include-records-count",
                description="List Catalogs with field metadata and record counts.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directories.get",
        mcp_alias="kaiten_get_custom_directory",
        description="Get a Kaiten Catalog (custom directory).",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "include_fields": {
                    "type": "boolean",
                    "description": "Include directory field definitions.",
                },
                "include_author": {"type": "boolean", "description": "Include author user object."},
                "include_records_count": {
                    "type": "boolean",
                    "description": "Include records_count.",
                },
            },
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}",
            path_fields=("directory_id",),
            query_fields=("include_fields", "include_author", "include_records_count"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directories get --directory-id dir-uuid",
                description="Get a Catalog.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directories.create",
        mcp_alias="kaiten_create_custom_directory",
        description="Create a Kaiten Catalog (custom directory).",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Custom directory name"},
                "description": {
                    "type": ["string", "null"],
                    "description": "No description",
                    "x-documentation-alternatives": [
                        {"type": "null", "description": "No description"},
                        {"type": "string", "description": "Custom directory description"},
                    ],
                },
                "settings": {
                    "type": "object",
                    "description": "Directory settings, for example multi_select or allow_editing.",
                },
                "fields": {
                    "type": "array",
                    "description": "Directory fields definition",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 256,
                                "description": "Field name",
                            },
                            "type": {
                                "enum": [
                                    "string",
                                    "number",
                                    "date",
                                    "email",
                                    "url",
                                    "phone",
                                    "checkbox",
                                    "select",
                                    "user",
                                    "catalog",
                                    "directory_link",
                                    "file",
                                ],
                                "description": "Field type",
                                "type": "string",
                            },
                            "required": {
                                "type": "boolean",
                                "default": False,
                                "description": "Required field flag",
                            },
                            "sort_order": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Field position",
                            },
                            "custom_property_uid": {
                                "description": "Empty custom property reference",
                                "format": "uuid",
                                "type": ["null", "string"],
                                "x-documentation-alternatives": [
                                    {
                                        "type": "null",
                                        "description": "Empty custom property reference",
                                    },
                                    {
                                        "type": "string",
                                        "format": "uuid",
                                        "description": "Custom property UID (required for select/user/catalog fields)",
                                    },
                                ],
                            },
                            "linked_directory_id": {
                                "description": "Empty linked directory reference",
                                "format": "uuid",
                                "type": ["null", "string"],
                                "x-documentation-alternatives": [
                                    {
                                        "type": "null",
                                        "description": "Empty linked directory reference",
                                    },
                                    {
                                        "type": "string",
                                        "format": "uuid",
                                        "description": "Linked custom directory ID (required for directory_link fields)",
                                    },
                                ],
                            },
                        },
                        "required": ["name", "type"],
                    },
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
                "multi_select": {
                    "type": "boolean",
                    "default": False,
                    "description": "When enabled, directory records can store multiple values per field",
                },
                "allow_editing": {
                    "type": "boolean",
                    "default": False,
                    "description": "When enabled, directory records can be edited from cards without custom properties permission",
                },
                "display_field_index": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Index of the field to use as a display field. If omitted, the first field is used.",
                },
            },
            "required": ["name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-directories",
            body_fields=(
                "name",
                "description",
                "settings",
                "fields",
                "payload",
                "multi_select",
                "allow_editing",
                "display_field_index",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directories create --name "Contacts" --settings \'{"multi_select":false,"allow_editing":true}\'',
                description="Create a Catalog.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directories.update",
        mcp_alias="kaiten_update_custom_directory",
        description="Update a Kaiten Catalog (custom directory).",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "name": {"type": "string", "description": "Custom directory name"},
                "description": {
                    "type": ["string", "null"],
                    "description": "No description",
                    "x-documentation-alternatives": [
                        {"type": "null", "description": "No description"},
                        {"type": "string", "description": "Custom directory description"},
                    ],
                },
                "settings": {"type": "object", "description": "Directory settings."},
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Custom directory condition",
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
                "multi_select": {
                    "type": "boolean",
                    "description": "When enabled, directory records can store multiple values per field",
                },
                "allow_editing": {
                    "type": "boolean",
                    "description": "When enabled, directory records can be edited from cards without custom properties permission",
                },
                "fields": {
                    "type": "array",
                    "description": "Full fields list. Fields omitted from this array are soft-deleted (condition=removed).",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "format": "uuid",
                                "description": "Field ID (for updating an existing field)",
                            },
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 256,
                                "description": "Field name",
                            },
                            "type": {
                                "enum": [
                                    "string",
                                    "number",
                                    "date",
                                    "email",
                                    "url",
                                    "phone",
                                    "checkbox",
                                    "select",
                                    "user",
                                    "catalog",
                                    "directory_link",
                                    "file",
                                ],
                                "description": "Field type",
                                "type": "string",
                            },
                            "required": {"type": "boolean", "description": "Required field flag"},
                            "is_display": {
                                "type": "boolean",
                                "description": "Display field flag (only one field should have is_display=true)",
                            },
                            "sort_order": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Field position",
                            },
                            "custom_property_uid": {
                                "description": "Empty custom property reference",
                                "format": "uuid",
                                "type": ["null", "string"],
                                "x-documentation-alternatives": [
                                    {
                                        "type": "null",
                                        "description": "Empty custom property reference",
                                    },
                                    {
                                        "type": "string",
                                        "format": "uuid",
                                        "description": "Custom property UID (required for select/user/catalog fields)",
                                    },
                                ],
                            },
                            "linked_directory_id": {
                                "description": "Empty linked directory reference",
                                "format": "uuid",
                                "type": ["null", "string"],
                                "x-documentation-alternatives": [
                                    {
                                        "type": "null",
                                        "description": "Empty linked directory reference",
                                    },
                                    {
                                        "type": "string",
                                        "format": "uuid",
                                        "description": "Linked custom directory ID (required for directory_link fields)",
                                    },
                                ],
                            },
                        },
                    },
                },
            },
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-directories/{directory_id}",
            path_fields=("directory_id",),
            body_fields=(
                "name",
                "description",
                "settings",
                "condition",
                "payload",
                "multi_select",
                "allow_editing",
                "fields",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directories update --directory-id dir-uuid --name "Clients"',
                description="Update a Catalog.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directories.delete",
        mcp_alias="kaiten_delete_custom_directory",
        description="Delete a Kaiten Catalog (custom directory).",
        input_schema={
            "type": "object",
            "properties": {"directory_id": DIRECTORY_ID},
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-directories/{directory_id}",
            path_fields=("directory_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directories delete --directory-id dir-uuid",
                description="Delete a Catalog.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.list",
        mcp_alias="kaiten_list_custom_directory_fields",
        description="List fields (columns) of a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "include_author": {"type": "boolean", "description": "Include author user object"},
                "conditions": {
                    "type": "array",
                    "description": "Filter by condition values: active | inactive | removed",
                    "items": {"type": "string"},
                },
            },
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}/fields",
            path_fields=("directory_id",),
            query_fields=("include_author", "conditions"),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-fields list --directory-id dir-uuid",
                description="List Catalog fields.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.get",
        mcp_alias="kaiten_get_custom_directory_field",
        description="Get a field (column) of a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {"directory_id": DIRECTORY_ID, "field_id": FIELD_ID},
            "required": ["directory_id", "field_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
            path_fields=("directory_id", "field_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-fields get --directory-id dir-uuid --field-id field-uuid",
                description="Get a Catalog field.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.create",
        mcp_alias="kaiten_create_custom_directory_field",
        description="Create a field (column) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "name": {"type": "string", "description": "Field name"},
                "type": {
                    "type": "string",
                    "description": "Field type, for example string, email, phone, or catalog.",
                },
                "required": {
                    "type": "boolean",
                    "description": "Required field flag",
                    "default": False,
                },
                "is_display": {
                    "type": "boolean",
                    "description": "Display field flag",
                    "default": False,
                },
                "sort_order": {"type": ["number", "integer"], "description": "Field position"},
                "settings": {"type": "object", "description": "Type-specific field settings."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
            },
            "required": ["directory_id", "name", "type"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-directories/{directory_id}/fields",
            path_fields=("directory_id",),
            body_fields=(
                "name",
                "type",
                "required",
                "is_display",
                "sort_order",
                "settings",
                "payload",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-fields create --directory-id dir-uuid --name Email --type email",
                description="Create a Catalog field.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.update",
        mcp_alias="kaiten_update_custom_directory_field",
        description="Update a field (column) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "field_id": {"type": "string", "description": "Custom directory field ID (UUID)."},
                "name": {"type": "string", "description": "Field name"},
                "required": {"type": "boolean", "description": "Required field flag"},
                "is_display": {"type": "boolean", "description": "Display field flag"},
                "sort_order": {"type": ["number", "integer"], "description": "Field position"},
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Custom directory field condition",
                },
                "settings": {"type": "object", "description": "Type-specific field settings."},
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
            },
            "required": ["directory_id", "field_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
            path_fields=("directory_id", "field_id"),
            body_fields=(
                "name",
                "required",
                "is_display",
                "sort_order",
                "condition",
                "settings",
                "payload",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-fields update --directory-id dir-uuid --field-id field-uuid --required",
                description="Update a Catalog field.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.delete",
        mcp_alias="kaiten_delete_custom_directory_field",
        description="Delete a field (column) from a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {"directory_id": DIRECTORY_ID, "field_id": FIELD_ID},
            "required": ["directory_id", "field_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
            path_fields=("directory_id", "field_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-fields delete --directory-id dir-uuid --field-id field-uuid",
                description="Delete a Catalog field.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.list",
        mcp_alias="kaiten_list_custom_directory_records",
        description="List records (rows) of a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "query": {"type": "string", "description": "Quick search by record display value"},
                "profile": {
                    "type": "string",
                    "enum": ["none", "summary", "details", "full"],
                    "description": "Controls included relations in response",
                    "x-documentation-constraints": "none | summary | details | full",
                },
                "include_values": {
                    "type": "boolean",
                    "description": "Legacy: include values array",
                },
                "include_author": {"type": "boolean", "description": "Include author user object"},
                "conditions": {
                    "type": "array",
                    "description": "Filter by condition values: active | inactive | removed",
                    "items": {"type": "string"},
                },
                "filters": {"type": "object", "description": "Advanced field-based filters (JSON)"},
                "filter_operator": {
                    "type": "string",
                    "enum": ["and", "or"],
                    "description": "Boolean operator for filters (default: and)",
                    "x-documentation-constraints": "and | or",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results, capped by Kaiten at 100.",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}/records",
            path_fields=("directory_id",),
            query_fields=(
                "query",
                "profile",
                "include_values",
                "include_author",
                "conditions",
                "filters",
                "filter_operator",
                "limit",
                "offset",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=100, result_kind="list"),
        runtime_behavior=RuntimeBehavior(request_shaper=encode_object_query_request),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-records list --directory-id dir-uuid --profile summary",
                description="List Catalog records.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.get",
        mcp_alias="kaiten_get_custom_directory_record",
        description="Get a record (row) from a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "record_id": {
                    "type": "string",
                    "description": "Custom directory record ID (UUID).",
                },
                "profile": {
                    "type": "string",
                    "enum": ["none", "summary", "details", "full"],
                    "description": "Controls included relations in response",
                    "x-documentation-constraints": "none | summary | details | full",
                },
            },
            "required": ["directory_id", "record_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}/records/{record_id}",
            path_fields=("directory_id", "record_id"),
            query_fields=("profile",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-records get --directory-id dir-uuid --record-id record-uuid",
                description="Get a Catalog record.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.create",
        mcp_alias="kaiten_create_custom_directory_record",
        description="Create a record (row) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "values": {
                    "type": ["object", "array"],
                    "description": "Values map where keys are custom directory field IDs. Each value is either an object (single-value) or an array of objects (multi-select).",
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
                "response_profile": {
                    "type": "string",
                    "description": "Controls response size. Use `none` to return `{ id }` only.",
                    "x-documentation-constraints": "none | summary | details | full",
                },
            },
            "required": ["directory_id", "values"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-directories/{directory_id}/records",
            path_fields=("directory_id",),
            body_fields=("values", "payload"),
            query_fields=("response_profile",),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directory-records create --directory-id dir-uuid --values \'{"field-uuid":"Alice"}\'',
                description="Create a Catalog record.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.update",
        mcp_alias="kaiten_update_custom_directory_record",
        description="Update a record (row) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "record_id": {
                    "type": "string",
                    "description": "Custom directory record ID (UUID).",
                },
                "values": {
                    "type": ["object", "array"],
                    "description": "Values map where keys are custom directory field IDs. Each value is either an object (single-value) or an array of objects (multi-select).",
                },
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Custom directory record condition",
                },
                "payload": {
                    "type": "object",
                    "description": "Extra JSON body fields from the Kaiten API docs. Merged into the request body.",
                },
                "response_profile": {
                    "type": "string",
                    "description": "Controls response size. Use `none` to return `{ id }` only.",
                    "x-documentation-constraints": "none | summary | details | full",
                },
            },
            "required": ["directory_id", "record_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-directories/{directory_id}/records/{record_id}",
            path_fields=("directory_id", "record_id"),
            body_fields=("values", "condition", "payload"),
            query_fields=("response_profile",),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directory-records update --directory-id dir-uuid --record-id record-uuid --values \'{"field-uuid":"Bob"}\'',
                description="Update a Catalog record.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.delete",
        mcp_alias="kaiten_delete_custom_directory_record",
        description="Delete a record (row) from a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {"directory_id": DIRECTORY_ID, "record_id": RECORD_ID},
            "required": ["directory_id", "record_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/company/custom-directories/{directory_id}/records/{record_id}",
            path_fields=("directory_id", "record_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-records delete --directory-id dir-uuid --record-id record-uuid",
                description="Delete a Catalog record.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.cards.list",
        mcp_alias="kaiten_list_custom_directory_record_cards",
        description="List cards linked to a Kaiten Catalog record.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": {"type": "string", "description": "Custom directory ID (UUID)."},
                "record_id": {
                    "type": "string",
                    "description": "Custom directory record ID (UUID).",
                },
                "filter": {"type": "string", "description": "Base64-encoded JSON card filter"},
                "limit": {
                    "type": "integer",
                    "description": "Max results, capped by Kaiten at 100.",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
            "required": ["directory_id", "record_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/custom-directories/{directory_id}/records/{record_id}/cards",
            path_fields=("directory_id", "record_id"),
            query_fields=("filter", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=100, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json custom-directory-records cards list --directory-id dir-uuid --record-id record-uuid",
                description="List cards linked to a Catalog record.",
            ),
        ),
        search_terms=(
            "каталог",
            "каталоги",
            "справочник",
            "справочник-таблица",
            "справочник таблица",
            "табличный справочник",
        ),
        usage_notes=CATALOG_USAGE_NOTES,
    ),
)
