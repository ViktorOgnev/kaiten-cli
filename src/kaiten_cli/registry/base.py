"""Registry helpers."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior, ToolSpec


def shaping_properties() -> dict[str, dict]:
    """Schema for the two local response-shaping options a list read can expose."""

    return {
        "compact": {
            "type": "boolean",
            "description": "Return compact output without heavy nested fields.",
        },
        "fields": {
            "type": "string",
            "description": "Comma-separated field names to return.",
        },
    }


# A list read that accepts both shaping options above.
SHAPED_LIST_POLICY = ResponsePolicy(
    compact_supported=True, fields_supported=True, result_kind="list"
)
# A single small envelope: no shaping options, so none are advertised.
PLAIN_ENTITY_POLICY = ResponsePolicy(result_kind="entity")


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
