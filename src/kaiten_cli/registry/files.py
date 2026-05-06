"""Card file tool specs."""

from __future__ import annotations

from kaiten_cli.models import CACHE_POLICY_NONE, ExampleSpec, OperationSpec, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.support.files import execute_file_download, execute_file_upload


TOOLS = (
    make_tool(
        canonical_name="files.download",
        mcp_alias="kaiten_download_file",
        description=(
            "Download a Kaiten file attachment to disk. Supports card, document, comment, "
            "custom property, and conversation message file endpoints, plus Kaiten /api/... URLs."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Kaiten /api/... file URL, internal /files/... URL, or direct http(s) URL.",
                },
                "entity_type": {
                    "type": "string",
                    "enum": ["card", "document", "comment", "custom_property", "conversation_message"],
                    "description": "Attachment owner type when not passing --url.",
                },
                "file_id": {
                    "type": ["string", "integer"],
                    "description": "File identifier. UUID values may include the original extension.",
                },
                "card_id": {
                    "type": ["string", "integer"],
                    "description": "Card ID for card, comment, or custom property files.",
                },
                "card_uid": {
                    "type": "string",
                    "description": "Card UID for card, comment, or custom property files.",
                },
                "card_id_or_uid": {
                    "type": "string",
                    "description": "Card ID or UID for card, comment, or custom property files.",
                },
                "document_uid": {"type": "string", "description": "Document UID for document files."},
                "comment_uid": {"type": "string", "description": "Comment UID for comment files."},
                "custom_property_uid": {
                    "type": "string",
                    "description": "Custom property UID for custom property files.",
                },
                "conversation_uid": {
                    "type": "string",
                    "description": "Conversation UID for conversation message files.",
                },
                "conversation_message_uid": {
                    "type": "string",
                    "description": "Conversation message UID for conversation message files.",
                },
                "output": {
                    "type": "string",
                    "description": "Output file or directory. Defaults to the current working directory.",
                },
                "name": {
                    "type": "string",
                    "description": "Preferred local filename when --output is a directory or omitted.",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Replace an existing output file.",
                },
                "continue": {
                    "type": "boolean",
                    "description": "Resume an existing .part file with HTTP Range. Enabled by default.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/files/download"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_file_download,
            cache_policy=CACHE_POLICY_NONE,
        ),
        examples=(
            ExampleSpec(
                command=(
                    "kaiten files download --entity-type document --document-uid <document_uid> "
                    "--file-id <file_uid> --json"
                ),
                description="Download a document attachment into the current directory.",
            ),
            ExampleSpec(
                command=(
                    "kaiten files download --entity-type card --card-id 123 --file-id <file_uid> "
                    "--output ./downloads/ --json"
                ),
                description="Download a card attachment into a directory.",
            ),
            ExampleSpec(
                command=(
                    "kaiten files download --url "
                    '"https://hq.kaiten.ru/api/documents/<document_uid>/files/<file_uid>" '
                    "--output ./file.bin --overwrite --json"
                ),
                description="Download from a Kaiten report/browser file URL.",
            ),
        ),
        usage_notes=(
            "By default the command writes to the current working directory.",
            "Downloads stream to <target>.part first and are renamed into place only after completion.",
            "Existing .part files are resumed with HTTP Range by default, similar to wget --continue.",
            "For Kaiten file endpoints the command resolves a short-lived storage URL internally and does not print it.",
        ),
    ),
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
        canonical_name="files.upload",
        mcp_alias="kaiten_upload_card_file",
        description="Upload a local binary file to a Kaiten card using multipart/form-data.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID."},
                "file": {"type": "string", "description": "Local file path to upload."},
            },
            "required": ["card_id", "file"],
        },
        operation=OperationSpec(method="PUT", path_template="/cards/{card_id}/files", path_fields=("card_id",)),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_file_upload,
            cache_policy=CACHE_POLICY_NONE,
        ),
        examples=(
            ExampleSpec(command="kaiten files upload --card-id 123 --file ./report.json --json", description="Upload a local file to a card."),
        ),
        usage_notes=(
            "Uploads the local file as multipart/form-data field `file`.",
            "The uploaded filename is the local file basename.",
            "This command uses the public card file endpoint; the beta private file endpoint is not used.",
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
