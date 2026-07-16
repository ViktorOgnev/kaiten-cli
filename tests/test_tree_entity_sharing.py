from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import BatchExecutionError, MutationBlockedError, ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.tree_sharing import shape_tree_entity_share

ENTITY_1 = "11111111-1111-4111-8111-111111111111"
ENTITY_2 = "22222222-2222-4222-8222-222222222222"
SHARE_1 = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
SHARE_2 = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
FUTURE = "2099-01-01T00:00:00Z"


def _share_payload(share_uid: str, **overrides):
    payload = {
        "uid": share_uid,
        "expired_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "is_expired": False,
        "disabled": False,
    }
    payload.update(overrides)
    return payload


def _credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def test_share_tools_build_expected_requests():
    cases = [
        ("tree-entities.share.get", "GET", None),
        ("tree-entities.share.enable", "POST", {"expired_at": FUTURE}),
        ("tree-entities.share.update", "PATCH", {"expired_at": None}),
        ("tree-entities.share.disable", "DELETE", None),
    ]

    for canonical_name, method, expected_body in cases:
        tool = resolve_tool(canonical_name)
        raw = {"entity_uid": ENTITY_1}
        if canonical_name.endswith("enable"):
            raw["expired_at"] = FUTURE
        if canonical_name.endswith("update"):
            raw["expired_at"] = "null"
        payload = merge_inputs(tool, raw)
        path, query, body = build_request(tool, payload)

        assert tool.operation.method == method
        assert path == f"/tree-entities/{ENTITY_1}/share"
        assert query is None
        assert body == expected_body


def test_shape_share_builds_tenant_and_custom_host_urls():
    share = _share_payload(SHARE_1)

    tenant = shape_tree_entity_share(
        entity_uid=ENTITY_1,
        share=share,
        origin="https://sandbox.kaiten.ru",
        changed=False,
    )
    local = shape_tree_entity_share(
        entity_uid=ENTITY_1,
        share=share,
        origin="http://localhost:3000/",
        changed=False,
    )

    assert tenant["public_url"] == f"https://sandbox.kaiten.ru/p/{SHARE_1}"
    assert local["public_url"] == f"http://localhost:3000/p/{SHARE_1}"
    assert tenant["shared"] is True


def test_shape_share_keeps_disabled_or_expired_uid_but_marks_inactive():
    disabled = shape_tree_entity_share(
        entity_uid=ENTITY_1,
        share=_share_payload(SHARE_1, disabled=True),
        origin="https://sandbox.kaiten.ru",
        changed=False,
    )
    expired = shape_tree_entity_share(
        entity_uid=ENTITY_1,
        share=_share_payload(SHARE_1, is_expired=True),
        origin="https://sandbox.kaiten.ru",
        changed=False,
    )

    assert disabled["shared"] is False
    assert expired["shared"] is False
    assert disabled["uid"] == SHARE_1
    assert expired["public_url"].endswith(SHARE_1)


@pytest.mark.asyncio
@respx.mock
async def test_get_share_returns_existing_public_link(monkeypatch):
    _credentials(monkeypatch)
    route = respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share").mock(
        return_value=Response(200, json=_share_payload(SHARE_1))
    )

    tool = resolve_tool("tree-entities.share.get")
    result = await execute_tool(tool, merge_inputs(tool, {"entity_uid": ENTITY_1}))

    assert route.called
    assert result == {
        "entity_uid": ENTITY_1,
        "shared": True,
        "uid": SHARE_1,
        "public_url": f"https://sandbox.kaiten.ru/p/{SHARE_1}",
        "expired_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "is_expired": False,
        "disabled": False,
        "changed": False,
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_share_returns_explicit_inactive_state_for_null(monkeypatch):
    _credentials(monkeypatch)
    respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share").mock(
        return_value=Response(200, json=None)
    )

    tool = resolve_tool("tree-entities.share.get")
    result = await execute_tool(tool, merge_inputs(tool, {"entity_uid": ENTITY_1}))

    assert result["entity_uid"] == ENTITY_1
    assert result["shared"] is False
    assert result["uid"] is None
    assert result["public_url"] is None
    assert result["changed"] is False


@pytest.mark.asyncio
@respx.mock
async def test_enable_share_creates_when_missing(monkeypatch):
    _credentials(monkeypatch)
    get_route = respx.get(
        f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    ).mock(return_value=Response(200, json=None))
    post_route = respx.post(
        f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share",
        json={"expired_at": FUTURE},
    ).mock(return_value=Response(200, json=_share_payload(SHARE_1, expired_at=FUTURE)))

    tool = resolve_tool("tree-entities.share.enable")
    payload = merge_inputs(tool, {"entity_uid": ENTITY_1, "expired_at": FUTURE})
    result = await execute_tool(tool, payload)

    assert get_route.called
    assert post_route.called
    assert result["shared"] is True
    assert result["changed"] is True
    assert result["expired_at"] == FUTURE


@pytest.mark.asyncio
@respx.mock
async def test_enable_share_is_idempotent_when_already_active(monkeypatch):
    _credentials(monkeypatch)
    get_route = respx.get(
        f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    ).mock(return_value=Response(200, json=_share_payload(SHARE_1)))

    tool = resolve_tool("tree-entities.share.enable")
    result = await execute_tool(tool, merge_inputs(tool, {"entity_uid": ENTITY_1}))

    assert get_route.call_count == 1
    assert result["shared"] is True
    assert result["changed"] is False
    assert respx.calls.last.request.method == "GET"


@pytest.mark.asyncio
@respx.mock
async def test_enable_share_compares_normalized_expiration_semantically(monkeypatch):
    _credentials(monkeypatch)
    get_route = respx.get(
        f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    ).mock(
        return_value=Response(
            200,
            json=_share_payload(SHARE_1, expired_at="2099-01-01T00:00:00.000+00:00"),
        )
    )

    tool = resolve_tool("tree-entities.share.enable")
    result = await execute_tool(
        tool,
        merge_inputs(tool, {"entity_uid": ENTITY_1, "expired_at": FUTURE}),
    )

    assert get_route.call_count == 1
    assert result["changed"] is False
    assert respx.calls.last.request.method == "GET"


@pytest.mark.asyncio
@respx.mock
async def test_enable_share_renews_expired_share_without_changing_uid(monkeypatch):
    _credentials(monkeypatch)
    path = f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    respx.get(path).mock(
        return_value=Response(
            200,
            json=_share_payload(
                SHARE_1,
                expired_at="2020-01-01T00:00:00Z",
                is_expired=True,
            ),
        )
    )
    patch_route = respx.patch(path, json={"expired_at": None}).mock(
        return_value=Response(200, json=_share_payload(SHARE_1))
    )

    tool = resolve_tool("tree-entities.share.enable")
    result = await execute_tool(tool, merge_inputs(tool, {"entity_uid": ENTITY_1}))

    assert patch_route.called
    assert result["uid"] == SHARE_1
    assert result["shared"] is True
    assert result["changed"] is True


@pytest.mark.asyncio
@respx.mock
async def test_enable_disabled_share_reuses_uid_and_applies_requested_expiration(monkeypatch):
    _credentials(monkeypatch)
    path = f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    old_expiration = "2020-01-01T00:00:00Z"
    respx.get(path).mock(
        return_value=Response(
            200,
            json=_share_payload(
                SHARE_1,
                expired_at=old_expiration,
                is_expired=True,
                disabled=True,
            ),
        )
    )
    post_route = respx.post(path).mock(
        return_value=Response(
            200,
            json=_share_payload(SHARE_1, expired_at=old_expiration, is_expired=True),
        )
    )
    patch_route = respx.patch(path, json={"expired_at": FUTURE}).mock(
        return_value=Response(200, json=_share_payload(SHARE_1, expired_at=FUTURE))
    )

    tool = resolve_tool("tree-entities.share.enable")
    result = await execute_tool(
        tool,
        merge_inputs(tool, {"entity_uid": ENTITY_1, "expired_at": FUTURE}),
    )

    assert post_route.called
    assert patch_route.called
    assert result["uid"] == SHARE_1
    assert result["expired_at"] == FUTURE
    assert result["changed"] is True


@pytest.mark.asyncio
@respx.mock
async def test_update_and_disable_are_idempotent(monkeypatch):
    _credentials(monkeypatch)
    path = f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    get_route = respx.get(path).mock(
        side_effect=[
            Response(200, json=_share_payload(SHARE_1)),
            Response(200, json=_share_payload(SHARE_1)),
            Response(200, json=_share_payload(SHARE_1, disabled=True)),
        ]
    )
    delete_route = respx.delete(path).mock(
        return_value=Response(200, json={"message": "Sharing disabled successfully"})
    )

    update_tool = resolve_tool("tree-entities.share.update")
    unchanged = await execute_tool(
        update_tool,
        merge_inputs(update_tool, {"entity_uid": ENTITY_1, "expired_at": "null"}),
    )
    disable_tool = resolve_tool("tree-entities.share.disable")
    disabled = await execute_tool(
        disable_tool, merge_inputs(disable_tool, {"entity_uid": ENTITY_1})
    )
    disabled_again = await execute_tool(
        disable_tool, merge_inputs(disable_tool, {"entity_uid": ENTITY_1})
    )

    assert get_route.call_count == 3
    assert unchanged["changed"] is False
    assert disabled["changed"] is True
    assert disabled["shared"] is False
    assert disabled_again["changed"] is False
    assert delete_route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_batch_get_deduplicates_and_preserves_first_seen_order(monkeypatch):
    _credentials(monkeypatch)
    respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share").mock(
        return_value=Response(200, json=_share_payload(SHARE_1))
    )
    respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_2}/share").mock(
        return_value=Response(200, json=_share_payload(SHARE_2))
    )

    tool = resolve_tool("tree-entities.share.batch-get")
    payload = merge_inputs(
        tool,
        {"entity_uids": json.dumps([ENTITY_2, ENTITY_1, ENTITY_2]), "workers": 2},
    )
    result = await execute_tool(tool, payload)

    assert [item["entity_uid"] for item in result["items"]] == [ENTITY_2, ENTITY_1]
    assert result["errors"] == []
    assert result["meta"] == {
        "requested": 3,
        "requested_count": 3,
        "unique_count": 2,
        "succeeded": 2,
        "failed": 0,
        "changed": 0,
        "unchanged": 2,
        "workers": 2,
    }


@pytest.mark.asyncio
@respx.mock
async def test_batch_enable_reports_changed_unchanged_and_partial_errors(monkeypatch):
    _credentials(monkeypatch)
    path_1 = f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share"
    path_2 = f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_2}/share"
    respx.get(path_1).mock(return_value=Response(200, json=_share_payload(SHARE_1)))
    respx.get(path_2).mock(return_value=Response(403, json={"error": "Access denied"}))

    tool = resolve_tool("tree-entities.share.batch-enable")
    payload = merge_inputs(tool, {"entity_uids": json.dumps([ENTITY_1, ENTITY_2])})
    result = await execute_tool(tool, payload)

    assert [item["entity_uid"] for item in result["items"]] == [ENTITY_1]
    assert result["items"][0]["changed"] is False
    assert result["errors"] == [
        {
            "entity_uid": ENTITY_2,
            "error_type": "api_error",
            "message": "Access denied",
            "status_code": 403,
        }
    ]
    assert result["meta"]["succeeded"] == 1
    assert result["meta"]["failed"] == 1
    assert result["meta"]["changed"] == 0
    assert result["meta"]["unchanged"] == 1


@pytest.mark.asyncio
@respx.mock
async def test_batch_get_raises_structured_error_when_every_entity_fails(monkeypatch):
    _credentials(monkeypatch)
    for entity_uid in (ENTITY_1, ENTITY_2):
        respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{entity_uid}/share").mock(
            return_value=Response(404, json={"error": "not found"})
        )

    tool = resolve_tool("tree-entities.share.batch-get")
    payload = merge_inputs(tool, {"entity_uids": json.dumps([ENTITY_1, ENTITY_2])})

    with pytest.raises(BatchExecutionError) as exc_info:
        await execute_tool(tool, payload)

    assert exc_info.value.data["meta"]["succeeded"] == 0
    assert exc_info.value.data["meta"]["failed"] == 2
    assert [item["entity_uid"] for item in exc_info.value.data["errors"]] == [
        ENTITY_1,
        ENTITY_2,
    ]


def test_share_validation_rejects_bad_uuid_workers_and_past_expiration():
    single = resolve_tool("tree-entities.share.enable")
    with pytest.raises(ValidationError, match="valid UUID"):
        merge_inputs(single, {"entity_uid": "not-a-uuid"})
    with pytest.raises(ValidationError, match="future"):
        merge_inputs(single, {"entity_uid": ENTITY_1, "expired_at": "2020-01-01T00:00:00Z"})
    with pytest.raises(ValidationError, match="invalid type"):
        merge_inputs(single, {"entity_uid": ENTITY_1, "expired_at": 123})

    batch = resolve_tool("tree-entities.share.batch-enable")
    with pytest.raises(ValidationError, match="non-empty array"):
        merge_inputs(batch, {"entity_uids": "[]"})
    with pytest.raises(ValidationError, match="between 1 and 6"):
        merge_inputs(batch, {"entity_uids": json.dumps([ENTITY_1]), "workers": 7})


@pytest.mark.asyncio
async def test_batch_enable_is_blocked_by_read_only_mode(monkeypatch):
    _credentials(monkeypatch)
    tool = resolve_tool("tree-entities.share.batch-enable")
    payload = merge_inputs(tool, {"entity_uids": json.dumps([ENTITY_1])})

    with pytest.raises(MutationBlockedError):
        await execute_tool(tool, payload, read_only=True)


@respx.mock
def test_nested_cli_command_returns_public_link(runner):
    route = respx.get(f"https://sandbox.kaiten.ru/api/latest/tree-entities/{ENTITY_1}/share").mock(
        return_value=Response(200, json=_share_payload(SHARE_1))
    )
    result = runner.invoke(
        cli,
        ["--json", "tree-entities", "share", "get", "--entity-uid", ENTITY_1],
        env={"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"},
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["success"] is True
    assert payload["data"]["public_url"] == f"https://sandbox.kaiten.ru/p/{SHARE_1}"
    assert route.called
