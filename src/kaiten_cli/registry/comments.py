"""Comment tool specs."""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.behaviors import (
    comment_format_request,
    execute_comments_batch_list,
    validate_card_id_batch,
)


TOOLS = (
    make_tool(
        canonical_name="comments.list",
        mcp_alias="kaiten_list_comments",
        description="List all comments on a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card whose comments to list."},
                "compact": {
                    "type": "boolean",
                    "description": "Return compact response without heavy fields (avatars, nested user objects).",
                    "default": False,
                },
            },
            "required": ["card_id"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/{card_id}/comments", path_fields=("card_id",)),
        response_policy=ResponsePolicy(compact_supported=True, result_kind="list"),
        examples=(
            ExampleSpec(command="kaiten comments list --card-id 10 --compact --json", description="List comments on a card."),
        ),
        usage_notes=(
            "This is a per-card read and becomes expensive when repeated across large card populations.",
            "For report and investigation workflows, prefer comments.batch-list over one-card-at-a-time loops.",
        ),
        bulk_alternative="comments.batch-list",
    ),
    make_tool(
        canonical_name="comments.batch-list",
        mcp_alias="kaiten_batch_list_comments",
        description="Fetch comments for multiple cards with bounded worker concurrency.",
        input_schema={
            "type": "object",
            "properties": {
                "card_ids": {"type": "array", "items": {"type": "integer"}, "description": "Card IDs to inspect"},
                "workers": {"type": "integer", "description": "Parallel workers (default 2, max 6)"},
                "compact": {"type": "boolean", "description": "Strip heavy fields from comment payloads"},
                "fields": {"type": "string", "description": "Comma-separated field names to keep for each comment"},
            },
            "required": ["card_ids"],
        },
        operation=OperationSpec(method="GET", path_template="/cards/comments/batch"),
        response_policy=ResponsePolicy(result_kind="entity", heavy=True),
        runtime_behavior=RuntimeBehavior(
            execution_mode="aggregated",
            payload_validator=validate_card_id_batch,
            custom_executor=execute_comments_batch_list,
        ),
        examples=(
            ExampleSpec(command="kaiten comments batch-list --card-ids '[1,2,3]' --json", description="Fetch comments for several cards in one CLI call."),
            ExampleSpec(command="kaiten comments batch-list --card-ids '[1,2,3]' --workers 2 --compact --fields id,text --json", description="Fetch narrowed comment payloads with bounded concurrency."),
        ),
        usage_notes=(
            "The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.",
            "Use this bulk path when you need comment evidence across many cards.",
        ),
    ),
    make_tool(
        canonical_name="comments.create",
        mcp_alias="kaiten_create_comment",
        description="Add a comment to a card.",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card to comment on."},
                "text": {"type": "string", "description": "Comment text. For format=html send HTML content."},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html"],
                    "description": "Comment format. 'markdown' (default) stores raw markdown, 'html' switches the request to HTML mode.",
                },
                "internal": {"type": "boolean", "description": "Mark the comment as internal (visible only to team)."},
            },
            "required": ["card_id", "text"],
        },
        operation=OperationSpec(
            method="POST",
            path_template="/cards/{card_id}/comments",
            path_fields=("card_id",),
            body_fields=("text", "format", "internal"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=comment_format_request),
        examples=(
            ExampleSpec(command='kaiten comments create --card-id 10 --text "Looks good" --json', description="Create a markdown comment."),
        ),
    ),
    make_tool(
        canonical_name="comments.update",
        mcp_alias="kaiten_update_comment",
        description="Update a comment on a card (author only).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "comment_id": {"type": "integer", "description": "ID of the comment to update."},
                "text": {"type": "string", "description": "New comment text. For format=html send HTML content."},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html"],
                    "description": "Comment format. 'html' switches the request to HTML mode, 'markdown' switches back to markdown.",
                },
            },
            "required": ["card_id", "comment_id", "text"],
        },
        operation=OperationSpec(
            method="PATCH",
            path_template="/cards/{card_id}/comments/{comment_id}",
            path_fields=("card_id", "comment_id"),
            body_fields=("text", "format"),
        ),
        runtime_behavior=RuntimeBehavior(request_shaper=comment_format_request),
        examples=(
            ExampleSpec(command='kaiten comments update --card-id 10 --comment-id 20 --text "Updated" --json', description="Update a comment."),
        ),
    ),
    make_tool(
        canonical_name="comments.delete",
        mcp_alias="kaiten_delete_comment",
        description="Delete a comment from a card (author only).",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "ID of the card."},
                "comment_id": {"type": "integer", "description": "ID of the comment to delete."},
            },
            "required": ["card_id", "comment_id"],
        },
        operation=OperationSpec(
            method="DELETE",
            path_template="/cards/{card_id}/comments/{comment_id}",
            path_fields=("card_id", "comment_id"),
        ),
        examples=(
            ExampleSpec(command="kaiten comments delete --card-id 10 --comment-id 20 --json", description="Delete a comment."),
        ),
    ),
)
