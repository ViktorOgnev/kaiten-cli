from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.executor import build_request, execute_tool
from kaiten_cli.input import merge_inputs
from kaiten_cli.registry import resolve_tool


def test_help_shows_webhooks_automations_and_workflows(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "webhooks" in result.output
    assert "incoming-webhooks" in result.output
    assert "automations" in result.output
    assert "workflows" in result.output


def test_resolve_webhook_and_automation_aliases():
    assert resolve_tool("kaiten_list_webhooks").canonical_name == "webhooks.list"
    assert resolve_tool("kaiten_create_incoming_webhook").canonical_name == "incoming-webhooks.create"
    assert resolve_tool("kaiten_copy_automation").canonical_name == "automations.copy"
    assert resolve_tool("kaiten_list_workflows").canonical_name == "workflows.list"


def test_build_request_for_copy_automation_maps_target_space_id():
    tool = resolve_tool("automations.copy")
    payload = merge_inputs(tool, {"space_id": 1, "automation_id": "auto-1", "target_space_id": 2})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/1/automations/auto-1/copy"
    assert query is None
    assert body == {"targetSpaceId": 2}


def test_build_request_for_create_automation_preserves_known_good_payload_shape():
    tool = resolve_tool("automations.create")
    payload = merge_inputs(
        tool,
        {
            "space_id": 1,
            "name": "Auto assign",
            "type": "on_action",
            "trigger": {"type": "card_created"},
            "actions": [
                {
                    "type": "add_assignee",
                    "created": "2026-01-01T00:00:00+00:00",
                    "data": {"variant": "specific", "userId": 42},
                }
            ],
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/1/automations"
    assert query is None
    assert body == {
        "name": "Auto assign",
        "type": "on_action",
        "trigger": {"type": "card_created"},
        "actions": [
            {
                "type": "add_assignee",
                "created": "2026-01-01T00:00:00+00:00",
                "data": {"variant": "specific", "userId": 42},
            }
        ],
    }


def test_build_request_for_create_incoming_webhook_includes_required_body():
    tool = resolve_tool("incoming-webhooks.create")
    payload = merge_inputs(tool, {"space_id": 1, "board_id": 2, "column_id": 3, "lane_id": 4, "owner_id": 5, "format": 2})

    path, query, body = build_request(tool, payload)

    assert path == "/spaces/1/webhooks"
    assert query is None
    assert body == {"board_id": 2, "column_id": 3, "lane_id": 4, "owner_id": 5, "format": 2}


@pytest.mark.asyncio
@respx.mock
async def test_execute_list_workflows_injects_default_limit(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    route = respx.get("https://sandbox.kaiten.ru/api/latest/company/workflows", params={"limit": "50"}).mock(
        return_value=Response(200, json=[{"id": "wf-1", "name": "Flow"}])
    )

    tool = resolve_tool("workflows.list")
    payload = merge_inputs(tool, {})
    result = await execute_tool(tool, payload)

    assert route.called
    assert result == [{"id": "wf-1", "name": "Flow"}]


@respx.mock
def test_cli_automation_alias_and_canonical_match(runner):
    respx.get("https://sandbox.kaiten.ru/api/latest/spaces/1/automations").mock(
        return_value=Response(200, json=[])
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}

    canonical = runner.invoke(cli, ["--json", "automations", "list", "--space-id", "1"], env=env)
    alias = runner.invoke(cli, ["--json", "kaiten_list_automations", "--space-id", "1"], env=env)

    assert canonical.exit_code == 0
    assert alias.exit_code == 0
    assert json.loads(canonical.output) == json.loads(alias.output)
