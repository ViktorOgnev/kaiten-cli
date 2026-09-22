"""Rendering helpers."""

from __future__ import annotations

import json
from typing import Any

from kaiten_cli.errors import CliError
from kaiten_cli.i18n import tr


def render_success(
    command: str, data: Any, json_mode: bool, stats: dict[str, Any] | None = None
) -> str:
    if json_mode:
        payload = {"success": True, "command": command, "data": data}
        if stats is not None:
            payload["stats"] = stats
        return json.dumps(payload, ensure_ascii=False, default=str)
    if data is None:
        return tr("OK")
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def render_error(
    command: str | None,
    error: CliError,
    json_mode: bool,
    stats: dict[str, Any] | None = None,
) -> str:
    if json_mode:
        payload = {"success": False, "command": command, "error": error.to_dict()}
        if stats is not None:
            payload["stats"] = stats
        return json.dumps(payload, ensure_ascii=False, default=str)
    prefix = tr(error.error_type.replace("_", " ").capitalize())
    if hasattr(error, "status_code"):
        headline = tr(
            "{value_0} {value_1}: {value_2}",
            value_0=prefix,
            value_1=getattr(error, "status_code"),
            value_2=error.message,
        )
    else:
        headline = tr("{value_0}: {value_1}", value_0=prefix, value_1=error.message)
    if not error.details:
        return headline
    lines = [headline]
    if suggested_usage := error.details.get("suggested_usage"):
        lines.append(tr("Suggested usage: {value_0}", value_0=suggested_usage))
    if supported_options := error.details.get("supported_options"):
        lines.append(tr("Supported options: {value_0}", value_0=", ".join(supported_options)))
    if bulk_alternative := error.details.get("bulk_alternative"):
        lines.append(tr("Bulk alternative: {value_0}", value_0=bulk_alternative))
    if next_step := error.details.get("next"):
        lines.append(tr("Next: {value_0}", value_0=next_step))
    return "\n".join(lines)
