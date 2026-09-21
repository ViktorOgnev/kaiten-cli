"""Document and document-group tool specs."""

from __future__ import annotations

from kaiten_cli.models import (
    CACHE_POLICY_NONE,
    CACHE_POLICY_PERSISTENT_OPT_IN,
    ExampleSpec,
    OperationSpec,
    ResponsePolicy,
    RuntimeBehavior,
)
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    document_list_search_request,
    prepare_document_request,
    prevent_redirect_request,
)
from kaiten_cli.runtime.support.files import execute_file_upload
from kaiten_cli.runtime.support.markdown_export import execute_document_get


DOCUMENT_PARENT_USAGE_NOTES = (
    "`parent_entity_uid` places the document under a document group/container in the sidebar tree.",
    "Do not use document parent fields for UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.",
)

DOCUMENT_GROUP_USAGE_NOTES = (
    "Document groups are document folders/containers in the sidebar tree.",
    "Use `document-groups.*` when a request says document catalog, folder, or container.",
    "They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.",
    "Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.",
)


TOOLS = (
    make_tool(
        canonical_name="documents.list",
        mcp_alias="kaiten_list_documents",
        description="List Kaiten documents.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search filter"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results (default: 50, max: 100)",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
                "version": {
                    "type": "integer",
                    "description": "Search version. Use 2 for OpenSearch result/position response.",
                },
                "condition": {"type": "integer", "description": "Filter condition for version=2"},
                "search_fields": {
                    "type": "string",
                    "description": "Comma-separated API search fields for version=2. Sent as Kaiten query parameter 'fields'.",
                },
                "start_position": {
                    "type": "string",
                    "description": "Search cursor for version=2 pagination.",
                },
                "include_search_preview": {
                    "type": "boolean",
                    "description": "Include search preview objects for version=2.",
                },
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field names to keep in the response. Example: 'uid,title'",
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
            path_template="/documents",
            query_fields=(
                "query",
                "limit",
                "offset",
                "version",
                "condition",
                "start_position",
                "include_search_preview",
            ),
        ),
        runtime_behavior=RuntimeBehavior(
            request_shaper=document_list_search_request,
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, default_limit=50, result_kind="list"
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json documents list --query "Design"',
                description="List documents.",
            ),
            ExampleSpec(
                command="kaiten --json documents list --compact --fields uid,title",
                description="List documents with a narrow response surface.",
            ),
        ),
    ),
    make_tool(
        canonical_name="documents.create",
        mcp_alias="kaiten_create_document",
        description="Create a new Kaiten document.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Document title"},
                "text": {
                    "type": "string",
                    "description": "Markdown content converted to ProseMirror.",
                },
                "data": {"type": "object", "description": "Raw ProseMirror JSON."},
                "parent_entity_uid": {
                    "type": ["string", "null"],
                    "description": "Parent document group UID",
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Parent tree entity uid"},
                        {"type": "null"},
                    ],
                },
                "sort_order": {
                    "type": ["integer", "number"],
                    "description": "Sort order (auto-generated if not provided)",
                },
                "key": {
                    "type": ["string", "null"],
                    "description": "Unique key identifier",
                    "pattern": "^[A-Z][A-Z0-9_]{1,9}$",
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "minLength": 2,
                            "maxLength": 10,
                            "pattern": "^[A-Z][A-Z0-9_]{1,9}$",
                            "description": "Unique key for document, used in API and web interface. Must be unique across entire company",
                        },
                        {"type": "null"},
                    ],
                },
                "for_everyone_access_role_id": {"type": "string"},
                "clone_uid": {"type": "string", "description": "Document uid to copy"},
                "clone_version": {"type": "number", "description": "Document version to copy"},
            },
            "required": [],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/documents",
            body_fields=(
                "title",
                "text",
                "data",
                "parent_entity_uid",
                "sort_order",
                "key",
                "for_everyone_access_role_id",
                "clone_uid",
                "clone_version",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten --json documents create --title "Spec" --text "# Header"',
                description="Create a document from markdown.",
            ),
        ),
        usage_notes=DOCUMENT_PARENT_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="documents.get",
        mcp_alias="kaiten_get_document",
        description="Get a Kaiten document by UID.",
        input_schema={
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID"},
                "markdown": {
                    "type": "boolean",
                    "description": "Save the document body as Markdown instead of returning JSON.",
                },
                "output": {
                    "type": "string",
                    "description": "Markdown output file or directory. Defaults to the current working directory.",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Replace an existing Markdown output file.",
                },
            },
            "required": ["document_uid"],
        },
        operation=OperationSpec(
            method="GET", path_template="/documents/{document_uid}", path_fields=("document_uid",)
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_document_get,
            cache_policy=CACHE_POLICY_PERSISTENT_OPT_IN,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json documents get --document-uid doc-1",
                description="Get a document.",
            ),
            ExampleSpec(
                command="kaiten --json documents get --document-uid doc-1 --markdown --output ./doc.md",
                description="Save a document as Markdown.",
            ),
        ),
        usage_notes=(
            "`--markdown` does the same document GET, renders the result locally, and saves a Markdown file instead of returning the document JSON.",
            "`--markdown` keeps document file links as Kaiten `/api/documents/<uid>/files/<file_id>` URLs.",
            "Use `--output` for the target file/directory and `--overwrite` to replace an existing Markdown file.",
            "Separate CLI processes do not share in-memory results, so default `--cache-mode auto` persists repeated safe document reads.",
        ),
    ),
    make_tool(
        canonical_name="documents.update",
        mcp_alias="kaiten_update_document",
        description="Update a Kaiten document.",
        input_schema={
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID"},
                "title": {"type": "string", "description": "New document title"},
                "text": {
                    "type": "string",
                    "description": "Markdown content converted to ProseMirror.",
                },
                "data": {"type": "object", "description": "Raw ProseMirror JSON."},
                "parent_entity_uid": {
                    "type": ["string", "null"],
                    "description": "New parent group UID",
                },
                "sort_order": {"type": ["integer", "number"], "description": "Sort order"},
                "key": {
                    "type": ["string", "null"],
                    "description": "Unique key identifier",
                    "pattern": "^[A-Z][A-Z0-9_]{1,9}$",
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "minLength": 2,
                            "maxLength": 10,
                            "pattern": "^[A-Z][A-Z0-9_]{1,9}$",
                            "description": "Unique key for document, used in API and web interface. Must be unique across entire company",
                        },
                        {"type": "null", "description": "Reset existing key"},
                    ],
                },
                "publish_date": {
                    "description": "Deadline. ISO 8601 format",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Deadline. ISO 8601 format"},
                        {"type": "null", "description": "Empty card description"},
                    ],
                },
                "access": {"enum": ["for_everyone", "by_invite"], "type": "string"},
                "for_everyone_access_role_id": {"type": "string"},
                "public": {"type": "boolean"},
                "redirect_url": {"type": ["string", "null"]},
                "hidden_on_public_site": {"type": "boolean"},
                "settings": {
                    "type": "object",
                    "description": "Server-side shallow merge: only the key(s) sent are changed, other existing settings are preserved. Sending a key with value null removes it (for keys whose schema allows null).",
                    "properties": {
                        "content_width": {
                            "type": "string",
                            "enum": ["default", "wide"],
                            "description": 'Setting this to "wide" is only available for companies in the documents-ui-settings rollout; other companies get a 403 (code doc_2) if they try. Setting it to "default" is always allowed.',
                        }
                    },
                    "x-documentation-additionalProperties": False,
                },
                "backup_version": {"type": "number"},
                "published_version": {
                    "description": "Version to publish on public site: a number, null, or current.",
                    "type": ["number", "null", "string"],
                    "oneOf": [
                        {"type": "number", "description": "Version to publish on public site"},
                        {
                            "type": "null",
                            "description": "No spicific version to publish on public site, current version will be published",
                        },
                        {"type": "string", "enum": ["current"]},
                    ],
                },
                "icon_type": {
                    "enum": ["emoji", "material_icon"],
                    "description": "Type of icon",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {"enum": ["emoji", "material_icon"], "description": "Type of icon"},
                        {"type": "null", "description": "No icon"},
                    ],
                },
                "icon_value": {
                    "maxLength": 100,
                    "description": "Icon value (emoji character or material icon name)",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "maxLength": 100,
                            "description": "Icon value (emoji character or material icon name)",
                        },
                        {"type": "null", "description": "No icon value"},
                    ],
                },
                "icon_color": {
                    "minimum": 1,
                    "maximum": 17,
                    "description": "Icon color index (1-17)",
                    "type": ["integer", "null"],
                    "x-documentation-alternatives": [
                        {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 17,
                            "description": "Icon color index (1-17)",
                        },
                        {"type": "null", "description": "No icon color"},
                    ],
                },
                "notification_period_start": {
                    "description": "Notification period start date",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Notification period start date"},
                        {"type": "null", "description": "Reset notification period start date"},
                    ],
                },
                "notification_period_end": {
                    "description": "Notification period end date",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {"type": "string", "description": "Notification period end date"},
                        {"type": "null", "description": "Reset notification period end date"},
                    ],
                },
                "slug": {
                    "minLength": 3,
                    "maxLength": 128,
                    "pattern": "^[a-z0-9-]+$",
                    "description": "Human-readable URL slug. Lowercase latin letters, digits and hyphens only. Must be unique within the public site subtree",
                    "type": ["string", "null"],
                    "x-documentation-alternatives": [
                        {
                            "type": "string",
                            "minLength": 3,
                            "maxLength": 128,
                            "pattern": "^[a-z0-9-]+$",
                            "description": "Human-readable URL slug. Lowercase latin letters, digits and hyphens only. Must be unique within the public site subtree",
                        },
                        {
                            "type": "null",
                            "description": "Reset slug (fall back to auto-slug generated from title)",
                        },
                    ],
                },
            },
            "required": ["document_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/documents/{document_uid}",
            path_fields=("document_uid",),
            body_fields=(
                "title",
                "text",
                "data",
                "parent_entity_uid",
                "sort_order",
                "key",
                "publish_date",
                "access",
                "for_everyone_access_role_id",
                "public",
                "redirect_url",
                "hidden_on_public_site",
                "settings",
                "backup_version",
                "published_version",
                "icon_type",
                "icon_value",
                "icon_color",
                "notification_period_start",
                "notification_period_end",
                "slug",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten --json documents update --document-uid doc-1 --text "**bold**"',
                description="Update a document body.",
            ),
        ),
        usage_notes=DOCUMENT_PARENT_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="documents.delete",
        mcp_alias="kaiten_delete_document",
        description="Delete a Kaiten document.",
        input_schema={
            "type": "object",
            "properties": {"document_uid": {"type": "string", "description": "Document UID"}},
            "required": ["document_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/documents/{document_uid}",
            path_fields=("document_uid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json documents delete --document-uid doc-1",
                description="Delete a document.",
            ),
        ),
    ),
    make_tool(
        canonical_name="document-files.get-url",
        mcp_alias="kaiten_get_document_file_url",
        description="Resolve a document file to a short-lived signed download URL.",
        input_schema={
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID"},
                "file_id": {"type": "string", "description": "Document file UID without extension"},
            },
            "required": ["document_uid", "file_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/documents/{document_uid}/files/{file_id}",
            path_fields=("document_uid", "file_id"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prevent_redirect_request),
        examples=(
            ExampleSpec(
                command="kaiten --json document-files get-url --document-uid doc-1 --file-id file-1",
                description="Resolve a private document file URL for download.",
            ),
        ),
        usage_notes=(
            "Uses `prevent_redirect=true`, so the response is JSON with a short-lived signed storage URL instead of an HTTP redirect.",
        ),
    ),
    make_tool(
        canonical_name="document-files.upload",
        mcp_alias="kaiten_upload_document_file",
        description="Upload a local binary file to a Kaiten document using multipart/form-data.",
        input_schema={
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID."},
                "file": {"type": "string", "description": "Local file path to upload."},
            },
            "required": ["document_uid", "file"],
        },
        operation=OperationSpec(
            method="PUT",
            path_template="/documents/{document_uid}/files",
            path_fields=("document_uid",),
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_file_upload,
            cache_policy=CACHE_POLICY_NONE,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json document-files upload --document-uid doc-1 --file ./screenshot.png",
                description="Upload a local file to a document.",
            ),
        ),
        usage_notes=(
            "Uploads the local file as multipart/form-data field `file`.",
            "The returned `id` can be used as a ProseMirror image node `attrs.fileId`.",
        ),
    ),
    make_tool(
        canonical_name="document-schemas.get",
        mcp_alias="kaiten_get_document_schema",
        description="Get a document data schema.",
        input_schema={
            "type": "object",
            "properties": {
                "schema_id": {"type": "integer", "description": "Document schema ID."},
                "format": {"description": "Response format. Default: draft-06.", "type": "string"},
            },
            "required": ["schema_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/document-schemas/{schema_id}",
            path_fields=("schema_id",),
            query_fields=("format",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json document-schemas get --schema-id 1",
                description="Get a document data schema.",
            ),
        ),
    ),
    make_tool(
        canonical_name="document-groups.list",
        mcp_alias="kaiten_list_document_groups",
        description="List Kaiten document groups.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search filter"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Max results (default: 50, max: 100)",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Pagination offset"},
                "version": {
                    "type": "integer",
                    "description": "Search version. Default: 1. Use version=2 to search via OpenSearch and enable the new response format with result and position fields",
                },
                "condition": {
                    "type": "integer",
                    "description": "Filter condition. Used with version=2",
                },
                "start_position": {
                    "type": "string",
                    "description": "Search cursor for version=2 pagination. Pass the position value from the previous version=2 response",
                },
                "role": {
                    "type": "integer",
                    "description": "Filter by minimum user role. 1 — reader, 2 — writer, 3 — admin",
                },
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/document-groups",
            query_fields=(
                "query",
                "limit",
                "offset",
                "version",
                "condition",
                "start_position",
                "role",
            ),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten --json document-groups list --query "Engineering"',
                description="List document groups.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="document-groups.create",
        mcp_alias="kaiten_create_document_group",
        description="Create a new Kaiten document group.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Group title"},
                "parent_entity_uid": {
                    "type": ["string", "null"],
                    "description": "Parent group UID for nesting",
                },
                "sort_order": {
                    "type": ["integer", "number"],
                    "description": "Sort order (auto-generated if not provided)",
                },
                "for_everyone_access_role_id": {
                    "type": ["string", "null"],
                    "format": "uuid",
                    "description": "Role id for everyone access",
                },
                "key": {
                    "type": ["string", "null"],
                    "maxLength": 256,
                    "description": "Unique document group key within company",
                },
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/document-groups",
            body_fields=(
                "title",
                "parent_entity_uid",
                "sort_order",
                "for_everyone_access_role_id",
                "key",
            ),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten --json document-groups create --title "Engineering"',
                description="Create a document group.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="document-groups.get",
        mcp_alias="kaiten_get_document_group",
        description="Get a Kaiten document group by UID.",
        input_schema={
            "type": "object",
            "properties": {"group_uid": {"type": "string", "description": "Document group UID"}},
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="GET", path_template="/document-groups/{group_uid}", path_fields=("group_uid",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json document-groups get --group-uid grp-1",
                description="Get a document group.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="document-groups.update",
        mcp_alias="kaiten_update_document_group",
        description="Update a Kaiten document group.",
        input_schema={
            "type": "object",
            "properties": {
                "group_uid": {"type": "string", "description": "Document group UID"},
                "title": {"type": "string", "description": "New group title"},
                "parent_entity_uid": {
                    "type": ["string", "null"],
                    "description": "Parent tree entity uid. Used to move document group in the tree",
                },
                "sort_order": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMinimum": 0,
                    "description": "Sort order",
                },
                "access": {
                    "enum": ["for_everyone", "by_invite"],
                    "description": "Document group access type",
                    "type": "string",
                },
                "for_everyone_access_role_id": {
                    "type": ["string", "null"],
                    "format": "uuid",
                    "description": "Role id for everyone access",
                },
                "hostname": {
                    "type": ["string", "null"],
                    "maxLength": 30,
                    "description": "Custom hostname for public site. Can contain only letters, numbers and «-», length 2–30 symbols, cannot end with «-»",
                },
                "redirect_url": {"type": ["string", "null"], "description": "Redirect URL"},
                "key": {
                    "type": ["string", "null"],
                    "maxLength": 256,
                    "description": "Unique document group key within company. Cannot be changed once set",
                },
                "icon_type": {
                    "type": ["string", "null"],
                    "enum": ["material_icon", None],
                    "description": "Icon type",
                },
                "icon_value": {
                    "type": ["string", "null"],
                    "description": "Icon value (icon name for material_icon type)",
                },
                "icon_color": {"type": ["integer", "null"], "description": "Icon color"},
                "hidden_on_public_site": {
                    "type": "boolean",
                    "description": "Hide document group on public site",
                },
                "news_feed": {
                    "type": "boolean",
                    "description": "Mark document group as news feed. Requires hostname to be set on this folder or one of its parent folders",
                },
                "index_document_uid": {
                    "type": ["string", "null"],
                    "format": "uuid",
                    "description": "UID of the document to use as the home page for this folder. Requires hostname to be set on this folder. Document must be within the document group tree, not archived and not hidden on public site",
                },
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/document-groups/{group_uid}",
            path_fields=("group_uid",),
            body_fields=(
                "title",
                "parent_entity_uid",
                "sort_order",
                "access",
                "for_everyone_access_role_id",
                "hostname",
                "redirect_url",
                "key",
                "icon_type",
                "icon_value",
                "icon_color",
                "hidden_on_public_site",
                "news_feed",
                "index_document_uid",
            ),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json document-groups update --group-uid grp-1 --title "Docs"',
                description="Update a document group.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="document-groups.delete",
        mcp_alias="kaiten_delete_document_group",
        description="Delete a Kaiten document group.",
        input_schema={
            "type": "object",
            "properties": {"group_uid": {"type": "string", "description": "Document group UID"}},
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/document-groups/{group_uid}",
            path_fields=("group_uid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json document-groups delete --group-uid grp-1",
                description="Delete a document group.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
)
