from __future__ import annotations

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import MutationBlockedError
from kaiten_cli.models import CACHE_POLICY_NONE
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.files import resolve_download_source


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


@pytest.mark.parametrize(
    ("name", "payload", "path"),
    [
        (
            "private-card-files.upload",
            {"card_uid": "card-1"},
            "/cards/card-1/files",
        ),
        (
            "private-comment-files.upload",
            {"card_uid": "card-1", "comment_uid": "comment-1"},
            "/cards/card-1/comments/comment-1/files",
        ),
        (
            "private-custom-property-files.upload",
            {"card_uid": "card-1", "property_uid": "property-1"},
            "/cards/card-1/custom-properties/property-1/files",
        ),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_private_uploads_use_multipart_post(monkeypatch, tmp_path, name, payload, path):
    _env(monkeypatch)
    upload = tmp_path / "private.txt"
    upload.write_text("private payload", encoding="utf-8")
    route = respx.post(f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"id": "file-1", "name": "private.txt"})
    )
    tool = resolve_tool(name)
    merged = merge_inputs(tool, {**payload, "file": str(upload)})

    result = await execute_tool(tool, merged)

    assert route.called
    request = route.calls[0].request
    assert request.method == "POST"
    assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"' in request.content
    assert b'filename="private.txt"' in request.content
    assert b"private payload" in request.content
    assert result["id"] == "file-1"


@pytest.mark.parametrize(
    ("name", "payload", "path"),
    [
        (
            "private-card-files.delete",
            {"card_uid": "card-1", "file_id": "file-1"},
            "/cards/card-1/files/file-1",
        ),
        (
            "private-comment-files.delete",
            {"card_uid": "card-1", "comment_uid": "comment-1", "file_id": "file-1"},
            "/cards/card-1/comments/comment-1/files/file-1",
        ),
        (
            "private-custom-property-files.delete",
            {"card_uid": "card-1", "property_uid": "property-1", "file_id": "file-1"},
            "/cards/card-1/custom-properties/property-1/files/file-1",
        ),
    ],
)
def test_private_delete_routes(name, payload, path):
    tool = resolve_tool(name)
    request = build_request(tool, merge_inputs(tool, payload))

    assert tool.operation.method == "DELETE"
    assert request == (path, None, None)


@pytest.mark.parametrize(
    ("name", "payload", "path"),
    [
        (
            "private-card-files.get",
            {"card_uid": "card-1", "file_id": "file-1"},
            "/cards/card-1/files/file-1",
        ),
        (
            "private-comment-files.get",
            {"card_uid": "card-1", "comment_uid": "new", "file_id": "file-1"},
            "/cards/card-1/comments/new/files/file-1",
        ),
        (
            "private-custom-property-files.get",
            {"card_uid": "card-1", "property_uid": "property-1", "file_id": "file-1"},
            "/cards/card-1/custom-properties/property-1/files/file-1",
        ),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_restricted_access_metadata_gets_are_uncached_read_only_reads(
    monkeypatch, name, payload, path
):
    _env(monkeypatch)
    signed_url = "https://storage.example.test/signed-file"
    route = respx.get(f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"id": "file-1", "url": signed_url})
    )
    tool = resolve_tool(name)

    result = await execute_tool(tool, merge_inputs(tool, payload), read_only=True)

    assert route.called
    assert tool.operation.method == "GET"
    assert tool.cache_policy == CACHE_POLICY_NONE
    assert tool.read_only_allowed is True
    assert result == {"id": "file-1", "url": signed_url}


@pytest.mark.parametrize(
    ("name", "payload", "path"),
    [
        (
            "private-card-files.update",
            {
                "card_uid": "card-1",
                "file_id": "file-1",
                "name": "report-final.pdf",
                "card_cover": True,
            },
            "/cards/card-1/files/file-1",
        ),
        (
            "private-comment-files.update",
            {
                "card_uid": "card-1",
                "comment_uid": "new",
                "file_id": "file-1",
                "name": "evidence-final.png",
                "card_cover": False,
            },
            "/cards/card-1/comments/new/files/file-1",
        ),
        (
            "private-custom-property-files.update",
            {
                "card_uid": "card-1",
                "property_uid": "property-1",
                "file_id": "file-1",
                "name": "contract-final.pdf",
                "card_cover": True,
            },
            "/cards/card-1/custom-properties/property-1/files/file-1",
        ),
    ],
)
def test_restricted_access_update_contracts(name, payload, path):
    tool = resolve_tool(name)

    request = build_request(tool, merge_inputs(tool, payload))

    assert tool.operation.method == "PATCH"
    assert request == (
        path,
        None,
        {"name": payload["name"], "card_cover": payload["card_cover"]},
    )


@pytest.mark.parametrize(
    ("name", "payload", "path"),
    [
        (
            "private-card-files.delete",
            {"card_uid": "card-1", "file_id": "file-1"},
            "/cards/card-1/files/file-1",
        ),
        (
            "private-comment-files.delete",
            {"card_uid": "card-1", "comment_uid": "comment-1", "file_id": "file-1"},
            "/cards/card-1/comments/comment-1/files/file-1",
        ),
        (
            "private-custom-property-files.delete",
            {"card_uid": "card-1", "property_uid": "property-1", "file_id": "file-1"},
            "/cards/card-1/custom-properties/property-1/files/file-1",
        ),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_private_deletes_execute_without_payload(monkeypatch, name, payload, path):
    _env(monkeypatch)
    route = respx.delete(f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"id": "file-1", "deleted": True})
    )
    tool = resolve_tool(name)

    result = await execute_tool(tool, merge_inputs(tool, payload))

    assert route.called
    assert route.calls[0].request.content == b""
    assert result["deleted"] is True


@pytest.mark.asyncio
async def test_private_upload_is_blocked_in_read_only_mode(monkeypatch, tmp_path):
    _env(monkeypatch)
    upload = tmp_path / "private.txt"
    upload.write_text("private", encoding="utf-8")
    tool = resolve_tool("private-card-files.upload")
    payload = merge_inputs(tool, {"card_uid": "card-1", "file": str(upload)})

    with pytest.raises(MutationBlockedError):
        await execute_tool(tool, payload, read_only=True)


@pytest.mark.parametrize(
    ("name", "payload"),
    [
        (
            "private-card-files.update",
            {"card_uid": "card-1", "file_id": "file-1", "name": "new.txt"},
        ),
        (
            "private-comment-files.update",
            {
                "card_uid": "card-1",
                "comment_uid": "comment-1",
                "file_id": "file-1",
                "name": "new.txt",
            },
        ),
        (
            "private-custom-property-files.update",
            {
                "card_uid": "card-1",
                "property_uid": "property-1",
                "file_id": "file-1",
                "name": "new.txt",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_restricted_access_updates_are_blocked_in_read_only_mode(name, payload):
    tool = resolve_tool(name)

    with pytest.raises(MutationBlockedError):
        await execute_tool(tool, merge_inputs(tool, payload), read_only=True)


def test_private_download_resolution_for_all_three_families():
    card = resolve_download_source(
        {"entity_type": "card", "card_uid": "card-1", "file_id": "file-1"}
    )
    comment = resolve_download_source(
        {
            "entity_type": "comment",
            "card_uid": "card-1",
            "comment_uid": "comment-1",
            "file_id": "file-1",
        }
    )
    custom_property = resolve_download_source(
        {
            "entity_type": "custom_property",
            "card_uid": "card-1",
            "custom_property_uid": "property-1",
            "file_id": "file-1",
        }
    )

    assert card.endpoint_path == "/cards/card-1/files/file-1"
    assert comment.endpoint_path == "/cards/card-1/comments/comment-1/files/file-1"
    assert custom_property.endpoint_path == (
        "/cards/card-1/custom-properties/property-1/files/file-1"
    )


def test_private_file_aliases_resolve():
    assert (
        resolve_tool("kaiten_upload_private_card_file").canonical_name
        == "private-card-files.upload"
    )
    assert (
        resolve_tool("kaiten_delete_private_comment_file").canonical_name
        == "private-comment-files.delete"
    )
    assert (
        resolve_tool("kaiten_upload_private_custom_property_file").canonical_name
        == "private-custom-property-files.upload"
    )
    assert resolve_tool("kaiten_get_private_card_file").canonical_name == "private-card-files.get"
    assert (
        resolve_tool("kaiten_update_private_card_file").canonical_name
        == "private-card-files.update"
    )
    assert (
        resolve_tool("kaiten_get_private_comment_file").canonical_name
        == "private-comment-files.get"
    )
    assert (
        resolve_tool("kaiten_update_private_comment_file").canonical_name
        == "private-comment-files.update"
    )
    assert (
        resolve_tool("kaiten_get_private_custom_property_file").canonical_name
        == "private-custom-property-files.get"
    )
    assert (
        resolve_tool("kaiten_update_private_custom_property_file").canonical_name
        == "private-custom-property-files.update"
    )
