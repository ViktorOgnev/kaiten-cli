"""Checklist and checklist item tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="checklists.list",
        mcp_alias="kaiten_list_checklists",
        description="List all checklists on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/checklists", path_fields=("card_id",)),
        examples=(
            ExampleSpec(command="kaiten checklists list --card-id 10 --json", description="List checklists on a card."),
        ),
    ),
    make_tool(
        canonical_name="checklists.create",
        mcp_alias="kaiten_create_checklist",
        description="Create a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "name": {"type": "string", "description": "Checklist name"},
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["card_id", "name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/checklists",
            path_fields=("card_id",),
            body_fields=("name", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten checklists create --card-id 10 --name "Ready for QA" --json', description="Create a checklist."),
        ),
    ),
    make_tool(
        canonical_name="checklists.update",
        mcp_alias="kaiten_update_checklist",
        description="Update a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
                "name": {"type": "string", "description": "Checklist name"},
                "sort_order": {"type": "number", "description": "Sort order"},
            },
            "required": ["card_id", "checklist_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/checklists/{checklist_id}",
            path_fields=("card_id", "checklist_id"),
            body_fields=("name", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten checklists update --card-id 10 --checklist-id 20 --name "Ready for QA" --json', description="Update a checklist."),
        ),
    ),
    make_tool(
        canonical_name="checklists.delete",
        mcp_alias="kaiten_delete_checklist",
        description="Delete a checklist from a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
            },
            "required": ["card_id", "checklist_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/cards/{card_id}/checklists/{checklist_id}", path_fields=("card_id", "checklist_id")),
        examples=(
            ExampleSpec(command="kaiten checklists delete --card-id 10 --checklist-id 20 --json", description="Delete a checklist."),
        ),
    ),
    make_tool(
        canonical_name="checklist-items.list",
        mcp_alias="kaiten_list_checklist_items",
        description="List all items in a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
            },
            "required": ["card_id", "checklist_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/checklists/{checklist_id}/items",
            path_fields=("card_id", "checklist_id"),
        ),
        examples=(
            ExampleSpec(command="kaiten checklist-items list --card-id 10 --checklist-id 20 --json", description="List checklist items."),
        ),
    ),
    make_tool(
        canonical_name="checklist-items.create",
        mcp_alias="kaiten_create_checklist_item",
        description="Create an item in a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
                "text": {"type": "string", "description": "Item text"},
                "checked": {"type": "boolean", "description": "Whether the item is checked"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "user_id": {"type": "integer", "description": "Assigned user ID"},
                "due_date": {"type": "string", "description": "Due date (ISO 8601 format)"},
            },
            "required": ["card_id", "checklist_id", "text"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/checklists/{checklist_id}/items",
            path_fields=("card_id", "checklist_id"),
            body_fields=("text", "checked", "sort_order", "user_id", "due_date"),
        ),
        examples=(
            ExampleSpec(command='kaiten checklist-items create --card-id 10 --checklist-id 20 --text "Ship it" --json', description="Create a checklist item."),
        ),
    ),
    make_tool(
        canonical_name="checklist-items.update",
        mcp_alias="kaiten_update_checklist_item",
        description="Update an item in a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
                "item_id": {"type": "integer", "description": "Checklist item ID"},
                "text": {"type": "string", "description": "Item text"},
                "checked": {"type": "boolean", "description": "Whether the item is checked"},
                "sort_order": {"type": "number", "description": "Sort order"},
                "user_id": {"type": "integer", "description": "Assigned user ID"},
                "due_date": {"type": "string", "description": "Due date (ISO 8601 format)"},
            },
            "required": ["card_id", "checklist_id", "item_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/checklists/{checklist_id}/items/{item_id}",
            path_fields=("card_id", "checklist_id", "item_id"),
            body_fields=("text", "checked", "sort_order", "user_id", "due_date"),
        ),
        examples=(
            ExampleSpec(command='kaiten checklist-items update --card-id 10 --checklist-id 20 --item-id 30 --checked --json', description="Update a checklist item."),
        ),
    ),
    make_tool(
        canonical_name="checklist-items.delete",
        mcp_alias="kaiten_delete_checklist_item",
        description="Delete an item from a checklist on a Kaiten card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "checklist_id": {"type": "integer", "description": "Checklist ID"},
                "item_id": {"type": "integer", "description": "Checklist item ID"},
            },
            "required": ["card_id", "checklist_id", "item_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/checklists/{checklist_id}/items/{item_id}",
            path_fields=("card_id", "checklist_id", "item_id"),
        ),
        examples=(
            ExampleSpec(command="kaiten checklist-items delete --card-id 10 --checklist-id 20 --item-id 30 --json", description="Delete a checklist item."),
        ),
    ),
)
