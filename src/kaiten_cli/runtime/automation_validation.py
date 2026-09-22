"""Validate known automation variants while preserving server extensions."""

from __future__ import annotations

from kaiten_cli.errors import ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.input import _validate_schema


def validate_automation(tool, payload):
    # Lazy import avoids registry -> runtime -> registry initialization cycles.
    from kaiten_cli.registry.automation_schema import AUTOMATION_SCHEMAS

    creating = tool.action == "create"
    kind = payload.get("type")
    if creating:
        required = ["actions"]
        if kind in ("on_action", "on_date") or kind is None:
            required.append("trigger")
        if kind == "on_demand" or kind is None:
            required.append("name")
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValidationError(
                tr("Missing required field(s): {fields}", fields=", ".join(missing))
            )

    def validate_variant(value, family, path, partial=False):
        _validate_schema(value, {"type": "object"}, path=path)
        if "type" not in value:
            if partial:
                return
            raise ValidationError(tr("Missing required field(s) at {value_0}: type", value_0=path))
        _validate_schema(value["type"], {"type": "string"}, path=f"{path}.type")
        schema = AUTOMATION_SCHEMAS[family].get(value["type"])
        if schema is None:
            return  # Unknown variants are intentional extension points.
        if partial:
            schema = {**schema, "required": []}
        _validate_schema(value, schema, path=path)

    trigger = payload.get("trigger")
    if trigger is not None:
        validate_variant(trigger, "triggers", "trigger", partial=not creating)
        known = AUTOMATION_SCHEMAS["triggers"].get(trigger.get("type"))
        if creating and known and kind in ("on_action", "on_date"):
            if known["x-automation-type"] != kind:
                raise ValidationError(
                    tr(
                        "Field trigger.type is incompatible with automation type {value_0}.",
                        value_0=kind,
                    )
                )
        if known and known["x-automation-type"] == "on_date":
            data = trigger.get("data", {})
            if data.get("variant") in ("time_left_before_date", "time_passed_after_date"):
                if "offset" not in data:
                    raise ValidationError(tr("Missing required field(s) at trigger.data: offset"))
                if not any(key in data for key in ("offset_unit", "offset_units")):
                    raise ValidationError(
                        tr("Missing required field(s) at trigger.data: offset_unit or offset_units")
                    )
    else:
        known = None
    for index, action in enumerate(payload.get("actions", [])):
        path = f"actions[{index}]"
        validate_variant(action, "actions", path)
        if known and action["type"] in AUTOMATION_SCHEMAS["actions"]:
            if action["type"] not in known["x-allowed-actions"]:
                raise ValidationError(
                    tr(
                        "Field {value_0}.type is not allowed for trigger {value_1}.",
                        value_0=path,
                        value_1=trigger["type"],
                    )
                )

    def conditions(value, path, depth=0):
        if depth > 64:
            raise ValidationError(
                tr("Field {value_0} exceeds maximum condition nesting depth (64).", value_0=path)
            )
        _validate_schema(value, {"type": "object"}, path=path)
        if not value:
            return
        if "conditions" in value or "clause" in value:
            _validate_schema(
                value,
                {
                    "type": "object",
                    "properties": {
                        "clause": {"type": "string", "enum": ["and", "or"]},
                        "conditions": {"type": "array", "items": {"type": "object"}},
                        "created": {"type": "string"},
                    },
                    "required": ["clause", "conditions"],
                },
                path=path,
            )
            for i, child in enumerate(value["conditions"]):
                conditions(child, f"{path}.conditions[{i}]", depth + 1)
        else:
            validate_variant(value, "conditions", path)
            if known and value["type"] in AUTOMATION_SCHEMAS["conditions"]:
                if value["type"] not in known["x-allowed-conditions"]:
                    raise ValidationError(
                        tr(
                            "Field {value_0}.type is not allowed for trigger {value_1}.",
                            value_0=path,
                            value_1=trigger["type"],
                        )
                    )

    if "conditions" in payload:
        conditions(payload["conditions"], "conditions")
