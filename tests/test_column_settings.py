"""Column settings through public inputs and the HTTP transport."""

from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.i18n import use_locale
from kaiten_cli.registry import search


CASES = [
    ("columns.create", "POST", "/boards/10/columns", {"board_id": 10, "title": "Done", "type": 3}),
    ("columns.update", "PATCH", "/boards/10/columns/20", {"board_id": 10, "column_id": 20}),
    ("subcolumns.create", "POST", "/columns/20/subcolumns", {"column_id": 20, "title": "Done"}),
    (
        "subcolumns.update",
        "PATCH",
        "/columns/20/subcolumns/30",
        {"column_id": 20, "subcolumn_id": 30},
    ),
    ("boards.create", "POST", "/spaces/1/boards", {"space_id": 1, "title": "Board"}),
]


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")


def invoke(runner, name, payload, mode, tmp_path):
    args = ["--locale", "ru", "--json", "--cache-mode", "off"]
    if mode == "stdin":
        return runner.invoke(
            cli, [*args, "--stdin-json", *name.split(".")], input=json.dumps(payload)
        )
    if mode == "file":
        path = tmp_path / "input.json"
        path.write_text(json.dumps(payload))
        return runner.invoke(cli, [*args, "--from-file", str(path), *name.split(".")])
    args.extend(name.split("."))
    for key, value in payload.items():
        flag = "--" + key.replace("_", "-")
        if isinstance(value, bool):
            args.append(flag if value else "--no-" + key.replace("_", "-"))
        else:
            raw = (
                json.dumps(value)
                if value is None or isinstance(value, (list, dict))
                else str(value)
            )
            args.extend([flag, raw])
    return runner.invoke(cli, args)


@pytest.mark.parametrize(("name", "method", "path", "ids"), CASES)
@pytest.mark.parametrize("mode", ["flags", "file", "stdin"])
@pytest.mark.parametrize("days", [-2, -1, 0, 14])
@respx.mock
def test_archive_threshold_through_public_inputs(
    runner, tmp_path, name, method, path, ids, mode, days
):
    fields = {"archive_after_days": days}
    if name == "boards.create":
        fields = {"columns": [{"title": "Done", "type": 3, "archive_after_days": days}]}
    route = respx.request(method, "https://sandbox.kaiten.ru/api/latest" + path).mock(
        return_value=Response(200, json={"id": 20})
    )
    result = invoke(runner, name, ids | fields, mode, tmp_path)
    if days < -1:
        assert result.exit_code == 2, result.output
        assert "archive_after_days" in result.output or "archive-after-days" in result.output
        assert not route.called
    else:
        assert result.exit_code == 0, result.output
        assert route.call_count == 1
        body = json.loads(route.calls.last.request.content)
        for key, value in fields.items():
            assert body[key] == value


@pytest.mark.parametrize(("name", "method", "path", "ids"), [CASES[1], CASES[3]])
@pytest.mark.parametrize("mode", ["flags", "file", "stdin"])
@respx.mock
def test_empty_column_patch_is_rejected_before_http(
    runner, tmp_path, name, method, path, ids, mode
):
    route = respx.patch("https://sandbox.kaiten.ru/api/latest" + path).mock(
        return_value=Response(200, json={"id": 20})
    )
    result = invoke(runner, name, ids, mode, tmp_path)
    assert result.exit_code == 2, result.output
    assert not route.called


@pytest.mark.parametrize(("name", "method", "path", "ids"), [CASES[1], CASES[3]])
@pytest.mark.parametrize("fields", [{"pause_sla": False}, {"rules": 0}, {"default_tags": None}])
@pytest.mark.parametrize("mode", ["flags", "file", "stdin"])
@respx.mock
def test_falsy_field_is_a_valid_patch(runner, tmp_path, name, method, path, ids, fields, mode):
    route = respx.patch("https://sandbox.kaiten.ru/api/latest" + path).mock(
        return_value=Response(200, json={"id": 20})
    )
    result = invoke(runner, name, ids | fields, mode, tmp_path)
    assert result.exit_code == 0, result.output
    assert json.loads(route.calls.last.request.content) == fields


@pytest.mark.parametrize("locale", ["en", "ru"])
@pytest.mark.parametrize("query", ["column auto archive", "автоархивация колонок"])
def test_auto_archive_search_exposes_write_commands(locale, query):
    with use_locale(locale):
        names = {tool.canonical_name for tool in search(query, limit=5)}
    assert {"columns.create", "columns.update", "subcolumns.create", "subcolumns.update"} <= names
