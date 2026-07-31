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
    "Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.",
    "For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.",
    "Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.",
    "`custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.",
    "Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.",
    "Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.",
    "If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.",
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
                "include_fields": {
                    "type": "boolean",
                    "description": "Include directory field definitions.",
                },
                "include_author": {"type": "boolean", "description": "Include author user object."},
                "include_records_count": {
                    "type": "boolean",
                    "description": "Include records_count.",
                },
                "query": {"type": "string", "description": "Search by directory name."},
                "conditions": CONDITIONS,
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directories.create",
        mcp_alias="kaiten_create_custom_directory",
        description="Create a Kaiten Catalog (custom directory).",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Directory name."},
                "description": {
                    "type": ["string", "null"],
                    "description": "Directory description.",
                },
                "settings": {
                    "type": "object",
                    "description": "Directory settings, for example multi_select or allow_editing.",
                },
                "fields": {
                    "type": "array",
                    "description": "Initial directory fields, when supported by the API.",
                },
                "payload": PAYLOAD,
            },
            "required": ["name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-directories",
            body_fields=("name", "description", "settings", "fields", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directories create --name "Contacts" --settings \'{"multi_select":false,"allow_editing":true}\'',
                description="Create a Catalog.",
            ),
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
                "directory_id": DIRECTORY_ID,
                "name": {"type": "string", "description": "Directory name."},
                "description": {
                    "type": ["string", "null"],
                    "description": "Directory description.",
                },
                "settings": {"type": "object", "description": "Directory settings."},
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Directory condition.",
                },
                "payload": PAYLOAD,
            },
            "required": ["directory_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-directories/{directory_id}",
            path_fields=("directory_id",),
            body_fields=("name", "description", "settings", "condition", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directories update --directory-id dir-uuid --name "Clients"',
                description="Update a Catalog.",
            ),
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.list",
        mcp_alias="kaiten_list_custom_directory_fields",
        description="List fields (columns) of a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "include_author": {"type": "boolean", "description": "Include author user object."},
                "conditions": CONDITIONS,
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.create",
        mcp_alias="kaiten_create_custom_directory_field",
        description="Create a field (column) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "name": {"type": "string", "description": "Field name."},
                "type": {
                    "type": "string",
                    "description": "Field type, for example string, email, phone, or catalog.",
                },
                "required": {"type": "boolean", "description": "Whether the field is required."},
                "is_display": {
                    "type": "boolean",
                    "description": "Whether the field is used as display value.",
                },
                "sort_order": {"type": "number", "description": "Field sort order."},
                "settings": {"type": "object", "description": "Type-specific field settings."},
                "payload": PAYLOAD,
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-fields.update",
        mcp_alias="kaiten_update_custom_directory_field",
        description="Update a field (column) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "field_id": FIELD_ID,
                "name": {"type": "string", "description": "Field name."},
                "required": {"type": "boolean", "description": "Whether the field is required."},
                "is_display": {
                    "type": "boolean",
                    "description": "Whether the field is used as display value.",
                },
                "sort_order": {"type": "number", "description": "Field sort order."},
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Field condition.",
                },
                "settings": {"type": "object", "description": "Type-specific field settings."},
                "payload": PAYLOAD,
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.list",
        mcp_alias="kaiten_list_custom_directory_records",
        description="List records (rows) of a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "query": {"type": "string", "description": "Quick search by record display value."},
                "profile": {
                    "type": "string",
                    "enum": ["none", "summary", "details", "full"],
                    "description": "Controls included relations.",
                },
                "include_values": {
                    "type": "boolean",
                    "description": "Legacy flag to include values array.",
                },
                "include_author": {"type": "boolean", "description": "Include author user object."},
                "conditions": CONDITIONS,
                "filters": {
                    "type": "object",
                    "description": "Advanced field-based filters as JSON.",
                },
                "filter_operator": {
                    "type": "string",
                    "enum": ["and", "or"],
                    "description": "Boolean operator for filters.",
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.get",
        mcp_alias="kaiten_get_custom_directory_record",
        description="Get a record (row) from a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "record_id": RECORD_ID,
                "profile": {
                    "type": "string",
                    "enum": ["none", "summary", "details", "full"],
                    "description": "Controls included relations.",
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.create",
        mcp_alias="kaiten_create_custom_directory_record",
        description="Create a record (row) in a Kaiten Catalog.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "values": {
                    "type": ["object", "array"],
                    "description": "Field values for the record.",
                },
                "payload": PAYLOAD,
            },
            "required": ["directory_id", "values"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/company/custom-directories/{directory_id}/records",
            path_fields=("directory_id",),
            body_fields=("values", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directory-records create --directory-id dir-uuid --values \'{"field-uuid":"Alice"}\'',
                description="Create a Catalog record.",
            ),
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
                "directory_id": DIRECTORY_ID,
                "record_id": RECORD_ID,
                "values": {
                    "type": ["object", "array"],
                    "description": "Field values for the record.",
                },
                "condition": {
                    "type": "string",
                    "enum": ["active", "inactive", "removed"],
                    "description": "Record condition.",
                },
                "payload": PAYLOAD,
            },
            "required": ["directory_id", "record_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/custom-directories/{directory_id}/records/{record_id}",
            path_fields=("directory_id", "record_id"),
            body_fields=("values", "condition", "payload"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=payload_body_request),
        examples=(
            ExampleSpec(
                command='kaiten --json custom-directory-records update --directory-id dir-uuid --record-id record-uuid --values \'{"field-uuid":"Bob"}\'',
                description="Update a Catalog record.",
            ),
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="custom-directory-records.cards.list",
        mcp_alias="kaiten_list_custom_directory_record_cards",
        description="List cards linked to a Kaiten Catalog record.",
        input_schema={
            "type": "object",
            "properties": {
                "directory_id": DIRECTORY_ID,
                "record_id": RECORD_ID,
                "filter": {"type": "string", "description": "Base64-encoded JSON card filter."},
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
        usage_notes=CATALOG_USAGE_NOTES,
    ),
)
