"""Checklist and checklist item tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import execute_checklist_items_list, execute_checklists_list


TOOLS = (
    make_tool(
        canonical_name="checklist-cards.list",
        mcp_alias="kaiten_list_checklist_cards",
        description="List cards that share a checklist.",
        input_schema={
            "type": "object",
            "properties": {
                "checklist_id": {"type": "integer", "description": "Checklist ID."},
                "only_shared_cards": {
                    "type": "boolean",
                    "description": "Return only shared cards.",
                },
            },
            "required": ["checklist_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/checklists/{checklist_id}",
            path_fields=("checklist_id",),
            query_fields=("only_shared_cards",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json checklist-cards list --checklist-id 20 --only-shared-cards",
                description="List cards with a checklist.",
            ),
        ),
    ),
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
        operation=OperationSpec(
            method="GET", path_template="/cards/{card_id}", path_fields=("card_id",)
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="synthetic",
            custom_executor=execute_checklists_list,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json checklists list --card-id 10",
                description="List checklists on a card.",
            ),
        ),
        usage_notes=(
            "Direct checklist listing is unsupported on sandbox; this command reads the card "
            "and extracts embedded checklists.",
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
            ExampleSpec(
                command='kaiten --json checklists create --card-id 10 --name "Ready for QA"',
                description="Create a checklist.",
            ),
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
            ExampleSpec(
                command='kaiten --json checklists update --card-id 10 --checklist-id 20 --name "Ready for QA"',
                description="Update a checklist.",
            ),
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
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/checklists/{checklist_id}",
            path_fields=("card_id", "checklist_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json checklists delete --card-id 10 --checklist-id 20",
                description="Delete a checklist.",
            ),
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
            path_template="/cards/{card_id}",
            path_fields=("card_id",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="synthetic",
            custom_executor=execute_checklist_items_list,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json checklist-items list --card-id 10 --checklist-id 20",
                description="List checklist items.",
            ),
        ),
        usage_notes=(
            "Direct checklist item listing is unsupported on sandbox; this command reads the "
            "card and extracts items from the matching embedded checklist.",
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
            ExampleSpec(
                command='kaiten --json checklist-items create --card-id 10 --checklist-id 20 --text "Ship it"',
                description="Create a checklist item.",
            ),
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
            ExampleSpec(
                command="kaiten --json checklist-items update --card-id 10 --checklist-id 20 --item-id 30 --checked",
                description="Update a checklist item.",
            ),
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
            ExampleSpec(
                command="kaiten --json checklist-items delete --card-id 10 --checklist-id 20 --item-id 30",
                description="Delete a checklist item.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklists.list",
        mcp_alias="kaiten_list_space_template_checklists",
        description="List template checklists for a space.",
        input_schema={
            "type": "object",
            "properties": {"space_uid": {"type": "string", "description": "Space UID."}},
            "required": ["space_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_uid}/template-checklists",
            path_fields=("space_uid",),
        ),
        response_policy=ResponsePolicy(result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten --json space-template-checklists list --space-uid space-uuid",
                description="List space template checklists.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklists.create",
        mcp_alias="kaiten_create_space_template_checklist",
        description="Create a template checklist for a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "name": {"type": "string", "description": "Template checklist name."},
                "sort_order": {"type": "number", "description": "Sort order."},
            },
            "required": ["space_uid", "name"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_uid}/template-checklists",
            path_fields=("space_uid",),
            body_fields=("name", "sort_order"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json space-template-checklists create --space-uid space-uuid --name "Definition of Done"',
                description="Create a space template checklist.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklists.update",
        mcp_alias="kaiten_update_space_template_checklist",
        description="Update a template checklist for a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "template_checklist_uid": {
                    "type": "string",
                    "description": "Template checklist UID.",
                },
                "name": {"type": "string", "description": "Template checklist name."},
                "sort_order": {"type": "number", "description": "Sort order."},
            },
            "required": ["space_uid", "template_checklist_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_uid}/template-checklists/{template_checklist_uid}",
            path_fields=("space_uid", "template_checklist_uid"),
            body_fields=("name", "sort_order"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json space-template-checklists update --space-uid space-uuid --template-checklist-uid tmpl-uuid --name "Ready"',
                description="Update a space template checklist.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklists.delete",
        mcp_alias="kaiten_delete_space_template_checklist",
        description="Delete a template checklist from a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "template_checklist_uid": {
                    "type": "string",
                    "description": "Template checklist UID.",
                },
            },
            "required": ["space_uid", "template_checklist_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_uid}/template-checklists/{template_checklist_uid}",
            path_fields=("space_uid", "template_checklist_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json space-template-checklists delete --space-uid space-uuid --template-checklist-uid tmpl-uuid",
                description="Delete a space template checklist.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklist-items.create",
        mcp_alias="kaiten_create_space_template_checklist_item",
        description="Create an item in a space template checklist.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "template_checklist_uid": {
                    "type": "string",
                    "description": "Template checklist UID.",
                },
                "text": {"type": "string", "description": "Checklist item text."},
                "sort_order": {"type": "number", "description": "Sort order."},
            },
            "required": ["space_uid", "template_checklist_uid", "text"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items",
            path_fields=("space_uid", "template_checklist_uid"),
            body_fields=("text", "sort_order"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json space-template-checklist-items create --space-uid space-uuid --template-checklist-uid tmpl-uuid --text "Reviewed"',
                description="Create a space template checklist item.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklist-items.update",
        mcp_alias="kaiten_update_space_template_checklist_item",
        description="Update an item in a space template checklist.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "template_checklist_uid": {
                    "type": "string",
                    "description": "Template checklist UID.",
                },
                "item_uid": {"type": "string", "description": "Template checklist item UID."},
                "text": {"type": "string", "description": "Checklist item text."},
                "sort_order": {"type": "number", "description": "Sort order."},
            },
            "required": ["space_uid", "template_checklist_uid", "item_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items/{item_uid}",
            path_fields=("space_uid", "template_checklist_uid", "item_uid"),
            body_fields=("text", "sort_order"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json space-template-checklist-items update --space-uid space-uuid --template-checklist-uid tmpl-uuid --item-uid item-uuid --text "Reviewed"',
                description="Update a space template checklist item.",
            ),
        ),
    ),
    make_tool(
        canonical_name="space-template-checklist-items.delete",
        mcp_alias="kaiten_delete_space_template_checklist_item",
        description="Delete an item from a space template checklist.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UID."},
                "template_checklist_uid": {
                    "type": "string",
                    "description": "Template checklist UID.",
                },
                "item_uid": {"type": "string", "description": "Template checklist item UID."},
            },
            "required": ["space_uid", "template_checklist_uid", "item_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items/{item_uid}",
            path_fields=("space_uid", "template_checklist_uid", "item_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json space-template-checklist-items delete --space-uid space-uuid --template-checklist-uid tmpl-uuid --item-uid item-uuid",
                description="Delete a space template checklist item.",
            ),
        ),
    ),
)
