from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli import __version__
from kaiten_cli.app import cli
from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def test_resolve_upload_file_alias():
    assert resolve_tool("kaiten_upload_card_file").canonical_name == "files.upload"


def test_files_upload_is_put_mutation_without_cache():
    tool = resolve_tool("files.upload")

    assert tool.operation.method == "PUT"
    assert tool.is_mutation is True
    assert tool.cache_policy == "none"
    assert tool.execution_mode == "custom"


def test_build_request_for_upload_card_file(tmp_path):
    upload = tmp_path / "report.json"
    upload.write_text("{}", encoding="utf-8")

    tool = resolve_tool("files.upload")
    payload = merge_inputs(tool, {"card_id": 10, "file": str(upload)})
    path, query, body = build_request(tool, payload)

    assert path == "/cards/10/files"
    assert query is None
    assert body is None


@pytest.mark.asyncio
@respx.mock
async def test_upload_card_file_sends_multipart_put(monkeypatch, tmp_path):
    _env(monkeypatch)
    upload = tmp_path / "upload.txt"
    upload.write_text("hello upload", encoding="utf-8")
    route = respx.put("https://sandbox.kaiten.ru/api/latest/cards/123/files").mock(
        return_value=Response(
            200,
            json={
                "id": 2177127,
                "card_id": 123,
                "name": "upload.txt",
                "size": 12,
                "type": 1,
                "external": False,
                "url": "https://files.example/upload.txt",
            },
        )
    )

    tool = resolve_tool("files.upload")
    payload = merge_inputs(tool, {"card_id": 123, "file": str(upload)})
    result = await execute_tool(tool, payload)

    assert route.called
    request = route.calls[0].request
    assert request.headers["authorization"] == "Bearer test-token"
    assert request.headers["accept"] == "application/json"
    assert request.headers["user-agent"] == f"kaiten-cli/{__version__}"
    assert request.headers["x-kaiten-client-type"] == "cli"
    assert request.headers["x-kaiten-client-name"] == "kaiten-cli"
    assert request.headers["x-kaiten-client-version"] == __version__
    assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert request.headers["content-type"] != "application/json"
    body = request.content
    assert b'name="file"' in body
    assert b'filename="upload.txt"' in body
    assert b"Content-Type: text/plain" in body
    assert b"hello upload" in body
    assert result["id"] == 2177127
    assert result["name"] == "upload.txt"


@respx.mock
def test_cli_files_upload_uses_dynamic_command_path(runner, tmp_path):
    upload = tmp_path / "cli.bin"
    upload.write_bytes(b"cli")
    route = respx.put("https://sandbox.kaiten.ru/api/latest/cards/321/files").mock(
        return_value=Response(200, json={"id": 1, "card_id": 321, "name": "cli.bin"})
    )

    result = runner.invoke(
        cli,
        ["--json", "files", "upload", "--card-id", "321", "--file", str(upload)],
        env={"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"},
    )

    assert result.exit_code == 0
    assert route.called
    payload = json.loads(result.output)
    assert payload["success"] is True
    assert payload["data"]["id"] == 1


@pytest.mark.asyncio
async def test_upload_card_file_rejects_missing_file(monkeypatch, tmp_path):
    _env(monkeypatch)
    tool = resolve_tool("files.upload")
    payload = merge_inputs(tool, {"card_id": 123, "file": str(tmp_path / "missing.txt")})

    with pytest.raises(ValidationError, match="Upload file does not exist"):
        await execute_tool(tool, payload)


@pytest.mark.asyncio
async def test_upload_card_file_rejects_directory(monkeypatch, tmp_path):
    _env(monkeypatch)
    tool = resolve_tool("files.upload")
    payload = merge_inputs(tool, {"card_id": 123, "file": str(tmp_path)})

    with pytest.raises(ValidationError, match="Upload path is not a file"):
        await execute_tool(tool, payload)
