"""Dashboard-specific runtime helpers."""

from __future__ import annotations

from typing import Any

from kaiten_cli.errors import ValidationError


def validate_dashboard_compute_payload(tool, payload: dict[str, Any]) -> None:
    widget_ids = payload.get("widget_ids")
    if not isinstance(widget_ids, list) or not widget_ids:
        raise ValidationError("Field widget_ids must be a non-empty array.")
    if len(widget_ids) > 100:
        raise ValidationError("Field widget_ids must contain at most 100 items.")


async def execute_dashboard_widgets_list(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> Any:
    if reporter:
        reporter("execution: synthetic widget list from dashboards.get?include=widgets")
    dashboard = await client.get(path, params={"include": "widgets"}, timeout=timeout)
    if not isinstance(dashboard, dict):
        return dashboard
    widgets = dashboard.get("widgets")
    return widgets if isinstance(widgets, list) else []
