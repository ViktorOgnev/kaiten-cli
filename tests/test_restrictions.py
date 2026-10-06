"""Restrictions through public CLI inputs and mocked HTTP transport."""

from __future__ import annotations

import json
from copy import deepcopy

import httpx
import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.discovery import describe_tool
from kaiten_cli.i18n import use_locale
from kaiten_cli.registry import resolve_tool, search
from kaiten_cli.registry.live_contracts import get_live_contract

RULE_ID = "a52165d4-26cc-4483-a272-edfaeff2b1b2"
COPY_ID = "be90b44c-002f-454f-8910-169e2c7f98e6"
BASE_URL = "https://sandbox.kaiten.ru/api/latest"
ELEMENT = {
    "type": "cardType",
    "created": "2026-01-01T00:00:00Z",
    "operator": "eq",
    "data": {"typeIds": [1]},
}
MOVEMENT = {
    "type": "movement",
    "created": "2026-01-01T00:00:00Z",
    "operator": "eq",
    "data": {"pathType": "any"},
}
CREATE = {
    "conditions": [ELEMENT],
    "restrictions": [MOVEMENT],
    "name": "Правило",
    "error_text": "Заполните поле",
}
IDS = {"space_id": 1, "restriction_id": RULE_ID}
RULE = {"id": RULE_ID, "status": "active", "type": "on_action", **CREATE}
CASES = [
    ("list", "GET", "/spaces/1/restrictions", {"space_id": 1}, None, [RULE]),
    ("get", "GET", "/spaces/1/restrictions", IDS, None, [RULE]),
    ("create", "POST", "/spaces/1/restrictions", {"space_id": 1, **CREATE}, CREATE, RULE),
    (
        "update",
        "PATCH",
        f"/spaces/1/restrictions/{RULE_ID}",
        {**IDS, "status": "disabled"},
        {"status": "disabled"},
        {**RULE, "status": "disabled"},
    ),
    ("delete", "DELETE", f"/spaces/1/restrictions/{RULE_ID}", IDS, None, None),
    (
        "copy",
        "POST",
        "/spaces/2/restrictions",
        {"restriction_id": RULE_ID, "target_space_id": 2},
        {"source_restriction_id": RULE_ID},
        {**RULE, "id": COPY_ID, "status": "broken"},
    ),
]


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def invoke(runner, action, payload, mode, tmp_path, *, root_options=()):
    args = ["--locale", "ru", "--json", "--cache-mode", "off", *root_options]
    if mode in {"file", "legacy_file"}:
        path = tmp_path / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        flag = "--input-file" if mode == "file" else "--from-file"
        return runner.invoke(cli, [*args, flag, str(path), "restrictions", action])
    if mode == "stdin":
        return runner.invoke(
            cli, [*args, "--stdin-json", "restrictions", action], input=json.dumps(payload)
        )
    args += ["restrictions", action]
    for key, value in payload.items():
        raw = json.dumps(value) if value is None or isinstance(value, (dict, list)) else str(value)
        args += ["--" + key.replace("_", "-"), raw]
    return runner.invoke(cli, args)


@pytest.mark.parametrize(("action", "method", "path", "payload", "body", "response"), CASES)
@pytest.mark.parametrize("mode", ["flags", "file", "legacy_file", "stdin"])
@respx.mock
def test_commands_send_exact_requests(
    runner, tmp_path, action, method, path, payload, body, response, mode
):
    route = respx.request(method, BASE_URL + path).mock(
        return_value=Response(200, json=response) if response is not None else Response(200)
    )
    result = invoke(runner, action, payload, mode, tmp_path)
    assert result.exit_code == 0, result.output
    assert route.call_count == 1
    request = route.calls.last.request
    assert not request.url.query  # No pagination or shaping fields reach the server.
    assert request.headers["Authorization"] == "Bearer test-token"
    assert (json.loads(request.content) if request.content else None) == body
    data = json.loads(result.output)["data"]
    assert data == (RULE if action == "get" else response)
    assert json.loads(result.output)["stats"]["http_request_count"] == 1


@pytest.mark.parametrize("mode", ["flags", "file", "stdin"])
@pytest.mark.parametrize(
    "fields",
    [
        {"status": "active"},
        {"status": "disabled"},
        {"name": None},
        {"name": ""},
        {"conditions": []},
        {"restrictions": []},
        {"name": None, "error_text": None},
        {
            "conditions": [
                {
                    **ELEMENT,
                    "type": "server_specific",
                    "data": {"custom": [None, False, 0, {"key": "значение"}]},
                }
            ]
        },
    ],
)
@respx.mock
def test_partial_patch_preserves_values_and_replaces_arrays(runner, tmp_path, mode, fields):
    route = respx.patch(BASE_URL + f"/spaces/1/restrictions/{RULE_ID}").mock(
        return_value=Response(200, json=RULE)
    )
    result = invoke(runner, "update", {**IDS, **fields}, mode, tmp_path)
    assert result.exit_code == 0, result.output
    assert json.loads(route.calls.last.request.content) == fields


INVALID = [
    ("create", {"space_id": 1, "restrictions": []}),
    ("create", {"space_id": 1, "conditions": []}),
    ("create", {"space_id": 1, **CREATE, "name": "x" * 257}),
    ("create", {"space_id": 1, **CREATE, "error_text": "x" * 4097}),
    ("update", IDS),
    ("update", {**IDS, "error_text": "only"}),
    ("update", {**IDS, "status": "broken"}),
    ("update", {**IDS, "status": None}),
    ("update", {**IDS, "conditions": {}}),
    ("update", {**IDS, "restrictions": [None]}),
    ("get", {**IDS, "restriction_id": "invalid"}),
    ("get", {**IDS, "restriction_id": "urn:uuid:" + RULE_ID}),
    ("delete", {**IDS, "restriction_id": "{" + RULE_ID + "}"}),
    ("copy", {"restriction_id": "invalid", "target_space_id": 2}),
]
for field in ("conditions", "restrictions"):
    for key in ("type", "created", "operator", "data"):
        missing = deepcopy(ELEMENT)
        del missing[key]
        INVALID.append(("update", {**IDS, field: [missing]}))
    for key, value in (("type", 1), ("created", None), ("operator", "unknown"), ("data", [])):
        INVALID.append(("update", {**IDS, field: [{**ELEMENT, key: value}]}))


@pytest.mark.parametrize(("action", "payload"), INVALID)
@pytest.mark.parametrize("mode", ["flags", "file", "stdin"])
@respx.mock
def test_invalid_payload_never_reaches_http(runner, tmp_path, action, payload, mode):
    result = invoke(runner, action, payload, mode, tmp_path)
    assert result.exit_code == 2, result.output
    assert not respx.calls


@pytest.mark.parametrize("mode", ["file", "stdin"])
@pytest.mark.parametrize("field", ["status", "type", "source_restriction_id"])
@respx.mock
def test_create_rejects_unsupported_fields(runner, tmp_path, mode, field):
    result = invoke(runner, "create", {"space_id": 1, **CREATE, field: "disabled"}, mode, tmp_path)
    assert result.exit_code == 2, result.output
    assert not respx.calls


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{**RULE, "id": COPY_ID}],
        [{**RULE, "type": "on_workflow"}],
        [{**RULE, "status": "removed"}],
    ],
)
@respx.mock
def test_get_missing_rule_is_api_error(runner, tmp_path, items):
    respx.get(BASE_URL + "/spaces/1/restrictions").mock(return_value=Response(200, json=items))
    result = invoke(runner, "get", IDS, "flags", tmp_path)
    assert result.exit_code == 4, result.output
    error = json.loads(result.output)["error"]
    assert error["status_code"] == 404
    assert RULE_ID in error["message"]
    assert "не найдено" in error["message"]


@pytest.mark.parametrize(
    "items", [{"items": [RULE]}, None, [None], [{}], [{"id": 1}], [{"id": "invalid"}]]
)
@respx.mock
def test_get_rejects_malformed_list(runner, tmp_path, items):
    respx.get(BASE_URL + "/spaces/1/restrictions").mock(return_value=Response(200, json=items))
    result = invoke(runner, "get", IDS, "flags", tmp_path)
    assert result.exit_code == 5, result.output
    assert json.loads(result.output)["error"]["type"] == "transport_error"


@pytest.mark.parametrize("reverse", [False, True])
@respx.mock
def test_get_selects_before_any_transform_and_normalizes_uuid(runner, tmp_path, reverse):
    other = {**RULE, "id": COPY_ID}
    respx.get(BASE_URL + "/spaces/1/restrictions").mock(
        return_value=Response(200, json=[RULE, other] if reverse else [other, RULE])
    )
    result = invoke(runner, "get", {**IDS, "restriction_id": RULE_ID.upper()}, "flags", tmp_path)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["data"] == RULE


@respx.mock
def test_list_shapes_only_local_output(runner, tmp_path):
    route = respx.get(BASE_URL + "/spaces/1/restrictions").mock(
        return_value=Response(200, json=[RULE])
    )
    result = runner.invoke(
        cli,
        [
            "--locale",
            "ru",
            "--json",
            "restrictions",
            "list",
            "--space-id",
            "1",
            "--compact",
            "--fields",
            "id,status",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["data"] == [{"id": RULE_ID, "status": "active"}]
    assert not route.calls.last.request.url.query


@pytest.mark.parametrize(("action", "method", "path", "payload", "body", "response"), CASES)
@pytest.mark.parametrize("status", [400, 401, 402, 403, 404, 409])
@respx.mock
def test_api_errors_preserve_status_and_body(
    runner, tmp_path, action, method, path, payload, body, response, status
):
    error_body = {"message": "server supplied message", "code": "restriction_error"}
    route = respx.request(method, BASE_URL + path).mock(
        return_value=Response(status, json=error_body)
    )
    result = invoke(runner, action, payload, "flags", tmp_path)
    assert result.exit_code == 4, result.output
    error = json.loads(result.output)["error"]
    assert error["status_code"] == status
    assert error["body"] == error_body
    assert route.call_count == 1


@pytest.mark.parametrize(("action", "method", "path", "payload", "body", "response"), CASES[2:])
@pytest.mark.parametrize("policy", ["flag", "environment"])
@respx.mock
def test_read_only_blocks_all_mutations(
    runner, tmp_path, monkeypatch, action, method, path, payload, body, response, policy
):
    if policy == "environment":
        monkeypatch.setenv("KAITEN_CLI_READ_ONLY", "1")
    result = invoke(
        runner,
        action,
        payload,
        "file",
        tmp_path,
        root_options=("--read-only",) if policy == "flag" else (),
    )
    assert result.exit_code == 6, result.output
    assert json.loads(result.output)["error"]["type"] == "mutation_blocked"
    assert not respx.calls


@pytest.mark.parametrize(("action", "method", "path", "payload", "body", "response"), CASES[2:])
@pytest.mark.parametrize("failure", ["timeout", "server", "malformed_success"])
@respx.mock
def test_ambiguous_mutations_are_not_retried(
    runner, tmp_path, action, method, path, payload, body, response, failure
):
    route = respx.request(method, BASE_URL + path)
    if failure == "timeout":
        route.mock(side_effect=httpx.ReadTimeout("ambiguous"))
    else:
        route.mock(return_value=Response(500 if failure == "server" else 200, text="not JSON"))
    result = invoke(runner, action, payload, "flags", tmp_path)
    assert result.exit_code == 5, result.output
    assert route.call_count == 1
    assert "--cache-mode" in json.loads(result.output)["error"]["message"]


@pytest.mark.parametrize("locale", ["en", "ru"])
def test_discovery_contract_and_live_status(runner, locale):
    with use_locale(locale):
        assert {tool.namespace for tool in search("ограничения", limit=6)} == {"restrictions"}
    for action, *_ in CASES:
        name = f"restrictions.{action}"
        tool = resolve_tool(name)
        assert get_live_contract(name).status == "live_not_validated"
        contract = describe_tool(name)
        assert contract["mutation"] == (action not in {"list", "get"})
        assert contract["read_only_allowed"] == (action in {"list", "get"})
        assert tool.execution_mode == ("synthetic" if action == "get" else "direct_http")
        result = runner.invoke(cli, ["--locale", locale, "restrictions", action, "--help"])
        assert result.exit_code == 0, result.output
    create = resolve_tool("restrictions.create")
    assert "status" not in create.input_schema["properties"]
    listing = resolve_tool("restrictions.list")
    assert "limit" not in listing.input_schema["properties"]
    assert "offset" not in listing.input_schema["properties"]
