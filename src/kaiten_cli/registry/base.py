"""Registry helpers."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, ToolSpec


def make_tool(
    *,
    canonical_name: str,
    mcp_alias: str,
    description: str,
    input_schema: dict,
    operation: OperationSpec,
    response_policy: ResponsePolicy | None = None,
    examples: tuple[ExampleSpec, ...] = (),
) -> ToolSpec:
    namespace, action = canonical_name.split(".", 1)
    return ToolSpec(
        canonical_name=canonical_name,
        mcp_alias=mcp_alias,
        namespace=namespace,
        action=action,
        description=description,
        input_schema=input_schema,
        operation=operation,
        response_policy=response_policy or ResponsePolicy(),
        examples=examples,
    )

