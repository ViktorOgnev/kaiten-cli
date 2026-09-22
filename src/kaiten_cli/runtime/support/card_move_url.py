"""Helpers for moving cards from Kaiten UI URLs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from kaiten_cli.errors import ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.endpoints import KAITEN_HOST_SUFFIX, normalize_profile_domain

COLUMN_CHILD_KEYS = ("columns", "subcolumns", "children")


@dataclass(frozen=True, slots=True)
class ParsedCardUrl:
    domain: str
    space_id: int
    card_ref: str


@dataclass(frozen=True, slots=True)
class ParsedTargetUrl:
    domain: str
    space_id: int
    column_id: int


def normalize_kaiten_domain(value: str) -> str:
    return normalize_profile_domain(value)


def _domain_from_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    hostname = (parsed.hostname or "").lower()
    if not hostname.endswith(KAITEN_HOST_SUFFIX):
        raise ValidationError(tr("URL must point to a Kaiten tenant: {value_0}", value_0=raw_url))
    return normalize_kaiten_domain(hostname)


def _path_segments(raw_url: str) -> list[str]:
    parsed = urlparse(raw_url)
    return [unquote(segment) for segment in parsed.path.split("/") if segment]


def _space_id_from_segments(segments: list[str], *, raw_url: str) -> int:
    try:
        space_index = segments.index("space")
        return int(segments[space_index + 1])
    except (ValueError, IndexError) as exc:
        raise ValidationError(
            tr("URL must contain /space/<space_id>/: {value_0}", value_0=raw_url)
        ) from exc


def parse_card_url(raw_url: str) -> ParsedCardUrl:
    segments = _path_segments(raw_url)
    try:
        card_index = segments.index("card")
        if card_index == 0 or segments[card_index - 1] != "boards":
            raise ValueError
        card_ref = segments[card_index + 1]
    except (ValueError, IndexError) as exc:
        raise ValidationError(
            tr("Card URL must contain /boards/card/<id-or-key>: {value_0}", value_0=raw_url)
        ) from exc
    if not card_ref:
        raise ValidationError(
            tr("Card URL must contain a card ID or key: {value_0}", value_0=raw_url)
        )
    return ParsedCardUrl(
        domain=_domain_from_url(raw_url),
        space_id=_space_id_from_segments(segments, raw_url=raw_url),
        card_ref=card_ref,
    )


def parse_target_url(raw_url: str) -> ParsedTargetUrl:
    parsed = urlparse(raw_url)
    segments = _path_segments(raw_url)
    if "boards" not in segments:
        raise ValidationError(
            tr("Target URL must point to a board view: {value_0}", value_0=raw_url)
        )
    query = parse_qs(parsed.query)
    focus = (query.get("focus") or [""])[0]
    if focus != "column":
        raise ValidationError(tr("Target URL must use focus=column."))
    focus_ids = query.get("focusId")
    if not focus_ids or not focus_ids[0]:
        raise ValidationError(tr("Target URL must include focusId=<column_id>."))
    try:
        column_id = int(focus_ids[0])
    except ValueError as exc:
        raise ValidationError(tr("Target URL focusId must be an integer column ID.")) from exc
    return ParsedTargetUrl(
        domain=_domain_from_url(raw_url),
        space_id=_space_id_from_segments(segments, raw_url=raw_url),
        column_id=column_id,
    )


def validate_url_domain(url_domain: str, profile_domain: str, *, label: str) -> None:
    normalized_profile = normalize_kaiten_domain(profile_domain)
    if url_domain != normalized_profile:
        raise ValidationError(
            tr(
                "{value_0} host {value_1}.kaiten.ru does not match profile domain {value_2}.kaiten.ru. Pass --profile for the {value_3} tenant.",
                value_0=label,
                value_1=url_domain,
                value_2=normalized_profile,
                value_3=url_domain,
            )
        )


def _iter_column_nodes(columns: Any):
    if not isinstance(columns, list):
        return
    for column in columns:
        if not isinstance(column, dict):
            continue
        yield column
        for key in COLUMN_CHILD_KEYS:
            child_columns = column.get(key)
            if child_columns is not columns:
                yield from _iter_column_nodes(child_columns)


def find_column(board: dict[str, Any], column_id: int) -> dict[str, Any] | None:
    for column in _iter_column_nodes(board.get("columns")):
        if column.get("id") == column_id:
            return column
    return None


def lane_title(board: dict[str, Any], lane_id: int | None) -> str | None:
    if lane_id is None:
        return None
    for lane in board.get("lanes", []):
        if isinstance(lane, dict) and lane.get("id") == lane_id:
            return lane.get("title")
    return None


async def resolve_move_target(
    client,
    target: ParsedTargetUrl,
    *,
    lane_id: int | None,
    timeout: float,
) -> dict[str, Any]:
    boards = await client.get(f"/spaces/{target.space_id}/boards", timeout=timeout)
    if not isinstance(boards, list):
        raise ValidationError(
            tr("Expected a board list for space {value_0}.", value_0=target.space_id)
        )

    for board_summary in boards:
        if not isinstance(board_summary, dict) or "id" not in board_summary:
            continue
        board_id = board_summary["id"]
        board = board_summary
        if "columns" not in board or "lanes" not in board:
            board = await client.get(f"/boards/{board_id}", timeout=timeout)
        if not isinstance(board, dict):
            continue

        column = find_column(board, target.column_id)
        if column is None:
            continue

        lanes = [lane for lane in board.get("lanes", []) if isinstance(lane, dict)]
        resolved_lane_id = lane_id
        if resolved_lane_id is not None:
            lane_ids = {lane.get("id") for lane in lanes}
            if lane_ids and resolved_lane_id not in lane_ids:
                raise ValidationError(
                    tr(
                        "Lane {value_0} does not belong to target board {value_1}.",
                        value_0=resolved_lane_id,
                        value_1=board_id,
                    )
                )
        elif len(lanes) == 1 and isinstance(lanes[0].get("id"), int):
            resolved_lane_id = lanes[0]["id"]
        elif len(lanes) > 1:
            raise ValidationError(
                tr(
                    "Target board {value_0} has {value_1} lanes; pass --lane-id explicitly.",
                    value_0=board_id,
                    value_1=len(lanes),
                )
            )

        return {
            "space_id": target.space_id,
            "board_id": board_id,
            "board_title": board.get("title"),
            "column_id": target.column_id,
            "column_title": column.get("title"),
            "lane_id": resolved_lane_id,
            "lane_title": lane_title(board, resolved_lane_id),
        }

    raise ValidationError(
        tr(
            "Column {value_0} was not found in space {value_1}.",
            value_0=target.column_id,
            value_1=target.space_id,
        )
    )
