"""Local query tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.snapshots import execute_query_cards, execute_query_metrics, validate_query_filter


TOOLS = (
    make_tool(
        canonical_name="query.cards",
        mcp_alias="kaiten_query_cards",
        description="Run local card filtering against a stored snapshot without calling the Kaiten API.",
        input_schema={
            "type": "object",
            "properties": {
                "snapshot": {"type": "string", "description": "Snapshot name."},
                "filter": {"type": "object", "description": "Local filter object for card selection."},
                "view": {
                    "type": "string",
                    "enum": ["summary", "detail", "evidence"],
                    "description": "Local output view. summary is the default and keeps payloads narrow for repeated analytics and LLM workflows.",
                },
                "fields": {"type": "string", "description": "Comma-separated card or derived field names to keep."},
                "limit": {"type": "integer", "description": "Max returned rows. Default 100."},
                "offset": {"type": "integer", "description": "Pagination offset."},
                "compact": {"type": "boolean", "description": "Return a compact card response."},
            },
            "required": ["snapshot"],
        },
        operation=OperationSpec(method="GET", path_template="/local/query/cards"),
        response_policy=ResponsePolicy(compact_supported=True, fields_supported=True, result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_query_cards,
            payload_validator=validate_query_filter,
            cache_policy="none",
            requires_profile=False,
            apply_common_transforms=False,
        ),
        examples=(
            ExampleSpec(command="kaiten query cards --snapshot team-basic --filter '{\"board_ids\":[10],\"has_children\":true}' --fields id,title,has_children --json", description="Filter cards locally by board and derived flags in summary view."),
            ExampleSpec(command="kaiten query cards --snapshot team-basic --view evidence --filter '{\"comment_text_query\":\"blocked\"}' --compact --fields id,title,comment_text --json", description="Search local evidence text without extra API calls."),
        ),
        usage_notes=(
            "query cards never calls the Kaiten API; build or refresh the snapshot first.",
            "summary is the default view and keeps local card payloads narrow for LLM and report workflows.",
            "Use text_query, child_text_query, and comment_text_query to reduce candidate sets locally before involving an LLM.",
        ),
    ),
    make_tool(
        canonical_name="query.metrics",
        mcp_alias="kaiten_query_metrics",
        description="Compute local metrics over a stored snapshot without calling the Kaiten API.",
        input_schema={
            "type": "object",
            "properties": {
                "snapshot": {"type": "string", "description": "Snapshot name."},
                "metric": {
                    "type": "string",
                    "enum": ["count", "wip", "throughput", "lead_time", "cycle_time", "aging"],
                    "description": "Metric to compute locally.",
                },
                "filter": {"type": "object", "description": "Optional local filter object applied before metrics."},
                "group_by": {
                    "type": ["string", "null"],
                    "enum": ["board_id", "column_id", "lane_id", "type_id", "owner_id", "responsible_id", "state", "condition", None],
                    "description": "Optional grouping field.",
                },
            },
            "required": ["snapshot", "metric"],
        },
        operation=OperationSpec(method="GET", path_template="/local/query/metrics"),
        response_policy=ResponsePolicy(result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_query_metrics,
            payload_validator=validate_query_filter,
            cache_policy="none",
            requires_profile=False,
        ),
        examples=(
            ExampleSpec(command="kaiten query metrics --snapshot team-q1 --metric throughput --group-by board_id --json", description="Compute throughput locally over the snapshot window."),
            ExampleSpec(command="kaiten query metrics --snapshot team-basic --metric aging --filter '{\"board_ids\":[10],\"has_comments\":true}' --group-by column_id --json", description="Compute local WIP aging for a reduced candidate set."),
        ),
        usage_notes=(
            "throughput, lead_time, and cycle_time use the snapshot window when it exists; basic snapshots fall back to all locally known done transitions.",
            "For repeated report generation, query metrics after snapshot build instead of re-fetching topology, cards, and history on every run.",
        ),
    ),
)
