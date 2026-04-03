"""Card file tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="files.list",
        mcp_alias="kaiten_list_card_files",
        description="List all file attachments on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/files", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten files list --card-id 10 --json", description="List card files."),
        ),
    ),
    make_tool(
        canonical_name="files.create",
        mcp_alias="kaiten_create_card_file",
        description="Create a file attachment on a card by URL. This registers an external file link as a card attachment (does not upload binary data). File types: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "url": {"type": "string", "description": "URL of the file."},
                "name": {"type": "string", "description": "Display name of the file."},
                "type": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6], "description": "File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk."},
                "size": {"type": "integer", "description": "File size in bytes."},
                "sort_order": {"type": "number", "description": "Sort order of the file in the list."},
                "custom_property_id": {"type": "integer", "description": "Custom property ID to associate the file with."},
                "card_cover": {"type": "boolean", "description": "Set this file as the card cover image."},
            },
            "required": ["card_id", "url", "name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/files",
            path_fields=("card_id",),
            body_fields=("url", "name", "type", "size", "sort_order", "custom_property_id", "card_cover"),
        ),
        examples=(
            ExampleSpec(command='kaiten files create --card-id 10 --url "https://example.com/a.png" --name "a.png" --json', description="Attach a URL-backed file to a card."),
        ),
    ),
    make_tool(
        canonical_name="files.update",
        mcp_alias="kaiten_update_card_file",
        description="Update a file attachment on a card (name, URL, sort order, cover, etc.).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "file_id": {"type": "integer", "description": "File ID."},
                "url": {"type": "string", "description": "New URL of the file."},
                "name": {"type": "string", "description": "New display name."},
                "type": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6], "description": "File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk."},
                "size": {"type": "integer", "description": "File size in bytes."},
                "sort_order": {"type": "number", "description": "Sort order of the file in the list."},
                "custom_property_id": {"type": "integer", "description": "Custom property ID to associate the file with."},
                "card_cover": {"type": "boolean", "description": "Set this file as the card cover image."},
            },
            "required": ["card_id", "file_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/files/{file_id}",
            path_fields=("card_id", "file_id"),
            body_fields=("url", "name", "type", "size", "sort_order", "custom_property_id", "card_cover"),
        ),
        examples=(
            ExampleSpec(command='kaiten files update --card-id 10 --file-id 20 --name "a-v2.png" --json', description="Update a card file attachment."),
        ),
    ),
    make_tool(
        canonical_name="files.delete",
        mcp_alias="kaiten_delete_card_file",
        description="Delete a file attachment from a card. Files on blocked cards cannot be deleted.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "file_id": {"type": "integer", "description": "File ID."},
            },
            "required": ["card_id", "file_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/files/{file_id}", path_fields=("card_id", "file_id")),
        examples=(
            ExampleSpec(command="kaiten files delete --card-id 10 --file-id 20 --json", description="Delete a card file."),
        ),
    ),
)
