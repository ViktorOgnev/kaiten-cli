from __future__ import annotations

import json

from click import Group

from kaiten_cli.app import cli, main


def _visible_command_paths(command, path=()):
    yield path, command
    if isinstance(command, Group):
        for name, child in command.commands.items():
            if getattr(child, "hidden", False):
                continue
            yield from _visible_command_paths(child, path + (name,))


def test_help_shows_top_level_commands(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Kaiten API CLI optimized for humans and agents." in result.output
    assert "kaiten agent-help" in result.output
    assert "https://github.com/ViktorOgnev/kaiten-cli" in result.output
    assert "COMMAND_REFERENCE.md" in result.output
    assert "search-tools" in result.output
    assert "agent-help" in result.output
    assert "describe" in result.output
    assert "examples" in result.output
    assert "completion" in result.output
    assert "profile" in result.output
    assert "snapshot" in result.output
    assert "query" in result.output
    assert "cards" in result.output
    assert "spaces" in result.output
    assert "boards" in result.output
    assert "Search commands with usage guidance." in result.output
    assert "Карточки, bulk reads и card-heavy workflows." in result.output
    assert "Spaces and top-level workspace reads." in result.output
    assert "Local-only query and metrics commands over" in result.output
    assert "Manage Kaiten profiles." in result.output
    assert "Manage Bash and Zsh completion." in result.output


def test_all_visible_commands_support_short_help(runner):
    for path, command in _visible_command_paths(cli):
        result = runner.invoke(cli, [*path, "-h"] if path else ["-h"])
        assert result.exit_code == 0, path
        assert "Usage:" in result.output, path
        assert command.help or command.short_help, path


def test_namespace_help_shows_dynamic_commands(runner):
    result = runner.invoke(cli, ["cards", "--help"])
    assert result.exit_code == 0
    assert "Карточки, bulk reads и card-heavy workflows." in result.output
    assert "Contains 11 commands under:" in result.output
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
    assert (
        "kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active"
        in payload["error"]["message"]
    )
    assert "export KAITEN_DOMAIN=<company-subdomain-or-url>" in payload["error"]["message"]


def test_agent_help_returns_quickstart_and_docs(runner):
    result = runner.invoke(cli, ["--json", "agent-help"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["success"] is True
    assert payload["command"] == "agent-help"
    assert payload["data"]["summary"] == "Kaiten API CLI optimized for humans and agents."
    assert payload["data"]["llm_bootstrap"]
    assert payload["data"]["llm_bootstrap"][0].startswith("Discover first:")
    assert any("snapshot" in line for line in payload["data"]["llm_bootstrap"])
    assert payload["data"]["quickstart"]
    assert payload["data"]["docs"]["repository"] == "https://github.com/ViktorOgnev/kaiten-cli"
    assert payload["data"]["docs"]["command_reference"].endswith("/COMMAND_REFERENCE.md")
    assert payload["data"]["docs"]["skills"]["heavy_data"].endswith(
        "/skills/kaiten-cli-heavy-data/SKILL.md"
    )


def test_agent_help_human_output_is_bootstrap_focused(runner):
    result = runner.invoke(cli, ["agent-help"])

    assert result.exit_code == 0
    assert "Kaiten agent bootstrap" in result.output
    assert "LLM bootstrap:" in result.output
    assert 'discover: kaiten search-tools "wip cards"' in result.output
    assert "snapshot once for repeated analytics" in result.output
    assert "command reference:" in result.output
    assert "skills heavy-data:" in result.output


def test_discovery_commands_human_output_is_not_raw_json(runner):
    search = runner.invoke(cli, ["search-tools", "cards"])
    assert search.exit_code == 0
    assert not search.output.lstrip().startswith("[")
    assert "Search results for: cards" in search.output
    assert "CLI: kaiten cards list" in search.output
    assert "Next: kaiten describe" in search.output

    describe = runner.invoke(cli, ["describe", "cards.list-all"])
    assert describe.exit_code == 0
    assert not describe.output.lstrip().startswith("{")
    assert "Description: Fetch all cards matching filters" in describe.output
    assert "Arguments:" in describe.output
    assert "--board-id (integer, optional)" in describe.output
    assert "Examples:" in describe.output

    chart_description = runner.invoke(cli, ["describe", "charts.summary.get"])
    assert chart_description.exit_code == 0
    assert "mutation=yes" in chart_description.output
    assert "read-only=allowed" in chart_description.output
    assert "remote-effects=no" in chart_description.output

    examples = runner.invoke(cli, ["examples", "cards.list-all"])
    assert examples.exit_code == 0
    assert not examples.output.lstrip().startswith("{")
    assert "Examples for: cards.list-all" in examples.output
    assert "1. kaiten cards list-all" in examples.output


def test_discovery_commands_json_output_stays_machine_readable(runner):
    search = runner.invoke(cli, ["--json", "search-tools", "cards"])
    assert search.exit_code == 0
    search_payload = json.loads(search.output)
    assert search_payload["success"] is True
    assert search_payload["command"] == "search-tools"
    assert isinstance(search_payload["data"], list)
    assert search_payload["data"][0]["canonical_name"]

    describe = runner.invoke(cli, ["--json", "describe", "cards.list-all"])
    assert describe.exit_code == 0
    describe_payload = json.loads(describe.output)
    assert describe_payload["success"] is True
    assert describe_payload["command"] == "describe"
    assert describe_payload["data"]["canonical_name"] == "cards.list-all"

    examples = runner.invoke(cli, ["--json", "examples", "cards.list-all"])
    assert examples.exit_code == 0
    examples_payload = json.loads(examples.output)
    assert examples_payload["success"] is True
    assert examples_payload["command"] == "examples"
    assert examples_payload["data"]["examples"][0].startswith("kaiten cards list-all")
