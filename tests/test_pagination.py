from __future__ import annotations

from typing import Any

import pytest

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.runtime.support.pagination import fetch_all_offset_pages


class StubClient:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, dict[str, Any], float]] = []

    async def get(self, path, *, params, timeout):
        self.calls.append((path, dict(params), timeout))
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_fetch_all_offset_pages_returns_empty_collection_from_first_page():
    client = StubClient([[]])

    result = await fetch_all_offset_pages(client, "/items", page_size=100, max_pages=2, timeout=1)

    assert result == []
    assert client.calls == [("/items", {"limit": 100, "offset": 0}, 1)]


@pytest.mark.asyncio
async def test_fetch_all_offset_pages_preserves_filters_and_order_across_full_pages():
    client = StubClient([[{"id": 1}, {"id": 2}], [{"id": 3}, {"id": 4}], []])

    result = await fetch_all_offset_pages(
        client,
        "/items",
        params={"condition": 1},
        page_size=2,
        max_pages=3,
        timeout=2,
    )

    assert result == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
    assert [call[1] for call in client.calls] == [
        {"condition": 1, "limit": 2, "offset": 0},
        {"condition": 1, "limit": 2, "offset": 2},
        {"condition": 1, "limit": 2, "offset": 4},
    ]


@pytest.mark.asyncio
async def test_fetch_all_offset_pages_stops_on_short_page():
    client = StubClient([[{"id": 1}, {"id": 2}], [{"id": 3}]])

    result = await fetch_all_offset_pages(client, "/items", page_size=2, max_pages=3, timeout=1)

    assert [item["id"] for item in result] == [1, 2, 3]
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_fetch_all_offset_pages_rejects_unexpected_response_shape():
    client = StubClient([{"data": []}])

    with pytest.raises(ConfigError, match="expected a list response"):
        await fetch_all_offset_pages(client, "/items", page_size=100, max_pages=2, timeout=1)


@pytest.mark.asyncio
async def test_fetch_all_offset_pages_fails_closed_on_full_safety_boundary():
    client = StubClient([[{"id": 1}, {"id": 2}], [{"id": 3}, {"id": 4}]])

    with pytest.raises(ConfigError, match=r"possibly truncated result \(4 rows read\)"):
        await fetch_all_offset_pages(client, "/items", page_size=2, max_pages=2, timeout=1)

    assert [call[1]["offset"] for call in client.calls] == [0, 2]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page_size", "max_pages"),
    [(0, 1), (101, 1), (1, 0), (1, 1001)],
)
async def test_fetch_all_offset_pages_rejects_invalid_bounds(page_size, max_pages):
    client = StubClient([])

    with pytest.raises(ValidationError):
        await fetch_all_offset_pages(
            client,
            "/items",
            page_size=page_size,
            max_pages=max_pages,
            timeout=1,
        )

    assert client.calls == []
