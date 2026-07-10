from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.markdown_export import document_to_markdown


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def test_document_to_markdown_serializes_common_prosemirror_nodes():
    company_uid = "4e2fe465-1a1a-445f-8f1b-7ca3d13884f9"
    document_uid = "426e98ee-4451-4f2b-972c-3d655f8d23d1"
    file_uid = "8b461699-43de-4316-a6c2-3a7e11fb8323"
    markdown = document_to_markdown(
        {
            "uid": document_uid,
            "title": "Spec",
            "data": json.dumps(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [{"type": "text", "text": "Intro"}],
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
                                {"type": "text", "text": " and "},
                                {
                                    "type": "text",
                                    "text": "link",
                                    "marks": [
                                        {"type": "link", "attrs": {"href": "https://example.test"}}
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "check_list",
                            "content": [
                                {
                                    "type": "check_list_item",
                                    "attrs": {"checked": True},
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"type": "text", "text": "done"}],
                                        }
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "table",
                            "content": [
                                {
                                    "type": "table_row",
                                    "content": [
                                        {
                                            "type": "table_header",
                                            "content": [{"type": "text", "text": "A|B"}],
                                        },
                                    ],
                                },
                                {
                                    "type": "table_row",
                                    "content": [
                                        {
                                            "type": "table_cell",
                                            "content": [{"type": "text", "text": "value"}],
                                        },
                                    ],
                                },
                            ],
                        },
                        {"type": "image", "attrs": {"fileId": file_uid, "alt": "Image"}},
                        {
                            "type": "file",
                            "attrs": {
                                "name": "legacy.png",
                                "url": (
                                    f"https://files/companies/{company_uid}/documents/"
                                    f"{document_uid}/{file_uid}.png"
                                ),
                            },
                        },
                    ],
                }
            ),
        }
    )

    assert 'type: "document"' in markdown
    assert "# Spec" in markdown
    assert "## Intro" in markdown
    assert "**bold** and [link](https://example.test)" in markdown
    assert "- [x] done" in markdown
    assert "| A\\|B |" in markdown
    assert f"![Image](/api/documents/{document_uid}/files/{file_uid})" in markdown
    assert f"[legacy.png](/api/documents/{document_uid}/files/{file_uid})" in markdown


@pytest.mark.asyncio
@respx.mock
async def test_documents_get_returns_json_without_markdown(monkeypatch):
    _env(monkeypatch)
    route = respx.get("https://sandbox.kaiten.ru/api/latest/documents/doc-1").mock(
        return_value=Response(200, json={"uid": "doc-1", "title": "Spec", "data": {"type": "doc"}})
    )

    tool = resolve_tool("documents.get")
    payload = merge_inputs(tool, {"document_uid": "doc-1"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == {"uid": "doc-1", "title": "Spec", "data": {"type": "doc"}}


@pytest.mark.asyncio
@respx.mock
async def test_documents_get_markdown_writes_file(monkeypatch, tmp_path):
    _env(monkeypatch)
    respx.get("https://sandbox.kaiten.ru/api/latest/documents/doc-1").mock(
        return_value=Response(
            200,
            json={
                "uid": "doc-1",
                "title": "Spec Doc",
                "data": json.dumps(
                    {
                        "type": "doc",
                        "content": [
                            {"type": "paragraph", "content": [{"type": "text", "text": "Body"}]}
                        ],
                    }
                ),
            },
        )
    )

    tool = resolve_tool("documents.get")
    payload = merge_inputs(
        tool, {"document_uid": "doc-1", "markdown": True, "output": str(tmp_path)}
    )
    result = await execute_tool(tool, payload)

    target = tmp_path / "spec-doc--doc-1.md"
    assert target.read_text(encoding="utf-8") == (
        '---\ntype: "document"\nuid: "doc-1"\ntitle: "Spec Doc"\n---\n\n# Spec Doc\n\nBody\n'
    )
    assert result["path"] == str(target)
    assert result["entity_type"] == "document"


@pytest.mark.asyncio
@respx.mock
async def test_cards_get_markdown_writes_description_and_attachments(monkeypatch, tmp_path):
    _env(monkeypatch)
    company_uid = "4e2fe465-1a1a-445f-8f1b-7ca3d13884f9"
    card_uid = "426e98ee-4451-4f2b-972c-3d655f8d23d1"
    file_uid = "8b461699-43de-4316-a6c2-3a7e11fb8323"
    respx.get("https://sandbox.kaiten.ru/api/latest/cards/123").mock(
        return_value=Response(
            200,
            json={
                "id": 123,
                "uid": card_uid,
                "title": "Card Title",
                "description": (
                    f"**Body** [asset](https://files/companies/{company_uid}/cards/{card_uid}/{file_uid}.png)"
                ),
            },
        )
    )
    respx.get(f"https://sandbox.kaiten.ru/api/latest/cards/{card_uid}/files").mock(
        return_value=Response(200, json=[{"id": file_uid, "name": "brief.pdf"}])
    )

    tool = resolve_tool("cards.get")
    payload = merge_inputs(tool, {"card_id": 123, "markdown": True, "output": str(tmp_path)})
    result = await execute_tool(tool, payload)

    target = tmp_path / "card-title--123.md"
    text = target.read_text(encoding="utf-8")
    assert "# Card Title" in text
    assert f"**Body** [asset](/api/cards/{card_uid}/files/{file_uid})" in text
    assert f"- [brief.pdf](/api/cards/{card_uid}/files/{file_uid})" in text
    assert result["attachment_count"] == 1


@pytest.mark.asyncio
@respx.mock
async def test_markdown_export_refuses_existing_file_without_overwrite(monkeypatch, tmp_path):
    _env(monkeypatch)
    target = tmp_path / "existing.md"
    target.write_text("old", encoding="utf-8")
    respx.get("https://sandbox.kaiten.ru/api/latest/documents/doc-1").mock(
        return_value=Response(200, json={"uid": "doc-1", "title": "Spec", "data": {"type": "doc"}})
    )

    tool = resolve_tool("documents.get")
    payload = merge_inputs(
        tool,
        {"document_uid": "doc-1", "markdown": True, "output": str(target)},
    )

    with pytest.raises(ValidationError, match="already exists"):
        await execute_tool(tool, payload)
    assert target.read_text(encoding="utf-8") == "old"


def test_cards_get_rejects_fields_with_markdown():
    tool = resolve_tool("cards.get")

    with pytest.raises(ValidationError, match="--fields"):
        merge_inputs(tool, {"card_id": 123, "markdown": True, "fields": "id,title"})
