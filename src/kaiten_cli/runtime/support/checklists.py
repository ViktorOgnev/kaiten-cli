"""Support helpers for checklist reads embedded in card payloads."""

from __future__ import annotations

from typing import Any


def extract_card_checklists(card: dict[str, Any]) -> list[Any]:
    """Return checklist payloads embedded in a card response."""
    checklists = card.get("checklists")
    return checklists if isinstance(checklists, list) else []


def _id_matches(value: Any, expected: int) -> bool:
    if value == expected:
        return True
    if isinstance(value, str):
        try:
            return int(value) == expected
        except ValueError:
            return False
    return False


def extract_checklist_items(card: dict[str, Any], checklist_id: int) -> list[Any]:
    """Return items for a checklist embedded in a card response."""
    for checklist in extract_card_checklists(card):
        if not isinstance(checklist, dict):
            continue
        if _id_matches(checklist.get("id"), checklist_id) or _id_matches(
            checklist.get("checklist_id"), checklist_id
        ):
            items = checklist.get("items")
            return items if isinstance(items, list) else []
    return []
