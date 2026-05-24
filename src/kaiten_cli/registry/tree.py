"""Tree navigation tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import execute_tree_children_list, execute_tree_get

TREE_CATALOG_USAGE_NOTES = (
    "This aggregated command builds its local catalog from `/spaces`, `/documents`, and `/document-groups`.",
    "`/spaces` is read once; `/documents` and `/document-groups` are paginated internally with `limit=500` and `offset=0,500,...` until a short page is returned.",
    "No pagination options are required or accepted for this command; callers control only `parent_entity_uid` for children listing or `root_uid`/`depth` for nested tree output.",
    "If the internal pagination safety cap is reached with full pages, the command fails instead of returning a silently truncated tree.",
    "Visible entities whose `parent_entity_uid` is missing or inaccessible in the fetched catalog are promoted to root-level output.",
)


TOOLS = (
    make_tool(
        canonical_name="tree-entities.list",
        mcp_alias="kaiten_list_tree_entities",
        description="List tree entities from Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "limit": {"type": "integer", "description": "Max results."},
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/tree-entities", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten tree-entities list --json", description="List tree entities."
            ),
        ),
    ),
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
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated", custom_executor=execute_tree_children_list
        ),
        examples=(
            ExampleSpec(
                command="kaiten tree children list --parent-entity-uid root-1 --json",
                description="List direct tree children.",
            ),
        ),
        usage_notes=TREE_CATALOG_USAGE_NOTES,
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
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated", custom_executor=execute_tree_get
        ),
        examples=(
            ExampleSpec(
                command="kaiten tree get --depth 1 --json",
                description="Build a bounded entity tree.",
            ),
        ),
        usage_notes=TREE_CATALOG_USAGE_NOTES,
    ),
)
