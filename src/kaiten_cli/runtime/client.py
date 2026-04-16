"""Async Kaiten HTTP client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any

import httpx

from kaiten_cli.errors import ApiError, ConfigError, TransportError
from kaiten_cli.models import CACHE_POLICY_NONE, DebugReporter
from kaiten_cli.runtime.cache import ExecutionContext

logger = logging.getLogger(__name__)

API_VERSION = "latest"
RATE_LIMIT_DELAY = 0.22
RETRY_DELAY = 2.0
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 20.0
HEAVY_TIMEOUT = 60.0


class KaitenClient:
    """Async HTTP client for Kaiten with low-load defaults."""

    def __init__(
        self,
        *,
        domain: str,
        token: str,
        reporter: DebugReporter | None = None,
        execution_context: ExecutionContext | None = None,
        cache_policy: str = CACHE_POLICY_NONE,
    ):
        if not domain:
            raise ConfigError("KAITEN_DOMAIN is required")
        if not token:
            raise ConfigError("KAITEN_TOKEN is required")
        self.domain = domain
        self.token = token
        self._reporter = reporter
        self.execution_context = execution_context
        self.cache_policy = cache_policy
        self.base_url = f"https://{domain}.kaiten.ru/api/{API_VERSION}"
        self._client: httpx.AsyncClient | None = None
        self._last_request_time = 0.0
        self._rate_lock = asyncio.Lock()

    def _debug(self, message: str) -> None:
        if self._reporter is not None:
            self._reporter(message)

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
                            self._debug(
                                f"retry: rate-limited on {method} {path}, waiting {delay:.1f}s from Retry-After"
                            )
                            logger.warning("Rate limited, retrying after %.1fs", delay)
                            await asyncio.sleep(delay)
                            continue
                    self._debug(
                        f"retry: rate-limited on {method} {path}, waiting {RETRY_DELAY * (attempt + 1):.1f}s"
                    )
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
                self._debug(
                    f"retry: timeout on {method} {path}, attempt {attempt + 1}/{MAX_RETRIES}, "
                    f"waiting {RETRY_DELAY * (attempt + 1):.1f}s"
                )
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            except httpx.HTTPError as exc:
                if attempt == MAX_RETRIES - 1:
                    raise TransportError(f"Connection error: {exc}") from exc
                self._debug(
                    f"retry: transport error on {method} {path}, attempt {attempt + 1}/{MAX_RETRIES}, "
                    f"waiting {RETRY_DELAY * (attempt + 1):.1f}s"
                )
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))

        raise TransportError("Rate limit retries exhausted")

    async def get(self, path: str, *, params: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        if self.execution_context is None:
            return await self._request("GET", path, params=params, timeout=timeout)
        return await self.execution_context.get_json(
            method="GET",
            path=path,
            params=params,
            cache_policy=self.cache_policy,
            fetch=lambda: self._request("GET", path, params=params, timeout=timeout),
        )

    async def post(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        result = await self._request("POST", path, json=json, timeout=timeout)
        if self.execution_context is not None:
            await self.execution_context.invalidate_after_mutation()
        return result

    async def patch(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        result = await self._request("PATCH", path, json=json, timeout=timeout)
        if self.execution_context is not None:
            await self.execution_context.invalidate_after_mutation()
        return result

    async def delete(self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
        result = await self._request("DELETE", path, json=json, timeout=timeout)
        if self.execution_context is not None:
            await self.execution_context.invalidate_after_mutation()
        return result

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
