from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ConfigError
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.tree import fetch_paginated_entities
from kaiten_cli.registry import resolve_tool


ORPHAN_GROUP_UID = "b560ad48-040f-4e2a-aeef-445f66f2aaae"


def test_help_shows_documents_and_tree_namespaces(runner):
    result = runner.invoke(cli, ["--help"])
    nested = runner.invoke(cli, ["tree", "children", "--help"])

    assert result.exit_code == 0
    assert nested.exit_code == 0
    assert "documents" in result.output
    assert "document-groups" in result.output
    assert "tree" in result.output
    assert "list" in nested.output


def test_resolve_document_and_tree_aliases():
    assert resolve_tool("kaiten_list_documents").canonical_name == "documents.list"
    assert resolve_tool("kaiten_get_document_file_url").canonical_name == "document-files.get-url"
    assert resolve_tool("kaiten_upload_document_file").canonical_name == "document-files.upload"
    assert resolve_tool("kaiten_create_document_group").canonical_name == "document-groups.create"
    assert resolve_tool("kaiten_list_children").canonical_name == "tree.children.list"
    assert resolve_tool("kaiten_get_tree").canonical_name == "tree.get"


def test_document_group_docs_disambiguate_catalog_terms():
    document_create = resolve_tool("documents.create")
    group_create = resolve_tool("document-groups.create")
    tree = resolve_tool("tree.children.list")

    assert any("parent_entity_uid" in note for note in document_create.usage_notes)
    assert any("document folders/containers" in note for note in group_create.usage_notes)
    assert any("custom-directories" in note for note in group_create.usage_notes)
    assert any("read-only aggregate views" in note for note in tree.usage_notes)


def test_build_request_for_create_document_text_sets_sort_order(monkeypatch):
    monkeypatch.setattr("kaiten_cli.runtime.support.documents.time.time", lambda: 1234)
    tool = resolve_tool("documents.create")
    payload = merge_inputs(tool, {"title": "Spec", "text": "# Header"})

    path, query, body = build_request(tool, payload)

    assert path == "/documents"
    assert query is None
    assert body == {
        "title": "Spec",
        "sort_order": 1234,
        "data": {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Header"}],
                }
            ],
        },
    }


def test_build_request_for_update_document_sanitizes_lists_and_marks():
    tool = resolve_tool("documents.update")
    payload = merge_inputs(
        tool,
        {
            "document_uid": "doc-1",
            "data": {
                "type": "doc",
                "content": [
                    {
                        "type": "bullet_list",
                        "content": [
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Item",
                                                "marks": [{"type": "bold"}],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/documents/doc-1"
    assert query is None
    assert body == {
        "data": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "• Item"}],
                }
            ],
        }
    }


def test_build_request_for_document_file_get_url_forces_prevent_redirect():
    tool = resolve_tool("document-files.get-url")
    payload = merge_inputs(tool, {"document_uid": "doc-1", "file_id": "file-1"})

    path, query, body = build_request(tool, payload)

    assert path == "/documents/doc-1/files/file-1"
    assert query == {"prevent_redirect": True}
    assert body is None


def test_build_request_for_document_file_upload(tmp_path):
    upload = tmp_path / "screenshot.png"
    upload.write_bytes(b"png")

    tool = resolve_tool("document-files.upload")
    payload = merge_inputs(tool, {"document_uid": "doc-1", "file": str(upload)})
    path, query, body = build_request(tool, payload)

    assert path == "/documents/doc-1/files"
    assert query is None
    assert body is None


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_documents_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"uid": "doc-1", "title": "Spec"}])
    )

    tool = resolve_tool("documents.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"uid": "doc-1", "title": "Spec"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_documents_compact_and_fields_are_local_transforms(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "50"}).mock(
        return_value=Response(
            200,
            json=[
                {
                    "uid": "doc-1",
                    "title": "Spec",
                    "content": {"type": "doc"},
                    "owner": {"id": 7, "full_name": "Alice", "avatar_url": "https://example.test/a.png"},
                }
            ],
        )
    )

    tool = resolve_tool("documents.list")
    payload = merge_inputs(tool, {"compact": True, "fields": "uid,title"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert dict(route.calls[0].request.url.params) == {"limit": "50"}
    assert result == [{"uid": "doc-1", "title": "Spec"}]


def test_build_request_for_documents_list_accepts_version_two_search_parameters():
    tool = resolve_tool("documents.list")
    payload = merge_inputs(
        tool,
        {
            "query": "design",
            "version": 2,
            "condition": 1,
            "search_fields": "title,text",
            "start_position": "cursor-1",
            "include_search_preview": True,
            "fields": "uid,title",
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/documents"
    assert body is None
    assert query == {
        "query": "design",
        "limit": 50,
        "version": 2,
        "condition": 1,
        "start_position": "cursor-1",
        "include_search_preview": True,
        "fields": "title,text",
    }


@pytest.mark.asyncio
@respx.mock
async def test_execute_document_file_get_url_returns_signed_url(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/documents/doc-1/files/file-1",
        params={"prevent_redirect": "true"},
    ).mock(return_value=Response(200, json={"url": "https://storage.example.test/file-1"}))

    tool = resolve_tool("document-files.get-url")
    payload = merge_inputs(tool, {"document_uid": "doc-1", "file_id": "file-1"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == {"url": "https://storage.example.test/file-1"}


@pytest.mark.asyncio
@respx.mock
async def test_upload_document_file_sends_multipart_put(monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    upload = tmp_path / "screen.png"
    upload.write_bytes(b"fake png")
    route = respx.put("https://sandbox.kaiten.ru/api/latest/documents/doc-1/files").mock(
        return_value=Response(
            200,
            json={
                "id": "file-1",
                "name": "screen.png",
                "url": "https://files.example/screen.png",
            },
        )
    )

    tool = resolve_tool("document-files.upload")
    payload = merge_inputs(tool, {"document_uid": "doc-1", "file": str(upload)})
    result = await execute_tool(tool, payload)

    assert route.called
    request = route.calls[0].request
    assert request.headers["authorization"] == "Bearer test-token"
    assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"' in request.content
    assert b'filename="screen.png"' in request.content
    assert b"fake png" in request.content
    assert result["id"] == "file-1"


@pytest.mark.asyncio
@respx.mock
async def test_execute_tree_children_list_builds_sorted_result(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(
        return_value=Response(200, json=[{"id": 2, "uid": "space-b", "title": "Beta Space", "parent_entity_uid": "group-1"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[{"uid": "doc-2", "title": "API Spec", "parent_entity_uid": "group-1"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[{"uid": "group-2", "title": "Archive", "parent_entity_uid": "group-1"}])
    )

    tool = resolve_tool("tree.children.list")
    payload = merge_inputs(tool, {"parent_entity_uid": "group-1"})
    result = await execute_tool(tool, payload)

    assert result == [
        {"type": "document_group", "uid": "group-2", "title": "Archive", "parent_entity_uid": "group-1"},
        {"type": "space", "uid": "space-b", "id": 2, "title": "Beta Space", "parent_entity_uid": "group-1"},
        {"type": "document", "uid": "doc-2", "title": "API Spec", "parent_entity_uid": "group-1"},
    ]


@pytest.mark.asyncio
@respx.mock
async def test_execute_tree_get_builds_nested_tree(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(
        return_value=Response(200, json=[{"id": 1, "uid": "space-a", "title": "Alpha Space", "parent_entity_uid": None}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[{"uid": "doc-1", "title": "Notes", "parent_entity_uid": "space-a"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[])
    )

    tool = resolve_tool("tree.get")
    payload = merge_inputs(tool, {"depth": 1})
    result = await execute_tool(tool, payload)

    assert result == [
        {
            "type": "space",
            "uid": "space-a",
            "id": 1,
            "title": "Alpha Space",
            "children": [
                {
                    "type": "document",
                    "uid": "doc-1",
                    "title": "Notes",
                    "children": [],
                }
            ],
        }
    ]


@pytest.mark.asyncio
@respx.mock
async def test_execute_tree_get_fetches_documents_and_groups_after_first_page(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(
        return_value=Response(200, json=[{"id": 1, "uid": "space-a", "title": "Alpha Space", "parent_entity_uid": None}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(
            200,
            json=[
                {"uid": f"doc-{idx}", "title": f"Doc {idx:03d}", "parent_entity_uid": "space-a"}
                for idx in range(500)
            ],
        )
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "500"}).mock(
        return_value=Response(200, json=[{"uid": "doc-501", "title": "Late Doc", "parent_entity_uid": "space-a"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(
            200,
            json=[
                {"uid": f"group-{idx}", "title": f"Group {idx:03d}", "parent_entity_uid": "space-a"}
                for idx in range(500)
            ],
        )
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "500"}).mock(
        return_value=Response(200, json=[{"uid": "group-501", "title": "Late Group", "parent_entity_uid": "space-a"}])
    )

    tool = resolve_tool("tree.get")
    payload = merge_inputs(tool, {"depth": 1})
    result = await execute_tool(tool, payload)

    children = result[0]["children"]
    assert any(child["uid"] == "doc-501" for child in children)
    assert any(child["uid"] == "group-501" for child in children)


@pytest.mark.asyncio
@respx.mock
async def test_execute_tree_get_promotes_missing_parent_group_to_root(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(return_value=Response(200, json=[]))
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[{"uid": "b-child", "title": "B Child", "parent_entity_uid": ORPHAN_GROUP_UID}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[{"uid": ORPHAN_GROUP_UID, "title": "B", "parent_entity_uid": "missing-parent"}])
    )

    tool = resolve_tool("tree.get")
    full_tree = await execute_tool(tool, merge_inputs(tool, {"depth": 1}))
    branch = await execute_tool(tool, merge_inputs(tool, {"root_uid": ORPHAN_GROUP_UID, "depth": 0}))

    assert full_tree == [
        {
            "type": "document_group",
            "uid": ORPHAN_GROUP_UID,
            "title": "B",
            "children": [
                {
                    "type": "document",
                    "uid": "b-child",
                    "title": "B Child",
                    "children": [],
                }
            ],
        }
    ]
    assert branch == [
        {
            "type": "document",
            "uid": "b-child",
            "title": "B Child",
            "children": [],
        }
    ]


@pytest.mark.asyncio
async def test_fetch_paginated_entities_raises_when_safety_cap_is_full():
    class FullPageClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, int]] = []

        async def get(self, path, *, params, timeout):
            self.calls.append(dict(params))
            return [{"uid": f"{path}-{params['offset']}-{idx}"} for idx in range(params["limit"])]

    client = FullPageClient()

    with pytest.raises(ConfigError, match="possibly truncated"):
        await fetch_paginated_entities(client, "/documents", timeout=1, limit=2, max_pages=2)

    assert client.calls == [{"limit": 2, "offset": 0}, {"limit": 2, "offset": 2}]


@respx.mock
def test_cli_nested_tree_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(return_value=Response(200, json=[]))
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500", "offset": "0"}).mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "tree", "get"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_get_tree"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    canonical_payload = json.loads(canonical.output)
    alias_payload = json.loads(alias.output)
    canonical_payload.pop("stats", None)
    alias_payload.pop("stats", None)
    assert canonical_payload == alias_payload
