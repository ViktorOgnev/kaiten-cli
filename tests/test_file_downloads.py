from __future__ import annotations

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import TransportError, ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def test_resolve_download_file_alias():
    assert resolve_tool("kaiten_download_file").canonical_name == "files.download"


@pytest.mark.asyncio
@respx.mock
async def test_download_document_file_from_entity(monkeypatch, tmp_path):
    _env(monkeypatch)
    resolve_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/documents/doc-1/files/file-1",
        params={"prevent_redirect": "true", "response_type": "json"},
    ).mock(return_value=Response(200, json={"url": "https://storage.example.test/file.txt"}))
    storage_route = respx.get("https://storage.example.test/file.txt").mock(
        return_value=Response(200, content=b"hello", headers={"content-type": "text/plain"})
    )

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {
            "entity_type": "document",
            "document_uid": "doc-1",
            "file_id": "file-1",
            "output": str(tmp_path),
        },
    )
    result = await execute_tool(tool, payload)

    assert resolve_route.called
    assert storage_route.called
    target = tmp_path / "file.txt"
    assert target.read_bytes() == b"hello"
    assert result["path"] == str(target)
    assert result["bytes"] == 5
    assert result["resumed"] is False
    assert result["content_type"] == "text/plain"


@pytest.mark.asyncio
@respx.mock
async def test_download_card_file_asks_for_json_not_redirect(monkeypatch, tmp_path):
    _env(monkeypatch)
    resolve_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/cards/123/files/file-1",
        params={"prevent_redirect": "true", "response_type": "json"},
    ).mock(return_value=Response(200, json={"url": "https://storage.example.test/card.bin"}))
    respx.get("https://storage.example.test/card.bin").mock(return_value=Response(200, content=b"card"))

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {
            "entity_type": "card",
            "card_id": 123,
            "file_id": "file-1",
            "output": str(tmp_path / "card.bin"),
        },
    )
    result = await execute_tool(tool, payload)

    assert resolve_route.called
    assert (tmp_path / "card.bin").read_bytes() == b"card"
    assert result["source_kind"] == "kaiten_api"


@pytest.mark.asyncio
@respx.mock
async def test_download_from_report_api_url(monkeypatch, tmp_path):
    _env(monkeypatch)
    resolve_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/documents/doc-1/files/file-1",
        params={"prevent_redirect": "true", "response_type": "json"},
    ).mock(return_value=Response(200, json={"url": "https://storage.example.test/from-url.txt"}))
    respx.get("https://storage.example.test/from-url.txt").mock(return_value=Response(200, content=b"url"))

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {
            "url": "https://hq.kaiten.ru/api/documents/doc-1/files/file-1",
            "output": str(tmp_path),
        },
    )
    result = await execute_tool(tool, payload)

    assert resolve_route.called
    assert (tmp_path / "from-url.txt").read_bytes() == b"url"
    assert result["file_id"] == "file-1"


@pytest.mark.asyncio
@respx.mock
async def test_download_from_internal_files_url(monkeypatch, tmp_path):
    _env(monkeypatch)
    document_uid = "426e98ee-4451-4f2b-972c-3d655f8d23d1"
    file_uid = "8b461699-43de-4316-a6c2-3a7e11fb8323"
    company_uid = "4e2fe465-1a1a-445f-8f1b-7ca3d13884f9"
    resolve_route = respx.get(
        f"https://sandbox.kaiten.ru/api/latest/documents/{document_uid}/files/{file_uid}",
        params={"prevent_redirect": "true", "response_type": "json"},
    ).mock(return_value=Response(200, json={"url": "https://storage.example.test/image.png"}))
    respx.get("https://storage.example.test/image.png").mock(return_value=Response(200, content=b"png"))

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {
            "url": (
                f"https://files/companies/{company_uid}/documents/{document_uid}/{file_uid}.png"
            ),
            "output": str(tmp_path),
        },
    )
    result = await execute_tool(tool, payload)

    assert resolve_route.called
    assert (tmp_path / "image.png").read_bytes() == b"png"
    assert result["source_kind"] == "kaiten_internal_file_url"


@pytest.mark.asyncio
@respx.mock
async def test_download_resumes_part_file_with_range(monkeypatch, tmp_path):
    _env(monkeypatch)
    target = tmp_path / "file.txt"
    target.with_name("file.txt.part").write_bytes(b"abc")
    storage_route = respx.get("https://storage.example.test/file.txt").mock(
        return_value=Response(206, content=b"def")
    )

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {"url": "https://storage.example.test/file.txt", "output": str(target)},
    )
    result = await execute_tool(tool, payload)

    assert storage_route.called
    assert storage_route.calls[0].request.headers["range"] == "bytes=3-"
    assert target.read_bytes() == b"abcdef"
    assert not target.with_name("file.txt.part").exists()
    assert result["resumed"] is True


@pytest.mark.asyncio
@respx.mock
async def test_download_refuses_resume_when_range_is_ignored(monkeypatch, tmp_path):
    _env(monkeypatch)
    target = tmp_path / "file.txt"
    target.with_name("file.txt.part").write_bytes(b"abc")
    respx.get("https://storage.example.test/file.txt").mock(return_value=Response(200, content=b"def"))

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {"url": "https://storage.example.test/file.txt", "output": str(target)},
    )

    with pytest.raises(TransportError, match="did not honor the Range"):
        await execute_tool(tool, payload)
    assert target.with_name("file.txt.part").read_bytes() == b"abc"


@pytest.mark.asyncio
@respx.mock
async def test_download_refreshes_expired_signed_url(monkeypatch, tmp_path):
    _env(monkeypatch)
    resolve_route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/documents/doc-1/files/file-1",
        params={"prevent_redirect": "true", "response_type": "json"},
    ).mock(
        side_effect=[
            Response(200, json={"url": "https://storage.example.test/expired.txt"}),
            Response(200, json={"url": "https://storage.example.test/fresh.txt"}),
        ]
    )
    expired_route = respx.get("https://storage.example.test/expired.txt").mock(return_value=Response(403))
    fresh_route = respx.get("https://storage.example.test/fresh.txt").mock(
        return_value=Response(200, content=b"fresh")
    )

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {
            "entity_type": "document",
            "document_uid": "doc-1",
            "file_id": "file-1",
            "output": str(tmp_path / "fresh.txt"),
        },
    )
    result = await execute_tool(tool, payload)

    assert resolve_route.call_count == 2
    assert expired_route.called
    assert fresh_route.called
    assert (tmp_path / "fresh.txt").read_bytes() == b"fresh"
    assert result["bytes"] == 5


@pytest.mark.asyncio
@respx.mock
async def test_download_refuses_existing_output_without_overwrite(monkeypatch, tmp_path):
    _env(monkeypatch)
    target = tmp_path / "file.txt"
    target.write_bytes(b"old")
    respx.get("https://storage.example.test/file.txt").mock(return_value=Response(200, content=b"new"))

    tool = resolve_tool("files.download")
    payload = merge_inputs(
        tool,
        {"url": "https://storage.example.test/file.txt", "output": str(target)},
    )

    with pytest.raises(ValidationError, match="already exists"):
        await execute_tool(tool, payload)
    assert target.read_bytes() == b"old"
