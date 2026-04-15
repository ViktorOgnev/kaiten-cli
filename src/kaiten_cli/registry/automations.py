"""Automation and workflow tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime_behaviors import automation_copy_request


TOOLS = (
    make_tool(
        canonical_name="automations.list",
        mcp_alias="kaiten_list_automations",
        description="List all automations for a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/automations", path_fields=("space_id",)),
        examples=(
            ExampleSpec(command="kaiten automations list --space-id 1 --json", description="List space automations."),
        ),
    ),
    make_tool(
        canonical_name="automations.create",
        mcp_alias="kaiten_create_automation",
        description="Create a new automation in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "name": {"type": "string", "description": "Automation name"},
                "trigger": {"type": "object", "description": "Trigger configuration"},
                "actions": {"type": "array", "items": {"type": "object"}, "description": "Action configurations"},
                "conditions": {"type": "object", "description": "Conditions configuration"},
                "type": {"type": "string", "enum": ["on_action", "on_date", "on_demand", "on_workflow"], "description": "Automation type"},
                "sort_order": {"type": "number", "description": "Sort position"},
                "source_automation_id": {"type": "string", "description": "Automation ID to clone from"},
            },
            "required": ["space_id", "name", "trigger", "actions"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/automations",
            path_fields=("space_id",),
            body_fields=("name", "trigger", "actions", "conditions", "type", "sort_order", "source_automation_id"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten automations create --space-id 1 --name Auto --type on_action --trigger \'{"type":"card_created"}\' --actions \'[{"type":"add_assignee","created":"2026-01-01T00:00:00+00:00","data":{"variant":"specific","userId":42}}]\' --json',
                description="Create an automation using the known live-valid add_assignee payload shape.",
            ),
        ),
    ),
    make_tool(
        canonical_name="automations.get",
        mcp_alias="kaiten_get_automation",
        description="Get a specific automation in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
            },
            "required": ["space_id", "automation_id"],
        },
        operation=OperationSpec(method="GET", path_template="/spaces/{space_id}/automations/{automation_id}", path_fields=("space_id", "automation_id")),
        examples=(
            ExampleSpec(command="kaiten automations get --space-id 1 --automation-id auto-1 --json", description="Get an automation."),
        ),
    ),
    make_tool(
        canonical_name="automations.update",
        mcp_alias="kaiten_update_automation",
        description="Update an automation in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
                "name": {"type": "string", "description": "New automation name"},
                "trigger": {"type": "object", "description": "New trigger configuration"},
                "actions": {"type": "array", "items": {"type": "object"}, "description": "New action configurations"},
                "conditions": {"type": "object", "description": "New conditions configuration"},
                "status": {"type": "string", "enum": ["active", "disabled"], "description": "Automation status"},
                "sort_order": {"type": "number", "description": "Sort position"},
            },
            "required": ["space_id", "automation_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/automations/{automation_id}",
            path_fields=("space_id", "automation_id"),
            body_fields=("name", "trigger", "actions", "conditions", "status", "sort_order"),
        ),
        examples=(
            ExampleSpec(command='kaiten automations update --space-id 1 --automation-id auto-1 --status disabled --json', description="Disable an automation."),
        ),
    ),
    make_tool(
        canonical_name="automations.delete",
        mcp_alias="kaiten_delete_automation",
        description="Delete an automation from a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
            },
            "required": ["space_id", "automation_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/spaces/{space_id}/automations/{automation_id}", path_fields=("space_id", "automation_id")),
        examples=(
            ExampleSpec(command="kaiten automations delete --space-id 1 --automation-id auto-1 --json", description="Delete an automation."),
        ),
    ),
    make_tool(
        canonical_name="automations.copy",
        mcp_alias="kaiten_copy_automation",
        description="Copy an automation to another space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Source space ID"},
                "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
                "target_space_id": {"type": "integer", "description": "Target space ID"},
            },
            "required": ["space_id", "automation_id", "target_space_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_id}/automations/{automation_id}/copy",
            path_fields=("space_id", "automation_id"),
            body_fields=("target_space_id",),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=automation_copy_request),
        examples=(
            ExampleSpec(command="kaiten automations copy --space-id 1 --automation-id auto-1 --target-space-id 2 --json", description="Copy an automation."),
        ),
    ),
    make_tool(
        canonical_name="workflows.list",
        mcp_alias="kaiten_list_workflows",
        description="List company workflows.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of results"},
                "offset": {"type": "integer", "description": "Offset for pagination"},
            },
        },
        operation=OperationSpec(method="GET", path_template="/company/workflows", query_fields=("limit", "offset")),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten workflows list --json", description="List workflows."),
        ),
    ),
    make_tool(
        canonical_name="workflows.create",
        mcp_alias="kaiten_create_workflow",
        description="Create a new company workflow.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Workflow name"},
                "stages": {"type": "array", "items": {"type": "object"}, "description": "Workflow stages"},
                "transitions": {"type": "array", "items": {"type": "object"}, "description": "Workflow transitions"},
            },
            "required": ["name", "stages", "transitions"],
        },
        operation=OperationSpec(method="POST", path_template="/company/workflows", body_fields=("name", "stages", "transitions")),
        examples=(
            ExampleSpec(command='kaiten workflows create --name Flow --stages \'[{"id":"1","name":"Todo","type":"queue"}]\' --transitions \'[{"id":"t1"}]\' --json', description="Create a workflow."),
        ),
    ),
    make_tool(
        canonical_name="workflows.get",
        mcp_alias="kaiten_get_workflow",
        description="Get a specific company workflow by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
            },
            "required": ["workflow_id"],
        },
        operation=OperationSpec(method="GET", path_template="/company/workflows/{workflow_id}", path_fields=("workflow_id",)),
        examples=(
            ExampleSpec(command="kaiten workflows get --workflow-id wf-1 --json", description="Get a workflow."),
        ),
    ),
    make_tool(
        canonical_name="workflows.update",
        mcp_alias="kaiten_update_workflow",
        description="Update a company workflow.",
        input_schema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
                "name": {"type": "string", "description": "New workflow name"},
                "stages": {"type": "array", "items": {"type": "object"}, "description": "Updated stages"},
                "transitions": {"type": "array", "items": {"type": "object"}, "description": "Updated transitions"},
            },
            "required": ["workflow_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/workflows/{workflow_id}",
            path_fields=("workflow_id",),
            body_fields=("name", "stages", "transitions"),
        ),
        examples=(
            ExampleSpec(command='kaiten workflows update --workflow-id wf-1 --name Flow2 --json', description="Update a workflow."),
        ),
    ),
    make_tool(
        canonical_name="workflows.delete",
        mcp_alias="kaiten_delete_workflow",
        description="Delete a company workflow.",
        input_schema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
            },
            "required": ["workflow_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/company/workflows/{workflow_id}", path_fields=("workflow_id",)),
        examples=(
            ExampleSpec(command="kaiten workflows delete --workflow-id wf-1 --json", description="Delete a workflow."),
        ),
    ),
)
