"""Tag and card-tag tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.transforms import DEFAULT_LIMIT


TOOLS = (
    make_tool(
        canonical_name="tags.list",
        mcp_alias="kaiten_list_tags",
        description="List Kaiten tags. Note: API may return empty for company-level tags; tags are primarily card-scoped.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search filter (matches by name)"},
                "space_id": {"type": "integer", "description": "Filter tags by space (only tags used on cards in this space)"},
                "ids": {"type": "string", "description": "Comma-separated tag IDs to fetch specific tags"},
                "limit": {"type": "integer", "description": "Max results"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
        operation=OperationSpec(method="GET", path_template="/tags", query_fields=("query", "space_id", "ids", "limit", "offset")),
        response_policy=ResponsePolicy(default_limit=DEFAULT_LIMIT, result_kind="list"),
        examples=(
            ExampleSpec(command='kaiten tags list --query "backend" --json', description="Search tags by name."),
        ),
    ),
    make_tool(
        canonical_name="tags.create",
        mcp_alias="kaiten_create_tag",
        description="Create a new Kaiten tag. Color is assigned randomly by the server (1-17).",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tag name (1-255 chars, must be unique within the company)"},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="POST", path_template="/tags", body_fields=("name",)),
        examples=(
            ExampleSpec(command='kaiten tags create --name "backend" --json', description="Create a company tag."),
        ),
    ),
    make_tool(
        canonical_name="tags.update",
        mcp_alias="kaiten_update_tag",
        description="Update a Kaiten tag (name and/or color). Requires company tag management permission.",
        input_schema={
            "type": "object",
            "properties": {
                "tag_id": {"type": "integer", "description": "Tag ID"},
                "name": {"type": "string", "description": "New tag name (1-255 chars)"},
                "color": {"type": "integer", "description": "Color index (1-17)"},
            },
            "required": ["tag_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/tags/{tag_id}",
            path_fields=("tag_id",),
            body_fields=("name", "color"),
        ),
        examples=(
            ExampleSpec(command='kaiten tags update --tag-id 10 --name "backend" --json', description="Update a company tag."),
        ),
    ),
    make_tool(
        canonical_name="tags.delete",
        mcp_alias="kaiten_delete_tag",
        description="Delete a Kaiten tag. Requires company tag management permission. May be blocked if an async operation is in progress.",
        input_schema={
            "type": "object",
            "properties": {
                "tag_id": {"type": "integer", "description": "Tag ID"},
            },
            "required": ["tag_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/company/tags/{tag_id}", path_fields=("tag_id",)),
        examples=(
            ExampleSpec(command="kaiten tags delete --tag-id 10 --json", description="Delete a company tag."),
        ),
    ),
    make_tool(
        canonical_name="card-tags.add",
        mcp_alias="kaiten_add_card_tag",
        description="Add a tag to a Kaiten card by name. Creates the tag if it doesn't exist.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "name": {"type": "string", "description": "Tag name (1-255 chars)"},
            },
            "required": ["card_id", "name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/tags",
            path_fields=("card_id",),
            body_fields=("name",),
        ),
        examples=(
            ExampleSpec(command='kaiten card-tags add --card-id 10 --name "backend" --json', description="Add a tag to a card."),
        ),
    ),
    make_tool(
        canonical_name="card-tags.remove",
        mcp_alias="kaiten_remove_card_tag",
        description="Remove a tag from a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "tag_id": {"type": "integer", "description": "Tag ID"},
            },
            "required": ["card_id", "tag_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/tags/{tag_id}", path_fields=("card_id", "tag_id")),
        examples=(
            ExampleSpec(command="kaiten card-tags remove --card-id 10 --tag-id 20 --json", description="Remove a tag from a card."),
        ),
    ),
)
