from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.runtime.executor import build_request, execute_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.registry import resolve_tool


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
    assert resolve_tool("kaiten_create_document_group").canonical_name == "document-groups.create"
    assert resolve_tool("kaiten_list_children").canonical_name == "tree.children.list"
    assert resolve_tool("kaiten_get_tree").canonical_name == "tree.get"


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
async def test_execute_tree_children_list_builds_sorted_result(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(
        return_value=Response(200, json=[{"id": 2, "uid": "space-b", "title": "Beta Space", "parent_entity_uid": "group-1"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500"}).mock(
        return_value=Response(200, json=[{"uid": "doc-2", "title": "API Spec", "parent_entity_uid": "group-1"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500"}).mock(
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
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500"}).mock(
        return_value=Response(200, json=[{"uid": "doc-1", "title": "Notes", "parent_entity_uid": "space-a"}])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500"}).mock(
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


@respx.mock
def test_cli_nested_tree_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces").mock(return_value=Response(200, json=[]))
    respx.get("https://sandbox.kaiten.ru/api/latest/documents", params={"limit": "500"}).mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/document-groups", params={"limit": "500"}).mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "tree", "get"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_get_tree"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
