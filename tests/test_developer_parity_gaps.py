from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool, request_path_for_tool
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.client import KaitenClient


EXPECTED_NEW_TOOLS = {
    "cards.batch-update",
    "card-baselines.list",
    "card-tags.list",
    "card-members.update",
    "card-service-desk-external-recipients.add",
    "card-service-desk-external-recipients.remove",
    "card-allowed-users.list",
    "checklist-cards.list",
    "timesheet.list",
    "blocker-categories.list",
    "blocker-users.add",
    "current-user-blockers.list",
    "users.update",
    "space-users.get",
    "company-users.list",
    "company-users.update",
    "company-users.remove-virtual",
    "user-roles.create",
    "group-admins.add",
    "group-entities.add",
    "tree-entities.list",
    "card-types.tree-entities.add",
    "custom-properties.tree-entities.add",
    "custom-properties.catalog-values.list",
    "custom-properties.collective-score-values.create",
    "custom-properties.collective-vote-values.delete",
    "custom-directories.list",
    "custom-directory-fields.list",
    "custom-directory-records.list",
    "custom-directory-records.cards.list",
    "space-template-checklists.list",
    "space-template-checklist-items.create",
    "document-schemas.get",
    "scim.users.list",
    "scim.groups.update",
}


def test_developer_gap_tools_are_registered():
    for canonical_name in sorted(EXPECTED_NEW_TOOLS):
        assert resolve_tool(canonical_name).canonical_name == canonical_name


def test_build_request_for_cards_batch_update_merges_payload():
    tool = resolve_tool("cards.batch-update")
    payload = merge_inputs(
        tool,
        {
            "board_id": 10,
            "attributes": {"owner_id": 7},
            "payload": {"lane_id": 3},
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/cards"
    assert query is None
    assert body == {"board_id": 10, "attributes": {"owner_id": 7}, "lane_id": 3}


def test_build_request_for_custom_directories_catalog_record_search():
    tool = resolve_tool("custom-directory-records.list")
    payload = merge_inputs(
        tool,
        {
            "directory_id": "dir-uuid",
            "profile": "summary",
            "filters": {"field-uuid": {"eq": "Alice"}},
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/company/custom-directories/dir-uuid/records"
    assert query == {
        "profile": "summary",
        "filters": '{"field-uuid": {"eq": "Alice"}}',
        "limit": 100,
    }
    assert body is None


def test_custom_directory_docs_use_catalog_meaning():
    directory = resolve_tool("custom-directories.list")
    catalog_values = resolve_tool("custom-properties.catalog-values.list")

    assert any("Каталоги" in note for note in directory.usage_notes)
    assert any("not the UI" in note for note in catalog_values.usage_notes)


@pytest.mark.asyncio
@respx.mock
async def test_execute_custom_directory_records_cards_list(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/custom-directories/dir-uuid/records/record-uuid/cards",
        params={"limit": "100"},
    ).mock(return_value=Response(200, json=[{"id": 123, "title": "Deal"}]))

    tool = resolve_tool("custom-directory-records.cards.list")
    payload = merge_inputs(tool, {"directory_id": "dir-uuid", "record_id": "record-uuid"})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": 123, "title": "Deal"}]


@pytest.mark.asyncio
@respx.mock
async def test_execute_scim_uses_domain_root_not_api_latest(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get(
        "https://sandbox.kaiten.ru/scim/v2/Users",
        params={"startIndex": "2", "count": "10"},
    ).mock(return_value=Response(200, json={"Resources": []}))

    tool = resolve_tool("scim.users.list")
    payload = merge_inputs(tool, {"start_index": 2, "count": 10})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == {"Resources": []}


def test_scim_request_path_helper_points_to_domain_root():
    client = KaitenClient(domain="sandbox", token="test-token")
    tool = resolve_tool("scim.groups.get")

    try:
        assert (
            request_path_for_tool(tool, "/scim/v2/Groups/group-id", client)
            == "https://sandbox.kaiten.ru/scim/v2/Groups/group-id"
        )
    finally:
        # No HTTP client was opened, so this is intentionally synchronous cleanup.
        pass


@respx.mock
def test_cli_custom_directories_alias_and_nested_canonical_match(runner):
    respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/custom-directories",
        params={"limit": "200"},
    ).mock(return_value=Response(200, json=[]))
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "custom-directories", "list"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_custom_directories"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    canonical_payload = json.loads(canonical.output)
    alias_payload = json.loads(alias.output)
    canonical_payload.pop("stats", None)
    alias_payload.pop("stats", None)
    assert canonical_payload == alias_payload
