"""Experimental dashboard tool specs."""

from __future__ import annotations

from kaiten_cli.models import (
    CACHE_POLICY_NONE,
    ExampleSpec,
    OperationSpec,
    ResponsePolicy,
    RuntimeBehavior,
)
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.support.dashboards import (
    execute_dashboard_widgets_list,
    validate_dashboard_compute_payload,
)


DASHBOARD_WARNING = (
    "Dashboards are experimental and not yet documented in the public REST catalog; "
    "older Kaiten installations may return 404 or 405."
)
DASHBOARD_PERMISSION_NOTE = (
    "Only the owner can change title/publicity or delete a dashboard; editors can change "
    "layout/filter and manage users/widgets, while viewers have read access."
)
DASHBOARD_WIDGET_SCHEMA_NOTE = (
    "Current sources include distribution, cardsTrend, velocity, throughput, cycleTimeTrends, "
    "burndown, cfd, cycleTime, controlChart, blockResolutionTime, metric, fieldSum, "
    "sprintProgress, cardList, dueDates and timeSpent. Current visualizations include bar, "
    "horizontalBar, pie, donut, table, line, area, stackedArea, scatter, "
    "percentileHistogram, number, numberTrend and battery. Values are intentionally not "
    "client-enumerated because the dashboard schema is experimental."
)


def _shaping_properties() -> dict[str, dict]:
    return {
        "compact": {
            "type": "boolean",
            "description": "Return compact output without heavy nested fields.",
        },
        "fields": {
            "type": "string",
            "description": "Comma-separated field names to return.",
        },
    }


SHAPED_LIST = ResponsePolicy(
    compact_supported=True,
    fields_supported=True,
    result_kind="list",
)
SHAPED_ENTITY = ResponsePolicy(
    compact_supported=True,
    fields_supported=True,
    result_kind="entity",
)


TOOLS = (
    make_tool(
        canonical_name="dashboards.list",
        mcp_alias="kaiten_list_dashboards",
        description="List dashboards visible to the current user, including public dashboards.",
        input_schema={
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Search dashboard titles."},
                "limit": {
                    "type": "integer",
                    "description": "Maximum dashboards to return (server cap 50).",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
                **_shaping_properties(),
            },
        },
        operation=OperationSpec(
            method="GET",
            path_template="/dashboards",
            query_fields=("search", "limit", "offset"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=50,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json dashboards list --search "Requests" --fields id,title,is_public,role --compact',
                description="Find visible dashboards by title.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING,),
    ),
    make_tool(
        canonical_name="dashboards.get",
        mcp_alias="kaiten_get_dashboard",
        description="Get a dashboard and optionally include its widgets.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "include": {
                    "type": "string",
                    "description": "Comma-separated relations to include; currently widgets.",
                },
                **_shaping_properties(),
            },
            "required": ["dashboard_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/dashboards/{dashboard_id}",
            path_fields=("dashboard_id",),
            query_fields=("include",),
        ),
        response_policy=SHAPED_ENTITY,
        examples=(
            ExampleSpec(
                command="kaiten --json dashboards get --dashboard-id <dashboard_uuid> --include widgets",
                description="Get dashboard configuration and widgets.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, DASHBOARD_PERMISSION_NOTE),
    ),
    make_tool(
        canonical_name="dashboards.create",
        mcp_alias="kaiten_create_dashboard",
        description="Create a private or public dashboard owned by the current user.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Dashboard title."},
                "is_public": {
                    "type": "boolean",
                    "description": "Make the dashboard visible company-wide (default false).",
                },
            },
            "required": ["title"],
        },
        operation=OperationSpec(
            method="POST", path_template="/dashboards", body_fields=("title", "is_public")
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json dashboards create --title "Team health"',
                description="Create a private dashboard.",
            ),
            ExampleSpec(
                command='kaiten --json dashboards create --title "Company metrics" --is-public',
                description="Create a public dashboard.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, DASHBOARD_PERMISSION_NOTE),
    ),
    make_tool(
        canonical_name="dashboards.clone",
        mcp_alias="kaiten_clone_dashboard",
        description="Create a personal dashboard copy with new widget IDs.",
        input_schema={
            "type": "object",
            "properties": {
                "source_dashboard_id": {
                    "type": "string",
                    "description": "Accessible source dashboard UUID.",
                },
                "title": {"type": "string", "description": "Title for the new dashboard."},
                "is_public": {
                    "type": "boolean",
                    "description": "Override copied visibility; otherwise inherit it.",
                },
            },
            "required": ["source_dashboard_id", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/dashboards",
            body_fields=("source_dashboard_id", "title", "is_public"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json dashboards clone --source-dashboard-id <dashboard_uuid> --title "My copy"',
                description="Clone an accessible dashboard into a personal copy.",
            ),
        ),
        usage_notes=(
            DASHBOARD_WARNING,
            "Clone copies layout, filter and widgets with fresh widget IDs; shared users are not copied.",
        ),
    ),
    make_tool(
        canonical_name="dashboards.update",
        mcp_alias="kaiten_update_dashboard",
        description="Update dashboard metadata, filter, or layout.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "title": {"type": "string", "description": "New title (owner only)."},
                "is_public": {
                    "type": "boolean",
                    "description": "New visibility (owner only).",
                },
                "filter": {
                    "type": ["object", "null"],
                    "description": "Dashboard filter JSON; use null to clear it.",
                },
                "layout": {
                    "type": "object",
                    "description": "Responsive dashboard layout keyed by breakpoint and widget UUID.",
                },
            },
            "required": ["dashboard_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/dashboards/{dashboard_id}",
            path_fields=("dashboard_id",),
            body_fields=("title", "is_public", "filter", "layout"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboards update --dashboard-id <dashboard_uuid> --layout '{\"lg\":{}}'",
                description="Update an editable dashboard layout.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, DASHBOARD_PERMISSION_NOTE),
    ),
    make_tool(
        canonical_name="dashboards.delete",
        mcp_alias="kaiten_delete_dashboard",
        description="Archive a dashboard owned by the current user.",
        input_schema={
            "type": "object",
            "properties": {"dashboard_id": {"type": "string", "description": "Dashboard UUID."}},
            "required": ["dashboard_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/dashboards/{dashboard_id}",
            path_fields=("dashboard_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboards delete --dashboard-id <dashboard_uuid>",
                description="Archive an owned dashboard.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "Only the dashboard owner can delete it."),
    ),
    make_tool(
        canonical_name="dashboard-users.list",
        mcp_alias="kaiten_list_dashboard_users",
        description="List users with explicit access to a dashboard.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "limit": {
                    "type": "integer",
                    "description": "Maximum users to return (server cap 50).",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
                **_shaping_properties(),
            },
            "required": ["dashboard_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/dashboards/{dashboard_id}/users",
            path_fields=("dashboard_id",),
            query_fields=("limit", "offset"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=50,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-users list --dashboard-id <dashboard_uuid> --fields user_uid,role",
                description="List dashboard collaborators.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "Only owners and editors can list or manage access."),
    ),
    make_tool(
        canonical_name="dashboard-users.add",
        mcp_alias="kaiten_add_dashboard_user",
        description="Grant a company user viewer or editor access to a dashboard.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "user_uid": {"type": "string", "description": "Company user UUID."},
                "role": {
                    "type": "string",
                    "enum": ["viewer", "editor"],
                    "description": "Dashboard role.",
                },
            },
            "required": ["dashboard_id", "user_uid", "role"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/dashboards/{dashboard_id}/users",
            path_fields=("dashboard_id",),
            body_fields=("user_uid", "role"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-users add --dashboard-id <dashboard_uuid> --user-uid <user_uuid> --role viewer",
                description="Grant view access.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "The user must already belong to the company."),
    ),
    make_tool(
        canonical_name="dashboard-users.update",
        mcp_alias="kaiten_update_dashboard_user",
        description="Change a dashboard collaborator role.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "user_uid": {"type": "string", "description": "Company user UUID."},
                "role": {
                    "type": "string",
                    "enum": ["viewer", "editor"],
                    "description": "New dashboard role.",
                },
            },
            "required": ["dashboard_id", "user_uid", "role"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/dashboards/{dashboard_id}/users/{user_uid}",
            path_fields=("dashboard_id", "user_uid"),
            body_fields=("role",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-users update --dashboard-id <dashboard_uuid> --user-uid <user_uuid> --role editor",
                description="Promote a collaborator to editor.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "The owner role cannot be changed or downgraded."),
    ),
    make_tool(
        canonical_name="dashboard-users.remove",
        mcp_alias="kaiten_remove_dashboard_user",
        description="Revoke a collaborator's explicit dashboard access.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "user_uid": {"type": "string", "description": "Company user UUID."},
            },
            "required": ["dashboard_id", "user_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/dashboards/{dashboard_id}/users/{user_uid}",
            path_fields=("dashboard_id", "user_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-users remove --dashboard-id <dashboard_uuid> --user-uid <user_uuid>",
                description="Remove explicit dashboard access.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "The dashboard owner cannot be removed."),
    ),
    make_tool(
        canonical_name="dashboard-widgets.list",
        mcp_alias="kaiten_list_dashboard_widgets",
        description="List dashboard widgets through dashboards.get?include=widgets.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                **_shaping_properties(),
            },
            "required": ["dashboard_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/dashboards/{dashboard_id}",
            path_fields=("dashboard_id",),
        ),
        response_policy=SHAPED_LIST,
        runtime_behavior=RuntimeBehavior(
            execution_mode="synthetic", custom_executor=execute_dashboard_widgets_list
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-widgets list --dashboard-id <dashboard_uuid> --fields id,title,source,visualization",
                description="Extract widgets from a dashboard read.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING,),
    ),
    make_tool(
        canonical_name="dashboard-widgets.create",
        mcp_alias="kaiten_create_dashboard_widget",
        description="Create a widget without freezing the evolving source/config schema client-side.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "title": {"type": "string", "description": "Widget title."},
                "source": {
                    "type": "string",
                    "description": "Widget source; current examples include metric, cardList, distribution, cardsTrend.",
                },
                "visualization": {
                    "type": "string",
                    "description": "Visualization identifier accepted by the current Kaiten installation.",
                },
                "config": {"type": "object", "description": "Source-specific widget config JSON."},
            },
            "required": ["dashboard_id", "title", "source", "visualization", "config"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/dashboards/{dashboard_id}/widgets",
            path_fields=("dashboard_id",),
            body_fields=("title", "source", "visualization", "config"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json dashboard-widgets create --dashboard-id <dashboard_uuid> --title "Cards" --source cardList --visualization table --config \'{"filter":{}}\'',
                description="Create a card-list widget using server-validated config.",
            ),
        ),
        usage_notes=(
            DASHBOARD_WARNING,
            "Source, visualization and config are validated by Kaiten because their schema changes quickly.",
            DASHBOARD_WIDGET_SCHEMA_NOTE,
        ),
    ),
    make_tool(
        canonical_name="dashboard-widgets.update",
        mcp_alias="kaiten_update_dashboard_widget",
        description="Update a dashboard widget; config is merged by the server.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "widget_id": {"type": "string", "description": "Widget UUID."},
                "title": {"type": "string", "description": "Widget title."},
                "source": {"type": "string", "description": "Widget source."},
                "visualization": {"type": "string", "description": "Visualization identifier."},
                "config": {"type": "object", "description": "Partial config merged by Kaiten."},
            },
            "required": ["dashboard_id", "widget_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/dashboards/{dashboard_id}/widgets/{widget_id}",
            path_fields=("dashboard_id", "widget_id"),
            body_fields=("title", "source", "visualization", "config"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json dashboard-widgets update --dashboard-id <dashboard_uuid> --widget-id <widget_uuid> --title "Open cards"',
                description="Rename a widget.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, DASHBOARD_WIDGET_SCHEMA_NOTE),
    ),
    make_tool(
        canonical_name="dashboard-widgets.delete",
        mcp_alias="kaiten_delete_dashboard_widget",
        description="Delete a dashboard widget.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "widget_id": {"type": "string", "description": "Widget UUID."},
            },
            "required": ["dashboard_id", "widget_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/dashboards/{dashboard_id}/widgets/{widget_id}",
            path_fields=("dashboard_id", "widget_id"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-widgets delete --dashboard-id <dashboard_uuid> --widget-id <widget_uuid>",
                description="Delete a widget.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING,),
    ),
    make_tool(
        canonical_name="dashboard-compute-jobs.create",
        mcp_alias="kaiten_create_dashboard_compute_job",
        description="Queue computation for up to 100 widgets on an accessible dashboard.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "widget_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "JSON array containing 1 to 100 widget UUIDs.",
                },
                "force": {"type": "boolean", "description": "Force recomputation."},
            },
            "required": ["dashboard_id", "widget_ids"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/dashboards/{dashboard_id}/compute-jobs",
            path_fields=("dashboard_id",),
            body_fields=("widget_ids", "force"),
        ),
        runtime_behavior=RuntimeBehavior(payload_validator=validate_dashboard_compute_payload),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-compute-jobs create --dashboard-id <dashboard_uuid> --widget-ids '[\"<widget_uuid>\"]'",
                description="Queue widget computation and receive a compute_job_id.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "A successful queue operation returns HTTP 202."),
    ),
    make_tool(
        canonical_name="dashboard-compute-jobs.get",
        mcp_alias="kaiten_get_dashboard_compute_job",
        description="Poll a dashboard compute job without reusing cached status.",
        input_schema={
            "type": "object",
            "properties": {
                "dashboard_id": {"type": "string", "description": "Dashboard UUID."},
                "job_id": {
                    "type": ["string", "integer"],
                    "description": "Compute job ID returned by create.",
                },
                **_shaping_properties(),
            },
            "required": ["dashboard_id", "job_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/dashboards/{dashboard_id}/compute-jobs/{job_id}",
            path_fields=("dashboard_id", "job_id"),
        ),
        response_policy=SHAPED_ENTITY,
        runtime_behavior=RuntimeBehavior(cache_policy=CACHE_POLICY_NONE),
        examples=(
            ExampleSpec(
                command="kaiten --json dashboard-compute-jobs get --dashboard-id <dashboard_uuid> --job-id 123",
                description="Poll queued/running/completed/failed status.",
            ),
        ),
        usage_notes=(DASHBOARD_WARNING, "Polling bypasses both request and persistent cache."),
    ),
)
