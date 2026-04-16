"""Shared data models."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any


class _Unset:
    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "UNSET"


UNSET = _Unset()

CACHE_POLICY_NONE = "none"
CACHE_POLICY_REQUEST_SCOPE = "request_scope"
CACHE_POLICY_PERSISTENT_OPT_IN = "persistent_opt_in"

CACHE_MODE_OFF = "off"
CACHE_MODE_READWRITE = "readwrite"
CACHE_MODE_REFRESH = "refresh"

PERSISTENT_CACHE_DISCOVERY_ALLOWLIST = frozenset(
    {
        "spaces.list",
        "boards.list",
        "columns.list",
        "lanes.list",
        "card-types.list",
    }
)


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


DebugReporter = Callable[[str], None]
RequestShape = tuple[str, dict[str, Any] | None, dict[str, Any] | None]
RequestShaper = Callable[
    ["ToolSpec", dict[str, Any], str, dict[str, Any] | None, dict[str, Any] | None],
    RequestShape,
]
PayloadValidator = Callable[["ToolSpec", dict[str, Any]], None]
CustomExecutor = Callable[
    [Any, "ToolSpec", dict[str, Any], str, dict[str, Any] | None, dict[str, Any] | None, float, DebugReporter | None],
    Awaitable[Any],
]


@dataclass(slots=True, frozen=True)
class RuntimeBehavior:
    execution_mode: str = "direct_http"
    request_shaper: RequestShaper | None = None
    payload_validator: PayloadValidator | None = None
    custom_executor: CustomExecutor | None = None
    compact_default: bool | None = None
    cache_policy: str | None = None


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
    runtime_behavior: RuntimeBehavior = field(default_factory=RuntimeBehavior)
    examples: tuple[ExampleSpec, ...] = ()
    usage_notes: tuple[str, ...] = ()
    bulk_alternative: str | None = None

    @property
    def namespace_segments(self) -> tuple[str, ...]:
        if not self.namespace:
            return ()
        return tuple(segment for segment in self.namespace.split(".") if segment)

    @property
    def command_segments(self) -> tuple[str, ...]:
        return self.namespace_segments + (self.action,)

    @property
    def execution_mode(self) -> str:
        return self.runtime_behavior.execution_mode

    @property
    def cache_policy(self) -> str:
        if self.is_mutation:
            return CACHE_POLICY_NONE
        if self.runtime_behavior.cache_policy is not None:
            return self.runtime_behavior.cache_policy
        if (
            self.operation.method.upper() == "GET"
            and self.execution_mode == "direct_http"
            and self.response_policy.result_kind == "entity"
            and self.action == "get"
        ):
            return CACHE_POLICY_PERSISTENT_OPT_IN
        if self.canonical_name in PERSISTENT_CACHE_DISCOVERY_ALLOWLIST:
            return CACHE_POLICY_PERSISTENT_OPT_IN
        if self.operation.method.upper() == "GET":
            return CACHE_POLICY_REQUEST_SCOPE
        return CACHE_POLICY_NONE

    @property
    def is_mutation(self) -> bool:
        return self.operation.method.upper() in {"POST", "PATCH", "DELETE"}


@dataclass(slots=True)
class GlobalOptions:
    json_mode: bool = False
    profile_name: str | None = None
    from_file: str | None = None
    stdin_json: bool = False
    verbose: bool = False
    no_color: bool = False
    cache_mode: str | None = None
    cache_ttl_seconds: int | None = None


@dataclass(slots=True)
class ResolvedProfile:
    name: str | None
    domain: str
    token: str
    sandbox: bool = False
    source: str = "unknown"
    cache_mode: str = CACHE_MODE_OFF
    cache_ttl_seconds: int = 60


def format_schema_type(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type", "unknown")
    if isinstance(schema_type, list):
        return "|".join(str(item) for item in schema_type)
    return str(schema_type)


def example_commands(examples: Sequence[ExampleSpec]) -> list[str]:
    return [example.command for example in examples]
