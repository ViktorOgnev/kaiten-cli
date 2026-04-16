"""Chart and compute-job tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool

_HEAVY = ResponsePolicy(heavy=True)
_CHART_USAGE_NOTES = (
    "Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.",
    "If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.",
)

_COMMON_CHART_PROPS = {
    "space_id": {"type": "integer", "description": "Space ID"},
    "date_from": {"type": "string", "description": "Start date (ISO 8601)"},
    "date_to": {"type": "string", "description": "End date (ISO 8601)"},
    "tags": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Filter by tag IDs",
    },
    "only_asap_cards": {"type": "boolean", "description": "Include only ASAP (expedite) cards"},
    "card_types": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Filter by card type IDs",
    },
    "group_by": {"type": "string", "description": "Grouping mode"},
}

_CONTROL_EXTRA_PROPS = {
    "start_columns": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Start column IDs (required)",
    },
    "end_columns": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "End column IDs (required)",
    },
    "start_column_lanes": {
        "type": "object",
        "description": 'Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]}',
    },
    "end_column_lanes": {
        "type": "object",
        "description": 'Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]}',
    },
}

_CONTROL_EXTRA_KEYS = (
    "start_columns",
    "end_columns",
    "start_column_lanes",
    "end_column_lanes",
)


def _chart_create(
    *,
    canonical_name: str,
    mcp_alias: str,
    description: str,
    path_template: str,
    properties: dict,
    required: tuple[str, ...],
    body_fields: tuple[str, ...],
) -> tuple:
    return (
        make_tool(
            canonical_name=canonical_name,
            mcp_alias=mcp_alias,
            description=description,
            input_schema={"type": "object", "properties": properties, "required": list(required)},
            operation=OperationSpec(method="POST", path_template=path_template, body_fields=body_fields),
            response_policy=_HEAVY,
            examples=(
                ExampleSpec(command=f"kaiten {' '.join(canonical_name.split('.'))} --json", description=description),
            ),
            usage_notes=_CHART_USAGE_NOTES,
        ),
    )


TOOLS = (
    make_tool(
        canonical_name="charts.boards.get",
        mcp_alias="kaiten_get_chart_boards",
        description="Get board structure for chart configuration in a space.",
        input_schema={
            "type": "object",
            "properties": {"space_id": {"type": "integer", "description": "Space ID"}},
            "required": ["space_id"],
        },
        operation=OperationSpec(method="GET", path_template="/charts/{space_id}/boards", path_fields=("space_id",)),
        examples=(
            ExampleSpec(command="kaiten charts boards get --space-id 1 --json", description="Get chart board structure."),
        ),
    ),
    make_tool(
        canonical_name="charts.summary.get",
        mcp_alias="kaiten_chart_summary",
        description="Get done-card summary for a space within a date range.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "date_from": {"type": "string", "description": "Start date (ISO 8601)"},
                "date_to": {"type": "string", "description": "End date (ISO 8601)"},
                "done_columns": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Array of done column IDs",
                },
            },
            "required": ["space_id", "date_from", "date_to", "done_columns"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/charts/summary",
            body_fields=("space_id", "date_from", "date_to", "done_columns"),
        ),
        response_policy=_HEAVY,
        examples=(
            ExampleSpec(
                command="kaiten charts summary get --space-id 1 --date-from 2026-01-01 --date-to 2026-01-31 --done-columns '[10,11]' --json",
                description="Get a done-card summary.",
            ),
        ),
        usage_notes=_CHART_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="charts.block-resolution.get",
        mcp_alias="kaiten_chart_block_resolution",
        description="Get blocker resolution time data for a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "category_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by blocker category IDs",
                },
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/charts/block-resolution-time-chart",
            body_fields=("space_id", "category_ids"),
        ),
        response_policy=_HEAVY,
        examples=(
            ExampleSpec(command="kaiten charts block-resolution get --space-id 1 --json", description="Get blocker resolution data."),
        ),
        usage_notes=_CHART_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="charts.due-dates.get",
        mcp_alias="kaiten_chart_due_dates",
        description="Get due dates analysis for a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "card_date_from": {"type": "string", "description": "Card date range start (ISO 8601)"},
                "card_date_to": {"type": "string", "description": "Card date range end (ISO 8601)"},
                "checklist_item_date_from": {
                    "type": "string",
                    "description": "Checklist item date range start (ISO 8601)",
                },
                "checklist_item_date_to": {
                    "type": "string",
                    "description": "Checklist item date range end (ISO 8601)",
                },
                "due_date": {"type": "string", "description": "Due date filter (ISO 8601)"},
                "responsible_id": {"type": "integer", "description": "Responsible user ID"},
                "tz_offset": {"type": "integer", "description": "Timezone offset in minutes"},
                "lane_ids": {"type": "array", "items": {"type": "integer"}, "description": "Filter by lane IDs"},
                "column_ids": {"type": "array", "items": {"type": "integer"}, "description": "Filter by column IDs"},
                "card_type_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by card type IDs",
                },
                "tag_ids": {"type": "array", "items": {"type": "integer"}, "description": "Filter by tag IDs"},
            },
            "required": [
                "space_id",
                "card_date_from",
                "card_date_to",
                "checklist_item_date_from",
                "checklist_item_date_to",
            ],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/charts/due-dates",
            body_fields=(
                "space_id",
                "card_date_from",
                "card_date_to",
                "checklist_item_date_from",
                "checklist_item_date_to",
                "due_date",
                "responsible_id",
                "tz_offset",
                "lane_ids",
                "column_ids",
                "card_type_ids",
                "tag_ids",
            ),
        ),
        response_policy=_HEAVY,
        examples=(
            ExampleSpec(
                command="kaiten charts due-dates get --space-id 1 --card-date-from 2026-01-01 --card-date-to 2026-01-31 --checklist-item-date-from 2026-01-01 --checklist-item-date-to 2026-01-31 --json",
                description="Get due-date analysis.",
            ),
        ),
        usage_notes=_CHART_USAGE_NOTES,
    ),
    *_chart_create(
        canonical_name="charts.cfd.create",
        mcp_alias="kaiten_chart_cfd",
        description="Build a Cumulative Flow Diagram (CFD) for a space.",
        path_template="/charts/cfd",
        properties={
            **_COMMON_CHART_PROPS,
            "cardTypes": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by card type IDs (alternative field name used by CFD)",
            },
            "selectedLanes": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by lane IDs",
            },
        },
        required=("space_id", "date_from", "date_to"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "cardTypes", "group_by", "selectedLanes"),
    ),
    *_chart_create(
        canonical_name="charts.control.create",
        mcp_alias="kaiten_chart_control",
        description="Build a Control Chart for a space.",
        path_template="/charts/control-chart",
        properties={**_COMMON_CHART_PROPS, **_CONTROL_EXTRA_PROPS},
        required=("space_id", "date_from", "date_to", "start_columns", "end_columns", "start_column_lanes", "end_column_lanes"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", *_CONTROL_EXTRA_KEYS),
    ),
    *_chart_create(
        canonical_name="charts.spectral.create",
        mcp_alias="kaiten_chart_spectral",
        description="Build a Spectral Chart for a space.",
        path_template="/charts/spectral-chart",
        properties={**_COMMON_CHART_PROPS, **_CONTROL_EXTRA_PROPS},
        required=("space_id", "date_from", "date_to", "start_columns", "end_columns", "start_column_lanes", "end_column_lanes"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", *_CONTROL_EXTRA_KEYS),
    ),
    *_chart_create(
        canonical_name="charts.lead-time.create",
        mcp_alias="kaiten_chart_lead_time",
        description="Build a Lead Time Chart for a space.",
        path_template="/charts/lead-time",
        properties={**_COMMON_CHART_PROPS, **_CONTROL_EXTRA_PROPS},
        required=("space_id", "date_from", "date_to", "start_columns", "end_columns", "start_column_lanes", "end_column_lanes"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", *_CONTROL_EXTRA_KEYS),
    ),
    *_chart_create(
        canonical_name="charts.throughput-capacity.create",
        mcp_alias="kaiten_chart_throughput_capacity",
        description="Build a Throughput Capacity Chart for a space.",
        path_template="/charts/throughput-capacity-chart",
        properties={**_COMMON_CHART_PROPS, "end_column": {"type": "integer", "description": "End (done) column ID"}},
        required=("space_id", "date_from", "end_column"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", "end_column"),
    ),
    *_chart_create(
        canonical_name="charts.throughput-demand.create",
        mcp_alias="kaiten_chart_throughput_demand",
        description="Build a Throughput Demand Chart for a space.",
        path_template="/charts/throughput-demand-chart",
        properties={**_COMMON_CHART_PROPS, "start_column": {"type": "integer", "description": "Start (input) column ID"}},
        required=("space_id", "date_from", "start_column"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", "start_column"),
    ),
    *_chart_create(
        canonical_name="charts.task-distribution.create",
        mcp_alias="kaiten_chart_task_distribution",
        description="Build a Task Distribution Chart for a space.",
        path_template="/charts/task-distribution-chart",
        properties={
            "space_id": {"type": "integer", "description": "Space ID"},
            "timezone": {"type": "string", "description": "Timezone name (e.g. Europe/Moscow)"},
            "includeArchivedCards": {"type": "boolean", "description": "Include archived cards"},
            "only_asap_cards": {"type": "boolean", "description": "Include only ASAP (expedite) cards"},
            "card_types": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by card type IDs",
            },
            "itemsFilter": {"type": "object", "description": "Additional filter object for items"},
        },
        required=("space_id",),
        body_fields=("space_id", "timezone", "includeArchivedCards", "only_asap_cards", "card_types", "itemsFilter"),
    ),
    *_chart_create(
        canonical_name="charts.cycle-time.create",
        mcp_alias="kaiten_chart_cycle_time",
        description="Build a Cycle Time Chart for a space.",
        path_template="/charts/cycle-time-chart",
        properties={
            **_COMMON_CHART_PROPS,
            "start_column": {"type": "integer", "description": "Start column ID"},
            "end_column": {"type": "integer", "description": "End column ID"},
        },
        required=("space_id", "date_from", "date_to", "start_column", "end_column"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", "start_column", "end_column"),
    ),
    *_chart_create(
        canonical_name="charts.sales-funnel.create",
        mcp_alias="kaiten_chart_sales_funnel",
        description="Build a Sales Funnel Chart for a space.",
        path_template="/charts/sales-funnel",
        properties={
            **_COMMON_CHART_PROPS,
            "board_configs": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Array of board configuration objects.",
            },
        },
        required=("space_id", "date_from", "date_to", "board_configs"),
        body_fields=("space_id", "date_from", "date_to", "tags", "only_asap_cards", "card_types", "group_by", "board_configs"),
    ),
    make_tool(
        canonical_name="compute-jobs.get",
        mcp_alias="kaiten_get_compute_job",
        description="Get the status and result of an asynchronous compute job.",
        input_schema={
            "type": "object",
            "properties": {"job_id": {"type": "integer", "description": "Compute job ID"}},
            "required": ["job_id"],
        },
        operation=OperationSpec(method="GET", path_template="/users/current/compute-jobs/{job_id}", path_fields=("job_id",)),
        runtime_behavior=RuntimeBehavior(cache_policy="none"),
        examples=(
            ExampleSpec(command="kaiten compute-jobs get --job-id 1 --json", description="Get compute job status."),
        ),
    ),
    make_tool(
        canonical_name="compute-jobs.cancel",
        mcp_alias="kaiten_cancel_compute_job",
        description="Cancel a running or queued compute job.",
        input_schema={
            "type": "object",
            "properties": {"job_id": {"type": "integer", "description": "Compute job ID"}},
            "required": ["job_id"],
        },
        operation=OperationSpec(method="DELETE", path_template="/users/current/compute-jobs/{job_id}", path_fields=("job_id",)),
        examples=(
            ExampleSpec(command="kaiten compute-jobs cancel --job-id 1 --json", description="Cancel a compute job."),
        ),
    ),
)
