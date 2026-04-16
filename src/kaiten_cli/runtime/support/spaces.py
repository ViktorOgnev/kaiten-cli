"""Support helpers for space-scoped aggregated reads."""

from __future__ import annotations

from typing import Any


async def fetch_space_topology(client, space_id: int, *, timeout: float) -> dict[str, Any]:
    boards = await client.get(f"/spaces/{space_id}/boards", timeout=timeout)
    topology_boards: list[dict[str, Any]] = []
    for board in boards if isinstance(boards, list) else []:
        if not isinstance(board, dict) or "id" not in board:
            continue
        detail = await client.get(f"/boards/{board['id']}", timeout=timeout)
        if not isinstance(detail, dict):
            continue
        detail.setdefault("columns", [])
        detail.setdefault("lanes", [])
        topology_boards.append(detail)
    return {"space_id": space_id, "boards": topology_boards}
