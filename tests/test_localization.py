from __future__ import annotations

import asyncio
import copy
import importlib.util
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import click
import httpx
import pytest
import respx

from kaiten_cli.app import cli, main
from kaiten_cli.discovery import describe_tool, search_tools
from kaiten_cli.errors import ApiError
from kaiten_cli.i18n import catalog, get_locale, localize_schema, tr, use_locale
from kaiten_cli.localized_click import resolve_locale
from kaiten_cli.registry import describe, iter_tools
from kaiten_cli.runtime.output import render_error, render_success


@pytest.fixture(autouse=True)
def locale_environment(monkeypatch):
    monkeypatch.delenv("KAITEN_CLI_LOCALE", raising=False)


@pytest.mark.parametrize(
    "args,env,expected",
    [
        ([], None, "en"),
        ([], "ru", "ru"),
        (["--locale", "en"], "ru", "en"),
        (["--locale=ru"], "en", "ru"),
        (["--locale", "ru", "--locale=en"], None, "en"),
        (["cards", "create", "--title", "--locale=ru"], None, "en"),
        (["--", "--locale=ru"], None, "en"),
        (["--profile", "--locale=ru", "--json"], None, "en"),
        (["--json", "--profile", "main", "--locale", "ru"], "bad", "ru"),
    ],
)
def test_locale_precedence(args, env, expected, monkeypatch):
    monkeypatch.setenv("LANG", "ru_RU.UTF-8")
    monkeypatch.setenv("LC_ALL", "ru_RU.UTF-8")
    if env is not None:
        monkeypatch.setenv("KAITEN_CLI_LOCALE", env)
    assert resolve_locale(args) == expected


@pytest.mark.parametrize(
    "args", [["--locale", "de"], ["--locale"], ["--locale="], ["--locale", "RU"]]
)
def test_invalid_locale_is_structured_validation_error(args, capsys):
    assert main(["--json", *args, *([] if args == ["--locale"] else ["--help"])]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["type"] == "validation_error"
    assert "ru or en" in result["error"]["message"]
    assert get_locale() == "en"


def test_invalid_environment_can_be_overridden(runner, monkeypatch):
    monkeypatch.setenv("KAITEN_CLI_LOCALE", "xx")
    assert runner.invoke(cli, ["--help"]).exit_code == 2
    assert runner.invoke(cli, ["--locale", "ru", "--help"]).exit_code == 0


def command_paths(command, path=()):
    yield path
    if isinstance(command, click.Group):
        for name, child in command.commands.items():
            yield from command_paths(child, (*path, name))


def test_all_help_and_aliases_translate_without_mutating_commands(runner):
    for path in command_paths(cli):
        english = runner.invoke(cli, ["--locale", "en", *path, "--help"])
        russian = runner.invoke(cli, ["--locale", "ru", *path, "--help"])
        again = runner.invoke(cli, ["--locale", "en", *path, "--help"])
        assert english.exit_code == russian.exit_code == again.exit_code == 0, path
        assert english.output == again.output, path
        assert "Usage:" in english.output and "Использование:" in russian.output, path
        assert not re.search("[А-Яа-яЁё]", english.output), path
        assert "Show this message and exit." not in russian.output, path
    assert get_locale() == "en"


def remove_schema_prose(value):
    if isinstance(value, dict):
        return {
            k: remove_schema_prose(v) for k, v in value.items() if k not in ("title", "description")
        }
    if isinstance(value, list):
        return [remove_schema_prose(v) for v in value]
    return value


def remove_contract_prose(payload):
    result = copy.deepcopy(payload)
    result.pop("description")
    result.pop("usage_notes", None)
    result["input_schema"] = remove_schema_prose(result["input_schema"])
    for arg in result["arguments"]:
        arg.pop("description")
    for key in ("guidance", "refresh_hint", "off_hint", "readwrite_hint"):
        result["cache_guidance"].pop(key, None)
    if "live_contract" in result:
        result["live_contract"].pop("note")
    return result


def test_all_discovery_contracts_preserve_machine_fields_and_source():
    for tool in iter_tools():
        original = copy.deepcopy(describe(tool.canonical_name))
        with use_locale("ru"):
            russian = describe_tool(tool.canonical_name)
        english = describe_tool(tool.canonical_name)
        assert english == original == describe(tool.canonical_name)
        assert russian["description"] == catalog()[original["description"]]
        assert remove_contract_prose(russian) == remove_contract_prose(english)
        assert not re.search("[А-Яа-яЁё]", original["description"])
        assert all(not re.search("[А-Яа-яЁё]", note) for note in original.get("usage_notes", []))


@pytest.mark.parametrize(
    "query",
    [
        "карточки",
        "cards",
        "справочник таблица",
        "поле карточки справочник",
        "чеклисты",
        "комментарии",
    ],
)
def test_search_language_is_independent_of_output_locale(query):
    english = search_tools(query, limit=10)
    with use_locale("ru"):
        russian = search_tools(query, limit=10)
    assert english
    assert [x["canonical_name"] for x in english] == [x["canonical_name"] for x in russian]
    assert russian[0]["description"] == catalog()[english[0]["description"]]


def test_schema_translation_does_not_touch_defaults_enums_or_user_keys():
    schema = {
        "type": "object",
        "title": "Card",
        "properties": {
            "Card": {
                "description": "Card",
                "default": {"description": "Card"},
                "enum": ["Card", "Карточка"],
                "examples": ["Card"],
                "pattern": "Card",
            },
            "free": True,
        },
        "oneOf": [True, False],
    }
    original = copy.deepcopy(schema)
    with use_locale("ru"):
        result = localize_schema(schema)
    assert schema == original
    assert result["title"] == result["properties"]["Card"]["description"] == "Карточка"
    assert result["properties"]["Card"]["default"] == {"description": "Card"}
    for key in ("enum", "examples", "pattern"):
        assert result["properties"]["Card"][key] == original["properties"]["Card"][key]
    assert result["oneOf"] == [True, False]


def test_success_and_api_data_are_not_translated():
    data = {
        "title": "Card",
        "description": "Attachments",
        "error": "OK",
        "text": "Смешанный user content",
    }
    api_error = ApiError(400, "Card", body=data)
    english = render_success("cards.get", data, True)
    with use_locale("ru"):
        assert render_success("cards.get", data, True) == english
        assert render_success("cards.get", "Card", False) == "Card"
        result = json.loads(render_error("cards.get", api_error, True))
        assert result["error"]["message"] == "Card"
        assert result["error"]["body"] == data


def test_locale_resets_after_exceptions_and_nesting():
    with use_locale("ru"):
        with pytest.raises(RuntimeError), use_locale("en"):
            raise RuntimeError("boom")
        assert tr("Card") == "Карточка"
    assert get_locale() == "en"


def test_concurrent_threads_are_isolated():
    barrier = Barrier(2)

    def worker(locale):
        with use_locale(locale):
            barrier.wait()
            message = click.MissingParameter(
                param_hint="title", param_type="argument"
            ).format_message()
            return get_locale(), tr("Card"), message

    with ThreadPoolExecutor(max_workers=2) as pool:
        en = pool.submit(worker, "en")
        ru = pool.submit(worker, "ru")
        assert en.result()[:2] == ("en", "Card")
        assert ru.result()[:2] == ("ru", "Карточка")
        assert "Missing" in en.result()[2]
        assert "Missing" not in ru.result()[2]


@pytest.mark.asyncio
async def test_async_contexts_are_isolated():
    async def worker(locale):
        with use_locale(locale):
            await asyncio.sleep(0)
            return tr("Card")

    assert await asyncio.gather(worker("ru"), worker("en")) == ["Карточка", "Card"]


@pytest.mark.parametrize(
    "args",
    [["describe"], ["cards", "list", "--limit", "oops"], ["cards", "list", "--locale", "ru"]],
)
def test_parser_errors_are_localized_but_codes_are_stable(args, capsys):
    payloads = []
    for locale in ("en", "ru"):
        assert main(["--locale", locale, "--json", *args]) == 2
        payloads.append(json.loads(capsys.readouterr().out))
    assert payloads[0]["error"]["type"] == payloads[1]["error"]["type"] == "validation_error"
    assert payloads[0]["error"]["message"] != payloads[1]["error"]["message"]
    assert re.search("[А-Яа-яЁё]", payloads[1]["error"]["message"])
    assert get_locale() == "en"


def test_config_errors_and_agent_help_are_localized(runner, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)
    result = runner.invoke(cli, ["--locale", "ru", "--json", "cards", "list"])
    assert result.exit_code == 3
    payload = json.loads(result.output)
    assert payload["error"]["type"] == "config_error"
    assert "Missing Kaiten credentials." not in payload["error"]["message"]
    assert re.search("[А-Яа-яЁё]", payload["error"]["message"])
    for locale in ("en", "ru"):
        result = runner.invoke(cli, ["--locale", locale, "--json", "agent-help"])
        assert result.exit_code == 0
        assert "--locale ru" in result.output and "--locale en" in result.output


@respx.mock
def test_http_data_is_preserved_and_request_locale_is_not_forwarded(runner, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    card = {"id": 1, "title": "Card", "description": "Attachments"}
    route = respx.get("https://sandbox.kaiten.ru/api/latest/cards/1").mock(
        return_value=httpx.Response(200, json=card)
    )
    for locale in ("en", "ru"):
        result = runner.invoke(
            cli,
            ["--locale", locale, "--cache-mode", "off", "--json", "cards", "get", "--card-id", "1"],
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["data"] == card
    assert len(route.calls) == 2
    first, second = (call.request for call in route.calls)
    assert first.url == second.url and first.content == second.content
    assert first.headers == second.headers


def test_completion_source_is_locale_independent(runner):
    outputs = []
    for locale in ("en", "ru"):
        result = runner.invoke(cli, ["--locale", locale, "completion", "source", "bash"])
        assert result.exit_code == 0, result.output
        outputs.append(result.output)
    assert outputs[0] == outputs[1]


def test_gateway_passes_locale_to_child_and_instructs_agent():
    from kaiten_cli.agent_gateway import CODEX_ENV_ALLOWLIST, SYSTEM_PROMPT

    assert "KAITEN_CLI_LOCALE" in CODEX_ENV_ALLOWLIST
    assert "--locale ru or --locale en" in SYSTEM_PROMPT


def test_catalog_coverage_and_interpolation():
    path = Path(__file__).resolve().parents[1] / "scripts/check_locales.py"
    spec = importlib.util.spec_from_file_location("check_locales", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []
    assert list(module.unlocalized_message_calls('raise ValidationError("New error")'))
    assert list(module.unlocalized_message_calls('reporter(f"Retry {count}")'))
    assert not list(module.unlocalized_message_calls('raise ValidationError(tr("New error"))'))
    assert not list(module.unlocalized_message_calls("click.echo(api_response)"))


def test_markdown_only_translates_generated_headings():
    from kaiten_cli.runtime.support.markdown_export import card_to_markdown, document_to_markdown

    card = {"id": 1, "title": "Card", "description": "Attachments"}
    files = [{"id": 2, "name": "Document"}]
    english = card_to_markdown(card, files)
    with use_locale("ru"):
        russian = card_to_markdown(card, files)
        assert "# Документ" in document_to_markdown({})
    assert russian == english.replace("## Attachments", "## Вложения")
    assert "# Card" in russian and "[Document]" in russian


@pytest.mark.asyncio
async def test_batch_worker_errors_inherit_locale_and_preserve_user_values(monkeypatch):
    from kaiten_cli.errors import ValidationError
    from kaiten_cli.runtime.client import KaitenClient
    from kaiten_cli.runtime.input import coerce_value
    from kaiten_cli.runtime.support.batch import fetch_card_entity_batch

    async def fake_get(self, path, **kwargs):
        await asyncio.sleep(0)
        if path.endswith("/2"):
            coerce_value("bad", {"type": "integer"}, label="Card")
        return {"title": "Card"}

    monkeypatch.setattr(KaitenClient, "get", fake_get)
    results = []
    for locale in ("en", "ru"):
        with use_locale(locale):
            results.append(
                await fetch_card_entity_batch(
                    domain="sandbox",
                    token="unused",
                    card_ids=[1, 2],
                    workers=2,
                    timeout=1,
                    reporter=None,
                    path_for_card=lambda card_id: f"/cards/{card_id}",
                    result_field="card",
                    transform_item=lambda item: item,
                    worker_label="test",
                )
            )
    assert results[0]["items"] == results[1]["items"] == [{"card_id": 1, "card": {"title": "Card"}}]
    en, ru = (result["errors"][0] for result in results)
    assert en["error_type"] == ru["error_type"] == "validation_error"
    assert en["message"] != ru["message"] and "Card" in ru["message"]
    assert "Карточка" not in ru["message"]
    with use_locale("ru"), pytest.raises(ValidationError):
        coerce_value("bad", {"type": "integer"}, label="Card")
