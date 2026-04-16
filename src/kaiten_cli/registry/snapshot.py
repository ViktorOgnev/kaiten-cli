"""Local snapshot tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.snapshots import (
    execute_snapshot_build,
    execute_snapshot_delete,
    execute_snapshot_list,
    execute_snapshot_refresh,
    execute_snapshot_show,
    validate_snapshot_build,
)


TOOLS = (
    make_tool(
        canonical_name="snapshot.build",
        mcp_alias="kaiten_snapshot_build",
        description="Build a persistent local sqlite snapshot for headless reads, analytics, and report workflows.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Stable snapshot name."},
                "space_id": {"type": "integer", "description": "Source space ID."},
                "board_ids": {"type": "array", "items": {"type": "integer"}, "description": "Optional board IDs to keep inside the snapshot."},
                "preset": {
                    "type": "string",
                    "enum": ["basic", "analytics", "evidence", "full"],
                    "description": "Snapshot scope preset.",
                },
                "window_start": {"type": "string", "description": "Window start timestamp for analytics/full snapshots."},
                "window_end": {"type": "string", "description": "Window end timestamp for analytics/full snapshots."},
            },
            "required": ["name", "space_id"],
        },
        operation=OperationSpec(method="POST", path_template="/local/snapshots/{name}", path_fields=("name",)),
        response_policy=ResponsePolicy(heavy=True, result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_snapshot_build,
            payload_validator=validate_snapshot_build,
            cache_policy="none",
            requires_profile=True,
            enforce_mutation_guard=False,
        ),
        examples=(
            ExampleSpec(command="kaiten snapshot build --name team-basic --space-id 10 --preset basic --json", description="Build a reusable local snapshot with topology and cards."),
            ExampleSpec(command="kaiten snapshot build --name team-q1 --space-id 10 --preset analytics --window-start 2026-01-01T00:00:00Z --window-end 2026-03-31T23:59:59Z --json", description="Build an analytics snapshot with bounded activity and history data."),
        ),
        usage_notes=(
            "Build one snapshot, then run repeated local query cards/query metrics commands without extra Kaiten API calls.",
            "analytics and full presets require window_start/window_end because throughput and history are window-bound datasets.",
        ),
    ),
    make_tool(
        canonical_name="snapshot.refresh",
        mcp_alias="kaiten_snapshot_refresh",
        description="Rebuild an existing local snapshot in place using its stored snapshot definition.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Snapshot name to rebuild."},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="PATCH", path_template="/local/snapshots/{name}", path_fields=("name",)),
        response_policy=ResponsePolicy(heavy=True, result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_snapshot_refresh,
            cache_policy="none",
            requires_profile=True,
            enforce_mutation_guard=False,
        ),
        examples=(
            ExampleSpec(command="kaiten snapshot refresh --name team-q1 --json", description="Refresh a previously built snapshot."),
        ),
        usage_notes=(
            "refresh reuses the stored snapshot spec and rebuilds datasets in place; v1 is rebuild-oriented, not incremental.",
        ),
    ),
    make_tool(
        canonical_name="snapshot.list",
        mcp_alias="kaiten_snapshot_list",
        description="List locally stored snapshots with schema version and dataset counts.",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/local/snapshots"),
        response_policy=ResponsePolicy(result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_snapshot_list,
            cache_policy="none",
            requires_profile=False,
        ),
        examples=(
            ExampleSpec(command="kaiten snapshot list --json", description="Show available local snapshots."),
        ),
    ),
    make_tool(
        canonical_name="snapshot.show",
        mcp_alias="kaiten_snapshot_show",
        description="Show local snapshot metadata, schema version, dataset counts, and the last build trace summary.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Snapshot name."},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="GET", path_template="/local/snapshots/{name}", path_fields=("name",)),
        response_policy=ResponsePolicy(result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_snapshot_show,
            cache_policy="none",
            requires_profile=False,
        ),
        examples=(
            ExampleSpec(command="kaiten snapshot show --name team-q1 --json", description="Inspect snapshot metadata and dataset counts."),
        ),
    ),
    make_tool(
        canonical_name="snapshot.delete",
        mcp_alias="kaiten_snapshot_delete",
        description="Delete a local snapshot from sqlite storage.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Snapshot name."},
            },
            "required": ["name"],
        },
        operation=OperationSpec(method="DELETE", path_template="/local/snapshots/{name}", path_fields=("name",)),
        response_policy=ResponsePolicy(result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_snapshot_delete,
            cache_policy="none",
            requires_profile=False,
            enforce_mutation_guard=False,
        ),
        examples=(
            ExampleSpec(command="kaiten snapshot delete --name team-q1 --json", description="Delete a local snapshot."),
        ),
    ),
)
