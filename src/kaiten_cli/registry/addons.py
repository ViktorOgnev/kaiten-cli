"""Addon catalog, space installation and per-addon data tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, RuntimeBehavior
from kaiten_cli.registry.base import (
    PLAIN_ENTITY_POLICY,
    SHAPED_LIST_POLICY,
    make_tool,
    shaping_properties,
)
from kaiten_cli.runtime.support.addons import execute_addon_uid, validate_addon_uid_payload

ADDON_UID_NOTE = (
    "addon_uid is the addon's UUID, not its name. Take it from addons.list / "
    "space-addons.list, or derive it locally with addons.uid when the addon is "
    "mounted at a known URL path on a self-hosted installation."
)
SHARED_SCOPE_NOTE = (
    "Shared data is one row per card visible to everyone (writing it needs card.update); "
    "private data is a per-user row that only its owner reads and writes (card.read is enough)."
)
SHALLOW_MERGE_NOTE = (
    "The server shallow-merges data over the stored row by top-level key, so send the full "
    "replacement value for every key you set and omit keys you want to keep untouched."
)
ADDON_INSTALL_NOTE = (
    "The addon must be installed in the card's space before its per-card data can be written; "
    "otherwise the shared write is rejected with a permission error."
)

ADDON_UID_VALIDATION = RuntimeBehavior(payload_validator=validate_addon_uid_payload)


TOOLS = (
    make_tool(
        canonical_name="addons.list",
        mcp_alias="kaiten_list_addons",
        description="List published Kaiten addons available to the current company.",
        input_schema={
            "type": "object",
            "properties": {**shaping_properties()},
        },
        operation=OperationSpec(method="GET", path_template="/addons"),
        response_policy=SHAPED_LIST_POLICY,
        examples=(
            ExampleSpec(
                command="kaiten --json addons list --fields id,name",
                description="Find the UUID of an addon by its name.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE,),
    ),
    make_tool(
        canonical_name="addons.uid",
        mcp_alias="kaiten_derive_addon_uid",
        description="Derive an addon UUID locally from its mount path, without calling Kaiten.",
        input_schema={
            "type": "object",
            "properties": {
                "url_path": {
                    "type": "string",
                    "description": "Addon mount path, for example /github.",
                },
            },
            "required": ["url_path"],
        },
        operation=OperationSpec(method="GET", path_template="/local/addons/uid"),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute_addon_uid,
            cache_policy="none",
            requires_profile=False,
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json addons uid --url-path /github",
                description="Derive the GitHub addon UUID used by the addons-data endpoints.",
            ),
        ),
        usage_notes=(
            (
                "Local computation only: UUID v5 of the normalized path under the fixed Kaiten "
                "addons namespace, the same derivation self-hosted Kaiten uses."
            ),
            (
                "Deployments that registered an addon with an explicit UUID instead of deriving it "
                "from the mount path must read the real value from addons.list."
            ),
        ),
    ),
    make_tool(
        canonical_name="space-addons.list",
        mcp_alias="kaiten_list_space_addons",
        description="List addons installed in a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                **shaping_properties(),
            },
            "required": ["space_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_id}/addons",
            path_fields=("space_id",),
        ),
        response_policy=SHAPED_LIST_POLICY,
        examples=(
            ExampleSpec(
                command="kaiten --json space-addons list --space-id 1 --fields id,name",
                description="Check which addons a space has installed.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE,),
    ),
    make_tool(
        canonical_name="space-addons.install",
        mcp_alias="kaiten_install_space_addon",
        description="Install an addon into a Kaiten space or update its space settings.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "addon_uid": {"type": "string", "description": "Addon UUID"},
                "settings": {
                    "type": "object",
                    "description": "Space-level addon settings object; omit to only install.",
                },
            },
            "required": ["space_id", "addon_uid"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_id}/addons/{addon_uid}",
            path_fields=("space_id", "addon_uid"),
            body_fields=("settings",),
        ),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json space-addons install --space-id 1 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990",
                description="Install the GitHub addon into a space.",
            ),
        ),
        usage_notes=(
            ADDON_UID_NOTE,
            (
                "Installing an already installed addon without settings is rejected as a no-op; "
                "pass settings when you only need to update configuration."
            ),
        ),
    ),
    make_tool(
        canonical_name="space-addons.uninstall",
        mcp_alias="kaiten_uninstall_space_addon",
        description="Remove an addon from a Kaiten space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "integer", "description": "Space ID"},
                "addon_uid": {"type": "string", "description": "Addon UUID"},
            },
            "required": ["space_id", "addon_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_id}/addons/{addon_uid}",
            path_fields=("space_id", "addon_uid"),
        ),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json space-addons uninstall --space-id 1 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990",
                description="Detach an addon from a space.",
            ),
        ),
        usage_notes=(
            (
                "Uninstalling hides the addon in that space; per-card data rows written earlier are "
                "not deleted by this call."
            ),
        ),
    ),
    make_tool(
        canonical_name="card-addon-data.get",
        mcp_alias="kaiten_get_card_addon_data",
        description="Read the addon data rows stored on a card for one addon.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "addon_uid": {"type": "string", "description": "Addon UUID"},
                **shaping_properties(),
            },
            "required": ["card_id", "addon_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_id}/addons-data/{addon_uid}",
            path_fields=("card_id", "addon_uid"),
        ),
        response_policy=SHAPED_LIST_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json card-addon-data get --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990",
                description="Read the GitHub addon state stored on a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_NOTE,
            (
                "Returns every row the current user may see: the shared row (user_uid is null) plus "
                "their own private row, if either exists."
            ),
            SHARED_SCOPE_NOTE,
        ),
    ),
    make_tool(
        canonical_name="card-addon-data.set",
        mcp_alias="kaiten_set_card_addon_data",
        description="Write addon data on a card in the shared or private scope.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "addon_uid": {"type": "string", "description": "Addon UUID"},
                "type": {
                    "type": "string",
                    "enum": ["shared", "private"],
                    "description": "Data scope: shared for the whole card, private for the current user.",
                },
                "data": {
                    "type": "object",
                    "description": "Addon data object merged over the stored row by top-level key.",
                },
            },
            "required": ["card_id", "addon_uid", "type", "data"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/addons-data/{addon_uid}",
            path_fields=("card_id", "addon_uid"),
            body_fields=("type", "data"),
        ),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json card-addon-data set --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --type shared --data '{\"attachedPulls\": []}'",
                description="Replace one addon key on a card.",
            ),
            ExampleSpec(
                command="kaiten --json card-addon-data set --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --type shared --data @payload.json",
                description="Write an addon data object from a file.",
            ),
        ),
        usage_notes=(
            ADDON_UID_NOTE,
            SHALLOW_MERGE_NOTE,
            SHARED_SCOPE_NOTE,
            ADDON_INSTALL_NOTE,
            (
                "For the GitHub addon prefer the github-addon commands: they keep the exact widget "
                "payload shape and dedup attachments instead of overwriting the whole key."
            ),
        ),
    ),
    make_tool(
        canonical_name="user-addon-data.get",
        mcp_alias="kaiten_get_user_addon_data",
        description="Read the current user's company-level addon data for one addon.",
        input_schema={
            "type": "object",
            "properties": {
                "addon_uid": {"type": "string", "description": "Addon UUID"},
                **shaping_properties(),
            },
            "required": ["addon_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/company/users/current/addons-data/{addon_uid}",
            path_fields=("addon_uid",),
        ),
        response_policy=SHAPED_LIST_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json user-addon-data get --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990",
                description="Read the current user's addon-level settings.",
            ),
        ),
        usage_notes=(
            ADDON_UID_NOTE,
            (
                "This store is per user and per company; it holds addon-level user state, not "
                "per-card state."
            ),
        ),
    ),
    make_tool(
        canonical_name="user-addon-data.set",
        mcp_alias="kaiten_set_user_addon_data",
        description="Write the current user's company-level addon data for one addon.",
        input_schema={
            "type": "object",
            "properties": {
                "addon_uid": {"type": "string", "description": "Addon UUID"},
                "data": {
                    "type": "object",
                    "description": "Addon data object merged over the stored row by top-level key.",
                },
            },
            "required": ["addon_uid", "data"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/company/users/current/addons-data/{addon_uid}",
            path_fields=("addon_uid",),
            body_fields=("data",),
        ),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=ADDON_UID_VALIDATION,
        examples=(
            ExampleSpec(
                command="kaiten --json user-addon-data set --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --data '{\"selectedRepo\": null}'",
                description="Reset one key of the current user's addon state.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE, SHALLOW_MERGE_NOTE),
    ),
)
