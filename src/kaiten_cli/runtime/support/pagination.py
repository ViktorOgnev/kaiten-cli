"""Shared bounded offset pagination for Kaiten collection endpoints."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from kaiten_cli.errors import ConfigError, ValidationError


API_MAX_PAGE_SIZE = 100
DEFAULT_COLLECTION_MAX_PAGES = 100
MAX_COLLECTION_MAX_PAGES = 1000


def validate_page_bounds(
    *,
    page_size: int,
    max_pages: int,
    max_page_size: int = API_MAX_PAGE_SIZE,
    max_allowed_pages: int = MAX_COLLECTION_MAX_PAGES,
) -> None:
    """Defensively validate bounds used by internal pagination helpers."""
    if isinstance(page_size, bool) or not isinstance(page_size, int):
        raise ValidationError("Field page_size must be an integer.")
    if not 1 <= page_size <= max_page_size:
        raise ValidationError(f"Field page_size must be between 1 and {max_page_size}.")
    if isinstance(max_pages, bool) or not isinstance(max_pages, int):
        raise ValidationError("Field max_pages must be an integer.")
    if not 1 <= max_pages <= max_allowed_pages:
        raise ValidationError(f"Field max_pages must be between 1 and {max_allowed_pages}.")


def list_page_items(response: Any, *, path: str) -> list[Any]:
    """Require the list response shape documented for offset-paginated endpoints."""
    if isinstance(response, list):
        return response
    raise ConfigError(f"{path} pagination expected a list response from Kaiten.")


async def fetch_all_offset_pages(
    client,
    path: str,
    *,
    timeout: float,
    params: dict[str, Any] | None = None,
    page_size: int = API_MAX_PAGE_SIZE,
    max_pages: int = DEFAULT_COLLECTION_MAX_PAGES,
    extract_items: Callable[[Any], list[Any]] | None = None,
    reporter=None,
) -> list[Any]:
    """Fetch a complete collection or fail instead of returning a silent truncation."""
    validate_page_bounds(page_size=page_size, max_pages=max_pages)
    base_params = dict(params or {})
    rows: list[Any] = []

    if reporter is not None:
        reporter(f"pagination: path={path} page_size={page_size} max_pages={max_pages}")

    for page_index in range(max_pages):
        page_params = {
            **base_params,
            "limit": page_size,
            "offset": page_index * page_size,
        }
        response = await client.get(path, params=page_params, timeout=timeout)
        page = (
            extract_items(response)
            if extract_items is not None
            else list_page_items(response, path=path)
        )
        rows.extend(page)
        if len(page) < page_size:
            return rows

    raise ConfigError(
        f"{path} pagination reached {max_pages} full pages of {page_size} rows; "
        f"refusing to return a possibly truncated result ({len(rows)} rows read). "
        "Increase max_pages after reviewing the expected collection size."
    )
