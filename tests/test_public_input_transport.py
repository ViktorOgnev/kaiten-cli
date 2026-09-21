"""Regression coverage from public CLI inputs through the HTTP transport."""

from __future__ import annotations

from dataclasses import replace
import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import execute_tool
from kaiten_cli.runtime.input import _validate_schema, coerce_value, merge_inputs


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def invoke(runner, args, **kwargs):
    return runner.invoke(cli, ["--json", "--cache-mode", "off", *args], **kwargs)


@pytest.mark.parametrize(
    ("command", "method", "path", "flags", "body"),
    [
        (
            ["scim", "users", "create"],
            "POST",
            "/scim/v2/Users",
            ["--userName", "alice"],
            {"userName": "alice"},
        ),
        (
            ["scim", "groups", "create"],
            "POST",
            "/scim/v2/Groups",
            ["--displayName", "Team"],
            {"displayName": "Team"},
        ),
        *[
            (
                ["scim", entity, "update", id_flag, "1"],
                "PATCH",
                f"/scim/v2/{entity.title()}/1",
                ["--Operations", '[{"op":"replace","path":"active","value":false}]'],
                {"Operations": [{"op": "replace", "path": "active", "value": False}]},
            )
            for entity, id_flag in [("users", "--user-id"), ("groups", "--group-id")]
        ],
    ],
)
@respx.mock
def test_camel_case_body_flags_reach_http(runner, command, method, path, flags, body):
    route = respx.request(method, f"https://sandbox.kaiten.ru{path}").mock(
        return_value=Response(200, json={"id": "1"})
    )
    result = invoke(runner, command + flags)
    assert result.exit_code == 0, result.output
    assert json.loads(route.calls.last.request.content) == body


@pytest.mark.parametrize("enabled", [True, False])
@respx.mock
def test_camel_case_boolean_query_flags_reach_http(runner, enabled):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/company/users").mock(
        return_value=Response(200, json=[])
    )
    prefix = "--" if enabled else "--no-"
    result = invoke(
        runner,
        ["company-users", "list", prefix + "invitesOnly", prefix + "withTransferAccessStatus"],
    )
    assert result.exit_code == 0, result.output
    for field in ["invitesOnly", "withTransferAccessStatus"]:
        assert route.calls.last.request.url.params[field] == str(enabled).lower()


@respx.mock
def test_camel_case_order_query_flag_reaches_http(runner):
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1/allowed-users").mock(
        return_value=Response(200, json=[])
    )
    result = invoke(
        runner, ["card-allowed-users", "list", "--card-id", "1", "--orderBy", "full_name"]
    )
    assert result.exit_code == 0, result.output
    assert route.calls.last.request.url.params["orderBy"] == "full_name"


@pytest.mark.parametrize("value", ["1.5", "2"])
@pytest.mark.parametrize(
    ("command", "method", "path", "field"),
    [
        (
            ["boards", "update", "--space-id", "1", "--board-id", "2"],
            "PATCH",
            "/spaces/1/boards/2",
            field,
        )
        for field in ["top", "left"]
    ]
    + [
        (
            [
                "custom-directory-fields",
                "create",
                "--directory-id",
                "d",
                "--name",
                "F",
                "--type",
                "string",
            ],
            "POST",
            "/company/custom-directories/d/fields",
            "sort_order",
        ),
        (
            ["custom-directory-fields", "update", "--directory-id", "d", "--field-id", "f"],
            "PATCH",
            "/company/custom-directories/d/fields/f",
            "sort_order",
        ),
    ],
)
@respx.mock
def test_numeric_union_flags_reach_http(runner, value, command, method, path, field):
    route = respx.request(method, f"https://sandbox.kaiten.ru/api/latest{path}").mock(
        return_value=Response(200, json={"id": 1})
    )
    result = invoke(runner, command + ["--" + field.replace("_", "-"), value])
    assert result.exit_code == 0, result.output
    actual = json.loads(route.calls.last.request.content)[field]
    assert actual == float(value)
    assert isinstance(actual, int if value == "2" else float)


@pytest.mark.parametrize("types", [["integer", "number"], ["number", "integer"]])
def test_numeric_union_nullable_and_strict_integer(types):
    schema = {"type": types + ["null"]}
    assert coerce_value("null", schema, label="value") is None
    assert coerce_value("1.5", schema, label="value") == 1.5
    with pytest.raises(ValidationError, match="integer"):
        coerce_value("1.5", {"type": ["integer", "null"]}, label="value")


@respx.mock
def test_strict_integer_cli_flag_rejects_fraction_before_http(runner):
    result = invoke(runner, ["boards", "update", "--space-id", "1.5", "--board-id", "2"])
    assert result.exit_code != 0
    assert not respx.calls


@pytest.mark.parametrize("value", ["active,inactive", ["active", "inactive"]])
@pytest.mark.parametrize("mode", ["flag", "file", "stdin", "field_file", "field_stdin"])
@respx.mock
def test_conditions_string_and_array_input_modes(runner, tmp_path, value, mode):
    route = respx.get(
        "https://sandbox.kaiten.ru/api/latest/company/custom-properties/1/select-values"
    ).mock(return_value=Response(200, json=[]))
    command = ["custom-properties", "select-values", "list"]
    payload = {"property_id": 1, "conditions": value}
    stdin = None
    if mode == "flag":
        raw = value if isinstance(value, str) else json.dumps(value)
        args = command + ["--property-id", "1", "--conditions", raw]
    elif mode == "file":
        source = tmp_path / "payload.json"
        source.write_text(json.dumps(payload))
        args = ["--from-file", str(source), *command]
    elif mode == "stdin":
        args = ["--stdin-json", *command]
        stdin = json.dumps(payload)
    elif mode == "field_file":
        source = tmp_path / "conditions.json"
        source.write_text(json.dumps(value))
        args = command + ["--property-id", "1", "--conditions", f"@{source}"]
    else:
        args = command + ["--property-id", "1", "--conditions", "-"]
        stdin = json.dumps(value)
    result = invoke(runner, args, input=stdin)
    assert result.exit_code == 0, result.output
    expected = [value] if isinstance(value, str) else value
    assert route.calls.last.request.url.params.get_list("conditions") == expected


@pytest.mark.parametrize("mode", ["flag", "field_file", "field_stdin"])
@respx.mock
def test_malformed_explicit_json_is_not_sent_as_a_string(runner, tmp_path, mode):
    raw = '["active"'
    stdin = None
    if mode == "field_file":
        source = tmp_path / "bad.json"
        source.write_text(raw)
        raw = f"@{source}"
    elif mode == "field_stdin":
        stdin, raw = raw, "-"
    result = invoke(
        runner,
        ["custom-properties", "select-values", "list", "--property-id", "1", "--conditions", raw],
        input=stdin,
    )
    assert result.exit_code == 2
    assert "Invalid JSON for conditions" in result.output
    assert not respx.calls


@pytest.mark.parametrize("value", [5, 1.5, "current", None, "invalid", True])
@pytest.mark.parametrize("mode", ["flag", "file", "stdin"])
@respx.mock
def test_published_version_input_modes(runner, tmp_path, value, mode):
    route = respx.patch("https://sandbox.kaiten.ru/api/latest/documents/doc").mock(
        return_value=Response(200, json={"uid": "doc"})
    )
    command = ["documents", "update"]
    payload = {"document_uid": "doc", "published_version": value}
    stdin = None
    if mode == "flag":
        raw = value if isinstance(value, str) else json.dumps(value)
        args = command + ["--document-uid", "doc", "--published-version", raw]
    elif mode == "file":
        source = tmp_path / "version.json"
        source.write_text(json.dumps(payload))
        args = ["--from-file", str(source), *command]
    else:
        args = ["--stdin-json", *command]
        stdin = json.dumps(payload)
    result = invoke(runner, args, input=stdin)
    if value == "invalid" or value is True:
        assert result.exit_code == 2
        assert "published_version" in result.output
        assert not route.called
    else:
        assert result.exit_code == 0, result.output
        assert json.loads(route.calls.last.request.content) == {"published_version": value}


def test_one_of_requires_exactly_one_branch_and_checks_parent_constraints():
    schema = {"oneOf": [{"type": "integer"}, {"type": "number"}], "minimum": 1}
    _validate_schema(1.5, schema, path="value")
    for value in [1, "text", True]:
        with pytest.raises(ValidationError, match="oneOf"):
            _validate_schema(value, schema, path="value")
    with pytest.raises(ValidationError, match="greater than"):
        _validate_schema(0.5, schema, path="value")


@pytest.mark.parametrize("action", ["create", "update"])
@respx.mock
def test_record_response_profile_reaches_http(runner, action):
    path = "/company/custom-directories/d/records"
    flags = ["--directory-id", "d", "--values", "{}", "--response-profile", "none"]
    if action == "update":
        path += "/r"
        flags += ["--record-id", "r"]
    route = respx.request(
        "POST" if action == "create" else "PATCH", f"https://sandbox.kaiten.ru/api/latest{path}"
    ).mock(return_value=Response(200, json={"id": "r"}))
    result = invoke(runner, ["custom-directory-records", action, *flags])
    assert result.exit_code == 0, result.output
    assert route.calls.last.request.url.params["response_profile"] == "none"
    assert json.loads(route.calls.last.request.content) == {"values": {}}


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
@respx.mock
async def test_all_mutation_methods_forward_query_parameters(method):
    original = resolve_tool("custom-directory-records.create")
    tool = replace(original, operation=replace(original.operation, method=method))
    payload = merge_inputs(tool, {"directory_id": "d", "values": {}, "response_profile": "none"})
    route = respx.request(
        method, "https://sandbox.kaiten.ru/api/latest/company/custom-directories/d/records"
    ).mock(return_value=Response(200, json={"id": "r"}))
    await execute_tool(tool, payload, cache_mode="off")
    assert route.calls.last.request.url.params["response_profile"] == "none"
    assert json.loads(route.calls.last.request.content) == {"values": {}}
