"""Tree navigation tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime_behaviors import execute_tree_children_list, execute_tree_get


TOOLS = (
    make_tool(
        canonical_name="tree.children.list",
        mcp_alias="kaiten_list_children",
        description="List direct children of an entity in the Kaiten sidebar tree.",
        input_schema={
            "type": "object",
            "properties": {
                "parent_entity_uid": {
                    "type": "string",
                    "description": "Parent entity UID. Omit to list root-level entities.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/tree/children"),
        response_policy=ResponsePolicy(heavy=True, result_kind="list"),
        runtime_behavior=RuntimeBehavior(execution_mode="aggregated", custom_executor=execute_tree_children_list),
        examples=(
            ExampleSpec(command="kaiten tree children list --parent-entity-uid root-1 --json", description="List direct tree children."),
        ),
    ),
    make_tool(
        canonical_name="tree.get",
        mcp_alias="kaiten_get_tree",
        description="Build a nested entity tree from the Kaiten sidebar.",
        input_schema={
            "type": "object",
            "properties": {
                "root_uid": {
                    "type": "string",
                    "description": "Start tree from this entity UID. Omit for full tree from roots.",
                },
                "depth": {
                    "type": "integer",
                    "description": "Max recursion depth (0 = unlimited). Default: 0.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/tree"),
        response_policy=ResponsePolicy(heavy=True, result_kind="list"),
        runtime_behavior=RuntimeBehavior(execution_mode="aggregated", custom_executor=execute_tree_get),
        examples=(
            ExampleSpec(command="kaiten tree get --depth 1 --json", description="Build a bounded entity tree."),
        ),
    ),
)
