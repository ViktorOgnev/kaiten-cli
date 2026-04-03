"""Project tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool


TOOLS = (
    make_tool(
        canonical_name="projects.list",
        mcp_alias="kaiten_list_projects",
        description="List all Kaiten projects in the company.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/projects"),
        examples=(
            ExampleSpec(command="kaiten projects list --json", description="List company projects."),
        ),
    ),
    make_tool(
        canonical_name="projects.create",
        mcp_alias="kaiten_create_project",
        description="Create a new Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Project title (stored as 'name')"},
                "description": {"type": "string", "description": "Project description"},
                "work_calendar_id": {"type": "string", "description": "Work calendar UUID to attach to the project"},
                "settings": {"type": "object", "description": "Project settings"},
                "properties": {"type": "object", "description": "Custom property values as {id_<N>: value} pairs"},
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/projects",
            body_fields=("title", "description", "work_calendar_id", "settings", "properties"),
        ),
        examples=(
            ExampleSpec(command='kaiten projects create --title "Platform" --json', description="Create a project."),
        ),
    ),
    make_tool(
        canonical_name="projects.get",
        mcp_alias="kaiten_get_project",
        description="Get a Kaiten project by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
                "with_cards_data": {"type": "boolean", "description": "Include full card data with path info and custom properties"},
            },
            "required": ["project_id"],
        },
        operation=OperationSpec(method="GET", path_template="/projects/{project_id}", path_fields=("project_id",), query_fields=("with_cards_data",)),
        examples=(
            ExampleSpec(command="kaiten projects get --project-id p1 --json", description="Get a project by ID."),
        ),
    ),
    make_tool(
        canonical_name="projects.update",
        mcp_alias="kaiten_update_project",
        description="Update a Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
                "title": {"type": "string", "description": "Project title (stored as 'name')"},
                "description": {"type": "string", "description": "Project description"},
                "condition": {"type": "string", "enum": ["active", "inactive"], "description": "Project condition (active or inactive)"},
                "work_calendar_id": {"type": "string", "description": "Work calendar UUID to attach to the project"},
                "settings": {"type": "object", "description": "Project settings"},
                "properties": {"type": "object", "description": "Custom property values as {id_<N>: value} pairs; set a key to null to clear it"},
            },
            "required": ["project_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/projects/{project_id}",
            path_fields=("project_id",),
            body_fields=("title", "description", "condition", "work_calendar_id", "settings", "properties"),
        ),
        examples=(
            ExampleSpec(command='kaiten projects update --project-id p1 --title "Platform" --json', description="Update a project."),
        ),
    ),
    make_tool(
        canonical_name="projects.delete",
        mcp_alias="kaiten_delete_project",
        description="Delete a Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
            },
            "required": ["project_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/projects/{project_id}", path_fields=("project_id",)),
        examples=(
            ExampleSpec(command="kaiten projects delete --project-id p1 --json", description="Delete a project."),
        ),
    ),
    make_tool(
        canonical_name="projects.cards.list",
        mcp_alias="kaiten_list_project_cards",
        description="List cards in a Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects).",
                    "default": False,
                },
            },
            "required": ["project_id"],
        },
        operation=OperationSpec(method="GET", path_template="/projects/{project_id}/cards", path_fields=("project_id",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten projects.cards list --project-id p1 --compact --json", description="List project cards."),
        ),
    ),
    make_tool(
        canonical_name="projects.cards.add",
        mcp_alias="kaiten_add_project_card",
        description="Add a card to a Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
                "card_id": {"type": "integer", "description": "Card ID to add"},
            },
            "required": ["project_id", "card_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/projects/{project_id}/cards",
            path_fields=("project_id",),
            body_fields=("card_id",),
        ),
        examples=(
            ExampleSpec(command="kaiten projects.cards add --project-id p1 --card-id 10 --json", description="Add a card to a project."),
        ),
    ),
    make_tool(
        canonical_name="projects.cards.remove",
        mcp_alias="kaiten_remove_project_card",
        description="Remove a card from a Kaiten project.",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (UUID)"},
                "card_id": {"type": "integer", "description": "Card ID to remove"},
            },
            "required": ["project_id", "card_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/projects/{project_id}/cards/{card_id}", path_fields=("project_id", "card_id")),
        examples=(
            ExampleSpec(command="kaiten projects.cards remove --project-id p1 --card-id 10 --json", description="Remove a card from a project."),
        ),
    ),
)
