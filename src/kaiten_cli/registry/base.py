"""Registry helpers."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior, ToolSpec


def make_tool(
    *,
    canonical_name: str,
    mcp_alias: str,
    description: str,
    input_schema: dict,
    operation: OperationSpec,
    response_policy: ResponsePolicy | None = None,
    runtime_behavior: RuntimeBehavior | None = None,
    examples: tuple[ExampleSpec, ...] = (),
    usage_notes: tuple[str, ...] = (),
    bulk_alternative: str | None = None,
) -> ToolSpec:
    *namespace_segments, action = canonical_name.split(".")
    return ToolSpec(
        canonical_name=canonical_name,
        mcp_alias=mcp_alias,
        namespace=".".join(namespace_segments),
        action=action,
        description=description,
        input_schema=input_schema,
        operation=operation,
        response_policy=response_policy or ResponsePolicy(),
        runtime_behavior=runtime_behavior or RuntimeBehavior(),
        examples=examples,
        usage_notes=usage_notes,
        bulk_alternative=bulk_alternative,
    )
