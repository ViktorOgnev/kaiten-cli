from __future__ import annotations

import json

from kaiten_cli.app import cli, main


def test_help_shows_top_level_commands(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Kaiten API CLI optimized for humans and agents." in result.output
    assert "kaiten agent-help" in result.output
    assert "https://github.com/ViktorOgnev/kaiten-cli" in result.output
    assert "search-tools" in result.output
    assert "agent-help" in result.output
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


def test_agent_help_returns_quickstart_and_docs(runner):
    result = runner.invoke(cli, ["--json", "agent-help"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["success"] is True
    assert payload["command"] == "agent-help"
    assert payload["data"]["summary"] == "Kaiten API CLI optimized for humans and agents."
    assert payload["data"]["llm_bootstrap"]
    assert payload["data"]["llm_bootstrap"][0].startswith("Discover first:")
    assert payload["data"]["quickstart"]
    assert payload["data"]["docs"]["repository"] == "https://github.com/ViktorOgnev/kaiten-cli"
    assert payload["data"]["docs"]["skills"]["heavy_data"].endswith("/skills/kaiten-cli-heavy-data/SKILL.md")


def test_agent_help_human_output_is_bootstrap_focused(runner):
    result = runner.invoke(cli, ["agent-help"])

    assert result.exit_code == 0
    assert "Kaiten agent bootstrap" in result.output
    assert "LLM bootstrap:" in result.output
    assert 'discover: kaiten search-tools "wip cards"' in result.output
    assert "skills heavy-data:" in result.output
