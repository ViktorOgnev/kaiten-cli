"""Rendering helpers."""

from __future__ import annotations

import json
from typing import Any

from kaiten_cli.errors import CliError


def _default_json(value: Any) -> Any:
    return value


def render_success(command: str, data: Any, json_mode: bool) -> str:
    if json_mode:
        return json.dumps({"success": True, "command": command, "data": data}, ensure_ascii=False, default=str)
    if data is None:
        return "OK"
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def render_error(command: str | None, error: CliError, json_mode: bool) -> str:
    if json_mode:
        payload = {"success": False, "command": command, "error": error.to_dict()}
        return json.dumps(payload, ensure_ascii=False, default=str)
    prefix = error.error_type.replace("_", " ").capitalize()
    if hasattr(error, "status_code"):
        return f"{prefix} {getattr(error, 'status_code')}: {error.message}"
    return f"{prefix}: {error.message}"

