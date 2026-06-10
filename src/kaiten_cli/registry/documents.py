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
from kaiten_cli.runtime.behaviors import prepare_document_request, prevent_redirect_request
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
                "limit": {"type": "integer", "description": "Max results (default: 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/documents", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten documents list --query "Design" --json',
                description="List documents.",
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
                "parent_entity_uid": {"type": "string", "description": "Parent document group UID"},
                "sort_order": {
                    "type": "integer",
                    "description": "Sort order (auto-generated if not provided)",
                },
                "key": {"type": "string", "description": "Unique key identifier"},
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/documents",
            body_fields=("title", "text", "data", "parent_entity_uid", "sort_order", "key"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten documents create --title "Spec" --text "# Header" --json',
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
                command="kaiten documents get --document-uid doc-1 --json",
                description="Get a document.",
            ),
            ExampleSpec(
                command="kaiten documents get --document-uid doc-1 --markdown --output ./doc.md --json",
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
                "parent_entity_uid": {"type": "string", "description": "New parent group UID"},
                "sort_order": {"type": "integer", "description": "Sort order"},
                "key": {"type": "string", "description": "Unique key identifier"},
            },
            "required": ["document_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/documents/{document_uid}",
            path_fields=("document_uid",),
            body_fields=("title", "text", "data", "parent_entity_uid", "sort_order", "key"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten documents update --document-uid doc-1 --text "**bold**" --json',
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
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID"},
            },
            "required": ["document_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/documents/{document_uid}",
            path_fields=("document_uid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten documents delete --document-uid doc-1 --json",
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
                command="kaiten document-files get-url --document-uid doc-1 --file-id file-1 --json",
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
                command="kaiten document-files upload --document-uid doc-1 --file ./screenshot.png --json",
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
            "properties": {"schema_id": {"type": "integer", "description": "Document schema ID."}},
            "required": ["schema_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/document-schemas/{schema_id}",
            path_fields=("schema_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten document-schemas get --schema-id 1 --json",
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
                "limit": {"type": "integer", "description": "Max results (default: 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/document-groups",
            query_fields=("query", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command='kaiten document-groups list --query "Engineering" --json',
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
                    "type": "string",
                    "description": "Parent group UID for nesting",
                },
                "sort_order": {
                    "type": "integer",
                    "description": "Sort order (auto-generated if not provided)",
                },
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/document-groups",
            body_fields=("title", "parent_entity_uid", "sort_order"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=prepare_document_request),
        examples=(
            ExampleSpec(
                command='kaiten document-groups create --title "Engineering" --json',
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
            "properties": {
                "group_uid": {"type": "string", "description": "Document group UID"},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="GET", path_template="/document-groups/{group_uid}", path_fields=("group_uid",)
        ),
        examples=(
            ExampleSpec(
                command="kaiten document-groups get --group-uid grp-1 --json",
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
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/document-groups/{group_uid}",
            path_fields=("group_uid",),
            body_fields=("title",),
        ),
        examples=(
            ExampleSpec(
                command='kaiten document-groups update --group-uid grp-1 --title "Docs" --json',
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
            "properties": {
                "group_uid": {"type": "string", "description": "Document group UID"},
            },
            "required": ["group_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/document-groups/{group_uid}",
            path_fields=("group_uid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten document-groups delete --group-uid grp-1 --json",
                description="Delete a document group.",
            ),
        ),
        usage_notes=DOCUMENT_GROUP_USAGE_NOTES,
    ),
)
