from __future__ import annotations

import asyncio

import pytest

from kaiten_cli.runtime.client import KaitenClient


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
