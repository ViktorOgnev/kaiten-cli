"""Validation and selection for the undocumented restrictions API extension."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kaiten_cli.errors import ApiError, TransportError, ValidationError
from kaiten_cli.i18n import tr


def validate_restriction_payload(tool, payload: dict[str, Any]) -> None:
    if "restriction_id" in payload:
        try:
            identifier = UUID(payload["restriction_id"])
            if payload["restriction_id"].lower() not in (str(identifier), identifier.hex):
                raise ValueError("Unsupported UUID spelling")
        except ValueError as exc:
            raise ValidationError(tr("Restriction ID must be a UUID.")) from exc
    if tool.canonical_name == "restrictions.update" and not any(
        key in payload for key in ("name", "conditions", "restrictions", "status")
    ):
        raise ValidationError(
            tr(
                "Restriction update requires name, conditions, restrictions or status; error_text alone is not accepted."
            )
        )


def select_restriction(data: Any, restriction_id: str) -> dict[str, Any]:
    if not isinstance(data, list):
        raise TransportError(
            tr("Restriction list response must be an array of objects with UUID identifiers.")
        )
    target_id = UUID(restriction_id)
    selected = None
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise TransportError(
                tr("Restriction list response must be an array of objects with UUID identifiers.")
            )
        try:
            item_id = UUID(item["id"])
        except ValueError as exc:
            raise TransportError(
                tr("Restriction list response must be an array of objects with UUID identifiers.")
            ) from exc
        if (
            item_id == target_id
            and item.get("type") != "on_workflow"
            and item.get("status") != "removed"
        ):
            selected = item
    if selected is None:
        raise ApiError(
            404,
            tr(
                "Restriction {restriction_id} was not found in this space.",
                restriction_id=restriction_id,
            ),
        )
    return selected
