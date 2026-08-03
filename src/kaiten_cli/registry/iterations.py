"""Beta Iterations API tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy
from kaiten_cli.registry.base import make_tool


ITERATIONS_BETA_NOTE = (
    "Iterations are beta and require a Kaiten tariff with the Iterations feature enabled."
)
ITERATION_TRANSITION_NOTE = (
    "Statuses move forward only: planned -> active -> closed; activation requires start/finish "
    "dates and invalid transitions are rejected by Kaiten."
)


def _shaping_properties() -> dict[str, dict]:
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


SHAPED_LIST = ResponsePolicy(
    compact_supported=True,
    fields_supported=True,
    result_kind="list",
)
SHAPED_ENTITY = ResponsePolicy(
    compact_supported=True,
    fields_supported=True,
    result_kind="entity",
)


TOOLS = (
    make_tool(
        canonical_name="iterations.list",
        mcp_alias="kaiten_list_iterations",
        description="List iterations in a space with bounded pagination and optional cards data.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "status": {
                    "type": "string",
                    "description": "Comma-separated statuses: planned, active, closed.",
                },
                "with_data": {
                    "type": "string",
                    "enum": ["cards"],
                    "description": "Include related cards.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum iterations to return (server cap 100).",
                },
                "offset": {"type": "integer", "description": "Pagination offset."},
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Result order.",
                },
                **_shaping_properties(),
            },
            "required": ["space_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_uid}/iterations",
            path_fields=("space_uid",),
            query_fields=("status", "with_data", "limit", "offset", "order"),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True,
            fields_supported=True,
            default_limit=100,
            result_kind="list",
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json iterations list --space-uid <space_uuid> --status planned,active --with-data cards --fields id,title,status,start_date,finish_date",
                description="List current iterations and their cards.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE,),
    ),
    make_tool(
        canonical_name="iterations.get",
        mcp_alias="kaiten_get_iteration",
        description="Get an iteration by UUID within a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                **_shaping_properties(),
            },
            "required": ["space_uid", "iteration_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}",
            path_fields=("space_uid", "iteration_id"),
        ),
        response_policy=SHAPED_ENTITY,
        examples=(
            ExampleSpec(
                command="kaiten --json iterations get --space-uid <space_uuid> --iteration-id <iteration_uuid>",
                description="Read one iteration.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE,),
    ),
    make_tool(
        canonical_name="iterations.create",
        mcp_alias="kaiten_create_iteration",
        description="Create a planned iteration in a space.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "title": {"type": "string", "description": "Iteration title."},
                "goal": {"type": "string", "description": "Iteration goal."},
                "start_date": {"type": "string", "description": "ISO 8601 start date."},
                "finish_date": {"type": "string", "description": "ISO 8601 finish date."},
            },
            "required": ["space_uid", "title"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_uid}/iterations",
            path_fields=("space_uid",),
            body_fields=("title", "goal", "start_date", "finish_date"),
        ),
        examples=(
            ExampleSpec(
                command='kaiten --json iterations create --space-uid <space_uuid> --title "Iteration 12" --start-date 2026-08-03 --finish-date 2026-08-17',
                description="Create a dated planned iteration.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE,),
    ),
    make_tool(
        canonical_name="iterations.update",
        mcp_alias="kaiten_update_iteration",
        description="Update iteration metadata, dates, status, or card transfer target.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                "title": {"type": "string", "description": "New title."},
                "goal": {"type": "string", "description": "New goal."},
                "status": {
                    "type": "string",
                    "enum": ["planned", "active", "closed"],
                    "description": "Next iteration status.",
                },
                "start_date": {"type": "string", "description": "ISO 8601 start date."},
                "finish_date": {"type": "string", "description": "ISO 8601 finish date."},
                "actual_finish_date": {
                    "type": "string",
                    "description": "ISO 8601 actual finish date when closing.",
                },
                "new_iteration_id": {
                    "type": "string",
                    "description": "Target planned/active iteration for remaining cards.",
                },
            },
            "required": ["space_uid", "iteration_id"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}",
            path_fields=("space_uid", "iteration_id"),
            body_fields=(
                "title",
                "goal",
                "status",
                "start_date",
                "finish_date",
                "actual_finish_date",
                "new_iteration_id",
            ),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json iterations update --space-uid <space_uuid> --iteration-id <iteration_uuid> --status active",
                description="Activate a dated planned iteration.",
            ),
            ExampleSpec(
                command="kaiten --json iterations update --space-uid <space_uuid> --iteration-id <iteration_uuid> --status closed --new-iteration-id <target_uuid>",
                description="Close an iteration and transfer remaining cards.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE, ITERATION_TRANSITION_NOTE),
    ),
    make_tool(
        canonical_name="iterations.delete",
        mcp_alias="kaiten_delete_iteration",
        description="Delete an iteration and optionally move its cards to another iteration.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                "new_iteration_id": {
                    "type": "string",
                    "description": "Target planned/active iteration for cards before deletion.",
                },
            },
            "required": ["space_uid", "iteration_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}",
            path_fields=("space_uid", "iteration_id"),
            body_fields=("new_iteration_id",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json iterations delete --space-uid <space_uuid> --iteration-id <iteration_uuid> --new-iteration-id <target_uuid>",
                description="Delete and move cards to a valid target iteration.",
            ),
        ),
        usage_notes=(
            ITERATIONS_BETA_NOTE,
            "The transfer target must belong to the same space and be planned or active.",
        ),
    ),
    make_tool(
        canonical_name="iteration-cards.list",
        mcp_alias="kaiten_list_iteration_cards",
        description="List active or removed card relations for an iteration.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                "status": {
                    "type": "string",
                    "enum": ["active", "removed"],
                    "description": "Relation status filter.",
                },
                **_shaping_properties(),
            },
            "required": ["space_uid", "iteration_id"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}/cards",
            path_fields=("space_uid", "iteration_id"),
            query_fields=("status",),
        ),
        response_policy=SHAPED_LIST,
        examples=(
            ExampleSpec(
                command="kaiten --json iteration-cards list --space-uid <space_uuid> --iteration-id <iteration_uuid> --status active --fields card_uid,status",
                description="List active iteration cards.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE,),
    ),
    make_tool(
        canonical_name="iteration-cards.add",
        mcp_alias="kaiten_add_iteration_card",
        description="Add an active card from the space primary boards to an iteration.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                "card_uid": {"type": "string", "description": "Card UUID."},
            },
            "required": ["space_uid", "iteration_id", "card_uid"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}/cards",
            path_fields=("space_uid", "iteration_id"),
            body_fields=("card_uid",),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json iteration-cards add --space-uid <space_uuid> --iteration-id <iteration_uuid> --card-uid <card_uuid>",
                description="Add a card to a planned or active iteration.",
            ),
        ),
        usage_notes=(
            ITERATIONS_BETA_NOTE,
            "Only active cards on a primary board of the same space can be added.",
        ),
    ),
    make_tool(
        canonical_name="iteration-cards.remove",
        mcp_alias="kaiten_remove_iteration_card",
        description="Remove a card from a non-closed iteration.",
        input_schema={
            "type": "object",
            "properties": {
                "space_uid": {"type": "string", "description": "Space UUID."},
                "iteration_id": {"type": "string", "description": "Iteration UUID."},
                "card_uid": {"type": "string", "description": "Card UUID."},
            },
            "required": ["space_uid", "iteration_id", "card_uid"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/spaces/{space_uid}/iterations/{iteration_id}/cards/{card_uid}",
            path_fields=("space_uid", "iteration_id", "card_uid"),
        ),
        examples=(
            ExampleSpec(
                command="kaiten --json iteration-cards remove --space-uid <space_uuid> --iteration-id <iteration_uuid> --card-uid <card_uuid>",
                description="Remove a card from an open iteration.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE, "Cards cannot be removed from a closed iteration."),
    ),
    make_tool(
        canonical_name="card-iterations-history.list",
        mcp_alias="kaiten_list_card_iterations_history",
        description="List iteration membership history for a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_uid": {"type": "string", "description": "Card UUID."},
                **_shaping_properties(),
            },
            "required": ["card_uid"],
        },
        operation=OperationSpec(
            method="GET",
            path_template="/cards/{card_uid}/iterations-history",
            path_fields=("card_uid",),
        ),
        response_policy=SHAPED_LIST,
        examples=(
            ExampleSpec(
                command="kaiten --json card-iterations-history list --card-uid <card_uuid> --fields iteration_id,status,added_at,removed_at",
                description="Inspect a card's iteration history.",
            ),
        ),
        usage_notes=(ITERATIONS_BETA_NOTE,),
    ),
)
