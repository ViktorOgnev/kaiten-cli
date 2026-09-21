"""Shared nested schema traversal for terminal and generated documentation."""

from __future__ import annotations


def schema_rows(schema, path="", required=False):
    if path:
        yield path, schema, required
    for name, child in schema.get("properties", {}).items():
        yield from schema_rows(
            child, f"{path}.{name}" if path else name, name in schema.get("required", [])
        )
    if isinstance(schema.get("items"), dict):
        child = schema["items"]
        if child.get("properties") or child.get("x-variants"):
            yield from schema_rows(child, path + "[]")
    for pattern, child in schema.get("patternProperties", {}).items():
        yield from schema_rows(child, f"{path}[key matching {pattern}]")
    for variant, child in schema.get("x-variants", {}).items():
        yield from schema_rows(child, f"{path}<{variant}>")
    for index, child in enumerate(schema.get("oneOf", [])):
        yield from schema_rows(child, f"{path}<oneOf[{index}]>")
