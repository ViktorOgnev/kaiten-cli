"""External link tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="external-links.list",
        mcp_alias="kaiten_list_external_links",
        description="List all external links on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/external-links", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten external-links list --card-id 10 --json", description="List external links on a card."),
        ),
    ),
    make_tool(
        canonical_name="external-links.create",
        mcp_alias="kaiten_create_external_link",
        description="Create an external link on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "url": {"type": "string", "description": "URL of the external link"},
                "description": {"type": "string", "description": "Description of the external link"},
            },
            "required": ["card_id", "url"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/external-links",
            path_fields=("card_id",),
            body_fields=("url", "description"),
        ),
        examples=(
            ExampleSpec(command='kaiten external-links create --card-id 10 --url "https://example.com" --json', description="Attach an external link to a card."),
        ),
    ),
    make_tool(
        canonical_name="external-links.update",
        mcp_alias="kaiten_update_external_link",
        description="Update an external link on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "link_id": {"type": "integer", "description": "External link ID"},
                "url": {"type": "string", "description": "URL of the external link"},
                "description": {"type": "string", "description": "Description of the external link"},
            },
            "required": ["card_id", "link_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/external-links/{link_id}",
            path_fields=("card_id", "link_id"),
            body_fields=("url", "description"),
        ),
        examples=(
            ExampleSpec(command='kaiten external-links update --card-id 10 --link-id 20 --description "Spec" --json', description="Update a card external link."),
        ),
    ),
    make_tool(
        canonical_name="external-links.delete",
        mcp_alias="kaiten_delete_external_link",
        description="Delete an external link from a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "link_id": {"type": "integer", "description": "External link ID"},
            },
            "required": ["card_id", "link_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/external-links/{link_id}", path_fields=("card_id", "link_id")),
        examples=(
            ExampleSpec(command="kaiten external-links delete --card-id 10 --link-id 20 --json", description="Delete a card external link."),
        ),
    ),
)
