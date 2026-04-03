from __future__ import annotations

from kaiten_cli.app import cli


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

