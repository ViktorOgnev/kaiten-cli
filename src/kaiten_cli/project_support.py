"""Project-specific execution helpers."""

from __future__ import annotations

from typing import Any

from kaiten_cli.client import KaitenClient
from kaiten_cli.errors import ApiError


def extract_project_cards(payload: Any) -> list[Any] | None:
    if not isinstance(payload, dict):
        return None

    direct_cards = payload.get("cards")
    if isinstance(direct_cards, list):
        return direct_cards

    direct_cards_data = payload.get("cards_data")
    if isinstance(direct_cards_data, list):
        return direct_cards_data

    project_payload = payload.get("project")
    if isinstance(project_payload, dict):
        nested_cards = project_payload.get("cards")
        if isinstance(nested_cards, list):
            return nested_cards
        nested_cards_data = project_payload.get("cards_data")
        if isinstance(nested_cards_data, list):
            return nested_cards_data

    return None


async def fetch_project_cards(client: KaitenClient, project_id: str, *, timeout: float) -> list[Any]:
    try:
        result = await client.get(f"/projects/{project_id}/cards", timeout=timeout)
        if isinstance(result, list):
            return result
        return []
    except ApiError as exc:
        if exc.status_code != 405:
            raise
        project = await client.get(
            f"/projects/{project_id}",
            params={"with_cards_data": True},
            timeout=timeout,
        )
        cards = extract_project_cards(project)
        if cards is None:
            raise exc
        return cards
