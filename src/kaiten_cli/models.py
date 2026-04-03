"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


class _Unset:
    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "UNSET"


UNSET = _Unset()


@dataclass(slots=True, frozen=True)
class ExampleSpec:
    command: str
    description: str


@dataclass(slots=True, frozen=True)
class OperationSpec:
    method: str
    path_template: str
    path_fields: tuple[str, ...] = ()
    query_fields: tuple[str, ...] = ()
    body_fields: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class ResponsePolicy:
    compact_supported: bool = False
    fields_supported: bool = False
    default_limit: int | None = None
    heavy: bool = False
    result_kind: str = "entity"


@dataclass(slots=True, frozen=True)
class ToolSpec:
    canonical_name: str
    mcp_alias: str
    namespace: str
    action: str
    description: str
    input_schema: dict[str, Any]
    operation: OperationSpec
    response_policy: ResponsePolicy = field(default_factory=ResponsePolicy)
    examples: tuple[ExampleSpec, ...] = ()


@dataclass(slots=True)
class GlobalOptions:
    json_mode: bool = False
    profile_name: str | None = None
    from_file: str | None = None
    stdin_json: bool = False
    verbose: bool = False
    no_color: bool = False


@dataclass(slots=True)
class ResolvedProfile:
    name: str | None
    domain: str
    token: str
    sandbox: bool = False


def format_schema_type(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type", "unknown")
    if isinstance(schema_type, list):
        return "|".join(str(item) for item in schema_type)
    return str(schema_type)


def example_commands(examples: Sequence[ExampleSpec]) -> list[str]:
    return [example.command for example in examples]

