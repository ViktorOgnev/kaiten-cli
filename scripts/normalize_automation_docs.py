"""Convert reviewed portal modal tables to compatible, inspectable registry schemas."""

from __future__ import annotations
import copy
import json
from pathlib import Path
import re
from audit_public_api import schema_type

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src/kaiten_cli/registry/automation_schemas.json"


def table_schema(table: dict) -> dict:
    table = table.get("schema", table)
    columns = table.get("columns", [])
    if not columns or columns[0] != "Field name":
        return {"x-documentation-table": table}
    properties = {}
    patterns = {}
    required = []
    for row in table.get("data", []):
        row_columns = columns
        if (
            columns == ["Field name", "Type", "Required", "Description"]
            and len(row["entries"]) == 5
        ):
            # Several date tables omit the Constraints header but contain five cells.
            row_columns = ["Field name", "Type", "Constraints", "Required", "Description"]
        entries = row["entries"]
        if len(columns) == 5 and len(entries) == 4:
            row_columns = ["Field name", "Type", "Required", "Description"]
        if (
            len(columns) == 5
            and len(entries) == 6
            and row["key"] == "hasToFireOnCardCreation"
            and entries[3] == ""
        ):
            entries = entries[:3] + entries[4:]
        if len(row_columns) != len(entries):
            raise ValueError(f"Unrecognized automation table row: {row['key']}")
        values = dict(zip(row_columns, entries))
        name = row["key"]  # userIds has a typo in the visible Field name cell.
        schema = schema_type(values.get("Type", ""))
        if name == "type":
            schema["type"] = "string"
        description = values.get("Description", "")
        if description:
            schema["description"] = description
        constraints = values.get("Constraints", values.get("Constraint", ""))
        if constraints:
            schema["x-documentation-constraints"] = constraints
        # Numeric limits with unambiguous syntax only; conditional prose stays evidence.
        if isinstance(constraints, str):
            for keyword, value in re.findall(
                r"\b(minItems|maxItems|minLength|maxLength):\s*(\d+)", constraints
            ):
                schema[keyword] = int(value)
        enum = (
            values.get("Type")
            if isinstance(values.get("Type"), list)
            else constraints
            if values.get("Type") == "enum" and isinstance(constraints, list)
            else None
        )
        if enum:
            schema["enum"] = enum
            kinds = list(
                dict.fromkeys(
                    "boolean"
                    if isinstance(v, bool)
                    else "integer"
                    if isinstance(v, int)
                    else "number"
                    if isinstance(v, float)
                    else "string"
                    for v in enum
                )
            )
            schema["type"] = kinds[0] if len(kinds) == 1 else kinds
        elif values.get("Type") == "enum":
            schema["type"] = "string"
        nested = table.get("objectProperties", {}).get(name)
        if nested:
            converted = table_schema(nested)
            if schema.get("type") == "array":
                schema["items"] = converted
            else:
                declared_type = schema.get("type")
                schema.update(converted)
                if declared_type is not None:
                    schema["type"] = declared_type
        schema["x-documentation-required"] = values.get("Required", "no")
        if name in ("{uuid}", "{custom_property_id}"):
            pattern = r"^[0-9a-fA-F-]{36}$" if name == "{uuid}" else r"^customProperty_[0-9]+$"
            patterns[pattern] = schema
        else:
            if values.get("Required") == "yes" and name not in (
                "created",
                "hasToFireOnCardCreation",
            ):
                required.append(name)
            properties[name] = schema
    result = {"type": "object", "properties": properties, "required": required}
    if patterns:
        result["patternProperties"] = patterns
    return result


def normalize(tables: dict) -> dict:
    result = {"actions": {}, "conditions": {}, "triggers": {}, "create": {}, "update": {}}
    for family in ("actions", "conditions"):
        for entry in tables[family]:
            schema = table_schema(entry["attributes"])
            schema["description"] = entry.get("description", entry["name"])
            result[family][entry["type"]] = schema
    for entry in tables["triggers"]:
        schema = table_schema(entry["attributes"])
        if entry["automationType"] == "on_date":
            fields = schema["properties"]["data"]["properties"]
            # Modal tables use offset_units, while the official request example
            # uses offset_unit. Describe and preserve both without rewriting either.
            fields["offset_unit"] = copy.deepcopy(fields["offset_units"])
            fields["offset_unit"]["description"] = (
                "Unit spelling used by the official date automation request example."
            )
        schema["x-automation-type"] = entry["automationType"]
        schema["x-allowed-actions"] = entry["actions"]
        schema["x-allowed-conditions"] = entry["conditions"]
        if entry["type"] not in result["triggers"]:
            result["triggers"][entry["type"]] = schema
        else:
            result["triggers"][entry["type"]]["x-documentation-alternatives"] = [schema]
    for method in ("create", "update"):
        for kind, table in zip(("on_action", "on_date", "on_demand"), tables[method]):
            result[method][kind] = table_schema(table)
    return result


def write():
    tables = json.loads((ROOT / "docs/public-api/automation-tables.json").read_text())
    OUTPUT.write_text(
        json.dumps(normalize(copy.deepcopy(tables)), ensure_ascii=False, indent=2) + "\n"
    )


if __name__ == "__main__":
    write()
