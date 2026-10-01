"""Support helpers for embedded and individual checklist reads."""

from __future__ import annotations

from typing import Any

from kaiten_cli.errors import TransportError
from kaiten_cli.i18n import tr


def extract_card_checklists(card: dict[str, Any]) -> list[Any]:
    """Return checklist payloads embedded in a card response."""
    checklists = card.get("checklists")
    return checklists if isinstance(checklists, list) else []


def extract_checklist_items(checklist: Any) -> list[Any]:
    """Return items from an individual checklist without masking malformed responses."""
    if not isinstance(checklist, dict) or not isinstance(checklist.get("items"), list):
        raise TransportError(tr("Checklist response must be an object with an items array."))
    return checklist["items"]
