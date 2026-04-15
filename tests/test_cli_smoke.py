from __future__ import annotations

import json

from kaiten_cli.app import cli, main


def test_help_shows_top_level_commands(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "search-tools" in result.output
    assert "describe" in result.output
    assert "examples" in result.output
    assert "profile" in result.output
    assert "cards" in result.output
    assert "spaces" in result.output
    assert "boards" in result.output


def test_namespace_help_shows_dynamic_commands(runner):
    result = runner.invoke(cli, ["cards", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output
    assert "create" in result.output
    assert "update" in result.output
    assert "delete" in result.output


def test_namespace_without_subcommand_shows_help_without_config_error(capsys):
    exit_code = main(["cards"])
    captured = capsys.readouterr()
    combined = captured.out + captured.err

    assert exit_code == 0
    assert "Usage: kaiten cards" in combined
    assert "Config error" not in combined


def test_profile_group_without_subcommand_shows_help_without_config_error(capsys):
    exit_code = main(["profile"])
    captured = capsys.readouterr()
    combined = captured.out + captured.err

    assert exit_code == 0
    assert "Usage: kaiten profile" in combined
    assert "Config error" not in combined


def test_usage_errors_are_reported_as_validation_errors(capsys):
    exit_code = main(["describe"])
    captured = capsys.readouterr()
    combined = captured.out + captured.err

    assert exit_code == 2
    assert "Validation error: Missing argument 'IDENTIFIER'." in combined
    assert "Config error" not in combined


def test_json_config_error_envelope_contains_guidance(runner, config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)

    result = runner.invoke(cli, ["--json", "cards", "list"])
    payload = json.loads(result.output)

    assert result.exit_code == 3
    assert payload["success"] is False
    assert payload["error"]["type"] == "config_error"
    assert "Missing Kaiten credentials." in payload["error"]["message"]
    assert "kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active" in payload["error"]["message"]
    assert "export KAITEN_DOMAIN=<company-subdomain>" in payload["error"]["message"]
