from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.card_move_url import parse_card_url, parse_target_url, validate_url_domain


CARD_URL = "https://sandbox.kaiten.ru/space/1/boards/card/STORY-1"
TARGET_URL = "https://sandbox.kaiten.ru/space/20/boards?focus=column&focusId=10"


def test_parse_card_and_target_urls():
    card = parse_card_url(CARD_URL)
    target = parse_target_url(TARGET_URL)

    assert card.domain == "sandbox"
    assert card.space_id == 1
    assert card.card_ref == "STORY-1"
    assert target.domain == "sandbox"
    assert target.space_id == 20
    assert target.column_id == 10


def test_validate_url_domain_accepts_full_kaiten_profile_url():
    validate_url_domain("sandbox", "https://sandbox.kaiten.ru", label="Card URL")


@pytest.mark.parametrize(
    ("target_url", "message"),
    [
        ("https://sandbox.kaiten.ru/space/20/boards?focus=card&focusId=10", "focus=column"),
        ("https://sandbox.kaiten.ru/space/20/boards?focus=column", "focusId"),
        ("https://sandbox.kaiten.ru/space/20/boards?focus=column&focusId=x", "integer"),
    ],
)
def test_parse_target_url_rejects_unsupported_targets(target_url, message):
    with pytest.raises(ValidationError, match=message):
        parse_target_url(target_url)


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_move_by_url_resolves_subcolumn_and_verifies(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/20/boards").mock(
        return_value=Response(200, json=[{"id": 100, "title": "Triage"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={
                "id": 100,
                "title": "Triage",
                "columns": [
                    {
                        "id": 9,
                        "title": "Parent",
                        "subcolumns": [{"id": 10, "title": "Needs decision"}],
                    }
                ],
                "lanes": [{"id": 5, "title": "Default"}],
            },
        )
    )
    patch_route = respx.patch("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(200, json={"id": 1, "title": "Moved"})
    )
    get_route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(
            200,
            json={
                "id": 1,
                "title": "Moved",
                "description": "large",
                "board_id": 100,
                "column_id": 10,
                "lane_id": 5,
            },
        )
    )

    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(
        tool,
        {
            "card_url": CARD_URL,
            "target_url": TARGET_URL,
            "compact": True,
            "fields": "id,title,board_id,column_id,lane_id",
        },
    )
    result = await execute_tool(tool, payload)

    assert patch_route.called
    assert get_route.called
    assert json.loads(patch_route.calls[0].request.content) == {
        "board_id": 100,
        "column_id": 10,
        "lane_id": 5,
    }
    assert result["verified"] is True
    assert result["target"]["board_id"] == 100
    assert result["target"]["column_id"] == 10
    assert result["card"] == {
        "id": 1,
        "title": "Moved",
        "board_id": 100,
        "column_id": 10,
        "lane_id": 5,
    }


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_move_by_url_requires_lane_for_multi_lane_board(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/20/boards").mock(
        return_value=Response(200, json=[{"id": 100}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={
                "id": 100,
                "columns": [{"id": 10, "title": "Needs decision"}],
                "lanes": [{"id": 5}, {"id": 6}],
            },
        )
    )
    patch_route = respx.patch("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(200, json={"id": 1})
    )

    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(tool, {"card_url": CARD_URL, "target_url": TARGET_URL})

    with pytest.raises(ValidationError, match="pass --lane-id"):
        await execute_tool(tool, payload)
    assert not patch_route.called


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_move_by_url_uses_explicit_lane_and_sort_order(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/20/boards").mock(
        return_value=Response(200, json=[{"id": 100}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={
                "id": 100,
                "columns": [{"id": 10, "title": "Needs decision"}],
                "lanes": [{"id": 5, "title": "A"}, {"id": 6, "title": "B"}],
            },
        )
    )
    patch_route = respx.patch("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(
            200,
            json={"id": 1, "board_id": 100, "column_id": 10, "lane_id": 6},
        )
    )

    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(
        tool,
        {
            "card_url": CARD_URL,
            "target_url": TARGET_URL,
            "lane_id": 6,
            "sort_order": 1.5,
            "verify": False,
        },
    )
    result = await execute_tool(tool, payload)

    assert json.loads(patch_route.calls[0].request.content) == {
        "board_id": 100,
        "column_id": 10,
        "lane_id": 6,
        "sort_order": 1.5,
    }
    assert result["verified"] is False
    assert result["target"]["lane_title"] == "B"


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_move_by_url_reports_verify_mismatch(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/20/boards").mock(
        return_value=Response(200, json=[{"id": 100}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={
                "id": 100,
                "columns": [{"id": 10, "title": "Needs decision"}],
                "lanes": [{"id": 5}],
            },
        )
    )
    respx.patch("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(200, json={"id": 1})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(200, json={"id": 1, "board_id": 100, "column_id": 11, "lane_id": 5})
    )

    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(tool, {"card_url": CARD_URL, "target_url": TARGET_URL})

    with pytest.raises(ValidationError, match="column_id"):
        await execute_tool(tool, payload)


@pytest.mark.asyncio
@respx.mock
async def test_execute_cards_move_by_url_dry_run_skips_patch(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/20/boards").mock(
        return_value=Response(200, json=[{"id": 100}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/boards/100").mock(
        return_value=Response(
            200,
            json={
                "id": 100,
                "columns": [{"id": 10, "title": "Needs decision"}],
                "lanes": [{"id": 5}],
            },
        )
    )
    patch_route = respx.patch("https://sandbox.kaiten.ru/api/latest/cards/STORY-1").mock(
        return_value=Response(200, json={"id": 1})
    )

    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(
        tool,
        {"card_url": CARD_URL, "target_url": TARGET_URL, "dry_run": True},
    )
    result = await execute_tool(tool, payload)

    assert not patch_route.called
    assert result["dry_run"] is True
    assert result["would_patch"] == {"board_id": 100, "column_id": 10, "lane_id": 5}


@pytest.mark.asyncio
async def test_execute_cards_move_by_url_rejects_profile_host_mismatch(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("cards.move-by-url")
    payload = merge_inputs(
        tool,
        {
            "card_url": "https://hq.kaiten.ru/space/1/boards/card/STORY-1",
            "target_url": "https://hq.kaiten.ru/space/20/boards?focus=column&focusId=10",
        },
    )

    with pytest.raises(ValidationError, match="does not match profile domain"):
        await execute_tool(tool, payload)
