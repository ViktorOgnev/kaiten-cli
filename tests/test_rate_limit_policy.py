from __future__ import annotations

import asyncio
from email.utils import formatdate
from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from kaiten_cli import __version__
from kaiten_cli.errors import ApiError, TransportError
from kaiten_cli.models import ResolvedProfile
from kaiten_cli.runtime.cache import ExecutionContext
from kaiten_cli.runtime.client import MAX_RETRY_AFTER, RATE_LIMIT_DELAY, KaitenClient


class _FakeLoop:
    def __init__(self) -> None:
        self.values = iter([0.0, 0.1, 0.3, 0.35])

    def time(self) -> float:
        return next(self.values)


@pytest.mark.asyncio
async def test_rate_limit_waits(monkeypatch):
    client = KaitenClient(domain="sandbox", token="token")
    fake_loop = _FakeLoop()
    sleeps: list[float] = []

    async def fake_sleep(value: float) -> None:
        sleeps.append(value)

    monkeypatch.setattr(asyncio, "get_running_loop", lambda: fake_loop)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    await client._rate_limit()
    await client._rate_limit()

    assert sleeps
    assert sleeps[0] > 0


@pytest.mark.asyncio
async def test_clients_share_execution_context_rate_budget():
    context = ExecutionContext.for_profile(
        ResolvedProfile(name=None, domain="sandbox", token="token", cache_mode="off")
    )
    first = KaitenClient(domain="sandbox", token="token", execution_context=context)
    second = KaitenClient(domain="sandbox", token="token", execution_context=context)

    shared_wait = AsyncMock()
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(ExecutionContext, "wait_for_rate_slot", shared_wait)
        await first._rate_limit()
        await second._rate_limit()

    assert shared_wait.await_count == 2
    shared_wait.assert_awaited_with(RATE_LIMIT_DELAY)


def test_retry_after_supports_http_date(monkeypatch):
    monkeypatch.setattr("kaiten_cli.runtime.client.time.time", lambda: 1_000.0)
    header = formatdate(1_012.0, usegmt=True)

    assert KaitenClient._parse_retry_after(header) == pytest.approx(12.0)


@pytest.mark.asyncio
@respx.mock
async def test_api_requests_send_cli_identity_headers():
    client = KaitenClient(domain="sandbox", token="token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(200, json={"id": 1})
    )

    try:
        await client.get("/cards/1")
    finally:
        await client.close()

    assert route.called
    headers = route.calls[0].request.headers
    assert headers["user-agent"] == f"kaiten-cli/{__version__}"
    assert headers["x-kaiten-client-type"] == "cli"
    assert headers["x-kaiten-client-name"] == "kaiten-cli"
    assert headers["x-kaiten-client-version"] == __version__


@pytest.mark.asyncio
@respx.mock
async def test_get_retry_after_is_capped_and_retried(monkeypatch):
    client = KaitenClient(domain="sandbox", token="token")
    client._rate_limit = AsyncMock()
    sleeps: list[float] = []

    async def fake_sleep(value: float) -> None:
        sleeps.append(value)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr("kaiten_cli.runtime.client.random.uniform", lambda _start, _end: 0.0)
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        side_effect=[
            Response(429, json={"message": "slow down"}, headers={"Retry-After": "999"}),
            Response(200, json={"id": 1}),
        ]
    )

    try:
        result = await client.get("/cards/1")
    finally:
        await client.close()

    assert route.call_count == 2
    assert sleeps == [MAX_RETRY_AFTER]
    assert result == {"id": 1}


@pytest.mark.asyncio
@respx.mock
async def test_standalone_get_5xx_is_not_reported_as_mutation_outcome():
    client = KaitenClient(domain="sandbox", token="token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(502, json={"message": "upstream failed"})
    )

    try:
        with pytest.raises(ApiError, match="upstream failed"):
            await client.get("/cards/1")
    finally:
        await client.close()

    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_standalone_get_invalid_json_is_not_reported_as_mutation_outcome():
    client = KaitenClient(domain="sandbox", token="token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=Response(200, content=b"not-json")
    )

    try:
        with pytest.raises(TransportError, match="returned invalid JSON") as exc_info:
            await client.get("/cards/1")
    finally:
        await client.close()

    assert "remote change" not in str(exc_info.value)
    assert route.call_count == 1
