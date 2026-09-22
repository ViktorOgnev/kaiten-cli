"""Input merging and schema coercion."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.models import UNSET, ToolSpec


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
        raise ValidationError(
            tr("Invalid JSON for {value_0}: {value_1}", value_0=label, value_1=exc.msg)
        ) from exc


def _coerce_nullable_string(raw: str) -> str | None:
    if raw == "null":
        return None
    return raw


def coerce_value(
    raw: Any, schema: dict[str, Any], *, stdin_text: str | None = None, label: str
) -> Any:
    if raw is UNSET:
        return UNSET

    schema_type = schema.get("type")
    type_list = schema_type if isinstance(schema_type, list) else [schema_type]
    if raw is None:
        return None
    if "null" in type_list and isinstance(raw, str):
        raw = _coerce_nullable_string(raw)
        if raw is None:
            return None
    if "oneOf" in schema:
        # Preserve already typed values before attempting CLI string coercion.
        for variant in schema["oneOf"]:
            try:
                _validate_schema(raw, variant, path=label)
            except ValidationError:
                continue
            return raw
        for variant in schema["oneOf"]:
            try:
                candidate = coerce_value(raw, variant, stdin_text=stdin_text, label=label)
                _validate_schema(candidate, variant, path=label)
            except ValidationError:
                continue
            return candidate
        return raw  # Full validation reports the field and failed union.
    if "array" in type_list or "object" in type_list:
        if not isinstance(raw, str):
            return raw
        if "string" in type_list and raw != "-" and not raw.startswith("@"):
            # Plain strings remain valid in a union. Explicit JSON structures
            # and sources still fail loudly on malformed JSON.
            if not raw.lstrip().startswith(("[", "{", '"')):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    return raw
                return parsed if any(_type_matches(parsed, kind) for kind in type_list) else raw
        return _json_value(raw, stdin_text, label)
    if isinstance(raw, str) and "string" not in type_list:
        if "integer" in type_list:
            try:
                return int(raw)
            except ValueError as exc:
                if "number" not in type_list:
                    raise ValidationError(
                        tr("Field {value_0} must be an integer or null.", value_0=label)
                    ) from exc
        if "number" in type_list:
            try:
                return float(raw)
            except ValueError as exc:
                raise ValidationError(
                    tr("Field {value_0} must be a number or null.", value_0=label)
                ) from exc
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
        raise ValidationError(tr("Use either --stdin-json or --from-file, not both."))

    base_payload: dict[str, Any] = {}
    if from_file:
        payload = _json_value(f"@{from_file}", stdin_text, "--from-file")
        if not isinstance(payload, dict):
            raise ValidationError(tr("--from-file must contain a JSON object."))
        base_payload = payload
    elif stdin_json:
        payload = _json_value("-", stdin_text, "--stdin-json")
        if not isinstance(payload, dict):
            raise ValidationError(tr("--stdin-json must read a JSON object."))
        base_payload = payload

    properties = tool.input_schema.get("properties", {})
    unknown = set(base_payload) - set(properties)
    if unknown:
        raise ValidationError(
            tr("Unknown input field(s): {value_0}", value_0=", ".join(sorted(unknown)))
        )

    merged = dict(base_payload)
    for field_name, raw_value in option_values.items():
        if raw_value is UNSET:
            continue
        if raw_value is None:
            continue
        if field_name not in properties:
            continue
        schema = properties[field_name]
        merged[field_name] = coerce_value(
            raw_value, schema, stdin_text=stdin_text, label=field_name
        )

    validate_payload(tool, merged)
    if tool.runtime_behavior.payload_validator is not None:
        tool.runtime_behavior.payload_validator(tool, merged)
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


def _format_path(path: str) -> str:
    return path or "payload"


def _enum_contains(enum_values: list[Any], value: Any) -> bool:
    """Compare enum values without treating booleans as the integers 0 and 1."""
    for candidate in enum_values:
        if isinstance(candidate, bool) != isinstance(value, bool):
            continue
        if candidate == value:
            return True
    return False


def _validate_schema(value: Any, schema: dict[str, Any], *, path: str) -> None:
    if "oneOf" in schema:
        matches = 0
        for variant in schema["oneOf"]:
            try:
                _validate_schema(value, variant, path=path)
            except ValidationError:
                continue
            matches += 1
        if matches != 1:
            raise ValidationError(
                tr(
                    "Field {value_0} must match exactly one schema in oneOf.",
                    value_0=_format_path(path),
                )
            )
    schema_type = schema.get("type")
    if schema_type is not None:
        allowed_types = schema_type if isinstance(schema_type, list) else [schema_type]
        if not any(_type_matches(value, expected) for expected in allowed_types):
            expected = tr(" or ").join(str(item) for item in allowed_types)
            raise ValidationError(
                tr(
                    "Field {value_0} has invalid type; expected {value_1}.",
                    value_0=_format_path(path),
                    value_1=expected,
                )
            )

    enum_values = schema.get("enum")
    # Registry schemas use nullable types with a non-null enum as shorthand for
    # "one of these values, or null". Preserve that established convention.
    if enum_values is not None and value is not None and not _enum_contains(enum_values, value):
        allowed = ", ".join(map(str, enum_values))
        raise ValidationError(
            tr(
                "Field {value_0} must be one of: {value_1}",
                value_0=_format_path(path),
                value_1=allowed,
            )
        )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and value < minimum:
            raise ValidationError(
                tr(
                    "Field {value_0} must be greater than or equal to {value_1}.",
                    value_0=_format_path(path),
                    value_1=minimum,
                )
            )
        if maximum is not None and value > maximum:
            raise ValidationError(
                tr(
                    "Field {value_0} must be less than or equal to {value_1}.",
                    value_0=_format_path(path),
                    value_1=maximum,
                )
            )

    if isinstance(value, (str, list)):
        limits = ("minLength", "maxLength") if isinstance(value, str) else ("minItems", "maxItems")
        for keyword, compare in (
            (limits[0], lambda n, bound: n < bound),
            (limits[1], lambda n, bound: n > bound),
        ):
            bound = schema.get(keyword)
            if bound is not None and compare(len(value), bound):
                raise ValidationError(
                    tr(
                        "Field {value_0} violates {value_1}: {value_2}.",
                        value_0=_format_path(path),
                        value_1=keyword,
                        value_2=bound,
                    )
                )

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        missing = [field for field in required if field not in value]
        if missing:
            location = tr(" at {path}", path=_format_path(path)) if path else ""
            raise ValidationError(
                tr(
                    "Missing required field(s){value_0}: {value_1}",
                    value_0=location,
                    value_1=", ".join(sorted(missing)),
                )
            )

        pattern_matched = set()
        for pattern, pattern_schema in schema.get("patternProperties", {}).items():
            for field_name, field_value in value.items():
                if re.search(pattern, field_name):
                    pattern_matched.add(field_name)
                    field_path = f"{path}.{field_name}" if path else field_name
                    _validate_schema(field_value, pattern_schema, path=field_path)
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(properties) - pattern_matched
            if unknown:
                raise ValidationError(
                    tr(
                        "Unknown field(s) at {value_0}: {value_1}",
                        value_0=_format_path(path),
                        value_1=", ".join(sorted(unknown)),
                    )
                )

        for field_name, field_schema in properties.items():
            if field_name not in value:
                continue
            field_path = f"{path}.{field_name}" if path else field_name
            _validate_schema(value[field_name], field_schema, path=field_path)

    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        item_schema = schema["items"]
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]" if path else f"[{index}]"
            _validate_schema(item, item_schema, path=item_path)


def validate_payload(tool: ToolSpec, payload: dict[str, Any]) -> None:
    _validate_schema(payload, tool.input_schema, path="")
