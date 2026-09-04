"""Bounded company-user pagination helpers."""

from __future__ import annotations

from typing import Any

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.support.pagination import (
    LEGACY_OVERSIZED_FIRST_PAGE,
    LEGACY_REPEATED_FIRST_PAGE,
    REPEATED_PAGE_AFTER_PROGRESS,
    OffsetPageGuard,
    report_legacy_pagination,
)


COMPANY_USERS_MAX_PAGE_SIZE = 100
COMPANY_USERS_DEFAULT_MAX_PAGES = 100
COMPANY_USERS_MAX_PAGES = 1000


def validate_company_users_list_all(tool, payload: dict[str, Any]) -> None:
    page_size = payload.get("page_size", COMPANY_USERS_MAX_PAGE_SIZE)
    max_pages = payload.get("max_pages", COMPANY_USERS_DEFAULT_MAX_PAGES)
    if not isinstance(page_size, int) or not 1 <= page_size <= COMPANY_USERS_MAX_PAGE_SIZE:
        raise ValidationError(
            f"Field page_size must be between 1 and {COMPANY_USERS_MAX_PAGE_SIZE}."
        )
    if not isinstance(max_pages, int) or not 1 <= max_pages <= COMPANY_USERS_MAX_PAGES:
        raise ValidationError(f"Field max_pages must be between 1 and {COMPANY_USERS_MAX_PAGES}.")


def _page_items(response: Any) -> list[Any]:
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        for key in ("records", "users", "data"):
            value = response.get(key)
            if isinstance(value, list):
                return value
    raise ValidationError("Company users pagination expected a list response from Kaiten.")


async def execute_company_users_list_all(
    client,
    tool,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter,
) -> list[Any]:
    del tool, body
    page_size = payload.get("page_size", COMPANY_USERS_MAX_PAGE_SIZE)
    max_pages = payload.get("max_pages", COMPANY_USERS_DEFAULT_MAX_PAGES)
    base_query = dict(query or {})
    base_query.setdefault("for_members_section", True)
    users: list[Any] = []
    guard = OffsetPageGuard(page_size=page_size)

    if reporter:
        reporter(
            "execution: aggregated bounded pagination over /company/users "
            f"with page_size={page_size} max_pages={max_pages}"
        )

    for page_index in range(max_pages):
        page_query = {
            **base_query,
            "limit": page_size,
            "offset": page_index * page_size,
        }
        page = _page_items(await client.get(path, params=page_query, timeout=timeout))
        page_state = guard.observe(page, page_index=page_index)
        if page_state == LEGACY_OVERSIZED_FIRST_PAGE:
            report_legacy_pagination(
                client,
                path=path,
                reason=page_state,
                rows=len(page),
                reporter=reporter,
            )
            return page
        if page_state == LEGACY_REPEATED_FIRST_PAGE:
            report_legacy_pagination(
                client,
                path=path,
                reason=page_state,
                rows=len(users),
                reporter=reporter,
            )
            return users
        if page_state == REPEATED_PAGE_AFTER_PROGRESS:
            raise ValidationError(
                "Company users pagination repeated a previously received page after progress; "
                "refusing to return a possibly duplicated or truncated result."
            )
        users.extend(page)
        if len(page) < page_size:
            return users

    raise ValidationError(
        "Company users pagination reached max_pages while the last page was full; "
        f"refusing to return a silently truncated result ({len(users)} users read). "
        "Increase --max-pages after reviewing the expected company size."
    )
