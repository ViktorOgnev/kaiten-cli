"""Input merging and schema coercion."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.models import ToolSpec, UNSET


def _read_text_source(source: str, stdin_text: str | None) -> str:
    if source == "-":
        if stdin_text is not None:
            return stdin_text
        return sys.stdin.read()
    if source.startswith("@"):
        return Path(source[1:]).read_text(encoding="utf-8")
    return source


def _json_value(source: str, stdin_text: str | None, label: str) -> Any:
    text = _read_text_source(source, stdin_text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for {label}: {exc.msg}") from exc


def _coerce_nullable_string(raw: str) -> str | None:
    if raw == "null":
        return None
    return raw


def coerce_value(raw: Any, schema: dict[str, Any], *, stdin_text: str | None = None, label: str) -> Any:
    if raw is UNSET:
        return UNSET

    schema_type = schema.get("type")
    type_list = schema_type if isinstance(schema_type, list) else [schema_type]
    if raw is None:
        return None
    if "array" in type_list or "object" in type_list:
        if not isinstance(raw, str):
            return raw
        return _json_value(raw, stdin_text, label)
    if "null" in type_list and isinstance(raw, str):
        raw = _coerce_nullable_string(raw)
        if raw is None:
            return None
    if isinstance(raw, str) and "string" not in type_list:
        if "integer" in type_list:
            try:
                return int(raw)
            except ValueError as exc:
                raise ValidationError(f"Field {label} must be an integer or null.") from exc
        if "number" in type_list:
            try:
                return float(raw)
            except ValueError as exc:
                raise ValidationError(f"Field {label} must be a number or null.") from exc
    return raw


def merge_inputs(
    tool: ToolSpec,
    option_values: dict[str, Any],
    *,
    from_file: str | None = None,
    stdin_json: bool = False,
    stdin_text: str | None = None,
) -> dict[str, Any]:
    if stdin_json and from_file:
        raise ValidationError("Use either --stdin-json or --from-file, not both.")

    base_payload: dict[str, Any] = {}
    if from_file:
        payload = _json_value(f"@{from_file}", stdin_text, "--from-file")
        if not isinstance(payload, dict):
            raise ValidationError("--from-file must contain a JSON object.")
        base_payload = payload
    elif stdin_json:
        payload = _json_value("-", stdin_text, "--stdin-json")
        if not isinstance(payload, dict):
            raise ValidationError("--stdin-json must read a JSON object.")
        base_payload = payload

    properties = tool.input_schema.get("properties", {})
    unknown = set(base_payload) - set(properties)
    if unknown:
        raise ValidationError(f"Unknown input field(s): {', '.join(sorted(unknown))}")

    merged = dict(base_payload)
    for field_name, raw_value in option_values.items():
        if raw_value is UNSET:
            continue
        if raw_value is None:
            continue
        if field_name not in properties:
            continue
        schema = properties[field_name]
        schema_type = schema.get("type")
        allowed_types = schema_type if isinstance(schema_type, list) else [schema_type]
        merged[field_name] = coerce_value(raw_value, schema, stdin_text=stdin_text, label=field_name)

    validate_payload(tool, merged)
    return merged


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "null":
        return value is None
    return True


def validate_payload(tool: ToolSpec, payload: dict[str, Any]) -> None:
    properties = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(sorted(missing))}")

    unknown = set(payload) - set(properties)
    if unknown:
        raise ValidationError(f"Unknown input field(s): {', '.join(sorted(unknown))}")

    for field_name, value in payload.items():
        schema = properties[field_name]
        schema_type = schema.get("type")
        allowed_types = schema_type if isinstance(schema_type, list) else [schema_type]
        if not any(_type_matches(value, expected) for expected in allowed_types):
            raise ValidationError(f"Field {field_name} has invalid type.")
        enum_values = schema.get("enum")
        if enum_values and value is not None and value not in enum_values:
            raise ValidationError(f"Field {field_name} must be one of: {', '.join(map(str, enum_values))}")
