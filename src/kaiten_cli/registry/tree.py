"""Tree navigation tool specs."""

from __future__ import annotations

from kaiten_cli.models import (
    CACHE_POLICY_REQUEST_SCOPE,
    ExampleSpec,
    OperationSpec,
    ResponsePolicy,
    RuntimeBehavior,
)
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import execute_tree_children_list, execute_tree_get
from kaiten_cli.runtime.support.tree_sharing import (
    execute_tree_entity_share_batch_enable,
    execute_tree_entity_share_batch_get,
    execute_tree_entity_share_disable,
    execute_tree_entity_share_enable,
    execute_tree_entity_share_get,
    execute_tree_entity_share_update,
    validate_tree_entity_share_batch_payload,
    validate_tree_entity_share_payload,
)

TREE_CATALOG_USAGE_NOTES = (
    "This aggregated command builds its local catalog from `/spaces`, `/documents`, and `/document-groups`.",
    "Here `catalog` means an internal fetched entity index for tree assembly, not UI catalog tables (`custom-directories`) and not `custom-properties catalog-values`.",
    "Use `document-groups.*` to create, update, or delete document folder containers; tree commands are read-only aggregate views.",
    "`/spaces` is read once; `/documents` and `/document-groups` are paginated internally with `limit=500` and `offset=0,500,...` until a short page is returned.",
    "No pagination options are required or accepted for this command; callers control only `parent_entity_uid` for children listing or `root_uid`/`depth` for nested tree output.",
    "If the internal pagination safety cap is reached with full pages, the command fails instead of returning a silently truncated tree.",
    "Visible entities whose `parent_entity_uid` is missing or inaccessible in the fetched catalog are promoted to root-level output.",
)

TREE_ENTITY_SHARE_USAGE_NOTES = (
    "The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.",
    "GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.",
    "Supported tree entity types are spaces, documents, document groups, and story maps.",
    "This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.",
)

ENTITY_UID_PROPERTY = {
    "type": "string",
    "description": "Tree entity UUID for a space, document, document group, or story map.",
}

EXPIRED_AT_PROPERTY = {
    "type": ["string", "null"],
    "description": "Future ISO-8601 expiration timestamp; pass null to remove expiration.",
}

ENTITY_UIDS_PROPERTY = {
    "type": "array",
    "items": {"type": "string"},
    "description": "Explicit tree entity UUIDs to process in input order.",
}

WORKERS_PROPERTY = {
    "type": "integer",
    "description": "Parallel workers (default 2, max 6).",
}

EXAMPLE_ENTITY_UID = "11111111-1111-4111-8111-111111111111"
EXAMPLE_SECOND_ENTITY_UID = "22222222-2222-4222-8222-222222222222"
EXAMPLE_EXPIRED_AT = "2099-01-01T00:00:00Z"


TOOLS = (
    make_tool(
        canonical_name="tree-entities.list",
        mcp_alias="kaiten_list_tree_entities",
        description="List tree entities from Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "limit": {"type": "integer", "description": "Max results."},
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
        },
        operation=OperationSpec(
            method="GET", path_template="/tree-entities", query_fields=("query", "limit", "offset")
        ),
        response_policy=ResponsePolicy(default_limit=50, result_kind="list"),
        examples=(
            ExampleSpec(
                command="kaiten tree-entities list --json", description="List tree entities."
            ),
        ),
    ),
    make_tool(
        canonical_name="tree-entities.share.get",
        mcp_alias="kaiten_get_tree_entity_share",
        description="Get the public sharing state and ready-to-use public link for a tree entity.",
        input_schema={
            "type": "object",
            "properties": {"entity_uid": ENTITY_UID_PROPERTY},
            "required": ["entity_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/tree-entities/{entity_uid}/share",
            path_fields=("entity_uid",),
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_tree_entity_share_get,
            payload_validator=validate_tree_entity_share_payload,
            cache_policy=CACHE_POLICY_REQUEST_SCOPE,
        ),
        examples=(
            ExampleSpec(
                command=f"kaiten tree-entities share get --entity-uid {EXAMPLE_ENTITY_UID} --json",
                description="Get an existing public link without changing sharing state.",
            ),
        ),
        usage_notes=TREE_ENTITY_SHARE_USAGE_NOTES,
        bulk_alternative="tree-entities.share.batch-get",
    ),
    make_tool(
        canonical_name="tree-entities.share.enable",
        mcp_alias="kaiten_enable_tree_entity_share",
        description="Idempotently enable a public link for a tree entity.",
        input_schema={
            "type": "object",
            "properties": {
                "entity_uid": ENTITY_UID_PROPERTY,
                "expired_at": EXPIRED_AT_PROPERTY,
            },
            "required": ["entity_uid"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/tree-entities/{entity_uid}/share",
            path_fields=("entity_uid",),
            body_fields=("expired_at",),
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_tree_entity_share_enable,
            payload_validator=validate_tree_entity_share_payload,
        ),
        examples=(
            ExampleSpec(
                command=f"kaiten tree-entities share enable --entity-uid {EXAMPLE_ENTITY_UID} --json",
                description="Enable sharing and return the public link.",
            ),
            ExampleSpec(
                command=f'kaiten tree-entities share enable --entity-uid {EXAMPLE_ENTITY_UID} --expired-at "{EXAMPLE_EXPIRED_AT}" --json',
                description="Enable sharing with an expiration timestamp.",
            ),
        ),
        usage_notes=(
            *TREE_ENTITY_SHARE_USAGE_NOTES,
            "Repeated execution is safe: active shares are returned unchanged, while disabled or expired shares are reactivated using the existing share UID.",
        ),
        bulk_alternative="tree-entities.share.batch-enable",
    ),
    make_tool(
        canonical_name="tree-entities.share.update",
        mcp_alias="kaiten_update_tree_entity_share",
        description="Idempotently set or clear a tree entity public-link expiration.",
        input_schema={
            "type": "object",
            "properties": {
                "entity_uid": ENTITY_UID_PROPERTY,
                "expired_at": EXPIRED_AT_PROPERTY,
            },
            "required": ["entity_uid", "expired_at"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/tree-entities/{entity_uid}/share",
            path_fields=("entity_uid",),
            body_fields=("expired_at",),
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_tree_entity_share_update,
            payload_validator=validate_tree_entity_share_payload,
        ),
        examples=(
            ExampleSpec(
                command=f'kaiten tree-entities share update --entity-uid {EXAMPLE_ENTITY_UID} --expired-at "{EXAMPLE_EXPIRED_AT}" --json',
                description="Set a public-link expiration timestamp.",
            ),
            ExampleSpec(
                command=f"kaiten tree-entities share update --entity-uid {EXAMPLE_ENTITY_UID} --expired-at null --json",
                description="Remove the public-link expiration timestamp.",
            ),
        ),
        usage_notes=TREE_ENTITY_SHARE_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="tree-entities.share.disable",
        mcp_alias="kaiten_disable_tree_entity_share",
        description="Idempotently disable a tree entity public link.",
        input_schema={
            "type": "object",
            "properties": {"entity_uid": ENTITY_UID_PROPERTY},
            "required": ["entity_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/tree-entities/{entity_uid}/share",
            path_fields=("entity_uid",),
        ),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_tree_entity_share_disable,
            payload_validator=validate_tree_entity_share_payload,
        ),
        examples=(
            ExampleSpec(
                command=f"kaiten tree-entities share disable --entity-uid {EXAMPLE_ENTITY_UID} --json",
                description="Disable a public link without failing when it is already disabled.",
            ),
        ),
        usage_notes=TREE_ENTITY_SHARE_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="tree-entities.share.batch-get",
        mcp_alias="kaiten_batch_get_tree_entity_shares",
        description="Get public sharing states and links for explicit tree entity UUIDs.",
        input_schema={
            "type": "object",
            "properties": {
                "entity_uids": ENTITY_UIDS_PROPERTY,
                "workers": WORKERS_PROPERTY,
            },
            "required": ["entity_uids"],
        },
        operation=OperationSpec(method="GET", path_template="/tree-entities/share/batch"),
        response_policy=ResponsePolicy(heavy=True, result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_tree_entity_share_batch_get,
            payload_validator=validate_tree_entity_share_batch_payload,
            cache_policy=CACHE_POLICY_REQUEST_SCOPE,
        ),
        examples=(
            ExampleSpec(
                command=f'kaiten tree-entities share batch-get --entity-uids \'["{EXAMPLE_ENTITY_UID}","{EXAMPLE_SECOND_ENTITY_UID}"]\' --json',
                description="Get public links for several entities with bounded concurrency.",
            ),
        ),
        usage_notes=(
            *TREE_ENTITY_SHARE_USAGE_NOTES,
            "The command deduplicates UUIDs, preserves first-seen order, and returns per-entity errors without hiding successful links.",
        ),
    ),
    make_tool(
        canonical_name="tree-entities.share.batch-enable",
        mcp_alias="kaiten_batch_enable_tree_entity_shares",
        description="Idempotently enable public links for explicit tree entity UUIDs.",
        input_schema={
            "type": "object",
            "properties": {
                "entity_uids": ENTITY_UIDS_PROPERTY,
                "expired_at": EXPIRED_AT_PROPERTY,
                "workers": WORKERS_PROPERTY,
            },
            "required": ["entity_uids"],
        },
        operation=OperationSpec(method="POST", path_template="/tree-entities/share/batch"),
        response_policy=ResponsePolicy(heavy=True, result_kind="entity"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_tree_entity_share_batch_enable,
            payload_validator=validate_tree_entity_share_batch_payload,
        ),
        examples=(
            ExampleSpec(
                command=f'kaiten tree-entities share batch-enable --entity-uids \'["{EXAMPLE_ENTITY_UID}","{EXAMPLE_SECOND_ENTITY_UID}"]\' --workers 2 --json',
                description="Publish several entities and return every public link.",
            ),
        ),
        usage_notes=(
            *TREE_ENTITY_SHARE_USAGE_NOTES,
            "Only explicit entity UUIDs are accepted; the command does not publish an inferred query result or subtree.",
            "The result contains ordered items, per-entity errors, and changed/unchanged counters so partial failures remain visible and reruns stay safe.",
        ),
    ),
    make_tool(
        canonical_name="tree.children.list",
        mcp_alias="kaiten_list_children",
        description="List direct children of an entity in the Kaiten sidebar tree.",
        input_schema={
            "type": "object",
            "properties": {
                "parent_entity_uid": {
                    "type": "string",
                    "description": "Parent entity UID. Omit to list root-level entities.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/tree/children"),
        response_policy=ResponsePolicy(heavy=True, result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated", custom_executor=execute_tree_children_list
        ),
        examples=(
            ExampleSpec(
                command="kaiten tree children list --parent-entity-uid root-1 --json",
                description="List direct tree children.",
            ),
        ),
        usage_notes=TREE_CATALOG_USAGE_NOTES,
    ),
    make_tool(
        canonical_name="tree.get",
        mcp_alias="kaiten_get_tree",
        description="Build a nested entity tree from the Kaiten sidebar.",
        input_schema={
            "type": "object",
            "properties": {
                "root_uid": {
                    "type": "string",
                    "description": "Start tree from this entity UID. Omit for full tree from roots.",
                },
                "depth": {
                    "type": "integer",
                    "description": "Max recursion depth (0 = unlimited). Default: 0.",
                },
            },
        },
        operation=OperationSpec(method="GET", path_template="/tree"),
        response_policy=ResponsePolicy(heavy=True, result_kind="list"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated", custom_executor=execute_tree_get
        ),
        examples=(
            ExampleSpec(
                command="kaiten tree get --depth 1 --json",
                description="Build a bounded entity tree.",
            ),
        ),
        usage_notes=TREE_CATALOG_USAGE_NOTES,
    ),
)
