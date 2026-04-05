"""Document and document-group tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool


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
        operation=OperationSpec(method="GET", path_template="/documents", query_fields=("query", "limit", "offset")),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten documents list --query "Design" --json', description="List documents."),
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
                "text": {"type": "string", "description": "Markdown content converted to ProseMirror."},
                "data": {"type": "object", "description": "Raw ProseMirror JSON."},
                "parent_entity_uid": {"type": "string", "description": "Parent document group UID"},
                "sort_order": {"type": "integer", "description": "Sort order (auto-generated if not provided)"},
                "key": {"type": "string", "description": "Unique key identifier"},
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/documents",
            body_fields=("title", "text", "data", "parent_entity_uid", "sort_order", "key"),
        ),
        examples=(
            ExampleSpec(command='kaiten documents create --title "Spec" --text "# Header" --json', description="Create a document from markdown."),
        ),
    ),
    make_tool(
        canonical_name="documents.get",
        mcp_alias="kaiten_get_document",
        description="Get a Kaiten document by UID.",
        input_schema={
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "Document UID"},
            },
            "required": ["document_uid"],
        },
        operation=OperationSpec(method="GET", path_template="/documents/{document_uid}", path_fields=("document_uid",)),
        examples=(
            ExampleSpec(command="kaiten documents get --document-uid doc-1 --json", description="Get a document."),
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
                "text": {"type": "string", "description": "Markdown content converted to ProseMirror."},
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
        examples=(
            ExampleSpec(command='kaiten documents update --document-uid doc-1 --text "**bold**" --json', description="Update a document body."),
        ),
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
        operation=OperationSpec(method="DELETE", path_template="/documents/{document_uid}", path_fields=("document_uid",)),
        examples=(
            ExampleSpec(command="kaiten documents delete --document-uid doc-1 --json", description="Delete a document."),
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
        operation=OperationSpec(method="GET", path_template="/document-groups", query_fields=("query", "limit", "offset")),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten document-groups list --query "Engineering" --json', description="List document groups."),
        ),
    ),
    make_tool(
        canonical_name="document-groups.create",
        mcp_alias="kaiten_create_document_group",
        description="Create a new Kaiten document group.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Group title"},
                "parent_entity_uid": {"type": "string", "description": "Parent group UID for nesting"},
                "sort_order": {"type": "integer", "description": "Sort order (auto-generated if not provided)"},
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/document-groups",
            body_fields=("title", "parent_entity_uid", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten document-groups create --title "Engineering" --json', description="Create a document group."),
        ),
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
        operation=OperationSpec(method="GET", path_template="/document-groups/{group_uid}", path_fields=("group_uid",)),
        examples=(
            ExampleSpec(command="kaiten document-groups get --group-uid grp-1 --json", description="Get a document group."),
        ),
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
            ExampleSpec(command='kaiten document-groups update --group-uid grp-1 --title "Docs" --json', description="Update a document group."),
        ),
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
        operation=OperationSpec(method="DELETE", path_template="/document-groups/{group_uid}", path_fields=("group_uid",)),
        examples=(
            ExampleSpec(command="kaiten document-groups delete --group-uid grp-1 --json", description="Delete a document group."),
        ),
    ),
)
