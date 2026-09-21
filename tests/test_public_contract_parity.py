from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import describe, resolve_tool
from kaiten_cli.runtime.executor import build_request
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.cards import _card_query_params
from kaiten_cli.runtime.trace import redact_argv

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("name", "ids", "fields"),
    [
        (
            "boards.update",
            {"space_id": 1, "board_id": 2},
            {
                "automove_cards": False,
                "auto_assign_enabled": False,
                "cell_wip_limits": [],
                "card_properties": None,
                "default_tags": None,
            },
        ),
        (
            "boards.create",
            {"space_id": 1, "title": "Board"},
            {"columns": [], "lanes": [], "first_image_is_cover": True},
        ),
        (
            "columns.update",
            {"board_id": 1, "column_id": 2},
            {
                "card_hide_after_days": None,
                "archive_after_days": 0,
                "last_moved_warning_after_hours": 0,
                "pause_sla": False,
                "rules": 0,
            },
        ),
        (
            "subcolumns.update",
            {"column_id": 1, "subcolumn_id": 2},
            {"card_hide_after_days": 0, "pause_sla": False, "default_tags": None},
        ),
        (
            "lanes.update",
            {"board_id": 1, "lane_id": 2},
            {"default_tags": None, "last_moved_warning_after_minutes": 0},
        ),
        (
            "spaces.update",
            {"space_id": 1},
            {
                "settings": {"timeline": {"workDays": []}, "future": {"x": False}},
                "hidden_card_type_uids": [],
                "parent_entity_uid": None,
            },
        ),
        (
            "space-users.update",
            {"space_id": 1, "user_id": 2},
            {"notifications_enabled": False, "settings": {"extension": []}},
        ),
        (
            "users.update",
            {"user_id": 1},
            {"notification_settings": {}, "timezone": "UTC", "theme": "dark"},
        ),
        (
            "company-groups.update",
            {"group_uid": "group"},
            {"permissions": 0, "add_to_cards_and_spaces_enabled": False},
        ),
        (
            "documents.update",
            {"document_uid": "doc"},
            {"public": False, "hidden_on_public_site": False, "slug": "page", "settings": {}},
        ),
        (
            "document-groups.update",
            {"group_uid": "group"},
            {"hostname": "example.test", "index_document_uid": None, "news_feed": False},
        ),
        ("columns.delete", {"board_id": 1, "column_id": 2}, {"force": False}),
        ("lanes.delete", {"board_id": 1, "lane_id": 2}, {"force": True}),
        ("user-roles.delete", {"role_id": 1}, {"replace_role_id": 2}),
    ],
)
def test_documented_body_fields_survive_merge_and_request(name, ids, fields):
    tool = resolve_tool(name)
    payload = merge_inputs(tool, {}, stdin_json=True, stdin_text=json.dumps(ids | fields))
    _, query, body = build_request(tool, payload)
    assert query is None
    for key, value in fields.items():
        assert key in body
        assert body[key] == value


@pytest.mark.parametrize(
    ("name", "payload", "expected_path", "expected_body"),
    [
        (
            "checklists.update",
            {"card_id": 1, "checklist_id": 2, "target_card_id": 3},
            "/cards/1/checklists/2",
            {"card_id": 3},
        ),
        (
            "checklist-items.update",
            {"checklist_id": 2, "item_id": 4, "target_checklist_id": 3},
            "/checklists/2/items/4",
            {"checklist_id": 3},
        ),
        (
            "checklist-items.update",
            {"card_id": 1, "checklist_id": 2, "item_id": 4, "target_checklist_id": 3},
            "/cards/1/checklists/2/items/4",
            {"checklist_id": 3},
        ),
        (
            "space-template-checklists.update",
            {"space_uid": "source", "template_checklist_uid": "list", "target_space_uid": "target"},
            "/spaces/source/template-checklists/list",
            {"space_uid": "target"},
        ),
        (
            "card-children.add",
            {"card_id": 1, "child_card_id": 2},
            "/cards/1/children",
            {"card_id": 2},
        ),
    ],
)
def test_source_and_destination_ids_are_not_confused(name, payload, expected_path, expected_body):
    tool = resolve_tool(name)
    assert build_request(tool, merge_inputs(tool, payload)) == (expected_path, None, expected_body)


def test_named_alternative_create_forms():
    cases = [
        ("space-users.add", {"space_id": 1, "email": "user@example.test", "send_email": False}),
        ("blocker-categories.add", {"blocker_id": 1, "name": "External"}),
        ("custom-properties.create", {"formula": "1+1", "formula_source_card": {}}),
        (
            "custom-properties.collective-vote-values.create",
            {"card_id": 1, "property_id": 2, "number_vote": 0},
        ),
        ("scim.users.create", {"userName": "alice", "emails": [{"value": "alice@example.test"}]}),
        ("scim.groups.create", {"displayName": "Team"}),
        (
            "scim.users.update",
            {"user_id": "1", "Operations": [{"op": "replace", "path": "active", "value": False}]},
        ),
    ]
    for name, payload in cases:
        tool = resolve_tool(name)
        _, _, body = build_request(tool, merge_inputs(tool, payload))
        for field in set(payload) - set(tool.operation.path_fields):
            assert body[field] == payload[field]


def test_custom_property_uuid_settings_and_alternative_restrictions():
    tool = resolve_tool("custom-properties.update")
    uid = "11111111-1111-1111-1111-111111111111"
    fields = {
        "property_id": 1,
        "fields_settings": {uid: {"required": False, "future": 42}},
        "data": {"restrictions": {"max": 10}},
    }
    assert (
        build_request(tool, merge_inputs(tool, fields))[2]["fields_settings"]
        == fields["fields_settings"]
    )
    fields["fields_settings"][uid]["required"] = "false"
    with pytest.raises(ValidationError, match=r"fields_settings.*required"):
        merge_inputs(tool, fields)


@pytest.mark.parametrize(
    "name",
    ["private-card-files.get", "private-comment-files.get", "private-custom-property-files.get"],
)
def test_metadata_redirect_has_safe_download_guidance(name):
    tool = resolve_tool(name)
    payload = {field: "example" for field in tool.operation.path_fields}
    with pytest.raises(ValidationError, match=r"files.download"):
        merge_inputs(tool, payload | {"redirect": True})
    assert build_request(tool, merge_inputs(tool, payload | {"download": False}))[1] == {
        "download": False
    }


@respx.mock
def test_false_null_and_nested_json_through_flags_file_stdin_alias(runner, tmp_path):
    endpoint = respx.patch("https://sandbox.kaiten.ru/api/latest/spaces/1/boards/2").mock(
        return_value=Response(200, json={"id": 2})
    )
    env = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test"}
    payload = {
        "space_id": 1,
        "board_id": 2,
        "automove_cards": False,
        "card_properties": None,
        "cell_wip_limits": [],
    }
    file = tmp_path / "payload.json"
    file.write_text(json.dumps(payload))
    calls = [
        (
            [
                "--json",
                "boards",
                "update",
                "--space-id",
                "1",
                "--board-id",
                "2",
                "--no-automove-cards",
                "--card-properties",
                "null",
                "--cell-wip-limits",
                "[]",
            ],
            None,
        ),
        (["--json", "--from-file", str(file), "boards", "update"], None),
        (["--json", "--stdin-json", "kaiten_update_board"], json.dumps(payload)),
    ]
    for args, stdin in calls:
        result = runner.invoke(cli, args, input=stdin, env=env)
        assert result.exit_code == 0, result.output
        assert json.loads(endpoint.calls[-1].request.content) == {
            "automove_cards": False,
            "card_properties": None,
            "cell_wip_limits": [],
        }


def test_cards_bulk_preserves_new_public_query_options():
    fields = {"order_space_id": 42, "organizations_ids": "1,2", "broken_api": False}
    tool = resolve_tool("cards.list-all")
    result = _card_query_params(merge_inputs(tool, {"board_id": 1} | fields))
    for key, value in fields.items():
        assert result[key] == value


def test_password_arguments_are_redacted():
    assert redact_argv(
        ["users", "update", "--password", "new-secret", "--old-password=old-secret"]
    ) == ["users", "update", "--password", "[REDACTED]", "--old-password=[REDACTED]"]


def test_nested_discovery_exposes_variant_schemas():
    result = describe("automations.create")
    schema = result["input_schema"]["properties"]
    assert "card_created" in schema["trigger"]["x-variants"]
    assert "tag" in schema["conditions"]["x-variants"]
    assert "add_assignee" in schema["actions"]["items"]["x-variants"]
    board = describe("boards.update")["input_schema"]["properties"]["card_properties"]
    assert "required" in board["items"]["properties"]


def test_all_documentation_pages_are_accounted_for():
    audit = load_script("audit_public_api")
    snapshot = json.loads(audit.SNAPSHOT.read_text())
    results = audit.audit(snapshot)
    assert len(results) == len(snapshot["pages"])
    assert not [r for r in results if r["status"] in ("unparsed", "review", "missing")]
    assert results == json.loads(audit.SNAPSHOT.with_name("coverage.json").read_text())
    assert {p["section"] for p in snapshot["pages"]} >= {
        "REST API",
        "SCIM",
        "Imports",
        "Addons",
        "Webhooks",
        "External Webhooks",
        "User Metadata",
    }


def test_normalized_automation_schemas_match_source_tables(monkeypatch):
    audit = load_script("audit_public_api")
    monkeypatch.setitem(sys.modules, "audit_public_api", audit)
    normalizer = load_script("normalize_automation_docs")
    source = json.loads((ROOT / "docs/public-api/automation-tables.json").read_text())
    assert normalizer.normalize(source) == json.loads(normalizer.OUTPUT.read_text())


def test_parser_strips_badges_and_preserves_nullable_schema():
    audit = load_script("audit_public_api")
    page = audit.parse_page(
        "https://developers.kaiten.ru/example",
        """<span>PATCH</span><span>https://example.kaiten.ru/api/latest/things/{id}</span><h6>Query</h6><table><tr><th>Name</th><th>Type</th><th>Description</th></tr><tr><td>filter<span>BETA</span></td><td>object</td><td>Filter</td></tr></table><h6>Attributes</h6><pre>{"type":"object","properties":{"name":{"type":["string","null"]}}}</pre>""",
        "REST API",
    )
    assert page["body"]["properties"]["name"]["type"] == ["string", "null"]
    assert set(page["query"]["properties"]) == {"filter"}


PUBLIC_PAGES = [
    p
    for p in json.loads((ROOT / "docs/public-api/contracts.json").read_text())["pages"]
    if p["kind"] == "http"
]


@pytest.mark.parametrize("page", PUBLIC_PAGES, ids=lambda p: p["url"].split(".ru/")[1])
def test_every_public_operation_builds_its_documented_route(page):
    """Source-backed route checks include the non-canonical compatibility paths."""
    import re

    audit = load_script("audit_public_api")
    tool = audit.matching_tool(page)
    assert tool is not None
    payload = {}
    for field in tool.input_schema.get("required", []):
        typ = tool.input_schema["properties"][field].get("type")
        payload[field] = (
            {} if typ == "object" else [] if typ == "array" else "example" if typ == "string" else 1
        )
    for field in tool.operation.path_fields:
        payload.setdefault(field, 1)
    if page["url"].endswith("space-boards/get-board"):
        payload["space_id"] = 1
    if "/card-checklist-items/" in page["url"]:
        payload["card_id"] = 1
    path, _, _ = build_request(tool, payload)
    documented = page["path"].removeprefix("/api/latest")
    pattern = re.escape(documented)
    pattern = re.sub(r"\\\{[^}]+\\\}", "[^/]+", pattern)
    assert re.fullmatch(pattern, path), (documented, path)
    assert tool.operation.method == page["method"]


def test_unparsed_rest_operation_is_not_counted_as_reference():
    audit = load_script("audit_public_api")
    page = audit.parse_page(
        "https://developers.kaiten.ru/cards/new-operation",
        "<h1>Temporary maintenance</h1>",
        "REST API",
    )
    assert page["kind"] == "unparsed"


def test_file_download_note_does_not_hide_new_contract_gaps():
    audit_module = load_script("audit_public_api")
    snapshot = json.loads((ROOT / "docs/public-api/contracts.json").read_text())
    page = next(
        page
        for page in snapshot["pages"]
        if page["kind"] == "http"
        and (tool := audit_module.matching_tool(page)) is not None
        and tool.canonical_name.startswith("private-")
        and tool.action == "get"
    )
    page["query"] = {"type": "object", "properties": {"future_required_query": {"type": "string"}}}
    result = audit_module.audit({"pages": [page]})[0]
    assert result["status"] == "review"
    assert result["issues"] == [{"field": "query.future_required_query", "issue": "missing"}]
    assert result["notes"]
