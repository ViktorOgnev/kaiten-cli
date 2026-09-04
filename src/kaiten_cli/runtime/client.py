"""Async Kaiten HTTP client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import random
import time
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from kaiten_cli import __version__
from kaiten_cli.errors import ApiError, ConfigError, TransportError
from kaiten_cli.models import CACHE_POLICY_NONE, DebugReporter
from kaiten_cli.runtime.cache import ExecutionContext
from kaiten_cli.runtime.endpoints import profile_api_base_url, profile_origin

logger = logging.getLogger(__name__)

API_VERSION = "latest"
# Keep the client below Kaiten's 50 requests/second API limit.
RATE_LIMIT_DELAY = 0.025
RETRY_DELAY = 2.0
MAX_RETRIES = 3
MAX_RETRY_AFTER = 30.0
RETRY_JITTER_MAX = 0.25
RETRYABLE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
DEFAULT_TIMEOUT = 20.0
HEAVY_TIMEOUT = 60.0
CLIENT_TYPE = "cli"
CLIENT_NAME = "kaiten-cli"
CLIENT_USER_AGENT = f"{CLIENT_NAME}/{__version__}"
CLIENT_IDENTITY_HEADERS = {
    "User-Agent": CLIENT_USER_AGENT,
    "X-Kaiten-Client-Type": CLIENT_TYPE,
    "X-Kaiten-Client-Name": CLIENT_NAME,
    "X-Kaiten-Client-Version": __version__,
}


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
        mutates_remote_state: bool = True,
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
        self.mutates_remote_state = mutates_remote_state
        self.root_url = profile_origin(domain)
        self.base_url = profile_api_base_url(domain, api_version=API_VERSION)
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
                    "Accept": "application/json",
                    **CLIENT_IDENTITY_HEADERS,
                },
            )
        return self._client

    async def _rate_limit(self) -> None:
        if self.execution_context is not None:
            await self.execution_context.wait_for_rate_slot(RATE_LIMIT_DELAY)
            return
        async with self._rate_lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < RATE_LIMIT_DELAY:
                await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
            self._last_request_time = asyncio.get_running_loop().time()

    @staticmethod
    def _retry_delay(attempt: int, retry_after: float | None = None) -> float:
        base_delay = retry_after if retry_after is not None else RETRY_DELAY * (attempt + 1)
        non_negative_delay = max(0.0, base_delay)
        jitter = random.uniform(0.0, min(RETRY_JITTER_MAX, non_negative_delay * 0.1))
        return min(non_negative_delay + jitter, MAX_RETRY_AFTER)

    @staticmethod
    def _parse_retry_after(value: str | None) -> float | None:
        if not value:
            return None
        with contextlib.suppress(ValueError):
            return float(value)
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return max(0.0, parsed.timestamp() - time.time())

    @staticmethod
    def _parse_rate_limit_reset(value: str | None) -> float | None:
        if not value:
            return None
        try:
            reset_at = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, reset_at - time.time())

    @staticmethod
    def _ambiguous_mutation_error(method: str, path: str, detail: str) -> TransportError:
        return TransportError(
            f"{detail} calling {method} {path}. The request was not retried because it may "
            "have changed Kaiten; the remote outcome is unknown. Verify the remote state with "
            "--cache-mode off or --cache-mode refresh before retrying."
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: Any = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Any:
        client = await self._get_client()
        method = method.upper()
        retryable = method in RETRYABLE_METHODS
        mutation_attempt = self.mutates_remote_state and not retryable
        attempts = MAX_RETRIES if retryable else 1
        if params:
            params = {key: value for key, value in params.items() if value is not None}

        for attempt in range(attempts):
            await self._rate_limit()
            started = time.perf_counter()
            try:
                response = await client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    files=files,
                    timeout=timeout,
                )
                if self.execution_context is not None:
                    self.execution_context.stats.record_http_attempt(
                        source="kaiten_api",
                        method=method,
                        path=path,
                        wait_ms=(time.perf_counter() - started) * 1000.0,
                        status_code=response.status_code,
                    )
                if response.status_code == 429 and retryable and attempt < attempts - 1:
                    parsed_retry_after = self._parse_retry_after(
                        response.headers.get("Retry-After")
                    )
                    if parsed_retry_after is None:
                        parsed_retry_after = self._parse_rate_limit_reset(
                            response.headers.get("X-RateLimit-Reset")
                        )
                    delay = self._retry_delay(attempt, parsed_retry_after)
                    self._debug(f"retry: rate-limited on {method} {path}, waiting {delay:.2f}s")
                    logger.warning("Rate limited, retrying after %.2fs", delay)
                    if self.execution_context is not None:
                        self.execution_context.stats.retry_count += 1
                    await asyncio.sleep(delay)
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
                    if mutation_attempt and response.status_code >= 500:
                        raise self._ambiguous_mutation_error(
                            method, path, f"HTTP {response.status_code}"
                        )
                    raise ApiError(response.status_code, message, body)

                if response.status_code == 204 or not response.content:
                    return None
                try:
                    return response.json()
                except ValueError as exc:
                    if mutation_attempt:
                        raise TransportError(
                            f"HTTP {response.status_code} succeeded for {method} {path}, but the "
                            "response was not valid JSON. The remote change may have been applied; "
                            "verify the remote state with --cache-mode off or --cache-mode refresh "
                            "before retrying."
                        ) from exc
                    raise TransportError(
                        f"Kaiten returned invalid JSON for {method} {path}."
                    ) from exc
            except ApiError:
                raise
            except httpx.TimeoutException as exc:
                if self.execution_context is not None:
                    self.execution_context.stats.record_http_attempt(
                        source="kaiten_api",
                        method=method,
                        path=path,
                        wait_ms=(time.perf_counter() - started) * 1000.0,
                        error=True,
                    )
                if mutation_attempt:
                    raise self._ambiguous_mutation_error(method, path, "Timeout") from exc
                if not retryable:
                    raise TransportError(f"Timeout calling Kaiten API: {exc}") from exc
                if attempt == attempts - 1:
                    raise TransportError(f"Timeout calling Kaiten API: {exc}") from exc
                delay = self._retry_delay(attempt)
                self._debug(
                    f"retry: timeout on {method} {path}, attempt {attempt + 1}/{MAX_RETRIES}, "
                    f"waiting {delay:.2f}s"
                )
                if self.execution_context is not None:
                    self.execution_context.stats.retry_count += 1
                await asyncio.sleep(delay)
            except httpx.HTTPError as exc:
                if self.execution_context is not None:
                    self.execution_context.stats.record_http_attempt(
                        source="kaiten_api",
                        method=method,
                        path=path,
                        wait_ms=(time.perf_counter() - started) * 1000.0,
                        error=True,
                    )
                if mutation_attempt:
                    raise self._ambiguous_mutation_error(method, path, "Connection error") from exc
                if not retryable:
                    raise TransportError(f"Connection error: {exc}") from exc
                if attempt == attempts - 1:
                    raise TransportError(f"Connection error: {exc}") from exc
                delay = self._retry_delay(attempt)
                self._debug(
                    f"retry: transport error on {method} {path}, attempt {attempt + 1}/{MAX_RETRIES}, "
                    f"waiting {delay:.2f}s"
                )
                if self.execution_context is not None:
                    self.execution_context.stats.retry_count += 1
                await asyncio.sleep(delay)

        raise TransportError("Rate limit retries exhausted")

    async def get(
        self, path: str, *, params: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT
    ) -> Any:
        if self.execution_context is None:
            return await self._request("GET", path, params=params, timeout=timeout)
        return await self.execution_context.get_json(
            method="GET",
            path=path,
            params=params,
            cache_policy=self.cache_policy,
            fetch=lambda: self._request("GET", path, params=params, timeout=timeout),
        )

    async def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        files: Any = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Any:
        try:
            return await self._request("POST", path, json=json, files=files, timeout=timeout)
        finally:
            await self._invalidate_after_remote_mutation()

    async def put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        files: Any = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Any:
        try:
            return await self._request("PUT", path, json=json, files=files, timeout=timeout)
        finally:
            await self._invalidate_after_remote_mutation()

    async def patch(
        self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT
    ) -> Any:
        try:
            return await self._request("PATCH", path, json=json, timeout=timeout)
        finally:
            await self._invalidate_after_remote_mutation()

    async def delete(
        self, path: str, *, json: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT
    ) -> Any:
        try:
            return await self._request("DELETE", path, json=json, timeout=timeout)
        finally:
            await self._invalidate_after_remote_mutation()

    async def _invalidate_after_remote_mutation(self) -> None:
        if self.execution_context is not None and self.mutates_remote_state:
            await self.execution_context.invalidate_after_mutation()

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
