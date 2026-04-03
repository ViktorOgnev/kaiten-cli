"""Async Kaiten HTTP client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any

import httpx

from kaiten_cli.errors import ApiError, ConfigError, TransportError

logger = logging.getLogger(__name__)

API_VERSION = "latest"
RATE_LIMIT_DELAY = 0.22
RETRY_DELAY = 2.0
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 20.0
HEAVY_TIMEOUT = 60.0


class KaitenClient:
    """Async HTTP client for Kaiten with low-load defaults."""

    def __init__(self, *, domain: str, token: str):
        if not domain:
            raise ConfigError("KAITEN_DOMAIN is required")
        if not token:
            raise ConfigError("KAITEN_TOKEN is required")
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}.kaiten.ru/api/{API_VERSION}"
        self._client: httpx.AsyncClient | None = None
        self._last_request_time = 0.0
        self._rate_lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def _rate_limit(self) -> None:
        async with self._rate_lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < RATE_LIMIT_DELAY:
                await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
            self._last_request_time = asyncio.get_running_loop().time()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Any:
        client = await self._get_client()
        if params:
            params = {key: value for key, value in params.items() if value is not None}

        for attempt in range(MAX_RETRIES):
            await self._rate_limit()
            try:
                response = await client.request(method, path, params=params, json=json, timeout=timeout)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        with contextlib.suppress(ValueError):
                            delay = float(retry_after)
                            logger.warning("Rate limited, retrying after %.1fs", delay)
                            await asyncio.sleep(delay)
                            continue
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue

                if response.status_code >= 400:
                    body = None
                    with contextlib.suppress(Exception):
                        body = response.json()
                    message = ""
                    if isinstance(body, dict):
                        message = str(body.get("message", body.get("error", "")))
                    if not message:
                        message = response.text[:500]
                    raise ApiError(response.status_code, message, body)

                if response.status_code == 204 or not response.content:
                    return None
                return response.json()
            except ApiError:
                raise
            except httpx.TimeoutException as exc:
                if attempt == MAX_RETRIES - 1:
                    raise TransportError(f"Timeout calling Kaiten API: {exc}") from exc
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            except httpx.HTTPError as exc:
                if attempt == MAX_RETRIES - 1:
                    raise TransportError(f"Connection error: {exc}") from exc
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))

        raise TransportError("Rate limit retries exhausted")

    async def get(self, path: str, *, params: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        return await self._request("GET", path, params=params, timeout=timeout)

    async def post(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        return await self._request("POST", path, json=json, timeout=timeout)

    async def patch(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        return await self._request("PATCH", path, json=json, timeout=timeout)

    async def delete(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        return await self._request("DELETE", path, json=json, timeout=timeout)

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

